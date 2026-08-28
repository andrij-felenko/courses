// Компіляція:  gcc dps.c -o dps $(pkg-config --cflags --libs libmodbus)
// libmodbus сама збирає кадр Modbus RTU і рахує CRC-16.
#include <modbus.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>   // sleep()

// Адреси регістрів (0-базовані) — з мапи DPS/DPH.
enum {
    REG_USET   = 0x00,  // задана напруга,  вольти × 100
    REG_ISET   = 0x01,  // заданий струм,   ампери × 1000  (!! інший множник)
    REG_UOUT   = 0x02,  // виміряна напруга, вольти × 100
    REG_IOUT   = 0x03,  // виміряний струм,  ампери × 1000
    REG_ONOFF  = 0x09,  // вмикач виходу,    0 / 1
};

int main(void) {
    // 1. Відкриваємо порт: 9600 бод, без парності (N), 8 біт, 1 стоп-біт.
    //    На Linux — "/dev/ttyUSB0", на Windows — "COM4" (як бачить система).
    modbus_t *ctx = modbus_new_rtu("/dev/ttyUSB0", 9600, 'N', 8, 1);
    if (!ctx) {
        fprintf(stderr, "не створити контекст: %s\n", modbus_strerror(errno));
        return 1;
    }
    modbus_set_slave(ctx, 1);   // адреса веденого за замовчуванням — 1

    if (modbus_connect(ctx) == -1) {
        fprintf(stderr, "порт не відкрився: %s\n", modbus_strerror(errno));
        modbus_free(ctx);
        return 1;
    }

    // 2. Кодуємо людські величини в «рідні» цілі числа приладу.
    //    5.00 В → 500 (× 100);   1.000 А → 1000 (× 1000).
    uint16_t uset = (uint16_t)(5.00  * 100 + 0.5);   // = 500
    uint16_t iset = (uint16_t)(1.000 * 1000 + 0.5);  // = 1000

    // 3. Пишемо задані значення (кожне — одна комірка, функція 0x06).
    if (modbus_write_register(ctx, REG_USET, uset) == -1 ||
        modbus_write_register(ctx, REG_ISET, iset) == -1) {
        fprintf(stderr, "запис U/I не вдався: %s\n", modbus_strerror(errno));
    }

    // 4. Вмикаємо вихід — БЕЗ цього кроку на клемах нуль, хоч що ти задав.
    modbus_write_register(ctx, REG_ONOFF, 1);

    sleep(1);  // даємо виходу встановитися під навантаженням

    // 5. Читаємо виміряні напругу й струм одним запитом: дві комірки від 0x02.
    uint16_t meas[2];   // meas[0] = U-OUT, meas[1] = I-OUT
    if (modbus_read_registers(ctx, REG_UOUT, 2, meas) == 2) {
        double u = meas[0] / 100.0;    // назад у вольти
        double i = meas[1] / 1000.0;   // назад в ампери (÷1000!)
        printf("на виході: %.2f В, %.3f А\n", u, i);
    } else {
        fprintf(stderr, "читання виміру не вдалося: %s\n", modbus_strerror(errno));
    }

    // 6. Прибираємо за собою.
    modbus_close(ctx);
    modbus_free(ctx);
    return 0;
}
