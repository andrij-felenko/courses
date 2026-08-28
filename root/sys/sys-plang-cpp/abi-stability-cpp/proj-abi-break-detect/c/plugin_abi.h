/* plugin_abi.h — C ABI інтерфейс (рівень двійкової сумісності) */
#ifndef PLUGIN_ABI_H
#define PLUGIN_ABI_H

#include <stdint.h>
#include <stddef.h>

#if defined(_WIN32)
  #ifdef PLUGIN_EXPORTS
    #define PLUGIN_API __declspec(dllexport)
  #else
    #define PLUGIN_API __declspec(dllimport)
  #endif
#else
  #define PLUGIN_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий дескриптор екземпляра плагіна */
typedef struct plugin_handle_opaque* plugin_handle_t;

/* Структура інформації про версію та сумісність */
typedef struct {
    uint32_t abi_version_major;
    uint32_t abi_version_minor;
    uint32_t patch_version;
    const char* plugin_name;
    const char* vendor_name;
} plugin_metadata_t;

/* Коди помилок операцій плагіна */
typedef enum {
    PLUGIN_SUCCESS = 0,
    PLUGIN_ERR_INVALID_ARG = -1,
    PLUGIN_ERR_EXECUTION_FAILED = -2,
    PLUGIN_ERR_OUT_OF_MEMORY = -3
} plugin_status_t;

/* Сигнатури точок входу динамічної бібліотеки */
PLUGIN_API plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta);
PLUGIN_API plugin_status_t plugin_create_instance(plugin_handle_t* out_handle);
PLUGIN_API plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric);
PLUGIN_API void            plugin_destroy_instance(plugin_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* PLUGIN_ABI_H */
