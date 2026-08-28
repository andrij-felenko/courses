public enum Config {
    INSTANCE;                                // єдина константа = єдиний екземпляр

    private final Map<String, String> settings;

    // конструктор enum викликається JVM рівно раз, потокобезпечно
    Config() {
        this.settings = loadFromDisk();      // дорога робота
    }

    public String get(String key) {
        return settings.get(key);
    }
}

// вживання:  Config.INSTANCE.get("db.host");
