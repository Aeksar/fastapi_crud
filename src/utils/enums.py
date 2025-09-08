from enum import Enum

class TaskStatusEnum(str, Enum):
    CREATED = "создано"
    IN_WORK = "в работе"
    COMLETED = "завершено"

class UserRoleEnum(str, Enum):
    USER = "Пользователь"
    REDACTOR = "Редактор"
    ADMIN = "Администратор"
    
class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"

class TokenName(str, Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    VERIFICATION_TOKEN = "verification_token"