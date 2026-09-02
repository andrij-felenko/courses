/* Порядок дій, коли чіп мовчить: спершу дивимося на лінії у стані спокою,
   потім витягуємо шину із зависання і лише тоді щось скануємо. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "i2c_bitbang.h"
#include "i2c_lines.h"
#include "i2c_scan.h"
#include "sim_lines.h"

/* Адреса акселерометра за даташитом (AD0 = 0) */
#define EXPECTED_ADDR 0x68u

static sim_fault_t pick_scenario(int argc, char **argv) {
    const char *name = (argc > 1) ? argv[1] : "ok";

    if (strcmp(name, "ok") == 0)       return SIM_FAULT_NONE;
    if (strcmp(name, "stuck") == 0)    return SIM_FAULT_SDA_STUCK_LOW;
    if (strcmp(name, "nopullup") == 0) return SIM_FAULT_NO_PULLUPS;
    if (strcmp(name, "nopower") == 0)  return SIM_FAULT_NO_POWER;

    fprintf(stderr, "Невідомий сценарій '%s'. Є: ok, stuck, nopullup, nopower\n", name);
    exit(2);
}

int main(int argc, char **argv) {
    sim_fault_t fault = pick_scenario(argc, argv);
    i2c_idle_state_t idle;
    i2c_scan_report_t report;
    i2c_verdict_t verdict;

    sim_bus_init((uint8_t)EXPECTED_ADDR, fault);
    i2c_lines_take();

    idle = i2c_read_idle_state();
    printf("Стан спокою: SCL=%d, SDA=%d\n", idle.scl_high ? 1 : 0, idle.sda_high ? 1 : 0);

    if (!idle.scl_high && !idle.sda_high) {
        printf("Обидві лінії в нулі — підтяжок немає або живлення відсутнє.\n"
               "Скануємо все одно, щоб побачити, як це виглядає з боку ведучого.\n");
    } else if (!idle.sda_high) {
        printf("SDA затиснута веденим. Виштовхуємо його байт дев'ятьма тактами SCL...\n");
        if (i2c_recover_bus()) {
            printf("Лінію звільнено, шина знову придатна до транзакцій.\n");
        } else {
            printf("Дев'ять тактів не допомогли — шукай замикання SDA на землю.\n");
        }
    } else if (!idle.scl_high) {
        printf("SCL у нулі при вільній SDA — обрив підтяжки SCL або ведений тримає такт.\n");
    }

    report = i2c_scan_range();
    verdict = i2c_classify(&report, (uint8_t)EXPECTED_ADDR);
    i2c_print_report(&report, (uint8_t)EXPECTED_ADDR, verdict);

    i2c_lines_release_to_peripheral();
    return (verdict == VERDICT_DEVICE_AS_EXPECTED) ? 0 : 1;
}
