from enum import Enum

from tortoise import Model, fields

class ProfileRole(Enum):
    user = "user"
    admin = "admin"

class Profile(Model):
    id = fields.TextField(primary_key=True)
    first_name = fields.TextField(null=False)
    last_name = fields.TextField(null=False)
    email = fields.TextField(null=False)
    role = fields.CharEnumField(ProfileRole, default="user")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "profiles"