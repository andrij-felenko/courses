/* Прогін чотирьох сценаріїв розділу 7 профілю на симульованому радіоканалі:
   один вузол, один-два пульти, керований годинник і керовані втрати пакетів. */
#include "sbo_client.h"
#include "sbo_node.h"

#include <stdio.h>

struct link {
    unsigned drops_left;   /* скільки найближчих кадрів проковтне ефір */
};

/* Передає кадр вузлу. Повертає довжину відповіді (0 — тиша в ефірі). */
static size_t link_send(struct link *l, struct sbo_node *node, uint32_t now_ms,
                        const uint8_t *req, size_t req_len,
                        uint8_t *rsp, size_t rsp_cap)
{
    if (l->drops_left > 0) {
        l->drops_left--;
        printf("    [ефір] кадр загублено\n");
        return 0;
    }
    return sbo_node_handle(node, req, req_len, now_ms, rsp, rsp_cap);
}

static void print_reply(const struct sbo_frame *r)
{
    printf("    борт -> пульт: %-12s стан=%-9s токен=0x%08X вікно=%u мс",
           sbo_msg_name(r->msg_type), sbo_state_name(r->sbo_state),
           r->sbo_token, (unsigned)r->timeout_ms);
    if (r->payload_len >= 1) {
        printf(" причина=%s", sbo_error_name(r->payload[0]));
    }
    printf("\n");
}

/* Обмін одним кадром: віддати, дочекатися, розібрати. */
static bool exchange(struct link *l, struct sbo_node *node, struct sbo_client *c,
                     uint32_t now_ms, const uint8_t *req, size_t req_len,
                     struct sbo_frame *reply)
{
    uint8_t rsp[SBO_MAX_FRAME];
    const size_t n = link_send(l, node, now_ms, req, req_len, rsp, sizeof(rsp));
    if (n == 0) {
        return false;
    }
    if (sbo_decode(rsp, n, reply) != SBO_DECODE_OK) {
        printf("    [пульт] квитанція не пройшла перевірку CRC\n");
        return false;
    }
    sbo_client_on_reply(c, reply);
    print_reply(reply);
    return true;
}

static void scenario_a(void)
{
    printf("\n=== Сценарій А: номінальна транзакція (з утратою першого кадру) ===\n");

    struct sbo_node node;
    struct sbo_client gcs;
    struct link air = { .drops_left = 1 };
    uint8_t req[SBO_MAX_FRAME];
    struct sbo_frame reply;
    uint32_t now = 0;

    sbo_node_init(&node, 0x02, 0xC0FFEEu);
    sbo_client_init(&gcs, SBO_ADDR_GCS);

    bool acked = false;
    for (unsigned attempt = 0; attempt <= SBO_N_RETRY && !acked; ++attempt) {
        printf("  спроба %u: SELECT_REQ cmd=0x0101 вікно=5000 мс\n", attempt + 1);
        const size_t len = sbo_client_select(&gcs, 0x02, SBO_COMP_ESC,
                                             CMD_EMERGENCY_MOTOR_CUT, 5000,
                                             req, sizeof(req));
        if (exchange(&air, &node, &gcs, now, req, len, &reply)) {
            acked = (reply.msg_type == SBO_MSG_SELECT_ACK);
        }
        if (!acked) {
            now += SBO_T_ACK_WAIT_MS;   /* вікно T_ack_wait сплило — повтор */
        }
    }
    if (!acked) {
        printf("  селекція не вдалася, оператор бачить відмову\n");
        return;
    }

    now += 1500;                        /* оператор тисне кнопку через 1.5 с */
    sbo_node_tick(&node, now);
    printf("  t=%u мс: залишок вікна %u мс, OPERATE_REQ з токеном 0x%08X\n",
           (unsigned)now, (unsigned)sbo_node_remaining_ms(&node, now), gcs.token);

    const size_t len = sbo_client_operate(&gcs, NULL, 0, req, sizeof(req));
    (void)exchange(&air, &node, &gcs, now, req, len, &reply);

    printf("  живлення моторів: %s, стан селектора: %s\n",
           node.act.motors_live ? "увімкнене" : "ЗНЯТО",
           sbo_state_name(node.state));
}

static void scenario_b(void)
{
    printf("\n=== Сценарій Б: вікно дійсності сплило ===\n");

    struct sbo_node node;
    struct sbo_client gcs;
    struct link air = { .drops_left = 0 };
    uint8_t req[SBO_MAX_FRAME];
    struct sbo_frame reply;
    uint32_t now = 0;

    sbo_node_init(&node, 0x02, 0x1BADB002u);
    sbo_client_init(&gcs, SBO_ADDR_GCS);

    size_t len = sbo_client_select(&gcs, 0x02, SBO_COMP_FC,
                                   CMD_FORCE_DISARM, 5000, req, sizeof(req));
    (void)exchange(&air, &node, &gcs, now, req, len, &reply);
    const uint32_t stale = gcs.token;

    now += 8000;                        /* оператор відволікся на вісім секунд */
    sbo_node_tick(&node, now);
    printf("  t=%u мс: стан борту %s, прапорці 0x%02X\n", (unsigned)now,
           sbo_state_name(node.state), sbo_node_heartbeat_flags(&node));

    gcs.token = stale;                  /* пульт іще вірить у свій токен */
    len = sbo_client_operate(&gcs, NULL, 0, req, sizeof(req));
    (void)exchange(&air, &node, &gcs, now, req, len, &reply);
    printf("  пульт бачить причину %s і вимагає повторної селекції\n",
           sbo_error_name(gcs.last_error));
}

