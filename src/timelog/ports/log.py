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

"""Log interface definition"""

from abc import ABC, abstractmethod

from timelog.models import Project


class LogPort(ABC):
    """Contract for the core class"""

    class ProjectAlreadyExistsError(RuntimeError):
        """Raised when a project can't be added because one by that name already exists"""

        def __init__(self, *, name: str):
            msg = f"A project named {name} already exists"
            super().__init__(msg)

    class ProjectDoesNotExistError(RuntimeError):
        """Raised when a project isn't found in the database"""

        def __init__(self, *, name: str):
            msg = f"No project named {name} exists"
            super().__init__(msg)

    @abstractmethod
    async def add_project(self, *, data: Project):
        """Adds a new project"""

    @abstractmethod
    async def activate_project(self, *, name: str):
        """Activates the given project"""

    @abstractmethod
    async def deactivate_project(self, *, name: str):
        """Deactivates the given project"""

    @abstractmethod
    async def deactivate_all_projects(self):
        """Deactivates all projects"""

    @abstractmethod
    async def get_project_duration(self, *, name: str) -> float:
        """Gets the total time spent, in hours, on the given project"""
