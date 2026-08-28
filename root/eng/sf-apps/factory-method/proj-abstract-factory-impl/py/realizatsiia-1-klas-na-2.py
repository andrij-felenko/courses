from abc import ABC, abstractmethod

class DbFactory(ABC):                        # абстрактна фабрика: метод на КОЖЕН вид
    @abstractmethod
    def create_connection(self) -> Connection: ...
    @abstractmethod
    def create_command(self) -> Command: ...
    @abstractmethod
    def create_transaction(self) -> Transaction: ...

class PostgresFactory(DbFactory):            # уся трійка — Postgres
    def __init__(self, cfg: "PgConfig"): self.cfg = cfg
    def create_connection(self) -> Connection:  return PgConnection(self.cfg)
    def create_command(self) -> Command:        return PgCommand()
    def create_transaction(self) -> Transaction: return PgTransaction()

class MySqlFactory(DbFactory):               # уся трійка — MySQL
    def __init__(self, cfg: "MyConfig"): self.cfg = cfg
    def create_connection(self) -> Connection:  return MyConnection(self.cfg)
    def create_command(self) -> Command:        return MyCommand()
    def create_transaction(self) -> Transaction: return MyTransaction()

# клієнт бачить лише DbFactory й тримає ОДНУ фабрику — уся трійка з однієї СУБД
async def load_user(db: DbFactory, id: int) -> "User":
    conn = db.create_connection()
    cmd  = db.create_command().bind(id)       # цей cmd — тієї ж СУБД, що й conn
    rows = await conn.run(cmd)
    return to_user(rows)
