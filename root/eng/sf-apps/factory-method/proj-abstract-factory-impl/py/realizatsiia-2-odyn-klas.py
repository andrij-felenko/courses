from typing import Protocol

class Prototype(Protocol):
    def clone(self) -> "Prototype": ...

# один клас на ВСІ родини: відмінність — у переданому реєстрі взірців
class PrototypeFactory:
    def __init__(self, registry: dict[str, Prototype]):
        self._registry = registry

    def _create(self, kind: str) -> Prototype:
        proto = self._registry.get(kind)
        if proto is None:
            raise KeyError(f"Немає прототипа для '{kind}'")
        return proto.clone()                  # народження = клон взірця

    def create_connection(self):  return self._create("connection")
    def create_command(self):     return self._create("command")
    def create_transaction(self): return self._create("transaction")

# «Postgres-фабрика» — той самий клас, лише інший НАБІР даних
postgres = PrototypeFactory({
    "connection":  PgConnection(pg_cfg),
    "command":     PgCommand(),
    "transaction": PgTransaction(),
})
# «MySQL-фабрика» — той самий клас, підмінили дані
mysql = PrototypeFactory({
    "connection":  MyConnection(my_cfg),
    "command":     MyCommand(),
    "transaction": MyTransaction(),
})
