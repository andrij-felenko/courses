#include "system_init.h"
#include "swd_driver.h"
#include "cdc_uart.h"
#include <stdint.h>
#include <stdbool.h>

/**
 * @file main.c
 * @brief Точка входу прошивки DAPLink, яка ініціалізує системи STM32F103,
 *        налаштовує VTOR та керує головним циклом обробки команд.
 */

/* Команди протоколу CMSIS-DAP */
#define ID_DAP_INFO             0x00U
#define ID_DAP_CONNECT          0x02U
#define ID_DAP_DISCONNECT       0x03U
#define ID_DAP_TRANSFER_CONF    0x04U
#define ID_DAP_TRANSFER         0x05U
#define ID_DAP_RESET_TARGET     0x0AU

#define DAP_OK                  0x00U
#define DAP_ERROR               0xFFU

/* Розмір пакета даних протоколу DAP (64 байти) */
#define DAP_PACKET_SIZE         64U

static uint8_t request_buf[DAP_PACKET_SIZE];
static uint8_t response_buf[DAP_PACKET_SIZE];

/**
 * @brief Обробник команд протоколу DAPLink
 */
static void process_dap_command(const uint8_t *req, uint8_t *resp) {
    uint8_t cmd_id = req[0];
    resp[0] = cmd_id;

    switch (cmd_id) {
        case ID_DAP_INFO:
            resp[1] = 0x06; /* Довжина рядка */
            resp[2] = 'D'; resp[3] = 'A'; resp[4] = 'P';
            resp[5] = 'L'; resp[6] = 'N'; resp[7] = 'K';
            break;

        case ID_DAP_CONNECT:
            swd_init();
            swd_line_reset();
            resp[1] = 0x01; /* Порт SWD активовано */
            break;

        case ID_DAP_DISCONNECT:
            swd_turnaround(true); /* Високий імпеданс для ліній */
            resp[1] = DAP_OK;
            break;

        case ID_DAP_TRANSFER: {
            uint8_t target_index = req[1];
            uint8_t transfer_count = req[2];
            uint8_t resp_count = 0;
            uint8_t ack = SWD_ACK_OK;
            uint16_t req_idx = 3;
            uint16_t resp_idx = 3;

            (void)target_index;

            for (uint8_t i = 0; i < transfer_count; i++) {
                uint8_t transfer_req = req[req_idx++];
                uint32_t val = 0;

                if (transfer_req & SWD_REQ_READ) {
                    if (transfer_req & SWD_REQ_AP) {
                        if (!swd_read_ap(transfer_req, &val)) ack = SWD_ACK_FAULT;
                    } else {
                        if (!swd_read_dp(transfer_req, &val)) ack = SWD_ACK_FAULT;
                    }
                    resp[resp_idx++] = (uint8_t)(val >> 0);
                    resp[resp_idx++] = (uint8_t)(val >> 8);
                    resp[resp_idx++] = (uint8_t)(val >> 16);
                    resp[resp_idx++] = (uint8_t)(val >> 24);
                } else {
                    val |= ((uint32_t)req[req_idx++]) << 0;
                    val |= ((uint32_t)req[req_idx++]) << 8;
                    val |= ((uint32_t)req[req_idx++]) << 16;
                    val |= ((uint32_t)req[req_idx++]) << 24;
                    if (transfer_req & SWD_REQ_AP) {
                        if (!swd_write_ap(transfer_req, val)) ack = SWD_ACK_FAULT;
                    } else {
                        if (!swd_write_dp(transfer_req, val)) ack = SWD_ACK_FAULT;
                    }
                }

                if (ack == SWD_ACK_OK) {
                    resp_count++;
                } else {
                    break;
                }
            }
            resp[1] = resp_count;
            resp[2] = ack;
            break;
        }

        case ID_DAP_RESET_TARGET:
            swd_line_reset();
            resp[1] = DAP_OK;
            break;

        default:
            resp[1] = DAP_ERROR;
            break;
    }
}

int main(void) {
    /* 1. Повна ініціалізація системи STM32F103 (VTOR, RCC, GPIO, NVIC) */
    system_init_all();

    /* 2. Ініціалізація драйвера шини SWD */
    swd_init();

    /* 3. Ініціалізація віртуального послідовного порту CDC UART */
    cdc_uart_init(115200);

    uint16_t req_pos = 0;

    /* 4. Головний цикл обробки команд та трансляції даних */
    while (1) {
        uint8_t byte;

        /* Читання команд з CDC UART та буферизація */
        if (cdc_uart_read_byte(&byte)) {
            request_buf[req_pos++] = byte;

            /* При накопиченні повного кадру пакета обробляємо команду */
            if (req_pos >= DAP_PACKET_SIZE || byte == '\n') {
                process_dap_command(request_buf, response_buf);

                /* Відправка відповіді через CDC UART */
                for (uint16_t i = 0; i < DAP_PACKET_SIZE; i++) {
                    cdc_uart_write_byte(response_buf[i]);
                }
                req_pos = 0;
            }
        }
    }

    return 0;
}
