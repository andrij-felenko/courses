#include "engine_api.h"
#include <iostream>
#include <memory>
#include <vector>
#include <span>
#include <string_view>
#include <functional>
#include <stdexcept>

// Власний Deleter для безпечного автоматичного виклику engine_destroy
struct EngineDeleter {
    void operator()(engine_ctx_t* ptr) const noexcept {
        engine_destroy(ptr);
    }
};

using ScopedEngineHandle = std::unique_ptr<engine_ctx_t, EngineDeleter>;

// Ідіоматична обгортка мовою C++ з повним контролем винятків та RAII
class CryptoEngine {
public:
    explicit CryptoEngine(std::string_view algo) {
        engine_ctx_t* raw_ptr = nullptr;
        engine_status_t st = engine_create(algo.data(), &raw_ptr);
        if (st != ENGINE_STATUS_OK) {
            throw std::runtime_error(std::string("Не вдалося ініціалізувати рушій: ") + 
                                     engine_get_last_error());
        }
        handle_.reset(raw_ptr);
    }

    // Реєстрація довільної лямбда-функції з підтримкою захоплення стану
    template <typename Callback>
    void set_progress_handler(Callback&& cb) {
        callback_holder_ = std::make_unique<std::function<void(size_t)>>(std::forward<Callback>(cb));

        // Статичний трамплін для перетворення C-виклику у виклик std::function
        auto trampoline = [](size_t bytes, void* user_data) noexcept {
            auto* target = static_cast<std::function<void(size_t)>*>(user_data);
            if (target && *target) {
                (*target)(bytes);
            }
        };

        engine_set_progress_callback(
            handle_.get(),
            trampoline,
            callback_holder_.get(),
            nullptr
        );
    }

    // Зручна обробка через контейнери та std::span
    std::vector<uint8_t> process(std::span<const uint8_t> input) {
        std::vector<uint8_t> output(input.size());
        size_t out_len = output.size();

        engine_status_t st = engine_process(handle_.get(),
                                            input.data(),
                                            input.size(),
                                            output.data(),
                                            &out_len);
        if (st != ENGINE_STATUS_OK) {
            throw std::runtime_error(std::string("Помилка обробки блоку даних: ") + 
                                     engine_get_last_error());
        }
        output.resize(out_len);
        return output;
    }

private:
    ScopedEngineHandle handle_;
    std::unique_ptr<std::function<void(size_t)>> callback_holder_;
};

int main() {
    try {
        CryptoEngine engine("XOR-FAST");

        size_t total_processed = 0;
        engine.set_progress_handler([&total_processed](size_t bytes) {
            total_processed += bytes;
            std::cout << "[C++ Client] Прогрес: оброблено +" << bytes 
                      << " байтів (сумарно: " << total_processed << ")\n";
        });

        const std::vector<uint8_t> input_data = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
        auto result = engine.process(input_data);

        std::cout << "[C++ Client] Завершено успішно. Результат[" << result.size() 
                  << " байтів], перший байт: 0x" << std::hex 
                  << static_cast<int>(result[0]) << std::dec << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "[C++ Client] Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
