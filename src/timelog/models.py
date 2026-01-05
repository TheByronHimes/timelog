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

"""Model definitions"""

from ghga_service_commons.utils.utc_dates import UTCDatetime
from pydantic import BaseModel, computed_field


class Session(BaseModel):
    """Represents a work session with a start and stop time"""

    start: UTCDatetime
    stop: UTCDatetime

    @property
    @computed_field
    def duration(self) -> int:
        """Returns the session duration in minutes"""
        return (self.stop - self.start).seconds // 60


class Project(BaseModel):
    """Represents a project and its basic data"""

    name: str
    created: UTCDatetime
    active: bool = False
    current_session_start: UTCDatetime | None = None
    sessions: list[Session]

    @property
    @computed_field
    def total_hours(self) -> float:
        """Returns the total hours spent on the project so far"""
        return round(sum(s.duration for s in self.sessions) / 60, 1)
