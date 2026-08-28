#ifdef __cplusplus
// Допоміжна inline C++ функція, невидима для C-компілятора
inline std::unique_ptr<engine_t, void(*)(engine_t*)> make_scoped_engine(const char* cfg) {
    engine_t* ptr = nullptr;
    if (engine_init(&ptr, cfg) == 0 && ptr) {
        return { ptr, engine_release };
    }
    return { nullptr, engine_release };
}
#endif
