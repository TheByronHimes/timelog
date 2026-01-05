"""Dao port def"""

from hexkit.protocols.dao import Dao

from timelog import models

ProjectDao = Dao[models.Project]
