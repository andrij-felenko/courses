water_flow_err_t water_flow_get_rate_lmin(const water_flow_handle_t *dev, float *flow_lmin) {
    if (!dev || !dev->is_initialized || !flow_lmin) {
        return WATER_FLOW_ERR_NOT_INITIALIZED;
    }
    *flow_lmin = dev->current_flow_lmin;
    return WATER_FLOW_OK;
}

water_flow_err_t water_flow_get_rate_m3h(const water_flow_handle_t *dev, float *flow_m3h) {
    if (!dev || !dev->is_initialized || !flow_m3h) {
        return WATER_FLOW_ERR_NOT_INITIALIZED;
    }
    *flow_m3h = dev->current_flow_lmin * 0.06f;
    return WATER_FLOW_OK;
}

water_flow_err_t water_flow_get_total_volume(const water_flow_handle_t *dev, double *volume_liters) {
    if (!dev || !dev->is_initialized || !volume_liters) {
        return WATER_FLOW_ERR_NOT_INITIALIZED;
    }
    *volume_liters = dev->total_volume_liters;
    return WATER_FLOW_OK;
}

water_flow_err_t water_flow_reset_total_volume(water_flow_handle_t *dev) {
    if (!dev || !dev->is_initialized) {
        return WATER_FLOW_ERR_NOT_INITIALIZED;
    }
    dev->total_volume_liters = 0.0;
    return WATER_FLOW_OK;
}
