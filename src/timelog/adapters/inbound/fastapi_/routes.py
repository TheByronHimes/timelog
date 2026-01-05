# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module containing the main FastAPI router and (optionally) top-level API endpoints.

Additional endpoints might be structured in dedicated modules
(each of them having a sub-router).
"""

from fastapi import APIRouter, HTTPException
from hexkit.utils import now_utc_ms_prec

from timelog.adapters.inbound.fastapi_ import dummies
from timelog.models import Project
from timelog.ports.log import LogPort

router = APIRouter()


@router.get("/", summary="health check")
async def health():
    """Return 200 just to show that the service is running."""
    return 200


@router.post(
    "/projects",
    summary="Add a new project",
    status_code=201,
)
async def add_project(name: str, log: dummies.LogDummy):
    """Add a project.

    Returns 409 if the project already exists.
    """
    try:
        data = Project(
            name=name,
            created=now_utc_ms_prec(),
            active=False,
            current_session_start=None,
            sessions=[],
        )
        await log.add_project(data=data)
    except LogPort.ProjectAlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err

    return 201


@router.patch(
    "/projects/{name}/activate",
    summary="Activates a project",
    status_code=204,
)
async def activate_project(name: str, log: dummies.LogDummy):
    """Activates a project.

    All other active projects will be deactivated.

    Returns 404 if the project doesn't exist.
    """
    try:
        await log.activate_project(name=name)
    except LogPort.ProjectDoesNotExistError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@router.patch(
    "/projects/{name}/deactivate",
    summary="Deactivates a project",
    status_code=204,
)
async def deactivate_project(name: str, log: dummies.LogDummy):
    """Deactivates a project.

    Returns 404 if the project doesn't exist.
    """
    try:
        await log.deactivate_project(name=name)
    except LogPort.ProjectDoesNotExistError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@router.patch(
    "/rpc/deactivate_all",
    summary="Deactivates all active projects",
    status_code=204,
)
async def deactivate_all(log: dummies.LogDummy):
    """Deactivates all active projects."""
    await log.deactivate_all_projects()


@router.get(
    "/projects/{name}/duration",
    summary="Retrieves project duration in hours, rounded to one decimal place",
    status_code=200,
)
async def get_project_duration(name: str, log: dummies.LogDummy) -> float:
    """Retrieves project duration in hours, rounded to one decimal place.

    Returns 404 if the project doesn't exist.
    """
    try:
        return await log.get_project_duration(name=name)
    except LogPort.ProjectDoesNotExistError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
