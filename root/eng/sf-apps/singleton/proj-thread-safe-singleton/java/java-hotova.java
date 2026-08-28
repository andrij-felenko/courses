public final class Config {
    // JVM гарантує: статичне поле ініціалізується рівно раз, під захистом,
    // ще до того, як хтось уперше торкнеться класу
    private static final Config INSTANCE = new Config();

    private final Map<String, String> settings;

    private Config() {                       // приватний — ззовні new не викличеш
        this.settings = loadFromDisk();      // дорога робота, робиться один раз
    }

    public static Config getInstance() {
        return INSTANCE;
    }

    public String get(String key) {
        return settings.get(key);
    }
}
