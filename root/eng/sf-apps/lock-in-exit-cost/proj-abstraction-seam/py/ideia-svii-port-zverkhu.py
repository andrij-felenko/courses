from abc import ABC, abstractmethod

# Свій порт: рівно потреба системи, у власних поняттях.
# Жодного типу постачальника тут немає — саме тому це шов, а не
# переодягнений SDK.
class ObjectStore(ABC):
    # Покласти байти під ключем. Кидає StoreError при збої (див. нижче).
    @abstractmethod
    def put(self, key: str, data: bytes) -> None:
        ...

    # Дістати байти. None означає «такого ключа немає»
    # (це НЕ помилка); StoreError — саме збій доступу.
    @abstractmethod
    def get(self, key: str) -> bytes | None:
        ...

    # Перелічити ключі, що починаються з префікса.
    @abstractmethod
    def list(self, prefix: str) -> list[str]:
        ...
