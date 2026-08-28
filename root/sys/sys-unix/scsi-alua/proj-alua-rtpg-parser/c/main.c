#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <scsi/sg.h>
#include <scsi/scsi.h>

#define RTPG_CDB_LEN       16
#define RTPG_BUF_SIZE      1024
#define SENSE_BUF_SIZE     64
#define DEFAULT_TIMEOUT_MS 5000

/* Текстове представлення асиметричного стану доступу за стандартом SPC-4 */
static const char *alua_state_str(uint8_t state) {
    switch (state & 0x0F) {
        case 0x00: return "Active/Optimized (AO)";
        case 0x01: return "Active/Non-Optimized (ANO)";
        case 0x02: return "Standby (SB)";
        case 0x03: return "Unavailable (UN)";
        case 0x0E: return "Standby Offline";
        case 0x0F: return "Transitioning (TO)";
        default:   return "Reserved / Unknown";
    }
}

/* Текстовий опис коду статусу TPG */
static const char *alua_status_str(uint8_t status) {
    switch (status) {
        case 0x00: return "No status / Normal";
        case 0x01: return "Altered by SET TARGET PORT GROUPS";
        case 0x02: return "Altered by Target controller (Implicit)";
        default:   return "Vendor specific";
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_пристрою_scsi> (наприклад /dev/sg1 або /dev/sdb)\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *dev_path = argv[1];
    int fd = open(dev_path, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій");
        return EXIT_FAILURE;
    }

    uint8_t cdb[RTPG_CDB_LEN];
    memset(cdb, 0, sizeof(cdb));
    cdb[0] = 0xA3; /* MAINTENANCE IN */
    cdb[1] = 0x0A; /* Service Action: REPORT TARGET PORT GROUPS */
    /* Allocation Length: 1024 байти (big-endian uint32 у байтах 6..9) */
    uint32_t alloc_len = htonl(RTPG_BUF_SIZE);
    memcpy(&cdb[6], &alloc_len, sizeof(alloc_len));

    uint8_t resp_buf[RTPG_BUF_SIZE];
    uint8_t sense_buf[SENSE_BUF_SIZE];
    memset(resp_buf, 0, sizeof(resp_buf));
    memset(sense_buf, 0, sizeof(sense_buf));

    struct sg_io_hdr io_hdr;
    memset(&io_hdr, 0, sizeof(io_hdr));
    io_hdr.interface_id = 'S';
    io_hdr.cmdp = cdb;
    io_hdr.cmd_len = sizeof(cdb);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len = sizeof(resp_buf);
    io_hdr.dxferp = resp_buf;
    io_hdr.sbp = sense_buf;
    io_hdr.mx_sb_len = sizeof(sense_buf);
    io_hdr.timeout = DEFAULT_TIMEOUT_MS;

    printf("Надсилання команди REPORT TARGET PORT GROUPS до %s...\n", dev_path);
    if (ioctl(fd, SG_IO, &io_hdr) < 0) {
        perror("Помилка виклику ioctl SG_IO");
        close(fd);
        return EXIT_FAILURE;
    }

    if (io_hdr.status != 0) {
        fprintf(stderr, "Пристрій повернув статус SCSI: 0x%02X (CHECK CONDITION)\n", io_hdr.status);
        if (io_hdr.sb_len_wr > 0) {
            uint8_t sense_key = sense_buf[2] & 0x0F;
            uint8_t asc = sense_buf[12];
            uint8_t ascq = sense_buf[13];
            fprintf(stderr, "Sense Key: 0x%02X, ASC: 0x%02X, ASCQ: 0x%02X\n", sense_key, asc, ascq);
        }
        close(fd);
        return EXIT_FAILURE;
    }

    /* Перші 4 байти — загальна довжина наступних даних дескрипторів (big-endian) */
    uint32_t data_len = (resp_buf[0] << 24) | (resp_buf[1] << 16) | (resp_buf[2] << 8) | resp_buf[3];
    printf("Отримано успішну відповідь. Довжина даних параметра: %u байтів\n\n", data_len);

    uint32_t offset = 4;
    uint32_t total_limit = 4 + data_len;
    if (total_limit > RTPG_BUF_SIZE) {
        total_limit = RTPG_BUF_SIZE;
    }

    int tpg_index = 1;
    while (offset + 8 <= total_limit) {
        uint8_t pref_state = resp_buf[offset];
        uint8_t is_pref = (pref_state & 0x80) ? 1 : 0;
        uint8_t state = pref_state & 0x0F;
        uint8_t sup_mask = resp_buf[offset + 1];
        uint16_t tpg_id = (resp_buf[offset + 2] << 8) | resp_buf[offset + 3];
        uint8_t status_code = resp_buf[offset + 4];
        uint16_t port_count = (resp_buf[offset + 6] << 8) | resp_buf[offset + 7];

        printf("=== [Цільова група портів #%d (TPG ID: %u / 0x%04X)] ===\n", tpg_index, tpg_id, tpg_id);
        printf("  Стан доступу ALUA:    %s\n", alua_state_str(state));
        printf("  Бажана група (PREF):  %s\n", is_pref ? "ТАК (Preferred)" : "НІ");
        printf("  Маска підтримки:      0x%02X (AO:%d, ANO:%d, SB:%d, UN:%d, TO:%d)\n",
               sup_mask,
               (sup_mask & 0x01) ? 1 : 0,
               (sup_mask & 0x02) ? 1 : 0,
               (sup_mask & 0x04) ? 1 : 0,
               (sup_mask & 0x08) ? 1 : 0,
               (sup_mask & 0x80) ? 1 : 0);
        printf("  Статус зміни:         %s\n", alua_status_str(status_code));
        printf("  Кількість портів:     %u\n", port_count);

        offset += 8;
        printf("  Список портів цілі:\n");
        for (uint16_t p = 0; p < port_count; ++p) {
            if (offset + 4 > total_limit) {
                fprintf(stderr, "  [Попередження: буфер обірвався передчасно]\n");
                break;
            }
            uint16_t port_id = (resp_buf[offset + 2] << 8) | resp_buf[offset + 3];
            printf("    - Порт #%u (Relative Target Port ID: %u / 0x%04X)\n", p + 1, port_id, port_id);
            offset += 4;
        }
        printf("\n");
        tpg_index++;
    }

    close(fd);
    return EXIT_SUCCESS;
}
