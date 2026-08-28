enum class LogLevel { Trace, Debug, Info, Warn, Error, Fatal };

struct LogRecord {
    std::chrono::system_clock::time_point timestamp;
    LogLevel level;
    std::string_view component;
    std::string_view message;
};

template <>
struct std::formatter<LogRecord> {
    enum class Mode { Full, Short, Json };
    Mode mode = Mode::Full;

    // 1. Компіляційний розбір специфікаторів у constexpr контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it != '}') {
            if (*it == 's') { mode = Mode::Short; ++it; }
            else if (*it == 'j') { mode = Mode::Json; ++it; }
            else if (*it == 'f') { mode = Mode::Full; ++it; }
            else { throw std::format_error("Unknown specifier for LogRecord"); }
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for LogRecord");
        }
        return it;
    }

    // Допоміжна функція перетворення рівня в рядок
    static constexpr std::string_view level_to_string(LogLevel lvl) noexcept {
        switch (lvl) {
            case LogLevel::Trace: return "TRACE";
            case LogLevel::Debug: return "DEBUG";
            case LogLevel::Info:  return "INFO";
            case LogLevel::Warn:  return "WARN";
            case LogLevel::Error: return "ERROR";
            case LogLevel::Fatal: return "FATAL";
        }
        return "UNKNOWN";
    }

    // 2. Генерація текстового виводу у вихідний ітератор
    template <typename FormatContext>
    auto format(const LogRecord& rec, FormatContext& ctx) const {
        std::string_view lvl_str = level_to_string(rec.level);

        if (mode == Mode::Short) {
            return std::format_to(ctx.out(), "{}: {}", lvl_str, rec.message);
        } 
        else if (mode == Mode::Json) {
            return std::format_to(ctx.out(), 
                "{{\"level\":\"{}\",\"comp\":\"{}\",\"msg\":\"{}\"}}", 
                lvl_str, rec.component, rec.message);
        }

        // За замовчуванням Full: дата-час + рівень + компонент + повідомлення
        return std::format_to(ctx.out(), 
            "[{:%Y-%m-%d %H:%M:%S}] [{}] [{}]: {}", 
            rec.timestamp, lvl_str, rec.component, rec.message);
    }
};
