#include <iostream>
#include <string_view>
#include <thread>
#include <dlfcn.h>
#include <stdexcept>

class DynamicPlugin {
    void* handle_{nullptr};

public:
    explicit DynamicPlugin(std::string_view path) {
        handle_ = ::dlopen(path.data(), RTLD_NOW);
        if (!handle_) {
            throw std::runtime_error(::dlerror());
        }
    }

    ~DynamicPlugin() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    void execute(std::string_view symbol_name) {
        using func_t = void (*)();
        auto func = reinterpret_cast<func_t>(::dlsym(handle_, symbol_name.data()));
        if (!func) {
            throw std::runtime_error(::dlerror());
        }
        func();
    }
};

int main(int argc, char** argv) {
    const std::string_view plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    std::jthread worker([plugin_path] {
        try {
            std::cout << "--> [Worker Thread] Динамічне завантаження плагіна...\n";
            DynamicPlugin plugin(plugin_path);
            plugin.execute("plugin_print_tls");
        } catch (const std::exception& ex) {
            std::cerr << "Помилка плагіна: " << ex.what() << '\n';
        }
    });

    return 0;
}
