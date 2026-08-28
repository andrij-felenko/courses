/* Бінарна структура повідомлення PARAM_REQUEST_READ */
typedef struct __mavlink_param_request_read_t {
    int16_t param_index;      /* індекс або -1 */
    uint8_t target_system;    /* ID системи */
    uint8_t target_component; /* ID компонента */
    char    param_id[16];     /* назва */
} mavlink_param_request_read_t;

/* Складання запиту за індексом */
void make_read_by_index_request(mavlink_param_request_read_t *req,
                                uint8_t target_sys, uint8_t target_comp,
                                int16_t index) {
    req->target_system = target_sys;
    req->target_component = target_comp;
    req->param_index = index;
    memset(req->param_id, 0, 16);
}

/* Складання запиту за назвою */
void make_read_by_name_request(mavlink_param_request_read_t *req,
                               uint8_t target_sys, uint8_t target_comp,
                               const char *name) {
    req->target_system = target_sys;
    req->target_component = target_comp;
    req->param_index = -1;
    strncpy(req->param_id, name, 16);
}
