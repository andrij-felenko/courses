from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar
import json

T = TypeVar("T")
DomainErrorKind = Literal["NotFound", "RuleViolation", "Conflict", "AccessDenied"]

# Семантична доменна помилка ядра
@dataclass(frozen=True)
class DomainError:
    kind: DomainErrorKind
    message: str
    invalid_params: dict[str, str] | None = None

# Типізований результат виконання сценарію (патерн Result)
@dataclass(frozen=True)
class Result(Generic[T]):
    ok: bool
    value: T | None = None
    error: DomainError | None = None

# Протокольна відповідь HTTP-адаптера
@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: str

# Обробник результату (Result Mapper): трансляція доменного результату в HTTP
class HttpResultMapper:
    _STATUS_MAP: dict[str, tuple[int, str]] = {
        "NotFound": (404, "Ресурс не знайдено"),
        "RuleViolation": (422, "Порушення бізнес-правила"),
        "Conflict": (409, "Конфлікт стану ресурсу"),
        "AccessDenied": (403, "Доступ заборонено"),
    }

    @classmethod
    def to_response(cls, result: Result[T], success_status: int = 200) -> HttpResponse:
        if result.ok:
            return HttpResponse(
                status=success_status,
                headers={"Content-Type": "application/json"},
                body=json.dumps(result.value),
            )

        assert result.error is not None
        err = result.error
        status, title = cls._STATUS_MAP.get(err.kind, (500, "Внутрішня помилка"))
        problem: dict[str, Any] = {
            "type": f"https://api.digitalhomes.io/errors/{err.kind.lower()}",
            "title": title,
            "status": status,
            "detail": err.message,
        }
        if err.invalid_params:
            problem["invalidParams"] = err.invalid_params

        return HttpResponse(
            status=status,
            headers={"Content-Type": "application/problem+json"},
            body=json.dumps(problem),
        )
