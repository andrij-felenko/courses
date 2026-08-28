/* transmitter_c.c — Реалізація відправника чистою мовою C */
#include <stdint.h>
#include <string.h>
#include "smart_multispectral/mavlink.h"

#define SENSOR_SYSID  1      /* System ID нашого безпілотного апарата */
#define SENSOR_COMPID 100    /* Component ID корисного навантаження (MAV_COMP_ID_PAYLOAD) */

/* Зовнішня низькорівнева функція передачі буфера через UART DMA */
extern void uart_dma_transmit(const uint8_t *data, uint16_t length);

void send_multispectral_telemetry(uint32_t boot_time_ms, float temp_c,
                                  const uint16_t channels[4], uint8_t filter,
                                  uint32_t photo_count, uint8_t sd_pct)
{
    mavlink_message_t msg;
    uint8_t tx_buffer[MAVLINK_MAX_PACKET_LEN];

    /* Пакування структури повідомлення з урахуванням полів розширення */
    mavlink_msg_multispectral_survey_status_pack(
        SENSOR_SYSID,
        SENSOR_COMPID,
        &msg,
        boot_time_ms,
        temp_c,
        channels,
        filter,
        0x01,         /* Прапорець: калібрування сенсора валідне */
        photo_count,  /* Поле розширення: лічильник знімків */
        sd_pct        /* Поле розширення: відсоток заповнення карти пам'яті */
    );

    /* Серіалізація кадру в плоский бінарний буфер (з відтинанням кінцевих нулів) */
    uint16_t len = mavlink_msg_to_send_buffer(tx_buffer, &msg);

    /* Відправка готового кадру в апаратний UART */
    uart_dma_transmit(tx_buffer, len);
}
