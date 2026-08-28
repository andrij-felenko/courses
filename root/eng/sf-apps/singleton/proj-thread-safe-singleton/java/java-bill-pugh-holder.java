public final class Config {
    private final Map<String, String> settings;

    private Config() {
        this.settings = loadFromDisk();      // дорога робота
    }

    // приватний вкладений клас; JVM НЕ вантажить його, поки на нього
    // вперше не пошлються — а це станеться лише в getInstance()
    private static class Holder {
        static final Config INSTANCE = new Config();
    }

    public static Config getInstance() {
        return Holder.INSTANCE;              // ось тут Holder уперше й вантажиться
    }

    public String get(String key) {
        return settings.get(key);
    }
}
