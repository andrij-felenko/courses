/* Бінарна структура повідомлення PARAM_EXT_VALUE */
typedef struct __mavlink_param_ext_value_t {
    uint16_t param_count;     /* загальна кількість */
    uint16_t param_index;     /* числовий індекс */
    char     param_id[16];    /* 16-байтна назва */
    char     param_value[128];/* 128-байтний буфер даних */
    uint8_t  param_type;      /* MAV_PARAM_TYPE */
} mavlink_param_ext_value_t;

/* Вичитування 64-бітного беззнакового цілого з розширеного буфера */
uint64_t get_ext_param_uint64(const mavlink_param_ext_value_t *msg) {
    uint64_t val = 0;
    memcpy(&val, msg->param_value, sizeof(uint64_t));
    return val;
}

/* Вичитування 64-бітного float подвійної точності */
double get_ext_param_real64(const mavlink_param_ext_value_t *msg) {
    double val = 0.0;
    memcpy(&val, msg->param_value, sizeof(double));
    return val;
}
