/* gcs_focus_manager.h — контекст вибору апарата на пульті оператора. */
#ifndef GCS_FOCUS_MANAGER_H
#define GCS_FOCUS_MANAGER_H

#include "sbo_protocol.h"

/* Скільки чекаємо квитанції по радіо, перш ніж визнати звʼязок утраченим. */
#define GCS_ACK_TIMEOUT_MS 400u
/* Запас, на який пульт закриває вікно раніше за борт: кадр іще має долетіти. */
#define GCS_GUARD_MS       150u
#define GCS_NAME_LEN       16u

typedef enum {
    GCS_FOCUS_NONE = 0,     /* апарат не обрано */
    GCS_FOCUS_WAIT_ACK,     /* SELECT_REQ надіслано, чекаємо SELECT_ACK */
    GCS_FOCUS_ARMED,        /* борт підтвердив: кнопка дії активна */
    GCS_FOCUS_WAIT_OP,      /* OPERATE_REQ надіслано, чекаємо квитанції */
    GCS_FOCUS_DONE,         /* борт відзвітував про виконання */
    GCS_FOCUS_LINK_LOST,    /* квитанція не надійшла за GCS_ACK_TIMEOUT_MS */
    GCS_FOCUS_REJECTED,     /* борт відмовив (NACK) */
    GCS_FOCUS_EXPIRED       /* вікно селекції спливло без дії */
} gcs_focus_status_t;

typedef struct {
    uint8_t            self_id;
    uint8_t            focused_target_id;
    uint8_t            focused_comp;
    char               target_name[GCS_NAME_LEN];
    uint16_t           pending_cmd_code;
    uint16_t           window_ms;
    uint32_t           token;
    uint32_t           sent_ms;            /* коли пішов останній запит */
    uint32_t           ack_deadline_ms;
    uint32_t           select_deadline_ms;
    uint8_t            seq;
    gcs_focus_status_t status;
    sbo_error_t        last_error;
} gcs_focus_t;

void gcs_focus_init(gcs_focus_t *focus, uint8_t self_id);

/* Клік по картці апарата: будує SELECT_REQ і запускає відлік квитанції.
 * false — ціль неприпустима (широкомовна адреса або власний ідентифікатор). */
bool gcs_focus_select(gcs_focus_t *focus, uint8_t target_id, uint8_t component,
                      const char *name, uint16_t cmd_code, uint16_t window_ms,
                      uint32_t now_ms, sbo_packet_t *out_select);

/* Викликати з циклу перемальовування інтерфейсу. */
void gcs_focus_tick(gcs_focus_t *focus, uint32_t now_ms);

void gcs_focus_on_response(gcs_focus_t *focus, const sbo_packet_t *rx, uint32_t now_ms);

/* Кнопка дії: віддає кадр лише зі зведеним замком і лише один раз. */
bool gcs_focus_build_operate(gcs_focus_t *focus, const uint8_t *payload, uint8_t payload_len,
                             uint32_t now_ms, sbo_packet_t *out_operate);

bool gcs_focus_build_cancel(gcs_focus_t *focus, uint32_t now_ms, sbo_packet_t *out_cancel);

bool        gcs_focus_button_enabled(const gcs_focus_t *focus, uint32_t now_ms);
const char *gcs_focus_badge(const gcs_focus_t *focus);   /* підпис на картці */
uint32_t    gcs_focus_frame_color(const gcs_focus_t *focus); /* 0xRRGGBB рамки картки */

#endif /* GCS_FOCUS_MANAGER_H */
