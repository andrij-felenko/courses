/* test_main.c — набір модульних тестів драйвера, що біжить на ПК.
 *
 * Збірка й запуск нативним компілятором, без жодної плати:
 *     cc -std=c99 -Wall -Wextra -O1 *.c -o chip_tests -lm && ./chip_tests
 * Ненульовий код повернення — сигнал для конвеєра неперервної інтеграції.
 */
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "chip_driver.h"
#include "chip_regs.h"
#include "mock_bus.h"

#define DEV_ADDR 0x19u

static unsigned g_checks;
static unsigned g_failures;

static void check_impl(bool ok, const char *expr, int line)
{
    ++g_checks;
    if (!ok) {
        ++g_failures;
        fprintf(stderr, "    [FAIL] рядок %d: %s\n", line, expr);
    }
}

#define CHECK(cond) check_impl((cond), #cond, __LINE__)

/* Порівняння з допуском: у плаваючій комі точна рівність — самообман. */
static bool near(float value, float expected, float eps)
{
    return fabsf(value - expected) <= eps;
}

/* Кожен тест починає з чистого кремнію: спільний стан між тестами — це
 * найдешевший спосіб отримати набір, що зеленіє лише в одному порядку. */
static void setup(mock_bus_ctx_t *mock, chip_dev_t *dev, bool do_init)
{
    mock_bus_reset(mock, DEV_ADDR);
    if (do_init) {
        chip_status_t st = chip_init(dev, mock_bus_ops(), mock, DEV_ADDR);
        CHECK(st == CHIP_OK);
    }
}

/* --- Тест 1: ініціалізація та конфігурація регістрів --------------------- */
static void test_init_configures_registers(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    setup(&mock, &dev, false);

    chip_status_t st = chip_init(&dev, mock_bus_ops(), &mock, DEV_ADDR);
    CHECK(st == CHIP_OK);
    CHECK(dev.is_initialized);

    /* Ідентифікатор читають до першого запису — інакше ми конфігуруємо
     * невідомий пристрій. Перевіряємо це за номером транзакції. */
    CHECK(mock.write_count >= 2u);
    CHECK(mock.write_log[0].seq > 1u);

    uint8_t ctrl1 = 0u;
    uint8_t ctrl4 = 0u;
    CHECK(mock_last_write(&mock, CHIP_REG_CTRL1, &ctrl1));
    CHECK(mock_last_write(&mock, CHIP_REG_CTRL4, &ctrl4));

    /* Осі увімкнені, частота задана, режим низької роздільності вимкнений. */
    CHECK((ctrl1 & CTRL1_XYZ_EN) == CTRL1_XYZ_EN);
    CHECK(((ctrl1 & CTRL1_ODR_MASK) >> CTRL1_ODR_SHIFT) == CHIP_ODR_100_HZ);
    CHECK((ctrl1 & CTRL1_LPEN) == 0u);

    /* BDU обов'язковий: без нього між читанням молодшого й старшого байта
     * чип встигає підкласти новий відлік, і виходить каліка з двох різних. */
    CHECK((ctrl4 & CTRL4_BDU) != 0u);
    CHECK((ctrl4 & CTRL4_HR) != 0u);
    CHECK((ctrl4 & CTRL4_FS_MASK) == 0u); /* ±2 g за замовчуванням */

    /* Жоден байт конфігурації не пішов у регістр лише для читання. */
    for (uint32_t i = 0; i < mock.write_count; ++i) {
        CHECK(mock.write_log[i].applied);
    }
    printf("[%s] Тест 1: ініціалізація та налаштування регістрів\n",
           g_failures == 0u ? "PASS" : "FAIL");
}

/* --- Тест 2: некоректний ідентифікатор і мовчання на шині ---------------- */
static void test_rejects_foreign_chip(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;

    const uint8_t bad_ids[] = {0x00u, 0xFFu, 0x32u};
    for (unsigned i = 0; i < sizeof(bad_ids) / sizeof(bad_ids[0]); ++i) {
        setup(&mock, &dev, false);
        mock_poke(&mock, CHIP_REG_WHO_AM_I, bad_ids[i]);

        chip_status_t st = chip_init(&dev, mock_bus_ops(), &mock, DEV_ADDR);
        CHECK(st == CHIP_ERR_NOT_FOUND);
        CHECK(!dev.is_initialized);
        /* Ключове: у чужий кремній не пішло жодного байта конфігурації. */
        CHECK(mock.write_count == 0u);
    }

    /* Пристрою на шині немає взагалі: усі спроби впираються в NACK. */
    setup(&mock, &dev, false);
    mock.nack_device_address = true;
    CHECK(chip_init(&dev, mock_bus_ops(), &mock, DEV_ADDR) == CHIP_ERR_COMM);
    CHECK(!dev.is_initialized);

    /* Правильний чип, але помилилися адресою на платі. */
    setup(&mock, &dev, false);
    CHECK(chip_init(&dev, mock_bus_ops(), &mock, 0x18u) == CHIP_ERR_COMM);

    /* Робота з неініціалізованим дескриптором заборонена. */
    chip_axes_data_si_t sample;
    CHECK(chip_read_sample_si(&dev, &sample) == CHIP_ERR_NOT_INIT);
    CHECK(chip_set_range(&dev, 4u) == CHIP_ERR_NOT_INIT);

    printf("[%s] Тест 2: захист від чужого чипа й мовчазної шини\n",
           g_failures == 0u ? "PASS" : "FAIL");
}

