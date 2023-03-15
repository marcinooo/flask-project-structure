"""Contains user schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserSchema(BaseModel):
    """User schema."""
    username: str
    email: str
    password: Optional[str]
    created: Optional[datetime]
    active: Optional[bool]

    class Config:
        """Model configuration."""
        orm_mode = True

    def dict(self, *args, **kwargs):  # pylint: disable=no-self-argument
        """Overwrites BAseModel's dict() methods to remove sensitive data."""
        data = super().dict(*args, **kwargs)
        data['created'] = data['created'].strftime('%Y-%m-%dT%H:%M:%S')
        if 'password' in data:
            data['password'] = '***'
        return data
