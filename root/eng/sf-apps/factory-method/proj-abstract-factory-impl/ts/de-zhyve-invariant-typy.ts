// реєстр нібито Postgres, але хтось помилково поклав MySQL-команду
const registry = new Map<string, Prototype>([
  ["connection",  new PgConnection(pgCfg)],
  ["command",     new MyCommand()],      // ← чужа родина!
  ["transaction", new PgTransaction()],
]);
const db = new PrototypeFactory(registry);

const conn = db.createConnection();       // Postgres-з'єднання
const cmd  = db.createCommand();          // а це — MySQL-команда
await conn.run(cmd);                      // ЗБИРАЄТЬСЯ. Падає лише тут, у рантаймі
