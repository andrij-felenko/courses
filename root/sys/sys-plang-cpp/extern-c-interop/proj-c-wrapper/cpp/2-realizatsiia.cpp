#include "engine_api.h"
#include <vector>
#include <string>
#include <memory>
#include <stdexcept>
#include <new>
#include <cstring>
#include <mutex>

/* Потоколокальне сховище останнього діагностичного повідомлення */
thread_local std::string g_last_error_message;

static void set_last_error(const std::string& msg) noexcept {
    g_last_error_message = msg;
}

/* Внутрішній клас обчислювального ядра */
class EngineCore {
public:
    explicit EngineCore(std::string algo) : algorithm_(std::move(algo)) {
        if (algorithm_.empty()) {
            throw std::invalid_argument("Ім'я алгоритму не може бути порожнім рядком");
        }
        if (algorithm_ != "AES-CTR-STREAM" && algorithm_ != "XOR-FAST") {
            throw std::invalid_argument("Непідтримуваний алгоритм: " + algorithm_);
        }
        buffer_.reserve(8192);
    }

    ~EngineCore() {
        // Якщо клієнт надав функцію очищення контексту, гарантовано викликаємо її
        if (cleanup_ && user_data_) {
            cleanup_(user_data_);
            user_data_ = nullptr;
        }
    }

    // Заборона копіювання для збереження унікального володіння
    EngineCore(const EngineCore&) = delete;
    EngineCore& operator=(const EngineCore&) = delete;

    void set_callback(engine_progress_cb cb, void* user_data, engine_cleanup_cb cleanup) noexcept {
        if (cleanup_ && user_data_ && user_data_ != user_data) {
            cleanup_(user_data_);
        }
        callback_ = cb;
        user_data_ = user_data;
        cleanup_ = cleanup;
    }

    size_t process_data(const uint8_t* in_data, size_t len, uint8_t* out_data, size_t max_out) {
        if (!in_data || !out_data) {
            throw std::invalid_argument("Вхідний або вихідний покажчик буфера дорівнює nullptr");
        }
        if (max_out < len) {
            throw std::runtime_error("Вихідний буфер замалий для збереження результату");
        }

        const uint8_t mask = (algorithm_ == "XOR-FAST") ? 0xAA : 0x55;
        for (size_t i = 0; i < len; ++i) {
            out_data[i] = in_data[i] ^ mask;
        }

        if (callback_) {
            callback_(len, user_data_);
        }
        return len;
    }

private:
    std::string algorithm_;
    std::vector<uint8_t> buffer_;
    engine_progress_cb callback_{nullptr};
    void* user_data_{nullptr};
    engine_cleanup_cb cleanup_{nullptr};
};

/* Повне визначення структури дескриптора у C++ одиниці трансляції */
struct engine_ctx_t {
    std::unique_ptr<EngineCore> core;
};

/* Реалізація експортованого інтерфейсу з повним бар'єром винятків */
extern "C" {

engine_status_t engine_create(const char* algorithm_name, engine_ctx_t** out_ctx) {
    if (!algorithm_name || !out_ctx) {
        set_last_error("Неприпустимий нульовий покажчик аргументу конфігурації");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }
    *out_ctx = nullptr;

    try {
        auto handle = std::make_unique<engine_ctx_t>();
        handle->core = std::make_unique<EngineCore>(std::string(algorithm_name));
        
        // Передаємо володіння сирому покажчику виключно після успішної ініціалізації
        *out_ctx = handle.release();
        return ENGINE_STATUS_OK;
    } catch (const std::invalid_argument& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_INVALID_ARG;
    } catch (const std::bad_alloc& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_OUT_OF_MEMORY;
    } catch (const std::exception& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_UNKNOWN;
    } catch (...) {
        set_last_error("Невідомий системний виняток у конструкторі рушія");
        return ENGINE_STATUS_ERR_UNKNOWN;
    }
}

void engine_destroy(engine_ctx_t* ctx) {
    if (!ctx) return;
    try {
        // Відновлюємо RAII-володіння: оператор delete викличе деструктори EngineCore,
        // std::string, std::vector та функцію очищення cleanup_
        std::unique_ptr<engine_ctx_t> cleaner(ctx);
    } catch (...) {
        // Захист межі C-ABI: жоден виняток під час руйнування не повинен покинути функцію
    }
}

engine_status_t engine_process(engine_ctx_t* ctx,
                               const uint8_t* input,
                               size_t input_len,
                               uint8_t* output,
                               size_t* inout_output_len) {
    if (!ctx || !ctx->core || !inout_output_len) {
        set_last_error("Недійсний дескриптор рушія або покажчик розміру виходу");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }

    try {
        size_t written = ctx->core->process_data(input, input_len, output, *inout_output_len);
        *inout_output_len = written;
        return ENGINE_STATUS_OK;
    } catch (const std::invalid_argument& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_INVALID_ARG;
    } catch (const std::runtime_error& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_PROCESSING;
    } catch (const std::bad_alloc& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_OUT_OF_MEMORY;
    } catch (const std::exception& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_UNKNOWN;
    } catch (...) {
        set_last_error("Критичний невідомий збій під час обробки даних");
        return ENGINE_STATUS_ERR_UNKNOWN;
    }
}

engine_status_t engine_set_progress_callback(engine_ctx_t* ctx,
                                             engine_progress_cb cb,
                                             void* user_data,
                                             engine_cleanup_cb cleanup) {
    if (!ctx || !ctx->core) {
        set_last_error("Недійсний дескриптор рушія");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }
    ctx->core->set_callback(cb, user_data, cleanup);
    return ENGINE_STATUS_OK;
}

const char* engine_get_last_error(void) {
    return g_last_error_message.c_str();
}

} // extern "C"
