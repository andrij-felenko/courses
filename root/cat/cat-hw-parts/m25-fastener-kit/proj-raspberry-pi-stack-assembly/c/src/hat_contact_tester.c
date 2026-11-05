/**
 * @file hat_contact_tester.c
 * @brief Реалізація відкриття пристрою /dev/i2c-1, конфігурації адреси веденого пристрою,
 *        опитування регістрів та підрахунку помилок зв'язку для перевірки контакту HAT.
 */

#include "hat_contact_tester.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <errno.h>
#include <string.h>

/**
 * @brief Значення за замовчуванням для конфігурації тестування HAT.
 */
void hat_tester_init_config(hat_test_config_t *config) {
    if (config == NULL) {
        return;
    }
    config->i2c_device_path = "/dev/i2c-1";
    config->slave_address = 0x48; // Типова адреса для датчиків/eeprom на HAT (наприклад, LM75 / AT24C)
    config->reg_address = 0x00;   // Базовий регістр конфігурації / даних
    config->total_cycles = 1000;  // 1000 циклів стрес-тестування
    config->delay_ms = 5;         // Затримка 5 мс між опитуваннями
}

/**
 * @brief Виконує один цикл транзакції запису-читання по шині I2C.
 */
static bool perform_single_transaction(int file_des, uint8_t reg_addr) {
    // Надсилаємо адресу регістра для зчитування
    if (write(file_des, &reg_addr, 1) != 1) {
        return false;
    }

    // Читаємо значення з регістра
    uint8_t data_buffer = 0;
    if (read(file_des, &data_buffer, 1) != 1) {
        return false;
    }

    return true;
}

bool hat_tester_run_stress_test(const hat_test_config_t *config, hat_test_stats_t *stats) {
    if (config == NULL || stats == NULL) {
        return false;
    }

    // Ініціалізація статистики
    stats->successful_transactions = 0;
    stats->failed_transactions = 0;
    stats->failure_rate_percent = 0.0;

    // Відкриття пристрою I2C шини
    int file_des = open(config->i2c_device_path, O_RDWR);
    if (file_des < 0) {
        fprintf(stderr, "[ПОМИЛКА] Не вдалося відкрити шину I2C '%s': %s\n", 
                config->i2c_device_path, strerror(errno));
        return false;
    }

    // Встановлення адреси веденого пристрою (slave address) через ioctl
    if (ioctl(file_des, I2C_SLAVE, config->slave_address) < 0) {
        fprintf(stderr, "[ПОМИЛКА] Не вдалося встановити I2C адресу 0x%02X: %s\n", 
                config->slave_address, strerror(errno));
        close(file_des);
        return false;
    }

    printf("[ІНФО] Початок стрес-тестування шини I2C (%d циклів, пристрій: 0x%02X)...\n", 
           config->total_cycles, config->slave_address);

    // Циклічні транзакції (стрес-тест)
    for (int i = 0; i < config->total_cycles; i++) {
        if (perform_single_transaction(file_des, config->reg_address)) {
            stats->successful_transactions++;
        } else {
            stats->failed_transactions++;
        }

        if (config->delay_ms > 0) {
            usleep(config->delay_ms * 1000);
        }
    }

    close(file_des);

    // Розрахунок відсотка збоїв
    int total = stats->successful_transactions + stats->failed_transactions;
    if (total > 0) {
        stats->failure_rate_percent = ((double)stats->failed_transactions / total) * 100.0;
    }

    return true;
}

void hat_tester_print_report(const hat_test_stats_t *stats) {
    if (stats == NULL) {
        return;
    }

    int total = stats->successful_transactions + stats->failed_transactions;

    printf("\n========================================================\n");
    printf("       ДІАГНОСТИЧНИЙ ЗВІТ ЯКОСТІ МОНТАЖУ ШИЛДА HAT        \n");
    printf("========================================================\n");
    printf(" Всього виконано транзакцій : %d\n", total);
    printf(" Успішних пакетів            : %d\n", stats->successful_transactions);
    printf(" Збійних пакетів (помилки)   : %d\n", stats->failed_transactions);
    printf(" Відсоток збоїв (Loss Rate)  : %.2f%%\n", stats->failure_rate_percent);
    printf("--------------------------------------------------------\n");
    printf(" ДІАГНОСТИЧНИЙ ВЕРДИКТ ТА РЕКОМЕНДАЦІЇ:\n");

    if (stats->failure_rate_percent == 0.0) {
        printf(" [ВІДМІННО] Контакт стабільний. Монтаж ідеальний,\n");
        printf(" перекосів контактів GPIO та проблем зі стійками М2.5 немає.\n");
    } else if (stats->failure_rate_percent < 2.0) {
        printf(" [ДОБРЕ] Незначні випадкові збої зв'язку (< 2%%).\n");
        printf(" Рекомендується перевірити щільність затягування стійок М2.5.\n");
    } else if (stats->failure_rate_percent < 10.0) {
        printf(" [ПОПЕРЕДЖЕННЯ] Виявлено помірну кількість збоїв (2%% - 10%%).\n");
        printf(" Можливий перекіс контактів роз'єму GPIO або нерівномірне\n");
        printf(" затягування гвинтів/стійок М2.5 fastener kit. Перевірте механічний монтаж.\n");
    } else {
        printf(" [КРИТИЧНО] Високий рівень збоїв (> 10%%)!\n");
        printf(" Серйозний контактний дефект. Потрібно повністю вимкнути живлення,\n");
        printf(" перевірити вирівнювання роз'єму HAT відносно пінів Raspberry Pi\n");
        printf(" та відрегулювати момент затягування стійок М2.5.\n");
    }
    printf("========================================================\n");
}
