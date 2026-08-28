#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define SECTOR_SIZE 64
#define NUM_DISKS 4

typedef struct {
    uint8_t data[SECTOR_SIZE];
    bool is_online;
} VirtualDisk;

typedef struct {
    VirtualDisk disks[NUM_DISKS];
    size_t disk_capacity_sectors;
} Raid5Array;

// Ініціалізація масиву
Raid5Array* raid5_create(size_t capacity_sectors) {
    Raid5Array *array = (Raid5Array*)malloc(sizeof(Raid5Array));
    if (!array) return NULL;
    
    array->disk_capacity_sectors = capacity_sectors;
    for (int i = 0; i < NUM_DISKS; i++) {
        array->disks[i].is_online = true;
        memset(array->disks[i].data, 0, SECTOR_SIZE);
    }
    return array;
}

void raid5_free(Raid5Array *array) {
    if (array) free(array);
}

// Побітове обчислення XOR-паритету
static void compute_xor(const uint8_t *src1, const uint8_t *src2, uint8_t *dest, size_t len) {
    for (size_t i = 0; i < len; i++) {
        dest[i] = src1[i] ^ src2[i];
    }
}

// Визначення дисків даних та паритету для страйпа
static int get_parity_disk(size_t stripe_idx) {
    // Left-Symmetric ротація паритету
    return (int)((NUM_DISKS - 1) - (stripe_idx % NUM_DISKS));
}

// Запис сектора у RAID 5
bool raid5_write_sector(Raid5Array *array, size_t logical_sector, const uint8_t *buf) {
    size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
    size_t data_col = logical_sector % (NUM_DISKS - 1);
    int parity_disk = get_parity_disk(stripe_idx);
    
    // Мапінг дисків: обхід диска паритету
    int target_disk = (int)data_col;
    if (target_disk >= parity_disk) {
        target_disk++;
    }

    if (!array->disks[target_disk].is_online) {
        fprintf(stderr, "Помилка: Цільовий диск %d офлайн, необхідна відбудова.\n", target_disk);
        return false;
    }

    // Запис даних на цільовий диск
    memcpy(array->disks[target_disk].data, buf, SECTOR_SIZE);

    // Оновлення паритету (переобчислення по всіх справних дисках даних)
    uint8_t new_parity[SECTOR_SIZE];
    memset(new_parity, 0, SECTOR_SIZE);
    
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == parity_disk) continue;
        compute_xor(new_parity, array->disks[d].data, new_parity, SECTOR_SIZE);
    }

    if (array->disks[parity_disk].is_online) {
        memcpy(array->disks[parity_disk].data, new_parity, SECTOR_SIZE);
    }
    return true;
}

// Читання сектора з RAID 5 (з підтримкою Degraded Mode)
bool raid5_read_sector(Raid5Array *array, size_t logical_sector, uint8_t *buf) {
    size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
    size_t data_col = logical_sector % (NUM_DISKS - 1);
    int parity_disk = get_parity_disk(stripe_idx);
    
    int target_disk = (int)data_col;
    if (target_disk >= parity_disk) {
        target_disk++;
    }

    // Нормальний режим: диск даних онлайн
    if (array->disks[target_disk].is_online) {
        memcpy(buf, array->disks[target_disk].data, SECTOR_SIZE);
        return true;
    }

    // Деградований режим: реконструкція «на льоту» через XOR
    printf("Диск %d недоступний. Реконструкція сектора %zu налету через XOR...\n", target_disk, logical_sector);
    memset(buf, 0, SECTOR_SIZE);

    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == target_disk) continue;
        if (!array->disks[d].is_online) {
            fprintf(stderr, "Фатальна помилка: Понад один диск офлайн! Втрата даних.\n");
            return false;
        }
        compute_xor(buf, array->disks[d].data, buf, SECTOR_SIZE);
    }
    return true;
}

// Симуляція відмови диска
void raid5_fail_disk(Raid5Array *array, int disk_idx) {
    if (disk_idx >= 0 && disk_idx < NUM_DISKS) {
        array->disks[disk_idx].is_online = false;
        memset(array->disks[disk_idx].data, 0, SECTOR_SIZE);
        printf("⚠️ Диск %d ФІЗИЧНО ВИЙШОВ З ЛАДУ!\n", disk_idx);
    }
}

// Процес відбудови (Rebuild / Resilver) на новий replacement-диск
bool raid5_rebuild(Raid5Array *array, int failed_disk_idx) {
    if (array->disks[failed_disk_idx].is_online) return true;

    printf("🔄 Розпочато процес відбудови диска %d...\n", failed_disk_idx);

    // Перевірка, що всі інші диски онлайн
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d != failed_disk_idx && !array->disks[d].is_online) {
            fprintf(stderr, "Відбудова неможлива: диск %d також офлайн.\n", d);
            return false;
        }
    }

    // Реконструкція даного диска через XOR решти дисків
    memset(array->disks[failed_disk_idx].data, 0, SECTOR_SIZE);
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == failed_disk_idx) continue;
        compute_xor(array->disks[failed_disk_idx].data, array->disks[d].data, 
                    array->disks[failed_disk_idx].data, SECTOR_SIZE);
    }

    array->disks[failed_disk_idx].is_online = true;
    printf("✅ Відбудову диска %d успішно завершено!\n", failed_disk_idx);
    return true;
}

int main(void) {
    Raid5Array *raid = raid5_create(100);
    
    const char *secret_msg = "Hello RAID 5 Architecture!";
    uint8_t write_buf[SECTOR_SIZE] = {0};
    strncpy((char*)write_buf, secret_msg, SECTOR_SIZE - 1);

    printf("1. Запис даних у логічний сектор 0...\n");
    raid5_write_sector(raid, 0, write_buf);

    uint8_t read_buf[SECTOR_SIZE] = {0};
    raid5_read_sector(raid, 0, read_buf);
    printf("Прочитано з масиву: \"%s\"\n\n", (char*)read_buf);

    printf("2. Симуляція аварї диска 0...\n");
    raid5_fail_disk(raid, 0);

    memset(read_buf, 0, SECTOR_SIZE);
    printf("3. Спроба зчитати дані у деградованому режимі...\n");
    raid5_read_sector(raid, 0, read_buf);
    printf("Результат налету reconstruction: \"%s\"\n\n", (char*)read_buf);

    printf("4. Заміна диска та відбудова масиву...\n");
    raid5_rebuild(raid, 0);

    memset(read_buf, 0, SECTOR_SIZE);
    raid5_read_sector(raid, 0, read_buf);
    printf("Прочитано після відбудови: \"%s\"\n", (char*)read_buf);

    raid5_free(raid);
    return 0;
}
