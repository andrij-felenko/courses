/* Демонстраційний прогін AT-рушія проти симулятора модуля.

   На залізі main виглядав би так само, тільки замість modem_sim стояли б
   HAL_UART_Transmit_DMA і HAL_GetTick, а at_engine_poll викликався б із
   головного циклу або з нитки RTOS. */

#include <stdio.h>

#include "at_engine.h"
#include "modem_sim.h"

static at_engine_t  g_engine;
static modem_sim_t  g_sim;
static uint32_t     g_now_ms;

/* --- апаратні гачки ----------------------------------------------------- */

static void hal_uart_tx(const uint8_t *data, size_t len)
{
    modem_sim_on_tx(&g_sim, data, len, g_now_ms);
}

static uint32_t hal_tick_ms(void)
{
    return g_now_ms;
}

static void hal_module_stuck(void *ctx)
{
    (void)ctx;
    printf("[%4u ms] ВІДНОВЛЕННЯ: модуль не відповідає — смикаємо PWRKEY\n", (unsigned)g_now_ms);
}

/* --- колбеки команд ----------------------------------------------------- */

static void on_cmd_done(at_status_t status, const char *resp, void *ctx)
{
    printf("[%4u ms] %-24s → %-7s %s\n",
           (unsigned)g_now_ms, (const char *)ctx, at_status_str(status),
           (resp != NULL) ? resp : "");
}

/* --- обробники URC ------------------------------------------------------ */

static void on_socket_closed(const char *line, void *ctx)
{
    (void)ctx;
    printf("[%4u ms] URC розрив сокета: %s\n", (unsigned)g_now_ms, line);

    /* Реентерабельність: команду ставимо в чергу прямо звідси. Це дозволено
       саме тому, що URC розбирається в контексті головного циклу, а черга
       захищена критичною секцією. */
    const at_request_t reopen = {
        .text          = "AT+QIOPEN=1,0,\"TCP\",\"example.net\",80,0,1",
        .expect_prefix = NULL,
        .timeout_ms    = 500U,
        .retries       = 1U,
        .done          = on_cmd_done,
        .ctx           = (void *)"AT+QIOPEN (з URC)",
    };
    if (!at_engine_send_cmd(&g_engine, &reopen)) {
        printf("[%4u ms] черга переповнена, перевідкриття відкладено\n", (unsigned)g_now_ms);
    }
}

static void on_socket_opened(const char *line, void *ctx)
{
    (void)ctx;
    printf("[%4u ms] URC сокет піднято: %s\n", (unsigned)g_now_ms, line);
}

static void on_generic_urc(const char *line, void *ctx)
{
    (void)ctx;
    printf("[%4u ms] URC: %s\n", (unsigned)g_now_ms, line);
}

/* --- стартова послідовність --------------------------------------------- */

static const uint8_t k_http_payload[] = "GET / HTTP/1.0\r\n\r\n";

static void submit_boot_sequence(at_engine_t *eng)
{
    const at_request_t boot[] = {
        { .text = "ATE0", .timeout_ms = 300U, .retries = 2U,
          .done = on_cmd_done, .ctx = (void *)"ATE0" },

        { .text = "AT+CFUN=1", .timeout_ms = 1000U, .retries = 2U,
          .done = on_cmd_done, .ctx = (void *)"AT+CFUN=1" },

        { .text = "AT+CSQ", .expect_prefix = "+CSQ:", .timeout_ms = 500U,
          .done = on_cmd_done, .ctx = (void *)"AT+CSQ" },

        /* Команда з запрошенням: після '>' у дріт ідуть сирі байти. */
        { .text = "AT+QISEND=0,18", .wait_prompt = true,
          .payload = k_http_payload, .payload_len = (uint16_t)(sizeof(k_http_payload) - 1U),
          .timeout_ms = 1000U, .done = on_cmd_done, .ctx = (void *)"AT+QISEND" },

        /* Та сама команда, але в закритий сокет: модуль відповість ERROR і
           запрошення не надішле ніколи. Рушій зобов'язаний закрити команду
           одразу, а не простояти цілу секунду в очікуванні '>'. */
        { .text = "AT+QISEND=1,4", .wait_prompt = true,
          .payload = k_http_payload, .payload_len = 4U,
          .timeout_ms = 1000U, .done = on_cmd_done, .ctx = (void *)"AT+QISEND (закритий)" },

        /* Три команди, на які модуль мовчить: показують ескалацію таймауту
           й аварійне відновлення після третьої поспіль. */
        { .text = "AT+QIDEACT=0", .timeout_ms = 250U,
          .done = on_cmd_done, .ctx = (void *)"AT+QIDEACT=0" },
        { .text = "AT+QIDEACT=1", .timeout_ms = 250U,
          .done = on_cmd_done, .ctx = (void *)"AT+QIDEACT=1" },
        { .text = "AT+QIDEACT=2", .timeout_ms = 250U,
          .done = on_cmd_done, .ctx = (void *)"AT+QIDEACT=2" },
    };

    for (size_t i = 0U; i < sizeof(boot) / sizeof(boot[0]); ++i) {
        if (!at_engine_send_cmd(eng, &boot[i])) {
            printf("[init] черга не прийняла %s\n", boot[i].text);
        }
    }
}

int main(void)
{
    const at_engine_hooks_t hooks = {
        .uart_tx         = hal_uart_tx,
        .tick_ms         = hal_tick_ms,
        .on_module_stuck = hal_module_stuck,
        .ctx             = NULL,
    };

    if (!at_engine_init(&g_engine, &hooks)) {
        fprintf(stderr, "рушій не ініціалізовано\n");
        return 1;
    }

    /* Симулятор пише в той самий масив, який на залізі був би ціллю DMA. */
    modem_sim_init(&g_sim, at_engine_rx_buffer(&g_engine));

    at_engine_register_urc(&g_engine, "+QIURC: \"closed\"", on_socket_closed, NULL);
    at_engine_register_urc(&g_engine, "+QIURC:", on_generic_urc, NULL);
    at_engine_register_urc(&g_engine, "+QIOPEN:", on_socket_opened, NULL);
    at_engine_register_urc(&g_engine, "RING", on_generic_urc, NULL);
    at_engine_register_urc(&g_engine, "+CMTI:", on_generic_urc, NULL);

    submit_boot_sequence(&g_engine);

    bool late_probe_sent = false;

    for (g_now_ms = 0U; g_now_ms < 3000U; g_now_ms += 5U) {
        modem_sim_tick(&g_sim, g_now_ms);
        at_engine_poll(&g_engine, modem_sim_cndtr(&g_sim));

        /* Після аварійного відновлення рушій мусить працювати далі. */
        if (!late_probe_sent && g_now_ms >= 2000U) {
            late_probe_sent = true;
            const at_request_t probe = {
                .text = "AT+CSQ", .expect_prefix = "+CSQ:", .timeout_ms = 500U,
                .done = on_cmd_done, .ctx = (void *)"AT+CSQ (після відновлення)",
            };
            at_engine_send_cmd(&g_engine, &probe);
        }
    }

    const at_engine_stats_t *s = at_engine_stats(&g_engine);
    printf("\nПідсумок: рядків %u, з них URC %u, луни відкинуто %u,\n"
           "          сиріт %u, переповнень рядка %u,\n"
           "          повторів %u, таймаутів %u, відновлень %u\n",
           (unsigned)s->lines_in, (unsigned)s->urc_lines, (unsigned)s->echo_dropped,
           (unsigned)s->orphan_lines, (unsigned)s->overflows,
           (unsigned)s->retries, (unsigned)s->timeouts, (unsigned)s->recoveries);

    return 0;
}
