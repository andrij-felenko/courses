/* test_sbo_suite.c — Автоматизований тестовий сценарій мовою C */
#include <stdio.h>
#include <assert.h>

void test_sbo_full_cycle(void) {
    sbo_target_context_t target;
    sbo_target_init(&target, 0x02, 0x12345678);

    uint32_t now = 1000;
    sbo_packet_t rx, tx;

    /* Сценарій 1: Спроба виконання без вибору (Повинна провалитися) */
    memset(&rx, 0, sizeof(rx));
    rx.magic = SBO_MAGIC_BYTE;
    rx.target_id = 0x02;
    rx.msg_type = SBO_MSG_OPERATE_REQ;
    rx.cmd_code = 0x0101;
    rx.sbo_token = 0x9999;
    sbo_error_t err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NOT_ARMED);
    assert(target.state == SBO_STATE_IDLE);

    /* Сценарій 2: Успішна селекція */
    rx.msg_type = SBO_MSG_SELECT_REQ;
    rx.source_id = 0xFE;
    rx.timeout_ms = 5000;
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NONE);
    assert(target.state == SBO_STATE_ARMED);
    uint32_t issued_token = tx.sbo_token;
    assert(issued_token != 0);

    /* Сценарій 3: Успішне виконання у межах вікна (1.5 сек пізніше) */
    now += 1500;
    rx.msg_type = SBO_MSG_OPERATE_REQ;
    rx.sbo_token = issued_token;
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NONE);
    assert(target.state == SBO_STATE_IDLE); /* Авто-скидання */

    /* Сценарій 4: Повторний клік з тим самим токеном (Повинен провалитися!) */
    err = sbo_target_process_packet(&target, &rx, &tx, now);
    assert(err == SBO_ERR_NOT_ARMED);
}
