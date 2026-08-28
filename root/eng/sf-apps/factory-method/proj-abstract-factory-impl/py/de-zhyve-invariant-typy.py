# реєстр нібито Postgres, але хтось помилково поклав MySQL-команду
registry = {
    "connection":  PgConnection(pg_cfg),
    "command":     MyCommand(),          # ← чужа родина!
    "transaction": PgTransaction(),
}
db = PrototypeFactory(registry)

conn = db.create_connection()             # Postgres-з'єднання
cmd  = db.create_command()                # а це — MySQL-команда
await conn.run(cmd)                       # ЗБИРАЄТЬСЯ. Падає лише тут, у рантаймі
