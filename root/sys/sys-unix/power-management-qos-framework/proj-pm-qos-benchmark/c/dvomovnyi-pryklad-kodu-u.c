#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define PM_QOS_DEV "/dev/cpu_dma_latency"

// Відкриває пристрій PM QoS і записує бажане обмеження затримки у мікросекундах
int set_cpu_latency_target(int32_t latency_us) {
    int fd = open(PM_QOS_DEV, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття " PM_QOS_DEV " (перевірте права root)");
        return -1;
    }

    if (write(fd, &latency_us, sizeof(latency_us)) != sizeof(latency_us)) {
        perror("Помилка запису цільового значення у " PM_QOS_DEV);
        close(fd);
        return -1;
    }

    return fd;
}

int main(void) {
    int32_t target_latency = 0; // 0 мкс: повна заборона станів сну C1..C10

    printf("[C] Запитуємо обмеження затримки CPU у %d мкс...\n", target_latency);
    int qos_fd = set_cpu_latency_target(target_latency);
    if (qos_fd < 0) {
        return EXIT_FAILURE;
    }

    printf("[C] Обмеження PM QoS активовано. Виконуємо критичну секцію обчислень...\n");
    
    // Імітація інтенсивної обробки даних
    usleep(500000); // 500 мс

    printf("[C] Критичну секцію завершено. Закриваємо дескриптор для зняття обмеження.\n");
    close(qos_fd); // Ядро автоматично вилучає запит зі списку агрегації

    return EXIT_SUCCESS;
}
