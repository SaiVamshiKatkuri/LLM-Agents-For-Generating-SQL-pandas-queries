class CustomException(Exception):
    def __init__(self, message=""):
        self.error_msg = ""
        super().__init__(message)

class InvalidInputException(CustomException):
    def __init__(self, message="Invalid Input"):
        super().__init__(message)

class UserAlreadyExistsException(CustomException):
    def __init__(self, username=""):
        message = f"{username} already exists! Please login instead!!"
        super().__init__(message)

class InvalidInputQueryException(CustomException):
    def __init__(self):
        message = "Potentially unsafe operations detected, so not executing the code!!"
        self.error_msg = message
        super().__init__(message)

class InvalidFileTypeException(CustomException):
    def __init__(self, filename):
        message = f"Currently, we only process csv files. {filename} is not a csv file!!"
        self.error_msg = "Unsupported file format. Please upload csv file!"
        super().__init__(message)