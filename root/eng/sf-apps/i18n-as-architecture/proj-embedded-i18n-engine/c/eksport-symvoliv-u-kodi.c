/* Оголошення символів лінкера для двійкового блоку у Flash (C99) */
extern const uint8_t _binary_locales_bin_start[];
extern const uint8_t _binary_locales_bin_end[];

void app_i18n_init(void) {
    size_t image_size = (size_t)(_binary_locales_bin_end - _binary_locales_bin_start);
    uint32_t uk_locale_id = emb_i18n_hash("uk-UA");
    
    emb_i18n_ctx_t ctx;
    if (emb_i18n_init(&ctx, _binary_locales_bin_start, image_size, uk_locale_id)) {
        const char *msg = emb_i18n_get(&ctx, "system.ready");
        display_print_status(msg);
    }
}
