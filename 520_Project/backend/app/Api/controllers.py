import pandas as pd
import uuid
from datetime import datetime
from flask import Blueprint, Flask, jsonify, request, redirect
from flask_classful import FlaskView, route
# from flask_cors import cross_origin
# from flask import make_response, request, current_app
# from datetime import timedelta, datetime
# from functools import update_wrapper
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from app.Api.llm_agent import process_pandas_result_to_json, query_pandas_agent, query_sql_agent
from app.Api.models import *
from app.Api.exceptions import *
from app.Api.enums import *
from app.Api.errors import *
# import logger
from app.logger import logger


allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]

class UserResource(FlaskView):
    """
    A resource class for handling user-related operations, such as file management and S3 upload URL generation.
    """

    route_base = '/api/user/'
    # route_base = '/'

    @route('all/files', methods=['GET','POST'])
    @jwt_required()
    def get_user_files(self):
        """
        Retrieve all files associated with the current user.

        Returns:
            JSON: A JSON response containing the list of user files.
        """
        user_id = get_jwt_identity()
        user = User.get(user_id) 
        logger.info(f"username: {user['user_id']}")
        return jsonify(UserFiles.get(user['user_id']))
    
    @route('delete/file', methods=['GET','POST'])
    @jwt_required()
    def delete_user_file(self):
        """
        Delete a specific file from the user's file list.

        Returns:
            JSON: A success message if the file is deleted, or an error message on failure.
        """
        user_id = get_jwt_identity()
        user = User.get(user_id) 
        file_id = request.json.get('file_id')
        remove_file = None
        try:
            userFiles = UserFiles.get(user['user_id'])
            logger.info(f"user files: {userFiles}")
            for file in userFiles['files']:
                if file['file_id'] == file_id:
                    remove_file  = file
                    break
            userFiles['files'].remove(remove_file)
            userFiles = UserFiles.from_dict(userFiles)
            userFiles.put()
            return jsonify({'msg':'success'}), 200
        except Exception as ex:
            logger.error(ex)
            return jsonify({'error': FILE_DELETE_ERROR_MESSAGE}), 400


    @route('upload/file', methods=['POST'])
    @jwt_required()
    def upload_file(self):
        """
        Upload file metadata to associate it with the user.

        Request Body:
            user_id (str): The ID of the user.
            file (dict): A dictionary containing 'filename', 'file_id', and 'size'.

        Returns:
            JSON: The updated list of user files.

        ## This function should be called after generate-upload-url from frontend
        request body:
        {
            'user_id': <user_id>,
            'file': {
                'filename': <filename>,
                'file_id': <file_id>,
                'size': <file-size-kb>
            }
        }
        """
        # user_id = request.json.get('user_id') # TODO: need to get from jwt_identity
        user_id = get_jwt_identity()
        userFiles = UserFiles.get(user_id)
        # current file
        filename = request.json.get('filename')
        file_id = request.json.get('file_id')
        date = str(datetime.utcnow())
        logger.info(request.json)
        logger.info(f"filename: {filename}")
        userFiles['files'].append({
            "filename": filename,
            "file_id": file_id,
            "date": date
        })
        userFiles = UserFiles.from_dict(userFiles)
        logger.info(userFiles)
        userFiles.put() # put in user-files
        logger.info("Successfully updated userfiles")
        return jsonify(userFiles.to_json())
    
    @route('generate-upload-url', methods=['GET'])
    def generate_upload_url(self):
        """
        Generate a presigned S3 URL for uploading a file.

        Query Parameters:
            filename (str): The name of the file being uploaded.

        Returns:
            JSON: The presigned upload URL and a unique file ID.
        """
        file_id = str(uuid.uuid4())
        try:
            filename = request.args.get('filename')
            logger.info(filename)
            if filename.split(".")[-1]!="csv":
                raise InvalidFileTypeException(filename)
            params = {
                'Bucket': S3_BUCKET_NAME,
                'Key': file_id,
                'ContentType': 'text/csv'
            }
            url = s3_client.generate_presigned_url('put_object', Params=params, ExpiresIn=600)
            return jsonify({
                'url': url,
                'file_id': file_id
                })
        except InvalidFileTypeException as e:
            logger.error(e)
            return jsonify({"error": INVALID_FILE_UPLOAD_ERROR})
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(e)
            return jsonify({'error': CREDENTIALS_ERROR}), 500
        except Exception as e:
            logger.error(e)
            return jsonify({'error': GENERATE_UPLOAD_URL_ERROR}), 500

    # @route('view/file-url', methods=['GET'])
    @route('generate-view-url', methods=['GET'])
    def generate_view_url(self):
        """
        Generate a presigned S3 URL for viewing a file.

        Query Parameters:
            file_id (str): The ID of the file to view.

        Returns:
            JSON: The presigned view URL.
        """
        try:
            file_id = request.args.get('file_id')
            params = {
                'Bucket': S3_BUCKET_NAME,
                'Key': file_id
            }
            url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
            logger.info(url)
            return jsonify({'url': url})
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(e)
            return jsonify({'error': CREDENTIALS_ERROR}), 500
        except Exception as e:
            logger.error(e)
            return jsonify({'error': GENERATE_DOWNLOAD_URL_ERROR}), 500

    
