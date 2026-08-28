/* sata_smart_reader.c — Пряме читання атрибутів SMART для SATA/ATA пристроїв */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h>

#define ATA_PASS_THROUGH_16 0x85
#define ATA_SMART_CMD       0xB0
#define ATA_SMART_READ_DATA 0xD0
#define SMART_LBA_MID       0x4F
#define SMART_LBA_HIGH      0xC2

#pragma pack(push, 1)
struct smart_attribute {
    uint8_t  id;
    uint16_t flags;
    uint8_t  current_value;
    uint8_t  worst_value;
    uint8_t  raw_bytes[6];
    uint8_t  reserved;
};

struct smart_data_sector {
    uint16_t               version;
    struct smart_attribute attributes[30];
    uint8_t                offline_data_collection_status;
    uint8_t                self_test_exec_status;
    uint16_t               offline_data_collection_time;
    uint8_t                vendor_specific_366;
    uint8_t                offline_data_collection_capability;
    uint16_t               smart_capability;
    uint8_t                error_logging_capability;
    uint8_t                vendor_specific_371;
    uint8_t                short_test_completion_time;
    uint8_t                extended_test_completion_time;
    uint8_t                conveyance_test_completion_time;
    uint16_t               extended_test_completion_time_ext;
    uint8_t                reserved[134];
    uint8_t                checksum;
};
#pragma pack(pop)

static uint64_t unpack_raw(const uint8_t raw[6]) {
    uint64_t val = 0;
    for (int i = 0; i < 6; ++i) {
        val |= ((uint64_t)raw[i]) << (i * 8);
    }
    return val;
}

static int read_sata_smart(const char *dev_path, struct smart_data_sector *out_data) {
    int fd = open(dev_path, O_RDONLY | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій");
        return -1;
    }

    uint8_t cdb[16];
    memset(cdb, 0, sizeof(cdb));
    cdb[0]  = ATA_PASS_THROUGH_16;
    /* [3:1] = 4 (PIO Data-In), [0] = 1 (T_DIR: від пристрою до хоста) */
    cdb[1]  = (4 << 1) | 1;
    /* [2] = 1 (T_LENGTH: довжина передається в Sector Count), [1:0] = 2 (у секторах) */
    cdb[2]  = (1 << 2) | 2;
    cdb[3]  = 0;                         /* Features (high) */
    cdb[4]  = ATA_SMART_READ_DATA;       /* Features (low) = D0h */
    cdb[5]  = 0;                         /* Sector Count (high) */
    cdb[6]  = 1;                         /* Sector Count (low) = 1 сектор (512B) */
    cdb[7]  = 0;                         /* LBA Low (high) */
    cdb[8]  = 0;                         /* LBA Low (low) */
    cdb[9]  = 0;                         /* LBA Mid (high) */
    cdb[10] = SMART_LBA_MID;             /* LBA Mid (low) = 4Fh */
    cdb[11] = 0;                         /* LBA High (high) */
    cdb[12] = SMART_LBA_HIGH;            /* LBA High (low) = C2h */
    cdb[13] = 0;                         /* Device register */
    cdb[14] = ATA_SMART_CMD;             /* Command register = B0h */

    uint8_t sense_buf[32];
    memset(sense_buf, 0, sizeof(sense_buf));

    struct sg_io_hdr io_hdr;
    memset(&io_hdr, 0, sizeof(io_hdr));
    io_hdr.interface_id    = 'S';
    io_hdr.cmd_len         = sizeof(cdb);
    io_hdr.mx_sb_len       = sizeof(sense_buf);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len       = sizeof(struct smart_data_sector);
    io_hdr.dxferp          = out_data;
    io_hdr.cmdp            = cdb;
    io_hdr.sbp             = sense_buf;
    io_hdr.timeout         = 5000; /* 5 секунд */

    int ret = ioctl(fd, SG_IO, &io_hdr);
    close(fd);

    if (ret < 0) {
        perror("Помилка виклику ioctl(SG_IO)");
        return -1;
    }

    if ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) {
        fprintf(stderr, "Помилка передачі SCSI/ATA: status=0x%02x, host_status=0x%02x\n",
                io_hdr.status, io_hdr.host_status);
        return -1;
    }

    /* Перевірка контрольної суми 512-байтового сектору */
    uint8_t sum = 0;
    const uint8_t *raw_ptr = (const uint8_t *)out_data;
    for (size_t i = 0; i < 512; ++i) {
        sum += raw_ptr[i];
    }
    if (sum != 0) {
        fprintf(stderr, "Попередження: контрольна сума сектору SMART не зійшлася (сума = 0x%02x)\n", sum);
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/sdX\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct smart_data_sector data;
    memset(&data, 0, sizeof(data));

    if (read_sata_smart(argv[1], &data) != 0) {
        return EXIT_FAILURE;
    }

    printf("=== SMART Таблиця накопичувача %s (Версія 0x%04x) ===\n", argv[1], data.version);
    printf("%-4s %-28s %-7s %-7s %-16s %-8s\n",
           "ID", "Назва атрибута", "Value", "Worst", "RAW Value", "Тип");
    printf("----------------------------------------------------------------------------\n");

    for (int i = 0; i < 30; ++i) {
        const struct smart_attribute *attr = &data.attributes[i];
        if (attr->id == 0) continue;

        const char *name = "Unknown Attribute";
        switch (attr->id) {
            case 0x01: name = "Raw Read Error Rate"; break;
            case 0x05: name = "Reallocated Sectors Count"; break;
            case 0x09: name = "Power-On Hours"; break;
            case 0x0A: name = "Spin Retry Count"; break;
            case 0x0C: name = "Power Cycle Count"; break;
            case 0xB8: name = "End-to-End Error"; break;
            case 0xC5: name = "Current Pending Sector"; break;
            case 0xC6: name = "Offline Uncorrectable"; break;
            case 0xC7: name = "UDMA CRC Error Count"; break;
            case 0xE7: name = "SSD Life Left / Wear"; break;
            case 0xE8: name = "Available Reserved Space"; break;
            case 0xF1: name = "Total LBAs Written"; break;
            case 0xF2: name = "Total LBAs Read"; break;
        }

        const char *type_str = (attr->flags & 0x0001) ? "Pre-fail" : "Old-age";
        printf("0x%02X %-28s %-7u %-7u %-16lu %-8s\n",
               attr->id, name, attr->current_value, attr->worst_value,
               (unsigned long)unpack_raw(attr->raw_bytes), type_str);
    }

    return EXIT_SUCCESS;
}
