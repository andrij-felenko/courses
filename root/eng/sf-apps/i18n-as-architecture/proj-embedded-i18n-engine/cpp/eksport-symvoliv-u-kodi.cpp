// Ідіоматична ініціалізація рушія з пам'яті Flash (C++20)
extern "C" const uint8_t _binary_locales_bin_start[];
extern "C" const uint8_t _binary_locales_bin_end[];

void app_i18n_init_cpp() {
    std::span<const uint8_t> blob{
        _binary_locales_bin_start,
        static_cast<size_t>(_binary_locales_bin_end - _binary_locales_bin_start)
    };
    constexpr uint32_t uk_locale_id = embedded::i18n::const_hash("uk-UA");
    
    if (auto engine = embedded::i18n::Engine::create(blob, uk_locale_id)) {
        std::string_view msg = engine->get("system.ready");
        display_print_status(msg.data());
    }
}
