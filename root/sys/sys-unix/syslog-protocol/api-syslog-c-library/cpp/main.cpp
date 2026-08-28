// Приклад ідіоматичної C++ обгортки (RAII Logger) над Syslog API
#include <syslog.h>
#include <string_view>
#include <string>
#include <format>
#include <utility>

class SyslogLogger {
public:
    enum class Facility : int {
        User     = LOG_USER,
        Daemon   = LOG_DAEMON,
        AuthPriv = LOG_AUTHPRIV,
        Local0   = LOG_LOCAL0
    };

    enum class Level : int {
        Emerg   = LOG_EMERG,
        Alert   = LOG_ALERT,
        Crit    = LOG_CRIT,
        Error   = LOG_ERR,
        Warning = LOG_WARNING,
        Notice  = LOG_NOTICE,
        Info    = LOG_INFO,
        Debug   = LOG_DEBUG
    };

    explicit SyslogLogger(std::string ident, 
                         Facility facility = Facility::Daemon, 
                         int options = LOG_PID)
        : m_ident(std::move(ident)) 
    {
        // openlog очікує вказівник на статичну пам'ять або об'єкт, який живе до closelog.
        // Зберігаємо рядок у полі класу m_ident.
        ::openlog(m_ident.c_str(), options, static_cast<int>(facility));
    }

    ~SyslogLogger() {
        ::closelog();
    }

    // Забороняємо копіювання, щоб уникнути подвійного closelog
    SyslogLogger(const SyslogLogger&) = delete;
    SyslogLogger& operator=(const SyslogLogger&) = delete;

    SyslogLogger(SyslogLogger&&) noexcept = default;
    SyslogLogger& operator=(SyslogLogger&&) noexcept = default;

    void set_max_level(Level max_level) noexcept {
        ::setlogmask(LOG_UPTO(static_cast<int>(max_level)));
    }

    template <typename... Args>
    void log(Level level, std::string_view fmt_str, Args&&... args) const {
        std::string message = std::vformat(fmt_str, std::make_format_args(args...));
        ::syslog(static_cast<int>(level), "%s", message.c_str());
    }

    template <typename... Args>
    void info(std::string_view fmt_str, Args&&... args) const {
        log(Level::Info, fmt_str, std::forward<Args>(args)...);
    }

    template <typename... Args>
    void error(std::string_view fmt_str, Args&&... args) const {
        log(Level::Error, fmt_str, std::forward<Args>(args)...);
    }

private:
    std::string m_ident;
};

int main() {
    SyslogLogger logger("cpp_service", SyslogLogger::Facility::Daemon, LOG_PID | LOG_PERROR);
    logger.set_max_level(SyslogLogger::Level::Info);

    logger.info("Службу C++ запущено. Порт: {}", 8080);
    logger.error("Виникла помилка з'єднання з ВБ: {}", "Connection refused");

    return 0;
}
