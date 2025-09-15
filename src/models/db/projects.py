import uuid

from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Project(Model):
    id = fields.TextField(primary_key=True, default=str(uuid.uuid4()))
    name = fields.CharField(null=False, unique=True, max_length=255)
    description = fields.TextField(null=False)
    github_url = fields.TextField(null=True)
    live_url = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "projects"

ProjectSchema = pydantic_model_creator(Project, name="ProjectSchema", exclude=tuple(["id", "created_at"]))
