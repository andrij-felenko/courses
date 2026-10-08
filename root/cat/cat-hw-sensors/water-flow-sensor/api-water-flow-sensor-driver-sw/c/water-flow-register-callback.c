typedef enum {
    WATER_FLOW_EVENT_MAX_THRESHOLD_EXCEEDED,
    WATER_FLOW_EVENT_ZERO_FLOW_DETECTED,
    WATER_FLOW_EVENT_LEAK_DETECTED
} water_flow_event_type_t;

typedef struct {
    water_flow_event_type_t event_type;
    float current_flow_lmin;
    double total_volume_liters;
} water_flow_event_data_t;

typedef void (*water_flow_callback_t)(const water_flow_event_data_t *event, void *user_data);

water_flow_err_t water_flow_register_callback(water_flow_handle_t *dev,
                                               water_flow_callback_t cb,
                                               void *user_data,
                                               float max_threshold_lmin) {
    if (!dev || !dev->is_initialized) {
        return WATER_FLOW_ERR_NOT_INITIALIZED;
    }
    dev->callback = cb;
    dev->user_data = user_data;
    dev->max_flow_threshold_lmin = max_threshold_lmin;
    return WATER_FLOW_OK;
}
