#include "modem_sim.h"

#include <stdlib.h>
#include <string.h>

static void sim_schedule(modem_sim_t *sim, const char *text,
                         uint32_t due_ms, uint16_t chunk, uint32_t gap_ms)
{
    if (sim->out_count >= SIM_OUT_CAP) {
        sim->dropped++;   /* у справжнього модуля теж є межа внутрішнього буфера */
        return;
    }
    const size_t len = strlen(text);
    if (len >= SIM_TEXT_CAP) {
        sim->dropped++;
        return;
    }

    sim_out_t *slot = &sim->out[sim->out_head];
    memcpy(slot->text, text, len + 1U);
    slot->len    = (uint16_t)len;
    slot->sent   = 0U;
    slot->chunk  = chunk;
    slot->gap_ms = gap_ms;
    slot->due_ms = due_ms;

    sim->out_head  = (uint8_t)((sim->out_head + 1U) % SIM_OUT_CAP);
    sim->out_count = (uint8_t)(sim->out_count + 1U);
}

static void sim_emit(modem_sim_t *sim, const char *bytes, uint16_t len)
{
    for (uint16_t i = 0U; i < len; ++i) {
        sim->dma_dst[sim->head] = (uint8_t)bytes[i];
        sim->head = (uint16_t)((sim->head + 1U) & AT_RX_MASK);
    }
}

void modem_sim_init(modem_sim_t *sim, uint8_t *dma_dst)
{
    memset(sim, 0, sizeof(*sim));
    sim->dma_dst = dma_dst;
    sim->echo    = true;   /* після подачі живлення модуль у режимі ATE1 */
}

/* --- реакція на команду ------------------------------------------------- */

static void sim_on_command(modem_sim_t *sim, uint32_t now)
{
    const char *cmd = sim->rx_line;

    if (cmd[0] == '\0') {
        return;
    }

    if (sim->echo) {
        char echo_line[SIM_TEXT_CAP];
        const size_t len = strlen(cmd);
        if (len + 3U < sizeof(echo_line)) {
            memcpy(echo_line, cmd, len);
            echo_line[len]      = '\r';
            echo_line[len + 1U] = '\n';
            echo_line[len + 2U] = '\0';
            sim_schedule(sim, echo_line, now, 0U, 0U);
        }
    }

    if (strcmp(cmd, "ATE0") == 0) {
        sim->echo = false;
        sim_schedule(sim, "\r\nOK\r\n", now + 10U, 0U, 0U);
        return;
    }

    if (strcmp(cmd, "AT+CFUN=1") == 0) {
        sim->cfun_attempts++;
        if (sim->cfun_attempts == 1U) {
            /* Перша спроба впирається в зайняту SIM — тимчасова помилка. */
            sim_schedule(sim, "\r\n+CME ERROR: 14\r\n", now + 30U, 0U, 0U);
        } else {
            /* Друга йде довго: підняти радіомодуль справді коштує часу. */
            sim_schedule(sim, "\r\nOK\r\n", now + 250U, 0U, 0U);
        }
        return;
    }

    if (strcmp(cmd, "AT+CSQ") == 0) {
        /* Відповідь навмисно рветься посеред рядка: перші 7 байтів, пауза
           25 мс, решта. Парсер зобов'язаний дочекатися '\n'. */
        sim_schedule(sim, "\r\n+CSQ: 24,99\r\n\r\nOK\r\n", now + 25U, 7U, 25U);
        return;
    }

    if (strncmp(cmd, "AT+QISEND=", 10) == 0) {
        const unsigned long socket_id = strtoul(cmd + 10, NULL, 10);
        const char *comma = strchr(cmd + 10, ',');
        sim->payload_expect = (comma != NULL) ? (uint16_t)strtoul(comma + 1, NULL, 10) : 0U;
        sim->payload_got    = 0U;

        if (socket_id != 0UL) {
            /* Сокет не відкритий. Модуль відмовляє одразу й запрошення не
               надсилає ВЗАГАЛІ — це та пастка, на якій зависає драйвер,
               що в стані очікування '>' дивиться самі лише сирі байти. */
            sim_schedule(sim, "\r\nERROR\r\n", now + 15U, 0U, 0U);
            return;
        }
        if (sim->payload_expect > 0U) {
            sim->await_payload = true;
            sim_schedule(sim, "\r\n> ", now + 15U, 0U, 0U);
        } else {
            sim_schedule(sim, "\r\nERROR\r\n", now + 15U, 0U, 0U);
        }
        return;
    }

    if (strncmp(cmd, "AT+QIOPEN", 9) == 0) {
        sim_schedule(sim, "\r\nOK\r\n", now + 20U, 0U, 0U);
        /* Результат відкриття сокета приходить окремим URC — сильно пізніше
           за "OK", і саме тому його не можна чекати в контексті команди. */
        sim_schedule(sim, "\r\n+QIOPEN: 0,0\r\n", now + 120U, 0U, 0U);
        return;
    }

    if (strncmp(cmd, "AT+QIDEACT", 10) == 0) {
        /* Мовчанка. Так поводиться модуль, у якого завис внутрішній стек. */
        return;
    }

    sim_schedule(sim, "\r\nOK\r\n", now + 20U, 0U, 0U);
}

