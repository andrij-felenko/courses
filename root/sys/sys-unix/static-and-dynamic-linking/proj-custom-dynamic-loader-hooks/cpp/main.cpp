// main.cpp — Ідіоматична C++ RAII-обгортка для завантаження плагіна
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <dlfcn.h>

// RAII deleter для автоматичного виклику dlclose
struct DlHandleDeleter {
    void operator()(void* handle) const noexcept {
        if (handle) {
            dlclose(handle);
        }
    }
};

using UniqueDlHandle = std::unique_ptr<void, DlHandleDeleter>;

class DynamicPlugin {
public:
    static std::expected<DynamicPlugin, std::string> load(std::string_view path) {
        void* raw_handle = dlopen(path.data(), RTLD_NOW | RTLD_LOCAL);
        if (!raw_handle) {
            const char* err = dlerror();
            return std::unexpected(err ? err : "Невідома помилка dlopen");
        }

        return DynamicPlugin(UniqueDlHandle(raw_handle));
    }

    template <typename FuncSig>
    std::expected<FuncSig*, std::string> get_symbol(std::string_view symbol_name) const {
        dlerror(); // Скидаємо попередній стан помилок
        void* sym = dlsym(m_handle.get(), symbol_name.data());
        const char* err = dlerror();
        if (err != nullptr) {
            return std::unexpected(err);
        }
        return reinterpret_cast<FuncSig*>(sym);
    }

private:
    explicit DynamicPlugin(UniqueDlHandle handle) : m_handle(std::move(handle)) {}
    UniqueDlHandle m_handle;
};

int main(int argc, char* argv[]) {
    std::string_view plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    auto plugin_result = DynamicPlugin::load(plugin_path);
    if (!plugin_result) {
        std::cerr << "Помилка завантаження плагіна: " << plugin_result.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& plugin = *plugin_result;
    using ProcessFn = void(const char*);
    
    auto func_result = plugin.get_symbol<ProcessFn>("plugin_process");
    if (!func_result) {
        std::cerr << "Помилка пошуку символу: " << func_result.error() << '\n';
        return EXIT_FAILURE;
    }

    auto process_func = *func_result;
    process_func("Тестовий пакет даних C++ RAII");

    // Деструктор UniqueDlHandle автоматично викличе dlclose при виході з зони видимості
    return EXIT_SUCCESS;
}
