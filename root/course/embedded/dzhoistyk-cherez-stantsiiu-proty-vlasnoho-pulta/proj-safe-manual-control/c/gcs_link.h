#ifndef GCS_LINK_H
#define GCS_LINK_H

#include "arbiter.h"
#include "mavlink_frame.h"

/* Радіоміст «наземна станція — борт»: розбирає потік із UART радіомодема,
 * відсіює чужі станції й чужі адреси і годує арбітра.
 *
 * Ключова деталь бар'єра 4: HEARTBEAT оновлює ЛИШЕ власну мітку часу.
 * Завислим вікном джойстика станція далі шле серцебиття 1 Гц — і якби воно
 * заходило в арбітра, таймаут ніколи б не спрацював. */

#define GCS_RELATCH_MS 3000u /* після такої тиші дозволяємо зафіксувати іншу станцію */

typedef struct {
    uint8_t our_sysid;
    uint8_t our_compid;

    uint8_t  gcs_sysid;          /* 0 — авторизованої станції ще немає */
    uint8_t  gcs_compid;
    uint32_t last_gcs_frame_ms;  /* останній кадр керування від «своєї» станції */
    uint32_t last_heartbeat_ms;  /* окремо від арбітражу — навмисно */

    mav_parser_t parser;
    uint8_t      tx_seq;
    uint8_t      ack[32];        /* готовий COMMAND_ACK на відправку в модем */
    size_t       ack_len;

    uint32_t n_manual;
    uint32_t n_heartbeat;
    uint32_t n_foreign;        /* пакети від незафіксованої станції */
    uint32_t n_wrong_target;   /* адресовані не нам */
    uint32_t n_arm_cmd;
} gcs_link_t;

void gcs_link_init(gcs_link_t *l, uint8_t sysid, uint8_t compid);
void gcs_link_feed(gcs_link_t *l, const uint8_t *data, size_t n, uint32_t now_ms, arbiter_t *arb);

/* Забирає підготовлений COMMAND_ACK (порожньо — нема чого слати). */
bool gcs_link_take_ack(gcs_link_t *l, const uint8_t **buf, size_t *len);

#endif /* GCS_LINK_H */
