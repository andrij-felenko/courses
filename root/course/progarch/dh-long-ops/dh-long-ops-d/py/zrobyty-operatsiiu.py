from dataclasses import dataclass
from typing import Optional, Literal

OpStatus = Literal["queued", "running", "succeeded", "failed", "canceled"]

@dataclass
class ClipOperation:
    id: str                        # /operations/{id} — за цим клієнт стежить
    status: OpStatus
    progress: int                  # 0..100, поки running
    request: dict                  # {"camera_id":…, "from":…, "to":…}
    result: Optional[dict] = None  # {"url":…, "expires_at":…} коли succeeded
    error: Optional[dict] = None   # {"code":…, "message":…} коли failed
    created_at: str = ""
