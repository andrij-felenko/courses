/* Бінарна структура повідомлення PARAM_REQUEST_LIST */
typedef struct __mavlink_param_request_list_t {
    uint8_t target_system;     /* ID системи-адресата */
    uint8_t target_component;  /* ID компонента-адресата */
} mavlink_param_request_list_t;

/* Функція пакування повідомлення у буфер */
int pack_param_request_list(uint8_t sys_id, uint8_t comp_id,
                            uint8_t target_sys, uint8_t target_comp,
                            uint8_t *buffer) {
    mavlink_message_t msg;
    mavlink_param_request_list_t payload;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    mavlink_msg_param_request_list_encode(sys_id, comp_id, &msg, &payload);
    return mavlink_msg_to_send_buffer(buffer, &msg);
}