void modem_sim_on_tx(modem_sim_t *sim, const uint8_t *data, size_t len, uint32_t now)
{
    for (size_t i = 0U; i < len; ++i) {
        const uint8_t b = data[i];

        if (sim->await_payload) {
            /* Сирі байти можуть містити і '\r', і '\n' — рахуємо їх за
               довжиною, оголошеною в команді, а не за термінатором. */
            sim->payload_got++;
            if (sim->payload_got >= sim->payload_expect) {
                sim->await_payload = false;
                sim_schedule(sim, "\r\nSEND OK\r\n", now + 40U, 0U, 0U);
            }
            continue;
        }

        if (b == (uint8_t)'\n') {
            sim->rx_line[sim->rx_len] = '\0';
            sim_on_command(sim, now);
            sim->rx_len = 0U;
            continue;
        }
        if (b == (uint8_t)'\r') {
            continue;
        }
        if (sim->rx_len < (AT_MAX_LINE_SIZE - 1U)) {
            sim->rx_line[sim->rx_len++] = (char)b;
        }
    }
}

void modem_sim_tick(modem_sim_t *sim, uint32_t now)
{
    /* Спонтанні події, яких ніхто не замовляв. */
    if (!sim->urc_closed_done && now >= 900U) {
        sim->urc_closed_done = true;
        /* Розрив сокета приходить двома кадрами: "+QIURC: \"clo" і решта
           через 20 мс. Наївний парсер тут розірве повідомлення навпіл. */
        sim_schedule(sim, "\r\n+QIURC: \"closed\",0\r\n", now, 12U, 20U);
    }
    if (!sim->urc_ring_done && now >= 1500U) {
        sim->urc_ring_done = true;
        sim_schedule(sim, "\r\nRING\r\n", now, 0U, 0U);
    }

    /* Видача запланованого. Порядок суворо FIFO: дріт один. */
    while (sim->out_count > 0U) {
        sim_out_t *front = &sim->out[sim->out_tail];
        if ((int32_t)(now - front->due_ms) < 0) {
            break;
        }

        uint16_t remain = (uint16_t)(front->len - front->sent);
        uint16_t take   = (front->chunk > 0U && front->chunk < remain) ? front->chunk : remain;

        sim_emit(sim, front->text + front->sent, take);
        front->sent = (uint16_t)(front->sent + take);

        if (front->sent >= front->len) {
            sim->out_tail  = (uint8_t)((sim->out_tail + 1U) % SIM_OUT_CAP);
            sim->out_count = (uint8_t)(sim->out_count - 1U);
            continue;
        }

        front->due_ms = now + front->gap_ms;
        break;
    }
}
