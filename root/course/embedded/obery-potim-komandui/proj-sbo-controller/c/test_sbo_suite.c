/* test_sbo_suite.c — перевірка інваріантів безпеки SBO.
 * Тут же живе заглушка платформи: замість реле й GPIO — лічильники. */
#include <stdio.h>
#include <string.h>

#include "gcs_focus_manager.h"
#include "sbo_target_engine.h"

static int g_checks = 0;
static int g_failed = 0;

#define CHECK(cond)                                                                 \
    do {                                                                            \
        ++g_checks;                                                                 \
        if (!(cond)) {                                                              \
            ++g_failed;                                                             \
            printf("  ПРОВАЛ %s:%d — %s\n", __FILE__, __LINE__, #cond);             \
        }                                                                           \
    } while (0)

/* --- Заглушка платформи ------------------------------------------------- */
static struct {
    int      exec_calls;
    uint16_t last_cmd;
    bool     fail_next;
    bool     armed_level;
    int      exec_pulses;
    int      drop_pulses;
} g_board;

bool sbo_actuator_execute(uint16_t cmd_code, const uint8_t *payload, uint8_t payload_len) {
    (void)payload;
    (void)payload_len;
    g_board.exec_calls++;
    g_board.last_cmd = cmd_code;
    if (g_board.fail_next) {
        g_board.fail_next = false;
        return false;               /* привід відзвітував про відмову */
    }
    return true;
}

void sbo_diag_set(sbo_diag_line_t line, bool level) {
    if (line == SBO_DIAG_ARMED) {
        g_board.armed_level = level;
    }
}

void sbo_diag_pulse(sbo_diag_line_t line, uint16_t width_us) {
    (void)width_us;
    if (line == SBO_DIAG_OP_EXEC) {
        g_board.exec_pulses++;
    } else if (line == SBO_DIAG_SECURITY_DROP) {
        g_board.drop_pulses++;
    }
}

/* --- Допоміжне ---------------------------------------------------------- */
#define TARGET_ID 0x02u
#define GCS_ID    0xFEu
#define CMD_ARM   0x0101u

static void make_request(sbo_packet_t *pkt, uint8_t msg_type, uint8_t source, uint8_t target,
                         uint16_t cmd, uint32_t token, uint16_t window) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->magic      = SBO_MAGIC_BYTE;
    pkt->msg_type   = msg_type;
    pkt->source_id  = source;
    pkt->target_id  = target;
    pkt->cmd_code   = cmd;
    pkt->sbo_token  = token;
    pkt->timeout_ms = window;
}

static void reset_board(void) {
    memset(&g_board, 0, sizeof(g_board));
}

/* --- Тести -------------------------------------------------------------- */

/* 1. Пряма команда без фази вибору не проходить. */
static void test_operate_without_select(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x12345678u);

    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0x9999u, 0u);
    sbo_error_t err = sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);

    CHECK(err == SBO_ERR_NOT_ARMED);
    CHECK(resp);
    CHECK(tx.msg_type == SBO_MSG_OPERATE_NACK);
    CHECK(tx.payload[0] == (uint8_t)SBO_ERR_NOT_ARMED);
    CHECK(node.state == SBO_STATE_IDLE);
    CHECK(g_board.exec_calls == 0);
}

/* 2. Номінальний цикл: вибір, зведення, виконання у вікні. */
static void test_nominal_cycle(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x12345678u);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u) == SBO_ERR_NONE);
    CHECK(tx.msg_type == SBO_MSG_SELECT_ACK);
    CHECK(node.state == SBO_STATE_ARMED);
    CHECK(g_board.armed_level);
    const uint32_t token = tx.sbo_token;
    CHECK(token != 0u);

    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, TARGET_ID, CMD_ARM, token, 0u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 2500u) == SBO_ERR_NONE);
    CHECK(tx.msg_type == SBO_MSG_OPERATE_ACK);
    CHECK(node.state == SBO_STATE_IDLE);          /* селектор одноразовий */
    CHECK(g_board.exec_calls == 1);
    CHECK(g_board.last_cmd == CMD_ARM);
    CHECK(g_board.exec_pulses == 1);              /* імпульс TP_SBO_OP_EXEC */
    CHECK(!g_board.armed_level);
}

/* 3. Дія після спливання вікна блокується саме як тайм-аут. */
static void test_timeout_expired(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0xA1B2C3D4u);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    (void)sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);
    const uint32_t token = tx.sbo_token;

    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, TARGET_ID, CMD_ARM, token, 0u);
    sbo_error_t err = sbo_target_process_packet(&node, &rx, &tx, &resp, 7000u);

    CHECK(err == SBO_ERR_TIMEOUT_EXPIRED);
    CHECK(tx.payload[0] == (uint8_t)SBO_ERR_TIMEOUT_EXPIRED);
    CHECK(node.state == SBO_STATE_IDLE);
    CHECK(node.timeout_count == 1u);
    CHECK(g_board.exec_calls == 0);
    CHECK(!g_board.armed_level);
}

