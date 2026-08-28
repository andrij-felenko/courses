interface Prototype { clone(): Prototype; }   // усе, що вміє себе клонувати

// один клас на ВСІ родини: відмінність — у переданому реєстрі взірців
class PrototypeFactory {
  constructor(private registry: Map<string, Prototype>) {}

  private create(kind: string): Prototype {
    const proto = this.registry.get(kind);
    if (!proto) throw new Error(`Немає прототипа для '${kind}'`);
    return proto.clone();                     // народження = клон взірця
  }
  createConnection()  { return this.create("connection")  as Connection; }
  createCommand()     { return this.create("command")     as Command; }
  createTransaction() { return this.create("transaction") as Transaction; }
}

// «Postgres-фабрика» — це той самий клас, лише інший НАБІР даних
const postgres = new PrototypeFactory(new Map<string, Prototype>([
  ["connection",  new PgConnection(pgCfg)],
  ["command",     new PgCommand()],
  ["transaction", new PgTransaction()],
]));
// «MySQL-фабрика» — той самий клас, підмінили дані
const mysql = new PrototypeFactory(new Map<string, Prototype>([
  ["connection",  new MyConnection(myCfg)],
  ["command",     new MyCommand()],
  ["transaction", new MyTransaction()],
]));
