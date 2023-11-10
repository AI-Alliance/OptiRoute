import uuid


class Solution:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        print("Solution created")


    def to_dict(self) -> dict:
        return {
            "id": self.id
        }
