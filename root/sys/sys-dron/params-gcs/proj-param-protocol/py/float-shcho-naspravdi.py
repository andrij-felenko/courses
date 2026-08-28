_INT_TYPES = {
    MAV_PARAM_TYPE_INT8,  MAV_PARAM_TYPE_INT16,  MAV_PARAM_TYPE_INT32,
    MAV_PARAM_TYPE_UINT8, MAV_PARAM_TYPE_UINT16, MAV_PARAM_TYPE_UINT32,
}

# Перетягнути значення в потрібне ціле за оголошеним типом:
def typed_int(p: ParamValue) -> int:
    if p.param_type in _INT_TYPES:
        return param_as_int(p.param_value)      # байти, не округлення
    return round(p.param_value)                 # справді float
