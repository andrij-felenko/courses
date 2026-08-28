#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <dlfcn.h>
#include <stdexcept>

// RAII обгортка для дескриптора динамічної бібліотеки dlopen
struct DynamicLibDeleter {
    void operator()(void* handle) const noexcept {
        if (handle) dlclose(handle);
    }
};

using ScopedSharedLib = std::unique_ptr<void, DynamicLibDeleter>;

class DynamicEngineLoader {
public:
    explicit DynamicEngineLoader(const std::string& lib_path) {
        void* handle = dlopen(lib_path.c_str(), RTLD_NOW | RTLD_LOCAL);
        if (!handle) {
            throw std::runtime_error(std::string("Помилка завантаження бібліотеки: ") + dlerror());
        }
        lib_ = ScopedSharedLib(handle);

        create_fn_ = reinterpret_cast<CreateFn>(dlsym(lib_.get(), "engine_create"));
        destroy_fn_ = reinterpret_cast<DestroyFn>(dlsym(lib_.get(), "engine_destroy"));
        process_fn_ = reinterpret_cast<ProcessFn>(dlsym(lib_.get(), "engine_process"));
        error_fn_ = reinterpret_cast<ErrorFn>(dlsym(lib_.get(), "engine_get_last_error"));

        if (!create_fn_ || !destroy_fn_ || !process_fn_ || !error_fn_) {
            throw std::runtime_error(std::string("Не знайдено C-символи: ") + dlerror());
        }
    }

    void run_demo() {
        struct engine_ctx_t* ctx = nullptr;
        if (create_fn_("XOR-FAST", &ctx) != 0) {
            throw std::runtime_error(std::string("Збій створення: ") + error_fn_());
        }

        const std::vector<uint8_t> data = {0xAA, 0xBB, 0xCC};
        std::vector<uint8_t> out(data.size());
        size_t out_len = out.size();

        process_fn_(ctx, data.data(), data.size(), out.data(), &out_len);
        std::cout << "[Dynamic C++] Успішно опрацьовано " << out_len << " байтів через dlopen/dlsym\n";

        destroy_fn_(ctx);
    }

private:
    using CreateFn = int (*)(const char*, struct engine_ctx_t**);
    using DestroyFn = void (*)(struct engine_ctx_t*);
    using ProcessFn = int (*)(struct engine_ctx_t*, const uint8_t*, size_t, uint8_t*, size_t*);
    using ErrorFn = const char* (*)(void);

    ScopedSharedLib lib_;
    CreateFn create_fn_{nullptr};
    DestroyFn destroy_fn_{nullptr};
    ProcessFn process_fn_{nullptr};
    ErrorFn error_fn_{nullptr};
};

int main() {
    try {
        DynamicEngineLoader loader("./libengine.so");
        loader.run_demo();
    } catch (const std::exception& ex) {
        std::cerr << "[Dynamic C++] Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
