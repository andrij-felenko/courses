struct PluginError : std::runtime_error {          // плагін не придатний, із поясненням
    using std::runtime_error::runtime_error;
};

using RegisterFn = void (*)(Host&);   // тип умовленої точки входу

// Оживити ОДИН .so, звірити версію, повернути вказівник на plugin_register.
// Кидає PluginError із людською причиною, якщо щось не так.
RegisterFn load_one(const fs::path& file) {
    const std::string name = file.filename().string();

    // -- фаза «завантажити»: dlopen вливає ЧУЖИЙ код у наш процес --
    // RTLD_NOW: зв'язати всі символи ОДРАЗУ, щоб биткий плагін упав тут,
    // а не колись потім усередині виклику. RTLD_LOCAL: не світити його символи.
    void* handle = dlopen(file.c_str(), RTLD_NOW | RTLD_LOCAL);
    if (!handle)
        throw PluginError(name + ": збій при завантаженні: " + dlerror());

    // -- фаза «звірити версію»: раніше, ніж чіпати plugin_register --
    auto* api = reinterpret_cast<const int*>(dlsym(handle, "PLUGIN_API"));
    if (!api || *api != HOST_API) {
        std::string had = api ? std::to_string(*api) : "?";
        dlclose(handle);                     // прибрати несумісний модуль
        throw PluginError(name + ": несумісний контракт (плагін під API "
                          + had + ", ядро дає " + std::to_string(HOST_API) + ")");
    }

    auto reg = reinterpret_cast<RegisterFn>(dlsym(handle, "plugin_register"));
    if (!reg) {
        dlclose(handle);
        throw PluginError(name + ": немає точки входу plugin_register(host)");
    }
    return reg;   // handle навмисно лишаємо відкритим: код плагіна має жити далі
}
