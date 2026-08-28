// plugin_abi.hpp — C++ ідіоматичний фасад поверх стабільного C ABI
#pragma once
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <span>
#include <system_error>

#if defined(_WIN32)
  #ifdef PLUGIN_EXPORTS
    #define PLUGIN_API __declspec(dllexport)
  #else
    #define PLUGIN_API __declspec(dllimport)
  #endif
#else
  #define PLUGIN_API __attribute__((visibility("default")))
#endif

extern "C" {
    struct plugin_handle_opaque;
    using plugin_handle_t = plugin_handle_opaque*;

    struct plugin_metadata_t {
        uint32_t abi_version_major;
        uint32_t abi_version_minor;
        uint32_t patch_version;
        const char* plugin_name;
        const char* vendor_name;
    };

    enum plugin_status_t : int32_t {
        PLUGIN_SUCCESS = 0,
        PLUGIN_ERR_INVALID_ARG = -1,
        PLUGIN_ERR_EXECUTION_FAILED = -2,
        PLUGIN_ERR_OUT_OF_MEMORY = -3
    };

    PLUGIN_API plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta);
    PLUGIN_API plugin_status_t plugin_create_instance(plugin_handle_t* out_handle);
    PLUGIN_API plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric);
    PLUGIN_API void            plugin_destroy_instance(plugin_handle_t handle);
}

namespace plugin_system {
inline namespace v1 {

// RAII кастомний деструктор для непрозорого C-дескриптора
struct PluginDeleter {
    void operator()(plugin_handle_t h) const noexcept {
        if (h) {
            plugin_destroy_instance(h);
        }
    }
};

using SafeHandle = std::unique_ptr<plugin_handle_opaque, PluginDeleter>;

// Безпечний C++ клас-клієнт із нульовими накладними витратами
class PluginClient {
public:
    PluginClient() {
        plugin_handle_t raw_handle = nullptr;
        plugin_status_t status = plugin_create_instance(&raw_handle);
        if (status != PLUGIN_SUCCESS || !raw_handle) {
            throw std::runtime_error("Не вдалося створити екземпляр плагіна");
        }
        handle_.reset(raw_handle);
    }

    double process(std::span<const uint8_t> buffer) {
        double result = 0.0;
        plugin_status_t status = plugin_process_data(handle_.get(), buffer.data(), buffer.size(), &result);
        if (status != PLUGIN_SUCCESS) {
            throw std::runtime_error("Збій обробки даних у плагіні");
        }
        return result;
    }

private:
    SafeHandle handle_;
};

} // namespace v1
} // namespace plugin_system