class AuthResource(FlaskView):
    """
    A resource class for handling authentication operations, such as login, logout, and user registration.
    """
    route_base = '/'

    @route('hello', methods=['GET', 'POST', 'OPTIONS'])
    def health_check(self):
        """
        A simple health check endpoint.

        Returns:
            JSON: A message indicating the service is running.
        """
        logger.info("Accessed Hello method")
        return jsonify({'hello': "hello"})
    
    @route('new_user', methods=['POST'])
    def add_new_user(self):
        """
        Register a new user.

        Request Body:
            username (str): The username of the user.
            name (str): The name of the user.
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.

        Returns:
            JSON: A message indicating success or failure of the registration.
        """
        username = request.json.get('username')
        name = request.json.get('name')
        email = request.json.get('email')
        hashed_password = request.json.get('hashed_password')
        data = {
            "username": username,
            "name": name,
            "email": email,
            "hashed_password": hashed_password
        }
        logger.info(data)
        try:
            # data.keys = ('username', 'name', 'email')
            # check if the user already exists
            logger.info(f"username: {data['username']}")
            user = User.get(data['username'])
            logger.info(user)
            if user is not None:
                user = User.from_dict(user)
                raise UserAlreadyExistsException(user.username)
            
            user, status = User.validate_nd_make_user(data)
            if status==Status.VALID:
                # 1. Add the user in user table
                user.put()
                logger.info("put the user!!")
                # 2. Add in user files table
                usr_files = UserFiles(user.user_id, files=[])
                usr_files.put()

            return jsonify({
                "msg": "New user added successfully!!"
            })
        except InvalidInputException as e:
            logger.error(f"error-1 : {e}")
            return jsonify({
                "error": str(e)
            }),400
        except UserAlreadyExistsException as e:
            logger.error(f"error-2: {e}")
            return jsonify({
                "error": USER_ALREADY_EXISTS_ERROR
            }),400
        except Exception as e:
            logger.error(f"error-3: {e.with_traceback()}")
            return jsonify({
                "error": f"{e}"
            }),404
        
    
    @route('login', methods=['POST'])
    def login(self):
        """
        Log in a user and generate a JWT token.

        Request Body:
            user_id (str): The ID of the user.
            password (str): The hashed password of the user.

        Returns:
            JSON: A success message with the JWT token or an error message on failure.
        """
        user_id = request.json.get('user_id')
        password = request.json.get('hashed_password')
        try: 
            resp = User.get(user_id)
            logger.info(resp)
            if resp is not None and resp['hashed_password']==password:
                access_token = create_access_token(identity=user_id)
                logger.info(f"created access token for user: {user_id}")
                response = jsonify({"msg": "Login successful"})
                set_access_cookies(response, access_token)  # Set JWT token as a cookie
                return response, 200
            else:
                logger.info("Wrong username or password!")
                return jsonify({"error": INVALID_CREDENTIALS_ERROR_MESSAGE}), 401
        except Exception as e:
            logger.error("error....",e)
            return jsonify({"error": INVALID_CREDENTIALS_ERROR_MESSAGE}), 401
    
    @route('auth_check', methods=['GET'])
    @jwt_required()
    def auth_check(self):
        """
        Check if the current user is authenticated.

        Returns:
            JSON: The user's authentication status.
        """
        current_user = get_jwt_identity()
        return jsonify(logged_in=True, user_id=current_user), 200

    @route("/logout", methods=["POST"])
    @jwt_required()
    def logout(self):
        """
        Log out the current user by clearing JWT cookies.

        Returns:
            JSON: A message indicating the user has logged out.
        """
        response = jsonify({"msg": "Logout successful"})
        unset_jwt_cookies(response)  # Clear JWT cookies
        logger.info("User logged out!!")
        return response, 200

class ApiResource(FlaskView):
    """
    A resource class for handling business logic, such as querying data in pandas or SQL.
    """
    route_base = '/'

    @route('get-pandas-query', methods=['POST'])
    @jwt_required()
    def get_pandas_query(self):
        """
        Generate and process a user query on a CSV file using pandas.

        Request Body:
            file_key (str): The S3 key of the file.
            query (str): The user's query.

        Returns:
            JSON: The results of the query or an error message on failure.
        """
        user_id=get_jwt_identity()
        logger.info(user_id)
        # Get CSV file key and user query from the request
        data = request.json
        file_key = data.get('file_key')
        user_query = data.get('query')

        if not file_key or not user_query:
            return jsonify({'error': FILE_KEY_QUERY_MISSING_ERROR}), 400

        # Get the file from S3
        params = {
                'Bucket': S3_BUCKET_NAME,
                'Key': file_key
            }
        try:
            url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
            logger.info(f'url: {url}')
            df = pd.read_csv(url)
            res = query_pandas_agent(df,user_query)
            llm_output = process_pandas_result_to_json(res)

            # Return the response back to the frontend
            return jsonify(llm_output), 200
        except InvalidInputQueryException as e:
            logger.error(e)
            return jsonify({"error": str(e)}),400
        except Exception as e:
            logger.error(e)
            return jsonify({"msg": "error"}), 404

    
    @route('get-sql-query', methods=['POST'])
    @jwt_required()
    def get_sql_query(self):
        """
        Generate  SQL query based on user input.

        Request Body:
            file_key (str): The S3 key of the file.
            query (str): The user's query.

        Returns:
            JSON: SQL query generated by LLM.
        """
        user_id=get_jwt_identity()
        logger.info(user_id)
        # Get CSV file key and user query from the request
        data = request.json
        file_key = data.get('file_key')
        user_query = data.get('query')

        if not file_key or not user_query:
            return jsonify({'error': FILE_KEY_QUERY_MISSING_ERROR}), 400

        # Get the file from S3
        params = {
                'Bucket': S3_BUCKET_NAME,
                'Key': file_key
            }
        try:
            url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
            logger.info(f'url: {url}')
            df = pd.read_csv(url)
            llm_output = query_sql_agent(df,user_query)

            # Return the response back to the frontend
            return jsonify(llm_output), 200
        except InvalidInputQueryException as e:
            logger.error(e)
            return jsonify({"error": str(e)}),400
        except Exception as e:
            logger.error(e)
            return jsonify({"msg": "error"}), 404