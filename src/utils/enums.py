from enum import Enum

class TaskStatusEnum(str, Enum):
    CREATED = "создано"
    IN_WORK = " в работе"
    COMLETED = "заверешено"