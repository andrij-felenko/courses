#include "legacy_adapter.hpp"
#include <cstdlib>
#include <cstring>

// Симуляція сторонньої бібліотеки епохи C++03
namespace vendor_cxx03 {
    struct VendorDatabaseEngine {
        bool init(const char* path) {
            return path != nullptr;
        }

        // Старий API повертає динамічно виділений C-рядок, який треба звільняти вручну
        char* process(const char* sql, int len) {
            if (!sql || len <= 0) return nullptr;
            const char* response_prefix = "SUCCESS_RESULT: ";
            std::size_t total_len = std::strlen(response_prefix) + static_cast<std::size_t>(len) + 1;
            char* buffer = static_cast<char*>(std::malloc(total_len));
            if (!buffer) return nullptr;
            std::strcpy(buffer, response_prefix);
            std::strncat(buffer, sql, static_cast<std::size_t>(len));
            return buffer;
        }

        void free_result(char* ptr) {
            std::free(ptr);
        }
    };
}

namespace modern_system {

struct LegacyEngineAdapter::Impl {
    vendor_cxx03::VendorDatabaseEngine engine;
};

LegacyEngineAdapter::LegacyEngineAdapter()
    : pimpl_(std::make_unique<Impl>()) {}

LegacyEngineAdapter::~LegacyEngineAdapter() = default;
LegacyEngineAdapter::LegacyEngineAdapter(LegacyEngineAdapter&&) noexcept = default;
LegacyEngineAdapter& LegacyEngineAdapter::operator=(LegacyEngineAdapter&&) noexcept = default;

bool LegacyEngineAdapter::configure(std::string_view config_path) {
    // Безпечне перетворення рядкового перегляду в сумісний null-terminated рядок
    std::string safe_path(config_path);
    return pimpl_->engine.init(safe_path.c_str());
}

std::string LegacyEngineAdapter::execute_query(std::string_view query) {
    std::string safe_query(query);
    char* raw_data = pimpl_->engine.process(
        safe_query.c_str(),
        static_cast<int>(safe_query.size())
    );

    if (!raw_data) {
        return {};
    }

    // Захоплення сирого вказівника у стандартний рядок C++ та негайне звільнення буфера
    std::string result(raw_data);
    pimpl_->engine.free_result(raw_data);
    return result;
}

} // namespace modern_system
