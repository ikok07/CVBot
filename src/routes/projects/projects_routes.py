from typing import Annotated

from clerk_backend_api import User
from fastapi import APIRouter, Depends, Body
from starlette import status
from tortoise.exceptions import DoesNotExist

from src.models.db import Profile, Project, ProjectSchema, ProjectInsert
from src.models.errors.api import APIError
from src.models.responses.generic import GenericResponse
from src.routes.dependencies.protect import protect_dependency

router = APIRouter()

@router.get("/")
async def get_all_projects(userdata: tuple[User, Profile] = Depends(protect_dependency)):
    projects = await Project.all()
    return GenericResponse(data=[(await ProjectSchema.from_tortoise_orm(project)).model_dump() for project in projects])

@router.post("/")
async def insert_product(project: Annotated[ProjectInsert, Body()], userdata: tuple[User, Profile] = Depends(protect_dependency)):
    db_project = Project(**project)
    await db_project.save()
    return GenericResponse(data=(await ProjectSchema.from_tortoise_orm(db_project)).model_dump())

@router.delete("/{project_id}")
async def delete_product(project_id: str, userdata: tuple[User, Profile] = Depends(protect_dependency)):
    try:
        project = await Project.get(id=project_id)
        await project.delete()
        return GenericResponse()
    except DoesNotExist as e:
        raise APIError(status_code=status.HTTP_404_NOT_FOUND, message="Project not found!")
    except Exception as e:
        print(f"Something went wrong while deleting project! {e}")
        raise APIError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Something went wrong!")