/* 4. Повтор кадру з уже використаним токеном. */
static void test_token_replay(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x0BADF00Du);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    (void)sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);
    const uint32_t token = tx.sbo_token;

    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, TARGET_ID, CMD_ARM, token, 0u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1500u) == SBO_ERR_NONE);

    /* Той самий кадр іще раз — луна ефіру або зловмисник. */
    sbo_error_t err = sbo_target_process_packet(&node, &rx, &tx, &resp, 1600u);
    CHECK(err == SBO_ERR_NOT_ARMED);
    CHECK(g_board.exec_calls == 1);               /* привід смикнули рівно раз */
}

/* 5. Широкомовний кадр критичної дії відкидається без відповіді. */
static void test_broadcast_rejected(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = true;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x11112222u);

    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, SBO_BROADCAST_ID, CMD_ARM, 0x1234u, 0u);
    sbo_error_t err = sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);

    CHECK(err == SBO_ERR_BROADCAST_FORBIDDEN);
    CHECK(!resp);                                  /* в ефір не відповідаємо */
    CHECK(g_board.drop_pulses == 1);               /* імпульс TP_SBO_SECURITY_DROP */
    CHECK(g_board.exec_calls == 0);

    /* Кадр сусіда проходить повз мовчки й нічого не ламає. */
    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, 0x07u, CMD_ARM, 0u, 5000u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1010u) == SBO_ERR_FOREIGN_TARGET);
    CHECK(!resp);
    CHECK(node.state == SBO_STATE_IDLE);
}

/* 6. Другий оператор не перехоплює зведений замок і не підставляє чужий токен. */
static void test_second_operator(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x5A5A5A5Au);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    (void)sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);
    const uint32_t token = tx.sbo_token;

    make_request(&rx, SBO_MSG_SELECT_REQ, 0xFDu, TARGET_ID, CMD_ARM, 0u, 5000u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1100u) == SBO_ERR_BUSY);
    CHECK(tx.msg_type == SBO_MSG_SELECT_NACK);
    CHECK(node.state == SBO_STATE_ARMED);          /* чужий запит не зірвав нашу селекцію */

    /* Токен підслухано й надіслано з іншої адреси. */
    make_request(&rx, SBO_MSG_OPERATE_REQ, 0xFDu, TARGET_ID, CMD_ARM, token, 0u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1200u) == SBO_ERR_SOURCE_MISMATCH);
    CHECK(node.state == SBO_STATE_IDLE);
    CHECK(g_board.exec_calls == 0);
    CHECK(g_board.drop_pulses == 1);
}

/* 7. Кадр на дроті: обіг туди-назад і зіпсований байт. */
static void test_frame_codec(void) {
    sbo_target_context_t node;
    sbo_packet_t rx;
    uint8_t wire[SBO_MAX_FRAME_LEN];
    uint8_t answer[SBO_MAX_FRAME_LEN];
    size_t wire_len = 0u;
    size_t ans_len = 0u;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x33445566u);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    rx.payload_len = 3u;
    rx.payload[0] = 0xDE;
    rx.payload[1] = 0xAD;
    rx.payload[2] = 0x01;
    CHECK(sbo_frame_encode(&rx, wire, sizeof(wire), &wire_len) == SBO_ERR_NONE);
    CHECK(wire_len == SBO_HEADER_LEN + 3u + SBO_CRC_LEN);

    sbo_packet_t back;
    CHECK(sbo_frame_decode(wire, wire_len, &back) == SBO_ERR_NONE);
    CHECK(back.msg_type == SBO_MSG_SELECT_REQ);
    CHECK(back.cmd_code == CMD_ARM);
    CHECK(back.payload_len == 3u);
    CHECK(back.payload[1] == 0xAD);

    /* Той самий кадр крізь повний тракт борту. */
    CHECK(sbo_target_handle_frame(&node, wire, wire_len, answer, sizeof(answer), &ans_len,
                                  1000u) == SBO_ERR_NONE);
    CHECK(ans_len >= SBO_MIN_FRAME_LEN);
    sbo_packet_t ack;
    CHECK(sbo_frame_decode(answer, ans_len, &ack) == SBO_ERR_NONE);
    CHECK(ack.msg_type == SBO_MSG_SELECT_ACK);
    CHECK(ack.sbo_token != 0u);

    /* Перешкода в ефірі перевернула біт у полі команди. */
    wire[12] ^= 0x08u;
    CHECK(sbo_frame_decode(wire, wire_len, &back) == SBO_ERR_BAD_CRC);
    wire[12] ^= 0x08u;
    wire[0] = 0x00u;
    CHECK(sbo_frame_decode(wire, wire_len, &back) == SBO_ERR_BAD_MAGIC);
    CHECK(sbo_frame_decode(wire, SBO_MIN_FRAME_LEN - 1u, &back) == SBO_ERR_BAD_LENGTH);
}

