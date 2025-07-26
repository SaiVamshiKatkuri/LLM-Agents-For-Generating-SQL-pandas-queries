# LLM-Powered Query Processing for CSVs

## Contents
- [Introduction](#introduction)
- [High Level Features](#high-level-features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Frontend Setup](#frontend-setup)
  - [Backend Setup](#backend-setup)
  - [AWS setup](#aws-setup)
    - [Prerequisites](#prerequisites)
    - [AWS Resources](#aws-resources)
        - [Create S3 Bucket](#1-create-s3-bucket)
        - [Create Dynamodb Tables](#2-create-dynamodb-tables)
        - [Permissions](#3-permissions)
  - [Environment Variables](#environment-variables)
- [Running](#running)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [Unit Testing](#unit-testing)
- [AI Models](#ai-models)
- [Demo Video](#demo-video)

---

## Introduction

This project leverages advanced Large Language Models (LLMs) to simplify querying and processing data from CSV files. It allows users to input natural language queries, converting them into precise SQL or Pandas commands. Designed for non-technical users and data analysts, the tool streamlines data operations and enhances accessibility. With support for text and voice inputs, it enables seamless interaction with uploaded datasets. The system generates accurate results, downloadable in CSV format, making data analysis intuitive and efficient.



## High Level Features  
- **User Authentication**: Users can register and login to the application
- **Natural Language Interface**: Accepts queries natural language queries in englist, through text and voice based inputs.  
- **User Spaces**: User can view all his uploaded csv files, upload new file, delete existing files.
- **Query Generation**: Converts user inputs into SQL or Pandas queries on the given csv file using LLMs.
- **Data Processing**: Returns downloadable results in `.csv` format.

---

## Technologies Used
- **Frontend**: `Angular` for an interactive user interface.  
- **Backend**: `Flask` for handling the backend, and `LangChain` for interfacing with the LLM.  
- **Database**: `AWS DynamoDB` for scalable cloud data storage.  
<!-- - **Deployment**: Docker for containerization and AWS/GCP for cloud deployment.   -->

---

## Installation  

### Frontend Setup  
1. Install Node.js: [Download here](https://nodejs.org/).  
2. Run the following commands:  
```bash  
   npm install -g @angular/cli  
   cd csv-query-app  
   npm install crypto-js  
   npm install prismjs
   npm install --save-dev @types/prismjs
```

### Backend Setup  
Install dependencies. Run from inside `520_Project/`:
```bash
    conda create -n querygenai python==3.10
    conda activate querygenai
    pip install -r requirements.txt
```

### AWS setup
Here’s a detailed explanation for creating and configuring the S3 bucket and DynamoDB tables. You can include the following instructions in your `README.md` file:


This project uses AWS services for storing user-uploaded files and relevant metadata. Below are the steps to configure the required AWS resources.

---

### Prerequisites

Ensure you have the following set up:
1. **AWS CLI** installed ([Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)).
2. An **AWS Account** with sufficient permissions to create S3 buckets and DynamoDB tables.
3. **IAM User/Role** with the following policies:
   - `AmazonS3FullAccess`
   - `AmazonDynamoDBFullAccess`

---

### AWS Resources

#### 1. Create S3 Bucket
The S3 bucket is used to store user-uploaded files.

##### S3 Bucket Details
- **Bucket Name**: `llm-query-generator`
- **Region**: `<your-region>`  `[us-east-1]`

##### Steps to Create the S3 Bucket
1. Open the AWS Management Console and navigate to the **S3 Service**.
2. Click **Create Bucket**.
3. Enter `llm-query-generator` as the **Bucket Name**.
4. Select your preferred **Region**.
5. Enable/Disable any additional settings like versioning or encryption based on your requirements.
6. Click **Create Bucket**.

##### Configure Bucket Policies
To ensure proper access to the bucket:
1. Go to the **Permissions** tab of your S3 bucket.
2. Add a bucket policy to allow read/write access for your application (modify `<AWS-Account-ID>` as needed):

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "AllowPutGet",
               "Effect": "Allow",
               "Principal": "*",
               "Action": ["s3:GetObject", "s3:PutObject"],
               "Resource": "arn:aws:s3:::llm-query-generator/*"
           }
       ]
   }
   ```

3. Save the policy.


#### 2. Create DynamoDB Tables

The DynamoDB tables store metadata related to users and their files.


| Table Name           | Purpose                              | Primary Key            |
|----------------------|--------------------------------------|------------------------|
| `llm-user-files`     | Tracks files uploaded by users       | `user_id` (String)     |
| `llm-user-table`     | Stores user details                 | `user_id` (String)     |

#### Steps to Create Each Table
1. Open the AWS Management Console and navigate to **DynamoDB Service**.
2. Click **Create Table**.
3. Enter the **Table Name** and **Primary Key** based on the table details above.
4. Leave **Sort Key** empty for `llm-user-table`.
5. Configure the **Read/Write capacity** (choose On-Demand or Provisioned as needed).
6. Click **Create Table**.

#### CLI Commands (Optional)
To create the tables via CLI:

```bash
# Create llm-user-files table
aws dynamodb create-table \
    --table-name llm-user-files \
    --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=file_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH AttributeName=file_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

# Create llm-file-table
aws dynamodb create-table \
    --table-name llm-file-table \
    --attribute-definitions AttributeName=file_id,AttributeType=S AttributeName=timestamp,AttributeType=S \
    --key-schema AttributeName=file_id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

# Create llm-user-table
aws dynamodb create-table \
    --table-name llm-user-table \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

---

### 3. Permissions
Ensure the application has IAM permissions to access these resources. Below is an example IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::llm-query-generator",
                "arn:aws:s3:::llm-query-generator/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
            "Resource": [
                "arn:aws:dynamodb:<your-region>:<AWS-Account-ID>:table/llm-user-files",
                "arn:aws:dynamodb:<your-region>:<AWS-Account-ID>:table/llm-file-table",
                "arn:aws:dynamodb:<your-region>:<AWS-Account-ID>:table/llm-user-table"
            ]
        }
    ]
}
```


### Environment Variables
Since we are using LLMs via the OpenAI API, the key needs to be set in the environment variables. For this, create a `.env` file inside of `backend/app/Api` with the following configuration:
```bash
    OPENAI_API_KEY="YOUR_KEY_HERE"
```

## Running

### Frontend
Open a terminal and run the following:
```bash
    cd csv-query-app  
    ng serve --configuration production
```

### Backend
Open another terminal and run the following:
```bash
    cd backend
    python run.py
```

Now the website can be visited at `http://localhost:4200/`.

## Unit Testing
For unit testing, run the following:
```bash
    cd backend/tests/
    pytest test_api_models.py        # tests the User and UserFile models used in the backend
    pytest test_sql_agent.py         # tests API for the SQL agent
    pytest test_pandas_agent.py      # tests API for the Pandas agent
    pytest test_validation.py        # tests query validation         
```
Alternatively, one can run all tests at once using `pytest *.py`

## AI Models

We use the following LLM models for processing results for various agents
```
Model for Pandas Agent = "gpt-3.5-turbo-instruct"
Model for SQL Agent = "gpt-4o-mini"
```

## Demo Video:
https://drive.google.com/file/d/1WT693CTNA-ejxAjdLeu0GIlnYCjIxB4Y/view?usp=sharing

## Report
https://github.com/Avi-2362/LLM-agents-for-SQL-Pandas-query-generation/blob/main/report.pdf

## Final Presentation Slides
https://github.com/Avi-2362/LLM-agents-for-SQL-Pandas-query-generation/blob/main/FinalPresentation.pdf
