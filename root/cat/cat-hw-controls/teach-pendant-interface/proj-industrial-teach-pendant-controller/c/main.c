#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "include/pendant_driver.h"

/**
 * @brief Допоміжна функція виводу дампа бінарного кадру телеметрії.
 */
static void print_frame_hex(const uint8_t *buffer, size_t len) {
    printf("   [HEX Кадр]: ");
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", buffer[i]);
    }
    printf("\n");
}

int main(void) {
    printf("===================================================\n");
    printf(" Контролер пульта налагодження роботів (Teach Pendant) \n");
    printf("===================================================\n\n");

    pendant_safety_state_t safety;
    pendant_joystick_t joystick;

    pendant_init(&safety, &joystick);

    uint8_t tx_buffer[64];
    uint32_t system_time_ms = 0;

    // -------------------------------------------------------------
    // Сценарій 1: Початковий стан — E-Stop OK, клавіш відпущено (Off)
    // -------------------------------------------------------------
    printf("1. Тест: E-Stop OK, Клавіш дозволу відпущено (Off):\n");
    pendant_update_safety(&safety, 1, 1, 0, 0, system_time_ms);
    pendant_update_joystick(&joystick, 3000, 2048, 2048); // Джойстик відхилено по X

    size_t frame_len = pendant_serialize_frame(&safety, &joystick, tx_buffer, sizeof(tx_buffer));
    printf("   Дозвіл руху (Safety OK): %s | Статус E-Stop: OK | Стан Enabling: Released\n",
           safety.safety_ok ? "TAK" : "НІ (ЗАБЛОКОВАНО)");
    printf("   Сила Jog (X, Y, Z): (%d, %d, %d)\n",
           ((pendant_frame_t*)tx_buffer)->jog_x,
           ((pendant_frame_t*)tx_buffer)->jog_y,
           ((pendant_frame_t*)tx_buffer)->jog_z);
    print_frame_hex(tx_buffer, frame_len);

    // -------------------------------------------------------------
    // Сценарій 2: Робочий режим — Клавіш у середньому положенні (Center Enabled)
    // -------------------------------------------------------------
    printf("\n2. Тест: Натискання клавіша дозволу в середнє положення (Center Enabled):\n");
    system_time_ms += 10;
    pendant_update_safety(&safety, 1, 1, 1, 1, system_time_ms);
    pendant_update_joystick(&joystick, 3500, 1000, 2048); // Відхилення X=3500, Y=1000

    frame_len = pendant_serialize_frame(&safety, &joystick, tx_buffer, sizeof(tx_buffer));
    printf("   Дозвіл руху (Safety OK): %s | Стан Enabling: Center Enabled\n",
           safety.safety_ok ? "ТАК (ДОЗВОЛЕНО)" : "НІ");
    printf("   Нормалізований Jog (X, Y, Z): (%d, %d, %d)\n",
           joystick.norm_x, joystick.norm_y, joystick.norm_z);
    print_frame_hex(tx_buffer, frame_len);

    // -------------------------------------------------------------
    // Сценарій 3: Панічне стискання клавіша (Panic Compressed)
    // -------------------------------------------------------------
    printf("\n3. Тест: Панічне стискання клавіша оператором (Panic Position 3):\n");
    system_time_ms += 10;
    pendant_update_safety(&safety, 1, 1, 2, 2, system_time_ms);

    frame_len = pendant_serialize_frame(&safety, &joystick, tx_buffer, sizeof(tx_buffer));
    printf("   Дозвіл руху (Safety OK): %s | Стан Enabling: Panic Compressed\n",
           safety.safety_ok ? "ТАК" : "НІ (АВАРІЙНИЙ ЗУПИН)");
    printf("   Вихідна дельта руху в кадрі: (%d, %d, %d)\n",
           ((pendant_frame_t*)tx_buffer)->jog_x,
           ((pendant_frame_t*)tx_buffer)->jog_y,
           ((pendant_frame_t*)tx_buffer)->jog_z);
    print_frame_hex(tx_buffer, frame_len);

    // -------------------------------------------------------------
    // Сценарій 4: Виявлення неузгодженості каналів E-Stop (Discrepancy Fault)
    // -------------------------------------------------------------
    printf("\n4. Тест: Перевірка таймера неузгодженості каналів E-Stop (Ch1=1, Ch2=0):\n");
    system_time_ms += 10;
    pendant_update_safety(&safety, 1, 0, 1, 1, system_time_ms); // Розсинхронізація 10 мс
    printf("   [Час %lu мс] Стан неузгодженості: %s | Safety OK: %s\n",
           (unsigned long)system_time_ms, safety.discrepancy_active ? "АКТИВНИЙ ВІДЛІК" : "НІ",
           safety.safety_ok ? "ТАК" : "НІ");

    system_time_ms += 60; // Пройшов час > 50 мс
    pendant_update_safety(&safety, 1, 0, 1, 1, system_time_ms);
    printf("   [Час %lu мс] Статус E-Stop: %s | Safety OK: %s\n",
           (unsigned long)system_time_ms,
           (safety.estop_status == ESTOP_FAULT_DISCREPANCY) ? "ПОМИЛКА КАНАЛІВ (DISCREPANCY FAULT)" : "OK",
           safety.safety_ok ? "ТАК" : "НІ (БЛОКУВАННЯ)");

    frame_len = pendant_serialize_frame(&safety, &joystick, tx_buffer, sizeof(tx_buffer));
    print_frame_hex(tx_buffer, frame_len);

    printf("\nТестування модуля прошивки Teach Pendant завершено успішно.\n");
    return 0;
}
