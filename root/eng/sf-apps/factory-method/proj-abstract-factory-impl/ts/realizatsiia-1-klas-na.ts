interface Connection {
  run(cmd: Command): Promise<Rows>;
  close(): Promise<void>;
}
interface Command {
  readonly sql: string;
  bind(...params: unknown[]): this;
}
interface Transaction {
  commit(): Promise<void>;
  rollback(): Promise<void>;
}
