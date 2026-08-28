// Ідіоматичний безпечний розбір через nlohmann::json і RAII
try {
    const auto root = nlohmann::json::parse(payload_view);
    if (!root.contains("device_id") || !root["device_id"].is_string()) {
        return std::unexpected(ErrorCode::MissingField);
    }
    const std::string device_id = root["device_id"].get<std::string>();
    // Пам'ять гарантовано звільняється деструктором при будь-якому виході
} catch (const nlohmann::json::parse_error&) {
    return std::unexpected(ErrorCode::InvalidJson);
}
