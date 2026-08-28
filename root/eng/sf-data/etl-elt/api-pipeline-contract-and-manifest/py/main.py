from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class ExecutionAudit:
    pipeline_id: str
    stage_name: str
    records_read: int
    records_written: int
    bytes_transferred: int
    duration_ms: int
    target_commit_id: str

class IPipelineStage(ABC):
    @abstractmethod
    def stage_name(self) -> str:
        """Повертає унікальну назву стадії конвеєра."""
        pass

class IExtractor(IPipelineStage):
    @abstractmethod
    def extract_batch(self, watermark_start: str, watermark_end: str, limit: int) -> Tuple[List[str], Optional[int]]:
        """Видобуває порцію сирих записів за діапазоном водяного знака."""
        pass

class ILoader(IPipelineStage):
    @abstractmethod
    def load_raw_staging(self, destination_table: str, raw_records: List[str]) -> Tuple[ExecutionAudit, Optional[int]]:
        """Здійснює неблокуюче завантаження у шар Bronze."""
        pass

class ITransformer(IPipelineStage):
    @abstractmethod
    def execute_transformation(self, sql_query: str, target_partition: str) -> Tuple[ExecutionAudit, Optional[int]]:
        """Виконує SQL-трансформацію всередині аналітичного рушія."""
        pass
