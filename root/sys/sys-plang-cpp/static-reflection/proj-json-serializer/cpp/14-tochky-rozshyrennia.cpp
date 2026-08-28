// Концепт для виявлення користувацького методу серіалізації
template <typename T>
concept CustomSerializable = requires(const T& val) {
    { to_custom_json(val) } -> std::same_as<std::string>;
};

// Приклад адаптера для часових міток std::chrono
inline auto to_custom_json(const std::chrono::system_clock::time_point& tp) -> std::string {
    auto epoch_ms = std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch()).count();
    return std::to_string(epoch_ms);
}
