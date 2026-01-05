# Copyright 2026 vscode
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Timelog logic"""

from hexkit.protocols.dao import ResourceAlreadyExistsError, ResourceNotFoundError
from hexkit.utils import now_utc_ms_prec

from timelog.models import Project, Session
from timelog.ports.dao import ProjectDao
from timelog.ports.log import LogPort


class Log(LogPort):
    """Core logic for project time management"""

    def __init__(self, *, project_dao: ProjectDao):
        """Set up the Log class"""
        self._dao = project_dao

    async def _deactivate_all_projects_except(self, *, name: str):
        """Deactivates all projects except for the specified project."""
        async for project in self._dao.find_all(mapping={"active": True}):
            if project.name != name:
                await self.deactivate_project(name=project.name)

    async def add_project(self, *, data: Project):
        """Adds a new project"""
        try:
            await self._dao.insert(data)
        except ResourceAlreadyExistsError as err:
            raise self.ProjectAlreadyExistsError(name=data.name) from err

    async def activate_project(self, *, name: str):
        """Activates the given project.

        Also deactivates all other projects.
        """
        await self._deactivate_all_projects_except(name=name)
        try:
            project = await self._dao.get_by_id(name)
        except ResourceNotFoundError as err:
            raise self.ProjectDoesNotExistError(name=name) from err

        project.active = True
        project.current_session_start = now_utc_ms_prec()
        await self._dao.update(project)

    async def deactivate_project(self, *, name: str):
        """Deactivate a project."""
        try:
            project = await self._dao.get_by_id(name)
        except ResourceNotFoundError as err:
            raise self.ProjectDoesNotExistError(name=name) from err

        now = now_utc_ms_prec()
        if project.current_session_start:
            session = Session(start=project.current_session_start, stop=now)
            project.active = False
            project.current_session_start = None
            project.sessions.append(session)
            await self._dao.update(project)

    async def deactivate_all_projects(self):
        """Deactivates all open projects"""
        async for project in self._dao.find_all(mapping={"active": True}):
            await self.deactivate_project(name=project.name)

    async def get_project_duration(self, *, name: str) -> float:
        """Gets the total time spent, in hours, on the given project"""
        try:
            project = await self._dao.get_by_id(name)
        except ResourceNotFoundError as err:
            raise self.ProjectDoesNotExistError(name=name) from err

        return project.total_hours