/* --- Тест 3: точність переходу до SI ------------------------------------- */
static void test_si_conversion(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_axes_data_si_t a;
    setup(&mock, &dev, true);

    /* ±2 g: половина шкали — це рівно 1 g. */
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
    CHECK(near(a.x, 0.0f, 0.001f));
    CHECK(near(a.y, 0.0f, 0.001f));
    CHECK(near(a.z, CHIP_G_M_S2, 0.001f));

    /* Від'ємні коди в доповняльному коді: знак мусить поширитися з 16 біт. */
    mock_set_raw_xyz(&mock, -16384, 0, 0);
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
    CHECK(near(a.x, -CHIP_G_M_S2, 0.001f));

    /* Край шкали: -32768 не має перетворитися на +32768. */
    mock_set_raw_xyz(&mock, -32768, 32767, 0);
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
    CHECK(near(a.x, -2.0f * CHIP_G_M_S2, 0.001f));
    CHECK(a.y > 0.0f);

    /* Зміна діапазону змінює ціну відліку рівно вдвічі й не чіпає інших
     * бітів CTRL4 — тінь у драйвері саме для цього. */
    CHECK(chip_set_range(&dev, 4u) == CHIP_OK);
    uint8_t ctrl4 = 0u;
    CHECK(mock_last_write(&mock, CHIP_REG_CTRL4, &ctrl4));
    CHECK((ctrl4 & CTRL4_BDU) != 0u);
    CHECK((ctrl4 & CTRL4_HR) != 0u);
    CHECK(((ctrl4 & CTRL4_FS_MASK) >> CTRL4_FS_SHIFT) == 1u);

    mock_set_raw_xyz(&mock, 0, 0, 16384);
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
    CHECK(near(a.z, 2.0f * CHIP_G_M_S2, 0.002f));

    /* Зворотний шлях: генератор задає фізичну величину, драйвер має її
     * повернути. Синусоїда по осі X — модель столу, що вібрує. */
    CHECK(chip_set_range(&dev, 8u) == CHIP_OK);
    for (int step = 0; step < 16; ++step) {
        float g = 3.0f * sinf((float)step * 0.4f);
        mock_set_accel_g(&mock, 8u, g, 0.0f, 1.0f);
        CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
        CHECK(near(a.x, g * CHIP_G_M_S2, 0.01f));
        CHECK(near(a.z, CHIP_G_M_S2, 0.01f));
    }

    /* Недозволений діапазон драйвер відхиляє, не чіпаючи кремнію. */
    uint32_t writes_before = mock.write_count;
    CHECK(chip_set_range(&dev, 3u) == CHIP_ERR_INVALID_PARAM);
    CHECK(mock.write_count == writes_before);
    CHECK(dev.active_range == 8u);

    printf("[%s] Тест 3: точність переходу до м/с² і зміна діапазону\n",
           g_failures == 0u ? "PASS" : "FAIL");
}

/* --- Тест 4: повторні спроби при короткочасних завадах ------------------- */
static void test_retries_on_transient_faults(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_axes_data_si_t a;
    setup(&mock, &dev, true);

    /* Дві поспіль невдачі — третя спроба вдала. */
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    mock.fail_reads_countdown = 2;
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);
    CHECK(near(a.z, CHIP_G_M_S2, 0.001f));

    /* Завада довша за політику повторів — драйвер чесно здається. */
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    mock.fail_reads_countdown = 10;
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_ERR_COMM);
    CHECK(mock.fail_reads_countdown == 10 - (int32_t)(dev.max_retries + 1u));

    /* Збій на записі теж повторюється: конфігурація не має губитися. */
    mock.fail_reads_countdown = 0;
    mock.fail_writes_countdown = 2;
    CHECK(chip_set_range(&dev, 16u) == CHIP_OK);
    CHECK(dev.active_range == 16u);

    /* Обрив пакетного читання на третьому байті: половина буфера — сміття,
     * і драйвер зобов'язаний повернути помилку, а не «майже правильні» осі. */
    setup(&mock, &dev, true);
    mock_set_raw_xyz(&mock, 1000, 2000, 3000);
    a.x = a.y = a.z = -1.0f;
    mock.break_read_at_byte = 3u;
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_ERR_COMM);
    CHECK(near(a.x, -1.0f, 0.0001f)); /* вихідну структуру не зіпсовано */

    printf("[%s] Тест 4: повтори спроб і обрив передачі\n",
           g_failures == 0u ? "PASS" : "FAIL");
}

