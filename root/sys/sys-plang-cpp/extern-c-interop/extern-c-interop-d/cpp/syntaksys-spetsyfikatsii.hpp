// Одиничне оголошення функції з C-зв'язуванням
extern "C" int crypto_calculate_hash(const char* data, size_t len);

// Одиничне оголошення глобальної змінної
extern "C" int g_crypto_active_sessions;

// Блокова специфікація зв'язування
extern "C" {
    int  crypto_engine_init(const char* config_json);
    int  crypto_engine_process(const uint8_t* in, uint8_t* out, size_t len);
    void crypto_engine_shutdown(void);
}
