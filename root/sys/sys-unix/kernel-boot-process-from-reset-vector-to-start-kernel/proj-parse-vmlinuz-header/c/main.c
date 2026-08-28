#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SETUP_HEADER_OFFSET 0x01F1
#define HDRS_MAGIC 0x53726448 /* "HdrS" у Little-Endian */

/* Спрощена структура setup_header відповідно до специфікації Linux Boot Protocol */
struct setup_header {
    uint8_t  setup_sects;
    uint16_t root_flags;
    uint32_t syssize;
    uint16_t ram_size;
    uint16_t vid_mode;
    uint16_t root_dev;
    uint16_t boot_flag;
    uint16_t jump;
    uint32_t header;            /* Сигнатура "HdrS" */
    uint16_t version;           /* Версія протоколу (напр. 0x020f) */
    uint32_t realmode_swtch;
    uint16_t start_sys_seg;
    uint16_t kernel_version;
    uint8_t  type_of_loader;
    uint8_t  loadflags;
    uint16_t setup_move_size;
    uint32_t code32_start;      /* 32-бітна адреса входу розпакувальника */
    uint32_t ramdisk_image;     /* Адреса initramfs */
    uint32_t ramdisk_size;      /* Розмір initramfs */
    uint32_t bootsect_kludge;
    uint16_t heap_end_ptr;
    uint8_t  ext_loader_ver;
    uint8_t  ext_loader_type;
    uint32_t cmd_line_ptr;      /* Адреса рядка командного рядка */
    uint32_t initrd_addr_max;   /* Максимально припустима адреса initramfs */
} __attribute__((packed));

static void print_loader_type(uint8_t type) {
    uint8_t high = type >> 4;
    switch (high) {
        case 0x0: printf("LILO / Direct\n"); break;
        case 0x1: printf("Loadlin\n"); break;
        case 0x2: printf("BOOTSECT / SYSLINUX\n"); break;
        case 0x7: printf("GRUB2\n"); break;
        case 0x8: printf("QEMU / KVM Direct Boot\n"); break;
        case 0xE: printf("EFI Boot Stub\n"); break;
        default:  printf("Невідомий завантажувач (0x%02X)\n", type); break;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_vmlinuz>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("Не вдалося відкрити файл ядра");
        return EXIT_FAILURE;
    }

    if (fseek(f, SETUP_HEADER_OFFSET, SEEK_SET) != 0) {
        perror("Помилка позиціонування у файлі");
        fclose(f);
        return EXIT_FAILURE;
    }

    struct setup_header hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) {
        fprintf(stderr, "Помилка: не вдалося зчитати setup_header\n");
        fclose(f);
        return EXIT_FAILURE;
    }
    fclose(f);

    /* Перевірка магічного числа "HdrS" */
    if (hdr.header != HDRS_MAGIC) {
        fprintf(stderr, "ПОМИЛКА: Невалідний заголовок! Сигнатура 0x%08X (очікувалося 'HdrS' 0x%08X)\n",
                hdr.header, HDRS_MAGIC);
        return EXIT_FAILURE;
    }

    uint8_t ver_major = hdr.version >> 8;
    uint8_t ver_minor = hdr.version & 0xFF;

    printf("=== Інспекція заголовка vmlinuz / bzImage ===\n");
    printf("Сигнатура:             HdrS (OK)\n");
    printf("Версія протоколу:      %d.%02d (0x%04X)\n", ver_major, ver_minor, hdr.version);
    printf("Точка входу (code32):  0x%08X\n", hdr.code32_start);
    printf("Максимальна адреса initrd: 0x%08X\n", hdr.initrd_addr_max);
    printf("Прапори завантаження:  0x%02X ", hdr.loadflags);
    if (hdr.loadflags & 0x01) printf("[LOADED_HIGH] ");
    if (hdr.loadflags & 0x80) printf("[CAN_BE_RELOCATED/KASLR] ");
    printf("\n");
    printf("Останній тип завантажувача: ");
    print_loader_type(hdr.type_of_loader);

    return EXIT_SUCCESS;
}