static void scenario_c(void)
{
    printf("\n=== Сценарій В: колізія двох пультів ===\n");

    struct sbo_node node;
    struct sbo_client cmdr, payload_op;
    struct link air = { .drops_left = 0 };
    uint8_t req[SBO_MAX_FRAME];
    struct sbo_frame reply;
    uint32_t now = 0;

    sbo_node_init(&node, 0x02, 0x5EED0002u);
    sbo_client_init(&cmdr, SBO_ADDR_GCS);
    sbo_client_init(&payload_op, SBO_ADDR_RELAY);

    printf("  пульт командира (0xFE) бере замок\n");
    size_t len = sbo_client_select(&cmdr, 0x02, SBO_COMP_ESC,
                                   CMD_EMERGENCY_MOTOR_CUT, 5000, req, sizeof(req));
    (void)exchange(&air, &node, &cmdr, now, req, len, &reply);

    now += 500;
    printf("  t=%u мс: пульт оператора навантаження (0xFD) пробує той самий борт\n",
           (unsigned)now);
    len = sbo_client_select(&payload_op, 0x02, SBO_COMP_FC,
                            CMD_PAYLOAD_DROP_ACTUATE, 5000, req, sizeof(req));
    (void)exchange(&air, &node, &payload_op, now, req, len, &reply);
    printf("  на екрані другого пульта: «борт заблоковано» (%s)\n",
           sbo_error_name(payload_op.last_error));

    /* Чужий CANCEL_REQ замка не знімає. */
    len = sbo_client_cancel(&payload_op, req, sizeof(req));
    (void)exchange(&air, &node, &payload_op, now, req, len, &reply);
    printf("  замок після чужого скасування: %s\n", sbo_state_name(node.state));
}

static void scenario_d(void)
{
    printf("\n=== Сценарій Г: критична команда на широкомовну адресу ===\n");

    struct sbo_node node;
    struct sbo_client rogue;
    struct link air = { .drops_left = 0 };
    uint8_t req[SBO_MAX_FRAME];
    uint8_t rsp[SBO_MAX_FRAME];
    uint32_t now = 0;

    sbo_node_init(&node, 0x02, 0xDEADBEEFu);
    sbo_client_init(&rogue, SBO_ADDR_GCS);

    /* Скомпрометований скрипт шле OPERATE_REQ усім одразу. */
    (void)sbo_client_select(&rogue, SBO_ADDR_BROADCAST, SBO_COMP_ESC,
                            CMD_EMERGENCY_MOTOR_CUT, 5000, req, sizeof(req));
    size_t len = sbo_client_operate(&rogue, NULL, 0, req, sizeof(req));
    size_t n = link_send(&air, &node, now, req, len, rsp, sizeof(rsp));
    printf("  відповідь в ефір: %s, у журналі безпеки: %u відкидань\n",
           n ? "є" : "немає", (unsigned)node.security_drops);
    printf("  живлення моторів: %s\n", node.act.motors_live ? "увімкнене" : "ЗНЯТО");

    /* Широкомовна телеметрія — звичайний клас, її фільтр пропускає. */
    struct sbo_client gcs;
    sbo_client_init(&gcs, SBO_ADDR_GCS);
    gcs.target_comp = SBO_COMP_FC;
    gcs.cmd_code = CMD_REQUEST_TELEMETRY;
    gcs.target_id = SBO_ADDR_BROADCAST;
    len = sbo_client_operate(&gcs, NULL, 0, req, sizeof(req));
    n = link_send(&air, &node, now, req, len, rsp, sizeof(rsp));
    struct sbo_frame reply;
    if (n && sbo_decode(rsp, n, &reply) == SBO_DECODE_OK) {
        print_reply(&reply);
    }
}

static void frame_dump(void)
{
    printf("\n=== Розклад байтів SELECT_REQ (розділ 8) ===\n");

    struct sbo_client gcs;
    uint8_t req[SBO_MAX_FRAME];
    sbo_client_init(&gcs, SBO_ADDR_GCS);
    gcs.seq = 1;

    const size_t len = sbo_client_select(&gcs, 0x02, SBO_COMP_FC,
                                         CMD_EMERGENCY_MOTOR_CUT, 5000,
                                         req, sizeof(req));
    for (size_t i = 0; i < len; ++i) {
        printf("%02X ", req[i]);
    }
    printf("\n  CRC-16-CCITT тіла: 0x%04X\n",
           sbo_crc16_ccitt(req, len - SBO_CRC_LEN));
}

int main(void)
{
    frame_dump();
    scenario_a();
    scenario_b();
    scenario_c();
    scenario_d();
    return 0;
}
