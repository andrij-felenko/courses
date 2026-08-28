template <size_t N>
struct FixedString {
    char data[N]{};
    constexpr FixedString(const char (&str)[N]) noexcept {
        for (size_t i = 0; i < N; ++i) data[i] = str[i];
    }
};

template <FixedString Str>
void print_compile_time_tag() {
    // Str доступний як константа часу компіляції безпосередньо в типі
}

// Виклик:
// print_compile_time_tag<"SYSTEM_LOG_TAG">();
