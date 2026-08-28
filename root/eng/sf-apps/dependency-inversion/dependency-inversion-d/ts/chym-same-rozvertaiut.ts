// Політика мусить СТВОРЮВАТИ з'єднання, але не сміє знати, чиє воно.
// Абстрактна фабрика — теж абстракція; стрілка політики впирається в неї.
interface Connection { query(sql: string): Row[]; close(): void; }
interface ConnectionFactory { open(): Connection; }        // порт-творець

class ReportService {
  constructor(private readonly factory: ConnectionFactory) {}

  daily(): Report {
    const conn = this.factory.open();     // створили, не назвавши деталь
    try { return build(conn.query("select ...")); }
    finally { conn.close(); }
  }
}
