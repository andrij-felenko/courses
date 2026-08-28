class Config {
  #snapshot: Resolved;                       // незмінний знімок; ротація підмінює його ЦІЛКОМ
  #reloading: Promise<void> | null = null;   // single-flight: не більше одного перечиту заразом

  private constructor(
    private readonly m: Record<string, Leaf>,
    private readonly store: SecretStore,
    initial: Resolved,
  ) { this.#snapshot = initial; }

  // СТАРТ: fail-closed. Немає секрета — застосунок НЕ піднімається (resolve кине).
  static async load(m: Record<string, Leaf>, store: SecretStore): Promise<Config> {
    return new Config(m, store, await resolve(m, store));
  }

  // Читач бере ВЕСЬ знімок за раз і працює з ним до кінця одиниці роботи.
  snapshot(): Resolved { return this.#snapshot; }

  // РОТАЦІЯ: перечитати секрети й підмінити знімок. Single-flight + fail-static.
  reload(): Promise<void> {
    if (this.#reloading) return this.#reloading;    // вже йде — приєднайся, не громадь стадо
    this.#reloading = this.#doReload().finally(() => { this.#reloading = null; });
    return this.#reloading;
  }

  async #doReload(): Promise<void> {
    let next: Resolved;
    try {
      next = await resolve(this.m, this.store);
    } catch (err) {
      log.warn("secret reload failed, keeping snapshot", { err: String(err) });
      return;                                        // fail-static: лишаємось на робочому знімку
    }
    this.#snapshot = next;                           // атомна підміна ОДНОГО посилання
  }
}
