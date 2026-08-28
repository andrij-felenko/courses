// src/main.cpp
#include <fastcodec/fastcodec.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>

struct FastCodecDeleter {
    void operator()(fastcodec_ctx_t* ctx) const noexcept {
        if (ctx) {
            fastcodec_free_context(ctx);
        }
    }
};

using SafeContext = std::unique_ptr<fastcodec_ctx_t, FastCodecDeleter>;

SafeContext make_codec_context() {
    fastcodec_config_t config;
    fastcodec_get_default_config(&config);
    
    fastcodec_ctx_t* raw = fastcodec_create_context(&config);
    if (!raw) {
        throw std::runtime_error("Не вдалося виділити ресурси для FastCodec");
    }
    return SafeContext(raw);
}

int main() {
    std::cout << "FastCodec C++ client, version " 
              << std::string_view(FASTCODEC_VERSION_STRING) << "\n";
    try {
        auto ctx = make_codec_context();
        std::cout << "Контекст стиснення успішно ініціалізовано через RAII.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
