from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, object_name: str, headers = None):
        if object_name:
            object_name = object_name.capitalize()
            detail = f"{object_name} not found"
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)

    
class InternalServerException(HTTPException):
    def __init__(self, detail = None, headers = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)