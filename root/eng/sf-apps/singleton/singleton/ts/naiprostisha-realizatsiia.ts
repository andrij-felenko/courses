class Config {
  private static instance: Config | null = null;
  private settings: Map<string, string>;

  // приватний конструктор: ззовні new Config() не викличеш
  private constructor() {
    this.settings = loadFromDisk();   // дорога робота — читаємо файл
  }

  static getInstance(): Config {
    if (Config.instance === null) {   // ще нема — створюємо
      Config.instance = new Config();
    }
    return Config.instance;           // завжди той самий об'єкт
  }

  get(key: string): string | undefined {
    return this.settings.get(key);
  }
}

// будь-де в програмі:
const dbHost = Config.getInstance().get("db.host");
