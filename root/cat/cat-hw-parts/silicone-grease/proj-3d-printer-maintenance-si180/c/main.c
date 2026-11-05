#include "t8_maintenance.h"
#include <stdio.h>

int main(void) {
    printf("Запуск системи моніторингу змащення кінематики осі Z (SI-180)...\n");

    /* Ініціалізуємо трекер для ходового гвинта T8 з POM-гайкою */
    t8_tracker_t z_axis;
    t8_tracker_init(&z_axis, NUT_MATERIAL_POM, 12.0); /* Початковий шар 12 мкм */

    printf("Початковий стан зафіксовано.\n");
    t8_tracker_print_report(&z_axis);

    /* Моделювання серії тривалих 3D-друків (імітація 15 великих деталей) */
    printf("\nМоделювання циклу експлуатації 3D-принтера...\n");
    
    for (int job = 1; job <= 15; job++) {
        /* Кожна деталь: висота 180 мм, шар 0.2 мм (900 шарів), на кожному шарі 2 Z-hop по 0.4 мм */
        for (int layer = 0; layer < 900; layer++) {
            /* Крок вгору на наступний шар */
            t8_tracker_log_movement(&z_axis, 0.2, 5.0, false, 1.2);
            /* Два Z-hop рухи */
            t8_tracker_log_movement(&z_axis, 0.4, 15.0, true, 1.2);
            t8_tracker_log_movement(&z_axis, 0.4, 15.0, true, 1.2);
        }

        /* Повернення осі в нуль на високій швидкості (холостий хід додому) */
        t8_tracker_log_movement(&z_axis, 180.0, 20.0, false, 1.2);

        if (job % 5 == 0) {
            printf("\n--- Завершено %d завдань друку ---", job);
            t8_tracker_print_report(&z_axis);
        }
    }

    /* Якщо потрібне ТО, проводимо регламентне очищення та сервіс */
    if (t8_tracker_needs_maintenance(&z_axis)) {
        printf("\nВиконується сервісний регламент: знежирення IPA 99.8%% та нанесення SI-180...\n");
        t8_tracker_perform_service(&z_axis, 10.0);
        printf("Регламент успішно виконано. Лічильники скинуто.\n");
        t8_tracker_print_report(&z_axis);
    }

    return 0;
}
