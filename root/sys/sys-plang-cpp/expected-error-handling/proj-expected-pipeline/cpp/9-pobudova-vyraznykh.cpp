// Побудова ланцюжка з вбудованим логуванням та метриками
std::expected<ServiceConfig, ConfigError> load_with_telemetry(std::string_view path) {
    return load_service_configuration(path)
        .transform([](ServiceConfig cfg) {
            Metrics::increment("config_load_success");
            Logger::info("Конфігурацію прочитано для хоста {}", cfg.db_host);
            return cfg;
        })
        .or_else([](ConfigError err) -> std::expected<ServiceConfig, ConfigError> {
            Metrics::increment("config_load_failure");
            Logger::error("Не вдалося завантажити конфігурацію: {}", to_string(err));
            return std::unexpected(err); // Передаємо помилку далі після логування
        });
}
