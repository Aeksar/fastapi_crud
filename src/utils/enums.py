from enum import Enum

class TaskStatusEnum(str, Enum):
    CREATED = "created"
    IN_WORK = "in_work"
    COMLETED = "completed"