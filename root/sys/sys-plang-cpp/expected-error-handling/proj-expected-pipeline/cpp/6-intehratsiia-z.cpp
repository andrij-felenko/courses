// Приклад інтеграції std::expected з асинхронною корутиною C++20
Task<std::expected<ServiceConfig, ConfigError>> async_load_config(std::string_view path) {
    auto file_res = co_await async_read_file(path);
    if (!file_res) {
        co_return std::unexpected(file_res.error());
    }

    auto parsed = parse_config_raw(*file_res);
    if (!parsed) {
        co_return std::unexpected(parsed.error());
    }

    co_return validate_config(std::move(*parsed));
}
