class FakeConn implements Conn {
  calls: [string, unknown[]][] = [];
  execute(sql: string, ...args: unknown[]) { this.calls.push([sql, args]); }
}
class FakeSmtp implements Smtp {
  sent: [string, string, string][] = [];
  send(from: string, to: string, body: string) { this.sent.push([from, to, body]); }
}

class TestableOrderManager extends OrderManager {  // підклас ЛИШЕ для тесту
  conn = new FakeConn();
  smtp = new FakeSmtp();
  protected openDb(): Conn { return this.conn; }   // шов спрацював
  protected openSmtp(): Smtp { return this.smtp; }
}
