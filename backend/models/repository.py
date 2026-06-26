from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IngestionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    source_url: str
    connector_type: str  # github | gitlab | local | bitbucket
    default_branch: str = "main"
    language_stats: dict[str, int] = Field(default_factory=dict)
    status: IngestionStatus = IngestionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
