// Декларативний конвеєр зчитування та парсингу налаштувань
std::expected<Config, AppError> load_config(std::string_view path) {
    return read_file_to_string(path)           // std::expected<std::string, AppError>
        .and_then(parse_json_structure)       // std::expected<JsonDoc, AppError>
        .and_then(validate_config_schema)     // std::expected<Config, AppError>
        .transform([](Config cfg) {
            cfg.is_loaded_from_cache = false;
            return cfg;
        })
        .or_else([](AppError err) -> std::expected<Config, AppError> {
            if (err == AppError::FileNotFound) {
                return Config::get_default(); // Відновлення після відсутності файлу
            }
            return std::unexpected(err); // Прокидання інших помилок далі
        });
}
