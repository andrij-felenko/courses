/* nvme_health_reader.c — Пряме читання NVMe Health Information Log */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

#pragma pack(push, 1)
struct nvme_smart_log {
    uint8_t  critical_warning;
    uint16_t temperature;                  /* у Кельвінах */
    uint8_t  avail_spare;                  /* відсотки */
    uint8_t  spare_thresh;
    uint8_t  percent_used;
    uint8_t  endu_grp_crit_warn_sumry;
    uint8_t  rsvd6[25];
    uint8_t  data_units_read[16];          /* 128-біт */
    uint8_t  data_units_written[16];       /* 128-біт */
    uint8_t  host_reads[16];
    uint8_t  host_writes[16];
    uint8_t  ctrl_busy_time[16];
    uint8_t  power_cycles[16];
    uint8_t  power_on_hours[16];
    uint8_t  unsafe_shutdowns[16];
    uint8_t  media_errors[16];
    uint8_t  num_err_log_entries[16];
    uint32_t warning_temp_time;
    uint32_t critical_comp_time;
    uint16_t temp_sensor[8];
    uint32_t thm_temp1_trans_count;
    uint32_t thm_temp2_trans_count;
    uint32_t thm_temp1_total_time;
    uint32_t thm_temp2_total_time;
    uint8_t  rsvd232[280];
};
#pragma pack(pop)

static uint64_t unpack_u128_low(const uint8_t buf[16]) {
    uint64_t val = 0;
    for (int i = 0; i < 8; ++i) {
        val |= ((uint64_t)buf[i]) << (i * 8);
    }
    return val;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/nvme0\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити NVMe контролер");
        return EXIT_FAILURE;
    }

    struct nvme_smart_log log_data;
    memset(&log_data, 0, sizeof(log_data));

    struct nvme_admin_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.opcode    = 0x02;        /* Get Log Page */
    cmd.nsid      = 0xFFFFFFFF;  /* Global Controller Log */
    cmd.addr      = (uint64_t)(uintptr_t)&log_data;
    cmd.data_len  = sizeof(log_data);
    /* cdw10: [7:0] = Log ID (0x02), [27:16] = Number of Dwords Lower (127 for 512 bytes) */
    cmd.cdw10     = 0x02 | (127 << 16);

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        perror("Помилка виклику ioctl(NVME_IOCTL_ADMIN_CMD)");
        close(fd);
        return EXIT_FAILURE;
    }
    close(fd);

    double temp_c = (double)log_data.temperature - 273.15;
    printf("=== Звіт здоров'я NVMe (%s) ===\n", argv[1]);
    printf("Критичні попередження (Critical Warning): 0x%02X\n", log_data.critical_warning);
    if (log_data.critical_warning & (1 << 0)) printf("  [!] Запасні блоки (Available Spare) нижче порогу!\n");
    if (log_data.critical_warning & (1 << 1)) printf("  [!] Перевищено температурний поріг!\n");
    if (log_data.critical_warning & (1 << 2)) printf("  [!] Надійність підсистеми NVM катастрофічно деградувала!\n");
    if (log_data.critical_warning & (1 << 3)) printf("  [!] Носій переведено в режим ТІЛЬКИ ДЛЯ ЧИТАННЯ (Read Only)!\n");
    if (log_data.critical_warning & (1 << 4)) printf("  [!] Збій пристрою резервного живлення кешу!\n");

    printf("Температура: %.1f °C (%u K)\n", temp_c, log_data.temperature);
    printf("Залишок резерву (Available Spare): %u%% (Поріг: %u%%)\n",
           log_data.avail_spare, log_data.spare_thresh);
    printf("Використано ресурсу (Percentage Used): %u%%\n", log_data.percent_used);

    /* 1 data unit = 1000 секторів по 512 байтів = 500 КБ */
    uint64_t units_written = unpack_u128_low(log_data.data_units_written);
    uint64_t units_read = unpack_u128_low(log_data.data_units_read);
    printf("Записано даних: %lu ГБ\n", (unsigned long)(units_written * 512000 / (1024 * 1024 * 1024)));
    printf("Прочитано даних: %lu ГБ\n", (unsigned long)(units_read * 512000 / (1024 * 1024 * 1024)));
    printf("Помилки носія (Media Errors): %lu\n", (unsigned long)unpack_u128_low(log_data.media_errors));
    printf("Аварійні вимкнення (Unsafe Shutdowns): %lu\n", (unsigned long)unpack_u128_low(log_data.unsafe_shutdowns));
    printf("Години роботи під напругою: %lu год\n", (unsigned long)unpack_u128_low(log_data.power_on_hours));

    return EXIT_SUCCESS;
}
