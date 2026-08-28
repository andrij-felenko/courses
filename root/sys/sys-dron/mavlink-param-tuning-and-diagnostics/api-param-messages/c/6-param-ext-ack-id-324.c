/* Бінарна структура повідомлення PARAM_EXT_ACK */
typedef struct __mavlink_param_ext_ack_t {
    char    param_id[16];     /* назва параметра */
    char    param_value[128]; /* підтверджене значення */
    uint8_t param_type;       /* MAV_PARAM_TYPE */
    uint8_t param_result;     /* результат операції (PARAM_ACK) */
} mavlink_param_ext_ack_t;

/* Перевірка успішності запису розширеного параметра */
bool is_ext_param_write_successful(const mavlink_param_ext_ack_t *ack) {
    return (ack->param_result == 0); /* 0 == PARAM_ACK_ACCEPTED */
}
