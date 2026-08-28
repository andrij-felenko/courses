enum class NetError { Timeout, HostNotFound, AccessDenied };

std::expected<std::string, NetError> fetch_data(std::string_view url);
std::expected<JsonDoc, NetError> parse_json(std::string_view text);

auto result = fetch_data("https://api.service.internal/config")
    .and_then(parse_json)
    .transform([](const JsonDoc& doc) { return doc["port"].as_int(); })
    .or_else([](NetError err) -> std::expected<int, NetError> {
        if (err == NetError::Timeout) return 8080; // Відновлення через резервний порт
        return std::unexpected(err); // Прокидання помилки далі
    });
