/* Приклад опитування промислового COTS-модуля (Modbus RTU) мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <modbus/modbus.h>

#define SLAVE_ID         1
#define REGISTER_START   0x0100
#define NUM_REGISTERS    4

int main(void) {
    modbus_t *ctx = modbus_new_rtu("/dev/ttyUSB0", 115200, 'N', 8, 1);
    if (!ctx) {
        perror("Не вдалося створити контекст Modbus");
        return EXIT_FAILURE;
    }

    modbus_set_slave(ctx, SLAVE_ID);
    modbus_set_response_timeout(ctx, 0, 500000); /* 500 мс таймаут */

    if (modbus_connect(ctx) == -1) {
        fprintf(stderr, "Помилка з'єднання: %s\n", modbus_strerror(errno));
        modbus_free(ctx);
        return EXIT_FAILURE;
    }

    uint16_t raw_data[NUM_REGISTERS];
    int rc = modbus_read_input_registers(ctx, REGISTER_START, NUM_REGISTERS, raw_data);
    if (rc == -1) {
        fprintf(stderr, "Помилка читання регістрів: %s\n", modbus_strerror(errno));
        modbus_close(ctx);
        modbus_free(ctx);
        return EXIT_FAILURE;
    }

    /* Інтерпретація каліброваних фізичних величин із COTS-блоку */
    float pressure_bar = (float)raw_data[0] * 0.01f;
    float temp_celsius = (float)((int16_t)raw_data[1]) * 0.1f;
    printf("Дані COTS: Тиск = %.2f бар, Температура = %.1f °C\n", pressure_bar, temp_celsius);

    modbus_close(ctx);
    modbus_free(ctx);
    return EXIT_SUCCESS;
}
