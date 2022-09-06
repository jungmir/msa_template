# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum


class BaseEnum(Enum):
    pass


class StrEnum(str, BaseEnum):
    pass


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"
