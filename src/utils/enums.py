from enum import Enum

class TaskStatusEnum(str, Enum):
    CREATED = "создано"
    IN_WORK = "в работе"
    COMLETED = "завершено"

class UserRoleEnum(str, Enum):
    USER = "Пользователь"
    REDACTOR = "Редактор"
    ADMIN = "Администратор"
    