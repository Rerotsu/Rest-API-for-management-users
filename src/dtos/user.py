from __future__ import annotations

import datetime
from typing import Optional

import msgspec


class UserCreateDTO(msgspec.Struct, kw_only=True, omit_defaults=True):
    name: str
    surname: str
    password: str


class UserUpdateDTO(msgspec.Struct, kw_only=True, omit_defaults=True):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None


class UserReadDTO(msgspec.Struct, kw_only=True):
    id: int
    name: str
    surname: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserListDTO(msgspec.Struct, kw_only=True):
    id: int
    name: str
    surname: str
