/* i3c_controller.c - Реалізація логіки DAA та диспетчера IBI */
#include "i3c_controller.h"
#include <string.h>

void i3c_bus_init(i3c_bus_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(i3c_bus_context_t));
    ctx->next_free_addr = 0x08; /* Перші 8 адрес зарезервовані */
}

/* Імітація апаратних функцій нижнього рівня */
extern void hw_i3c_start_open_drain(void);
extern void hw_i3c_stop_open_drain(void);
extern bool hw_i3c_write_byte_od(uint8_t byte);
extern bool hw_i3c_read_pid_bcr_dcr(uint64_t *pid, uint8_t *bcr, uint8_t *dcr);
extern bool hw_i3c_assign_addr_od(uint8_t addr);

i3c_status_t i3c_perform_daa(i3c_bus_context_t *ctx) {
    if (!ctx) return I3C_STATUS_BUS_LOST;

    ctx->target_count = 0;
    ctx->next_free_addr = 0x08;

    /* 1. START та широкомовна адреса 0x7E (W) */
    hw_i3c_start_open_drain();
    if (!hw_i3c_write_byte_od(I3C_BROADCAST_ADDR << 1)) {
        hw_i3c_stop_open_drain();
        return I3C_STATUS_NACK;
    }

    /* 2. Командний код CCC 0x07 (ENTDAA) */
    if (!hw_i3c_write_byte_od(I3C_CCC_ENTDAA)) {
        hw_i3c_stop_open_drain();
        return I3C_STATUS_NACK;
    }

    /* 3. Цикл арбітражу та роздачі адрес */
    while (ctx->target_count < I3C_MAX_DEVICES) {
        uint64_t pid = 0;
        uint8_t bcr = 0, dcr = 0;

        /* Повторний старт перед кожним раундом арбітражу */
        hw_i3c_start_open_drain();
        if (!hw_i3c_write_byte_od((I3C_BROADCAST_ADDR << 1) | 0x01)) {
            break; /* Жоден ведений не відгукнувся - DAA завершено */
        }

        /* Зчитування 48 бітів PID + BCR + DCR переможця арбітражу */
        if (!hw_i3c_read_pid_bcr_dcr(&pid, &bcr, &dcr)) {
            break;
        }

        /* Призначення унікальної 7-бітної динамічної адреси */
        uint8_t assigned_addr = ctx->next_free_addr++;
        if (!hw_i3c_assign_addr_od(assigned_addr << 1)) {
            hw_i3c_stop_open_drain();
            return I3C_STATUS_NACK;
        }

        /* Збереження дескриптора пристрою в таблиці контролера */
        i3c_target_desc_t *dev = &ctx->targets[ctx->target_count++];
        dev->provisional_id = pid;
        dev->bcr = bcr;
        dev->dcr = dcr;
        dev->dynamic_addr = assigned_addr;
        dev->ibi_enabled = (bcr & 0x02) != 0;
    }

    hw_i3c_stop_open_drain();
    return (ctx->target_count > 0) ? I3C_STATUS_OK : I3C_STATUS_NO_DEVICES;
}

i3c_status_t i3c_handle_ibi(i3c_bus_context_t *ctx, uint8_t *winning_addr,
                            uint8_t *mdb) 
{
    if (!ctx || !winning_addr || !mdb) return I3C_STATUS_BUS_LOST;

    /* Контролер фіксує перехід SDA в '0' при SCL=1 під час спокою */
    uint8_t addr_byte = 0;
    extern bool hw_i3c_clock_ibi_arbitration(uint8_t *addr_out);
    if (!hw_i3c_clock_ibi_arbitration(&addr_byte)) {
        return I3C_STATUS_BUS_LOST;
    }

    uint8_t target_addr = addr_byte >> 1;
    *winning_addr = target_addr;

    /* Знаходимо пристрій у реєстрі для перевірки підтримки корисного навантаження */
    bool has_payload = false;
    for (size_t i = 0; i < ctx->target_count; ++i) {
        if (ctx->targets[i].dynamic_addr == target_addr) {
            has_payload = (ctx->targets[i].bcr & 0x04) != 0;
            break;
        }
    }

    /* Відправляємо ACK на лінії відкритого стоку */
    extern void hw_i3c_send_ack(void);
    hw_i3c_send_ack();

    /* Зчитуємо обов'язковий байт даних переривання (MDB) */
    if (has_payload) {
        extern uint8_t hw_i3c_read_byte_with_t_bit(bool *is_last);
        bool is_last = false;
        *mdb = hw_i3c_read_byte_with_t_bit(&is_last);
    } else {
        *mdb = 0x00;
    }

    hw_i3c_stop_open_drain();
    return I3C_STATUS_OK;
}
