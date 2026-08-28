class SessionService {
  private hits = 0;                       // лічильник звернень «для метрик»
  private config: Config | null = null;   // лінивий кеш конфігурації
  private sessions = new Map<string, Session>();
  private readonly log: Logger;
  private readonly store: ConfigStore;

  constructor(log: Logger, store: ConfigStore) {
    this.log = log;
    this.store = store;
  }

  // «get» у назві — а всередині МІНЯЄ лічильник і ще й пише в журнал
  getSession(id: string): Session | undefined {
    this.hits += 1;                                  // ← прихована зміна
    this.log.info(`session lookup #${this.hits}: ${id}`); // ← ще ефект
    return this.sessions.get(id);
  }

  // теж «get» — а при першому виклику ЧИТАЄ з диска й КЕШУЄ
  getConfig(): Config {
    if (this.config === null) {
      this.config = this.store.load();               // ← прихована зміна
    }
    return this.config;
  }
}
