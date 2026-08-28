#include <stdint.h>
#include <stddef.h>

#define L2CAP_CID_BLE_SIGNALING          0x0006
#define L2CAP_CMD_CONN_PARAM_UPDATE_REQ  0x12

typedef struct __attribute__((packed)) {
    /* Заголовок кадру адаптації L2CAP */
    uint16_t l2cap_length;      /* Довжина поля сигналізації = 12 байтів */
    uint16_t l2cap_cid;         /* 0x0006 (LE Signaling Channel) */
    
    /* Заголовок команди сигналізації */
    uint8_t  command_code;      /* 0x12 (Connection Parameter Update Request) */
    uint8_t  identifier;        /* Унікальний ID транзакції для зіставлення з відповіддю */
    uint16_t command_length;    /* Довжина корисного навантаження команди = 8 байтів */
    
    /* Параметри зв'язку (усі числові поля у форматі Little-Endian) */
    uint16_t interval_min;      /* Мінімальний інтервал (одиниці 1.25 мс) */
    uint16_t interval_max;      /* Максимальний інтервал (одиниці 1.25 мс) */
    uint16_t slave_latency;     /* Дозволений пропуск подій зв'язку периферією */
    uint16_t timeout_multiplier;/* Supervision Timeout (одиниці 10 мс) */
} l2cap_conn_param_update_req_t;

/**
 * @brief Побудова пакета запиту оновлення параметрів зв'язку L2CAP.
 * @param out_buf Буфер для запису сформованого кадру (мінімум 16 байтів).
 * @param max_buf_len Максимальний розмір буфера.
 * @param pkt_id Унікальний лічильник транзакції.
 * @param min_ms Мінімальний інтервал у мілісекундах (наприклад, 100.0 мс).
 * @param max_ms Максимальний інтервал у мілісекундах (наприклад, 200.0 мс).
 * @param latency Кількість подій для пропуску (наприклад, 4).
 * @param timeout_ms Тайм-аут нагляду в мілісекундах (наприклад, 4000 мс).
 * @return Фактичний розмір зібраного пакета в байтах.
 */
size_t build_l2cap_param_update_req(uint8_t* out_buf, size_t max_buf_len,
                                    uint8_t pkt_id,
                                    float min_ms, float max_ms,
                                    uint16_t latency, uint16_t timeout_ms)
{
    if (!out_buf || max_buf_len < sizeof(l2cap_conn_param_update_req_t)) {
        return 0;
    }

    l2cap_conn_param_update_req_t* req = (l2cap_conn_param_update_req_t*)out_buf;

    req->l2cap_length    = 12; // 4 байти заголовка команди + 8 байтів параметрів
    req->l2cap_cid       = L2CAP_CID_BLE_SIGNALING;
    req->command_code    = L2CAP_CMD_CONN_PARAM_UPDATE_REQ;
    req->identifier      = pkt_id;
    req->command_length  = 8;

    /* Переведення часових інтервалів у стандартні протокольні дискрети */
    req->interval_min       = (uint16_t)(min_ms / 1.25f);
    req->interval_max       = (uint16_t)(max_ms / 1.25f);
    req->slave_latency      = latency;
    req->timeout_multiplier = (uint16_t)(timeout_ms / 10);

    return sizeof(l2cap_conn_param_update_req_t);
}
