template <std::size_t N>
struct FixedString {
    char data[N]{};

    // Конструктор виконується під час компіляції
    constexpr FixedString(const char (&str)[N]) {
        for (std::size_t i = 0; i < N; ++i) {
            data[i] = str[i];
        }
    }

    constexpr bool operator==(const FixedString&) const = default;
};

// Шаблон, параметризований рядком
template <FixedString Identifier>
class LoggerChannel {
public:
    void log(const char* msg) {
        std::cout << "[" << Identifier.data << "] " << msg << "\n";
    }
};

// Використання:
LoggerChannel<"NETWORK_CORE"> net_log; // Кожен рядок породжує унікальний тип!
