/* Bring-up Test Runner: чотири фази підряд, жодної RTOS і жодного стека
   протоколів. Кожна фаза відпрацьовує незалежно від попередньої — навіть
   мертвий кварц не має ховати від нас справний GPIO чи справну шину. */
#include "bringup.h"
#include "stm32f4_regs.h"

/* Звіт лежить у ОЗП під зовнішнім символом: у GDB це `p g_bringup_report`.
   Прошивка нічого не друкує — на першому ввімкненні друкувати ще нікуди. */
bringup_report_t g_bringup_report;

/* ~2 с меандру 100 кГц: вистачає, щоб спокійно обійти щупом усі майданчики. */
#define TP_ITERATIONS       100000U
#define TP_HEARTBEAT_CYCLES 1000U
#define TP_HEARTBEAT_PAUSE  200000U

int main(void)
{
    bringup_report_t *report = &g_bringup_report;
    bool bus_was_stuck = false;

    /* Фаза 1: тактові домени. */
    (void)bringup_clock_check(report);

    /* Фаза 2: контрольні майданчики. Виконуємо навіть після провалу HSE —
       на HSI ядро живе, а цілісність доріжок GPIO від кварцу не залежить. */
    bringup_gpio_toggle_testpoints(TP_ITERATIONS);

    /* Фаза 3: спершу звільняємо шину руками, потім піднімаємо модуль. */
    if (bringup_i2c_bus_clear(&bus_was_stuck) == BRINGUP_OK) {
        report->i2c_bus_was_stuck = bus_was_stuck;
        bringup_i2c_init();
        (void)bringup_scan_i2c_bus(report);
    } else {
        report->i2c_bus_was_stuck = true;
        report->i2c_status = BRINGUP_ERR_I2C_BUS_STUCK;
    }

    /* Фаза 4: опорне джерело й реальна напруга аналогового живлення. */
    (void)bringup_measure_vdda(report);

    /* Дійшли до кінця — показуємо це коротким пакетом імпульсів раз на
       200 мс. З осцилографа видно, що прошивка не зависла посеред фази. */
    for (;;) {
        bringup_gpio_toggle_testpoints(TP_HEARTBEAT_CYCLES);
        bringup_delay_us(TP_HEARTBEAT_PAUSE);
    }
}
