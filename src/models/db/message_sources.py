import uuid

from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator

class MessageSource(Model):
    id = fields.TextField(primary_key=True, default=str(uuid.uuid4()))
    message_id = fields.TextField(null=False)
    name = fields.TextField(null=False)
    url = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "message_sources"

MessageSourceSchema = pydantic_model_creator(MessageSource, name="MessageSource")