/* --- Тест 5: прапорець готовності даних ---------------------------------- */
static void test_data_ready_flag(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_axes_data_si_t a;
    setup(&mock, &dev, true);

    /* Одразу після ініціалізації нового відліку ще нема. */
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_ERR_NO_DATA);

    mock_set_raw_xyz(&mock, 0, 0, 16384);
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_OK);

    /* Відлік забрали — прапорець згас, повторне читання дає NO_DATA, а не
     * тихо той самий байт удруге. */
    CHECK(chip_read_sample_si(&dev, &a) == CHIP_ERR_NO_DATA);

    /* Не забраний вчасно відлік залишає слід перезапису в STATUS. */
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    mock_set_raw_xyz(&mock, 0, 0, 8192);
    CHECK((mock_peek(&mock, CHIP_REG_STATUS) & STATUS_ZYXOR) != 0u);

    printf("[%s] Тест 5: облік готовності й перезапису даних\n",
           g_failures == 0u ? "PASS" : "FAIL");
}

/* --- Тест 6: стійкість математики до сміття на шині ---------------------- */
static uint32_t xorshift(uint32_t *state)
{
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

static void test_fuzz_conversion(void)
{
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_axes_data_si_t a;
    setup(&mock, &dev, true);

    uint32_t state = 0xC0FFEEu; /* детермінований засів: збій відтворюваний */
    const float limit = (float)dev.active_range * CHIP_G_M_S2;
    unsigned ok_count = 0u;

    for (unsigned i = 0; i < 200000u; ++i) {
        uint32_t r = xorshift(&state);

        /* Сміття в блоці даних і у прапорцях статусу. */
        for (uint8_t reg = CHIP_REG_OUT_X_L; reg <= CHIP_REG_OUT_Z_H; ++reg) {
            mock_poke(&mock, reg, (uint8_t)(xorshift(&state) & 0xFFu));
        }
        mock_poke(&mock, CHIP_REG_STATUS, (uint8_t)(r & 0xFFu));
        mock.fail_reads_countdown = (int32_t)((r >> 8) & 0x3u);
        mock.break_read_at_byte   = (uint16_t)((r >> 12) & 0x7u);

        chip_status_t st = chip_read_sample_si(&dev, &a);
        CHECK(st == CHIP_OK || st == CHIP_ERR_NO_DATA || st == CHIP_ERR_COMM);
        if (st != CHIP_OK) {
            continue;
        }
        ++ok_count;

        /* Жодна комбінація байтів не має дати ні NaN, ні виходу за шкалу. */
        CHECK(isfinite(a.x) && isfinite(a.y) && isfinite(a.z));
        CHECK(fabsf(a.x) <= limit + 0.001f);
        CHECK(fabsf(a.y) <= limit + 0.001f);
        CHECK(fabsf(a.z) <= limit + 0.001f);

        if (g_failures > 0u) {
            break; /* не топимо консоль тисячами однакових рядків */
        }
    }

    CHECK(ok_count > 0u); /* набір, що жодного разу не дійшов до мети, брехня */
    printf("[%s] Тест 6: %u випадкових станів шини без NaN і виходу за шкалу\n",
           g_failures == 0u ? "PASS" : "FAIL", ok_count);
}

int main(void)
{
    printf("=== Модульні тести драйвера на моці (без плати) ===\n");

    test_init_configures_registers();
    test_rejects_foreign_chip();
    test_si_conversion();
    test_retries_on_transient_faults();
    test_data_ready_flag();
    test_fuzz_conversion();

    printf("\nПеревірок: %u, невдалих: %u\n", g_checks, g_failures);
    if (g_failures != 0u) {
        printf(">>> НАБІР ПРОВАЛЕНО <<<\n");
        return 1;
    }
    printf(">>> Усі перевірки пройдено <<<\n");
    return 0;
}
