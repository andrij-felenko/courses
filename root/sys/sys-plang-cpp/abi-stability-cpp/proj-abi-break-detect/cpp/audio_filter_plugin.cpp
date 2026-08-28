// audio_filter_plugin.cpp — реалізація плагіна обробки аудіо
#define PLUGIN_EXPORTS
#include "plugin_abi.hpp"
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>

// Внутрішній C++ клас плагіна (повністю прихований від клієнта)
struct plugin_handle_opaque {
    std::vector<double> coefficients;
    double gain = 1.0;
    uint64_t processed_frames = 0;

    plugin_handle_opaque() {
        coefficients.resize(64, 0.015625); // Фільтр ковзного середнього (FIR)
    }

    double compute_filtered_sample(const uint8_t* data, size_t len) {
        double accumulated = 0.0;
        for (size_t i = 0; i < len; ++i) {
            double normalized = static_cast<double>(data[i]) / 255.0;
            accumulated += normalized * coefficients[i % coefficients.size()];
        }
        processed_frames += len;
        return accumulated * gain;
    }
};

plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta) {
    if (!out_meta) return PLUGIN_ERR_INVALID_ARG;
    out_meta->abi_version_major = 1;
    out_meta->abi_version_minor = 0;
    out_meta->patch_version = 0;
    out_meta->plugin_name = "AudioLowPassFilter";
    out_meta->vendor_name = "AcousticLab";
    return PLUGIN_SUCCESS;
}

plugin_status_t plugin_create_instance(plugin_handle_t* out_handle) {
    if (!out_handle) return PLUGIN_ERR_INVALID_ARG;
    try {
        *out_handle = new plugin_handle_opaque();
        return PLUGIN_SUCCESS;
    } catch (...) {
        return PLUGIN_ERR_OUT_OF_MEMORY;
    }
}

plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric) {
    if (!handle || !in_data || size == 0 || !out_metric) {
        return PLUGIN_ERR_INVALID_ARG;
    }

    try {
        *out_metric = handle->compute_filtered_sample(in_data, size);
        return PLUGIN_SUCCESS;
    } catch (...) {
        return PLUGIN_ERR_EXECUTION_FAILED;
    }
}

void plugin_destroy_instance(plugin_handle_t handle) {
    // Звільнення пам'яті відбувається в тому самому модулі, де був виклик new
    delete handle;
}
