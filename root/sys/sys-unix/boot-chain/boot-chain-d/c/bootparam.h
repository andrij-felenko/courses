/*
 * Заголовок протоколу завантаження Linux/x86 — той самий контракт, що його
 * ядро тримає у arch/x86/include/uapi/asm/bootparam.h.
 *
 * Завантажувач зобов'язаний: вичитати заголовок з образу vmlinuz, перевірити
 * магічне число й версію протоколу, а тоді заповнити «свої» поля — адресу
 * initramfs, його розмір, адресу рядка cmdline і власний ідентифікатор.
 */
#ifndef BOOTPARAM_H
#define BOOTPARAM_H

#include <stddef.h>
#include <stdint.h>

/* Зсув setup_header усередині «нульової сторінки» (struct boot_params). */
#define SETUP_HEADER_OFFSET     0x01F1
/* Магічне число "HdrS" — підтвердження, що образ говорить цим протоколом. */
#define SETUP_HEADER_MAGIC      0x53726448u
/* Сигнатура завантажувального сектора в останніх двох байтах перших 512. */
#define SETUP_BOOT_FLAG         0xAA55u
/* З версії 2.02 є cmd_line_ptr; нижче за неї рядок передавали інакше. */
#define SETUP_PROTO_MIN         0x0202u
/* Поле initrd_addr_max з'явилося у версії 2.03. */
#define SETUP_PROTO_ADDR_MAX    0x0203u
/* Стеля для initramfs, коли протокол ще не мав initrd_addr_max. */
#define INITRD_ADDR_MAX_DEFAULT 0x37FFFFFFu

/* type_of_loader: 0xFF — завантажувач без зареєстрованого в ядрі номера. */
#define LOADER_TYPE_UNKNOWN     0xFFu
/* loadflags */
#define LOADFLAG_LOADED_HIGH    0x01u  /* захищений код ядра лежить вище 1 МіБ */
#define LOADFLAG_QUIET          0x20u  /* ядро мовчить на ранньому етапі */
#define LOADFLAG_CAN_USE_HEAP   0x80u  /* завантажувач виставив heap_end_ptr */

struct setup_header {
    uint8_t  setup_sects;        /* Кількість секторів коду налаштування */
    uint16_t root_flags;         /* Прапорці монтування кореня (1 = read-only) */
    uint32_t syssize;            /* Розмір захищеного коду в 16-байтних параграфах */
    uint16_t ram_size;           /* Застаріле поле розміру пам'яті */
    uint16_t vid_mode;           /* Відеорежим консолі */
    uint16_t root_dev;           /* Застарілий номер кореневого пристрою */
    uint16_t boot_flag;          /* Сигнатура 0xAA55 */
    uint16_t jump;               /* Інструкція короткого переходу (jmp) */
    uint32_t header;             /* Магічне число "HdrS" */
    uint16_t version;            /* Версія протоколу, 0x020f = 2.15 */
    uint32_t realmode_swtch;     /* Вказівник на функцію перемикання режимів */
    uint16_t start_sys_seg;      /* Сегмент старту системи */
    uint16_t kernel_version;     /* Зсув рядка версії ядра в коді налаштування */
    uint8_t  type_of_loader;     /* Ідентифікатор завантажувача */
    uint8_t  loadflags;          /* Прапорці завантаження */
    uint16_t setup_move_size;    /* Розмір переміщення коду налаштування */
    uint32_t code32_start;       /* Точка входу в захищений режим (0x100000) */
    uint32_t ramdisk_image;      /* Фізична адреса initramfs у пам'яті */
    uint32_t ramdisk_size;       /* Розмір initramfs у байтах */
    uint32_t bootsect_kludge;    /* Застаріле */
    uint16_t heap_end_ptr;       /* Зсув кінця купи завантажувача */
    uint8_t  ext_loader_ver;     /* Розширений номер версії завантажувача */
    uint8_t  ext_loader_type;    /* Розширений тип завантажувача */
    uint32_t cmd_line_ptr;       /* Фізична адреса рядка параметрів ядра */
    uint32_t initrd_addr_max;    /* Найвища допустима адреса кінця initramfs */
} __attribute__((packed));

enum bp_status {
    BP_OK = 0,
    BP_ERR_OPEN,        /* файл не відкрився */
    BP_ERR_READ,        /* збій позиціювання або читання */
    BP_ERR_SHORT,       /* образ коротший за заголовок */
    BP_ERR_MAGIC,       /* немає "HdrS" — це не bzImage */
    BP_ERR_BOOT_FLAG,   /* немає 0xAA55 */
    BP_ERR_OLD_PROTO,   /* протокол старіший за 2.02 */
    BP_ERR_NO_VERSION,  /* рядка версії ядра в образі немає */
    BP_ERR_RANGE        /* план розміщення не влазить у дозволені межі */
};

/* Куди завантажувач збирається покласти initramfs і рядок параметрів. */
struct bp_load_plan {
    uint32_t initrd_phys;   /* фізична адреса початку initramfs (0 — немає) */
    uint32_t initrd_size;   /* розмір initramfs у байтах */
    uint32_t cmdline_phys;  /* фізична адреса рядка cmdline */
};

const char   *bp_strerror(enum bp_status st);
enum bp_status bp_read_header(const char *path, struct setup_header *out);
enum bp_status bp_read_kernel_version(const char *path, const struct setup_header *h,
                                      char *buf, size_t buf_size);
enum bp_status bp_fill_loader_fields(struct setup_header *h, const struct bp_load_plan *plan);

size_t   bp_setup_size(const struct setup_header *h);      /* байтів коду налаштування */
uint64_t bp_protected_size(const struct setup_header *h);  /* байтів захищеного коду */
uint32_t bp_initrd_addr_max(const struct setup_header *h);

void bp_print_header(const struct setup_header *h, const char *path, const char *kver);

#endif /* BOOTPARAM_H */
