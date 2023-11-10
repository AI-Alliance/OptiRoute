import uuid


class Solution:
    def __init__(self, task_id: str):
        self.id: str = str(uuid.uuid4())
        self.task_id: str = task_id
        print("Solution created")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id
        }
