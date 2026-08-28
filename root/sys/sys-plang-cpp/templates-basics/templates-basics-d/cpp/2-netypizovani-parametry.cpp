template <std::size_t N>
struct FixedString {
    char buf[N]{};
    constexpr FixedString(const char (&str)[N]) {
        for (std::size_t i = 0; i < N; ++i) buf[i] = str[i];
    }
    constexpr bool operator==(const FixedString&) const = default;
};

// C++20: шаблон із рядковим літеральним параметром NTTP!
template <FixedString ChannelName>
void send_packet(const char* payload) {
    std::cout << "[" << ChannelName.buf << "] " << payload << "\n";
}

// Виклик:
send_packet<"TELEMETRY_MAIN">("GPS_LOCK_OK");
