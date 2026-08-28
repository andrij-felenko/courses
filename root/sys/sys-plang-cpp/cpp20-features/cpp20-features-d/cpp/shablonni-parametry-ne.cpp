template<double Scale>
double apply_gain(double val) {
    return val * Scale;
}

template<std::size_t N>
struct FixedString {
    char buf[N];
    constexpr FixedString(const char (&str)[N]) {
        std::copy_n(str, N, buf);
    }
};

template<FixedString Tag>
void log_tagged(std::string_view msg) {
    std::cout << "[" << Tag.buf << "] " << msg << "\n";
}

// Виклик шаблону з рядковим літералом як NTTP
log_tagged<"NETWORK">("Packet received");
