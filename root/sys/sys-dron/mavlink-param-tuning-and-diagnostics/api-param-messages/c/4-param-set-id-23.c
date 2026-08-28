/* Бінарна структура повідомлення PARAM_SET */
typedef struct __mavlink_param_set_t {
    float   param_value;      /* нове значення */
    uint8_t target_system;    /* ID цільової системи */
    uint8_t target_component; /* ID цільового компонента */
    char    param_id[16];     /* назва параметра */
    uint8_t param_type;       /* тип значення */
} mavlink_param_set_t;

/* Пакування цілого значення uint32 у float поле PARAM_SET */
void set_param_uint32(mavlink_param_set_t *set_msg,
                      uint8_t target_sys, uint8_t target_comp,
                      const char *name, uint32_t val) {
    set_msg->target_system = target_sys;
    set_msg->target_component = target_comp;
    strncpy(set_msg->param_id, name, 16);
    set_msg->param_type = MAV_PARAM_TYPE_UINT32;
    memcpy(&set_msg->param_value, &val, sizeof(float));
}
