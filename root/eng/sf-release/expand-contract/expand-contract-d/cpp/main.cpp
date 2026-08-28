// Фаза розширення (Expand): перевантаження або структура опцій
struct ConfigOptions {
    std::string_view filepath;
    std::chrono::milliseconds timeout{1000};
    int compression_level{0};
    bool sync_to_disk{true};
};

// Новий розширений інтерфейс
bool save_config(ConfigOptions const& opts);

// Старий інтерфейс як адаптер над новим
inline bool save_config(std::string_view filepath, std::chrono::milliseconds timeout) {
    return save_config(ConfigOptions{
        .filepath = filepath,
        .timeout = timeout,
        .compression_level = 0,
        .sync_to_disk = true
    });
}
