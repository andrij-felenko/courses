// замість глобального Config config; — функція, що будує його ліниво
Config& config() {
    static Config instance;   // збудується при ПЕРШОМУ виклику config(),
    return instance;          // а не в невизначений момент старту
}

// тепер конструктор Logger безпечно кличе config():
Logger::Logger() {
    auto host = config().get("log.host");   // config() гарантовано вже збудований
}
