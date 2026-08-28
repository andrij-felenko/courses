// Перетягнути значення в потрібне ціле за оголошеним типом:
int32_t typed_int(const mavlink_param_value_t *p) {
    switch (p->param_type) {
        case MAV_PARAM_TYPE_INT8:
        case MAV_PARAM_TYPE_INT16:
        case MAV_PARAM_TYPE_INT32:
        case MAV_PARAM_TYPE_UINT8:
        case MAV_PARAM_TYPE_UINT16:
        case MAV_PARAM_TYPE_UINT32:
            return param_as_int(p->param_value);   // байти, не округлення
        default:
            return (int32_t) lroundf(p->param_value);  // справді float
    }
}