/* 8. Пульт: мовчання борту гасить кнопку, квитанція її вмикає. */
static void test_gcs_link_loss(void) {
    gcs_focus_t focus;
    sbo_target_context_t node;
    sbo_packet_t req, tx;
    bool resp = false;
    reset_board();
    gcs_focus_init(&focus, GCS_ID);
    sbo_target_init(&node, TARGET_ID, 0x77665544u);

    CHECK(!gcs_focus_select(&focus, SBO_BROADCAST_ID, 0u, "ALL", CMD_ARM, 5000u, 0u, &req));

    CHECK(gcs_focus_select(&focus, TARGET_ID, 1u, "UAV-02", CMD_ARM, 5000u, 0u, &req));
    CHECK(focus.status == GCS_FOCUS_WAIT_ACK);
    CHECK(!gcs_focus_button_enabled(&focus, 10u));

    /* Квитанція не долетіла за 400 мс. */
    gcs_focus_tick(&focus, 401u);
    CHECK(focus.status == GCS_FOCUS_LINK_LOST);
    CHECK(strcmp(gcs_focus_badge(&focus), "Втрата зв'язку") == 0);
    CHECK(gcs_focus_frame_color(&focus) == 0xD0342Cu);
    CHECK(!gcs_focus_button_enabled(&focus, 401u));
    CHECK(!gcs_focus_build_operate(&focus, NULL, 0u, 401u, &tx));

    /* Друга спроба — цього разу борт відповів. */
    CHECK(gcs_focus_select(&focus, TARGET_ID, 1u, "UAV-02", CMD_ARM, 5000u, 500u, &req));
    CHECK(sbo_target_process_packet(&node, &req, &tx, &resp, 520u) == SBO_ERR_NONE);
    gcs_focus_on_response(&focus, &tx, 540u);
    CHECK(focus.status == GCS_FOCUS_ARMED);
    CHECK(gcs_focus_button_enabled(&focus, 600u));

    sbo_packet_t op;
    CHECK(gcs_focus_build_operate(&focus, NULL, 0u, 600u, &op));
    CHECK(op.sbo_token != 0u);
    CHECK(!gcs_focus_build_operate(&focus, NULL, 0u, 601u, &op));   /* другий клік — ні */

    CHECK(sbo_target_process_packet(&node, &op, &tx, &resp, 620u) == SBO_ERR_NONE);
    gcs_focus_on_response(&focus, &tx, 640u);
    CHECK(focus.status == GCS_FOCUS_DONE);
    CHECK(g_board.exec_calls == 1);

    /* Вікно селекції теж мусить гаснути само. */
    CHECK(gcs_focus_select(&focus, TARGET_ID, 1u, "UAV-02", CMD_ARM, 1000u, 1000u, &req));
    CHECK(sbo_target_process_packet(&node, &req, &tx, &resp, 1010u) == SBO_ERR_NONE);
    gcs_focus_on_response(&focus, &tx, 1020u);
    CHECK(focus.status == GCS_FOCUS_ARMED);
    gcs_focus_tick(&focus, 1900u);
    CHECK(focus.status == GCS_FOCUS_EXPIRED);
    CHECK(!gcs_focus_button_enabled(&focus, 1900u));
}

/* 9. Відмова приводу доїжджає до оператора як NACK. */
static void test_actuator_failure(void) {
    sbo_target_context_t node;
    sbo_packet_t rx, tx;
    bool resp = false;
    reset_board();
    sbo_target_init(&node, TARGET_ID, 0x24681357u);

    make_request(&rx, SBO_MSG_SELECT_REQ, GCS_ID, TARGET_ID, CMD_ARM, 0u, 5000u);
    (void)sbo_target_process_packet(&node, &rx, &tx, &resp, 1000u);
    const uint32_t token = tx.sbo_token;

    g_board.fail_next = true;
    make_request(&rx, SBO_MSG_OPERATE_REQ, GCS_ID, TARGET_ID, CMD_ARM, token, 0u);
    CHECK(sbo_target_process_packet(&node, &rx, &tx, &resp, 1200u) == SBO_ERR_INTERNAL_FAULT);
    CHECK(tx.msg_type == SBO_MSG_OPERATE_NACK);
    CHECK(node.state == SBO_STATE_IDLE);
    CHECK(g_board.exec_pulses == 0);
}

int main(void) {
    test_operate_without_select();
    test_nominal_cycle();
    test_timeout_expired();
    test_token_replay();
    test_broadcast_rejected();
    test_second_operator();
    test_frame_codec();
    test_gcs_link_loss();
    test_actuator_failure();

    printf("перевірок: %d, провалів: %d\n", g_checks, g_failed);
    return (g_failed == 0) ? 0 : 1;
}
