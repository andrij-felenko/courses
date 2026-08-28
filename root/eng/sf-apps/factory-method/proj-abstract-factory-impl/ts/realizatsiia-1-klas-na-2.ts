interface DbFactory {                       // абстрактна фабрика: метод на КОЖЕН вид
  createConnection(): Connection;
  createCommand(): Command;
  createTransaction(): Transaction;
}

class PostgresFactory implements DbFactory {   // уся трійка — Postgres
  createConnection(): Connection   { return new PgConnection(this.cfg); }
  createCommand():    Command      { return new PgCommand(); }
  createTransaction(): Transaction { return new PgTransaction(); }
  constructor(private cfg: PgConfig) {}
}
class MySqlFactory implements DbFactory {      // уся трійка — MySQL
  createConnection(): Connection   { return new MyConnection(this.cfg); }
  createCommand():    Command      { return new MyCommand(); }
  createTransaction(): Transaction { return new MyTransaction(); }
  constructor(private cfg: MyConfig) {}
}

// клієнт бачить лише DbFactory й тримає ОДНУ фабрику — уся трійка з однієї СУБД
async function loadUser(db: DbFactory, id: number): Promise<User> {
  const conn = db.createConnection();
  const cmd  = db.createCommand().bind(id);   // цей cmd — тієї ж СУБД, що й conn
  const rows = await conn.run(cmd);
  return toUser(rows);
}
