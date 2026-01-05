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

"""Dependency injection"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hexkit.providers.mongodb import MongoDbDaoFactory

from timelog.adapters.inbound.fastapi_ import dummies
from timelog.adapters.inbound.fastapi_.configure import get_configured_app
from timelog.adapters.outbound.dao import get_project_dao
from timelog.config import Config
from timelog.core.log import Log
from timelog.ports.log import LogPort


@asynccontextmanager
async def prepare_core(*, config: Config) -> AsyncGenerator[LogPort]:
    """Produce a configured Log class"""
    async with MongoDbDaoFactory.construct(config=config) as dao_factory:
        dao = await get_project_dao(dao_factory=dao_factory)
        yield Log(project_dao=dao)


@asynccontextmanager
async def prepare_rest_app(*, config: Config) -> AsyncGenerator[FastAPI]:
    """Construct and initialize a REST API app along with all its dependencies"""
    app = get_configured_app(config=config)

    async with prepare_core(config=config) as log:
        app.dependency_overrides[dummies.log_port] = lambda: log
        yield app
