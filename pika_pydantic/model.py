import json

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    def encode(self):
        """Serialization of a Model object - UTF-8 encoded binary JSON"""
        data = self.json()
        return data.encode("utf-8")

    @classmethod
    def decode(cls, body):
        """Deserializeation from data in the Queue into an object and validate."""
        data = json.loads(body.decode("utf-8"))
        return cls.validate(data)
