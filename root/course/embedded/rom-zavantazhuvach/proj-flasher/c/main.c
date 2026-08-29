#include "bootloader.h"
#include "serial.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Регістр розміру Flash у KiB лежить у різних родин за різними адресами,
   тому таблиця зв'язує PID із конкретною адресою й людською назвою. */
typedef struct {
    uint16_t pid;
    const char *name;
    uint32_t flash_size_reg;
} chip_info;

static const chip_info KNOWN_CHIPS[] = {
    {0x410, "STM32F10x medium-density", 0x1FFFF7E0u},
    {0x412, "STM32F10x low-density",    0x1FFFF7E0u},
    {0x414, "STM32F10x high-density",   0x1FFFF7E0u},
    {0x413, "STM32F405/407/415/417",    0x1FFF7A22u},
    {0x419, "STM32F42x/43x",            0x1FFF7A22u},
    {0x431, "STM32F411",                0x1FFF7A22u},
    {0x440, "STM32F05x",                0x1FFFF7CCu},
    {0x444, "STM32F03x",                0x1FFFF7CCu},
    {0x415, "STM32L47x/48x",            0x1FFF75E0u},
    {0x460, "STM32G07x/08x",            0x1FFF75E0u},
    {0x466, "STM32G03x/04x",            0x1FFF75E0u},
    {0x468, "STM32G43x/44x",            0x1FFF75E0u},
};

static const chip_info *find_chip(uint16_t pid)
{
    for (size_t i = 0; i < sizeof KNOWN_CHIPS / sizeof KNOWN_CHIPS[0]; ++i) {
        if (KNOWN_CHIPS[i].pid == pid) {
            return &KNOWN_CHIPS[i];
        }
    }
    return NULL;
}

typedef struct {
    uint8_t *data;
    size_t size;
} image;

static uint32_t read_u32_le(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* Читає .bin і доповнює хвіст 0xFF до межі подвійного слова: на кристалах
   з ECC у Flash невирівняний запис просто не пройде. */
static bool image_load(const char *path, image *img)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL) {
        fprintf(stderr, "не відкривається %s: %s\n", path, strerror(errno));
        return false;
    }

    if (fseek(f, 0, SEEK_END) != 0) {
        fprintf(stderr, "%s: файл не позиціонується\n", path);
        fclose(f);
        return false;
    }
    long raw = ftell(f);
    rewind(f);

    if (raw <= 0) {
        fprintf(stderr, "%s: порожній образ\n", path);
        fclose(f);
        return false;
    }

    size_t size = (size_t)raw;
    size_t padded = (size + 7u) & ~(size_t)7u;

    uint8_t *buf = malloc(padded);
    if (buf == NULL) {
        fprintf(stderr, "бракує пам'яті на %zu байтів\n", padded);
        fclose(f);
        return false;
    }

    if (fread(buf, 1, size, f) != size) {
        fprintf(stderr, "%s: обірване читання\n", path);
        free(buf);
        fclose(f);
        return false;
    }
    fclose(f);

    memset(buf + size, 0xFF, padded - size);
    if (padded != size) {
        printf("образ доповнено з %zu до %zu байтів (вирівнювання під ECC)\n", size, padded);
    }

    img->data = buf;
    img->size = padded;
    return true;
}

/* Дешева перевірка, що нам підсунули саме прошивку, а не .elf чи чужий файл:
   слово 0 — початковий стек у SRAM, слово 1 — Reset_Handler у Flash з бітом Thumb. */
static bool image_looks_like_firmware(const image *img)
{
    if (img->size < 8) {
        fprintf(stderr, "образ коротший за таблицю векторів\n");
        return false;
    }

    uint32_t stack_top = read_u32_le(img->data);
    uint32_t reset_vector = read_u32_le(img->data + 4);

    if ((stack_top & 0xFFF00000u) != 0x20000000u) {
        fprintf(stderr, "слово 0 = 0x%08X — це не вершина стека в SRAM\n", stack_top);
        return false;
    }
    if ((reset_vector & 1u) == 0 || reset_vector < BL_FLASH_BASE ||
        reset_vector >= BL_FLASH_BASE + img->size) {
        fprintf(stderr, "слово 1 = 0x%08X — Reset_Handler поза образом\n", reset_vector);
        return false;
    }
    return true;
}

static bl_status read_flash_size_kib(const serial_port *port, uint32_t reg, uint16_t *kib)
{
    uint8_t raw[2];
    bl_status st = bl_read_block(port, reg, raw, sizeof raw);
    if (st != BL_OK) {
        return st;
    }
    *kib = (uint16_t)((uint16_t)raw[0] | ((uint16_t)raw[1] << 8));
    return BL_OK;
}

static bool write_image(const serial_port *port, const image *img)
{
    for (size_t offset = 0; offset < img->size; offset += BL_MAX_BLOCK) {
        size_t chunk = img->size - offset;
        if (chunk > BL_MAX_BLOCK) {
            chunk = BL_MAX_BLOCK;
        }

        uint32_t addr = (uint32_t)(BL_FLASH_BASE + offset);
        bl_status st = bl_write_block(port, addr, img->data + offset, chunk);
        if (st != BL_OK) {
            fprintf(stderr, "\nзапис на 0x%08X зірвався: %s\n", addr, bl_status_text(st));
            return false;
        }

        printf("\r  запис 0x%08X  %3zu%%", addr, (offset + chunk) * 100u / img->size);
        fflush(stdout);
    }
    printf("\n");
    return true;
}

static bool verify_image(const serial_port *port, const image *img)
{
    uint8_t back[BL_MAX_BLOCK];

    for (size_t offset = 0; offset < img->size; offset += BL_MAX_BLOCK) {
        size_t chunk = img->size - offset;
        if (chunk > BL_MAX_BLOCK) {
            chunk = BL_MAX_BLOCK;
        }

        uint32_t addr = (uint32_t)(BL_FLASH_BASE + offset);
        bl_status st = bl_read_block(port, addr, back, chunk);
        if (st != BL_OK) {
            fprintf(stderr, "\nчитання 0x%08X зірвалося: %s\n", addr, bl_status_text(st));
            return false;
        }

        if (memcmp(back, img->data + offset, chunk) != 0) {
            for (size_t i = 0; i < chunk; ++i) {
                if (back[i] != img->data[offset + i]) {
                    fprintf(stderr, "\nрозбіжність на 0x%08X: у чипі 0x%02X, в образі 0x%02X\n",
                            (uint32_t)(addr + i), back[i], img->data[offset + i]);
                    break;
                }
            }
            return false;
        }

        printf("\r  звірка 0x%08X  %3zu%%", addr, (offset + chunk) * 100u / img->size);
        fflush(stdout);
    }
    printf("\n");
    return true;
}

static int flash(const char *port_path, const image *img)
{
    serial_port port;
    if (!serial_open(&port, port_path)) {
        fprintf(stderr, "порт %s: %s\n", port_path, strerror(errno));
        return 1;
    }

    int rc = 1;

    if (!serial_enter_bootloader(&port)) {
        fprintf(stderr, "DTR/RTS не керуються: %s\n", strerror(errno));
        goto out;
    }

    bl_status st = bl_sync(&port);
    if (st != BL_OK) {
        fprintf(stderr, "синхронізація: %s (перевір BOOT0 і перехідник)\n", bl_status_text(st));
        goto out;
    }

    uint8_t version = 0;
    uint8_t options[2] = {0, 0};
    st = bl_get_version(&port, &version, options);
    if (st != BL_OK) {
        fprintf(stderr, "Get Version: %s\n", bl_status_text(st));
        goto out;
    }
    printf("завантажувач версії %u.%u\n", version >> 4, version & 0x0Fu);

    uint16_t pid = 0;
    st = bl_get_id(&port, &pid);
    if (st != BL_OK) {
        fprintf(stderr, "Get ID: %s\n", bl_status_text(st));
        goto out;
    }

    const chip_info *chip = find_chip(pid);
    if (chip == NULL) {
        fprintf(stderr, "PID 0x%03X у таблиці відсутній — адреса регістра розміру невідома\n", pid);
        goto out;
    }
    printf("кристал 0x%03X — %s\n", pid, chip->name);

    /* Пробне читання водночас перевіряє захист: під RDP level 1 чип відповість NACK */
    uint16_t flash_kib = 0;
    st = read_flash_size_kib(&port, chip->flash_size_reg, &flash_kib);
    bool erased_by_unprotect = false;

    if (st == BL_ERR_NACK) {
        printf("читання заблоковано — RDP level 1; знімаємо захист, Flash буде стерто\n");
        st = bl_readout_unprotect(&port);
        if (st != BL_OK) {
            fprintf(stderr, "Readout Unprotect: %s\n", bl_status_text(st));
            goto out;
        }
        /* Чип сам перезавантажився — заходимо в System Memory ще раз */
        if (!serial_enter_bootloader(&port)) {
            fprintf(stderr, "повторне скидання: %s\n", strerror(errno));
            goto out;
        }
        st = bl_sync(&port);
        if (st != BL_OK) {
            fprintf(stderr, "повторна синхронізація: %s\n", bl_status_text(st));
            goto out;
        }
        st = read_flash_size_kib(&port, chip->flash_size_reg, &flash_kib);
        erased_by_unprotect = true;
    }

    if (st != BL_OK) {
        fprintf(stderr, "розмір Flash не читається: %s\n", bl_status_text(st));
        goto out;
    }

    if (flash_kib == 0 || flash_kib == 0xFFFF) {
        fprintf(stderr, "регістр розміру віддав 0x%04X — довіряти йому не можна\n", flash_kib);
        goto out;
    }
    printf("Flash %u KiB, образ %zu байтів\n", flash_kib, img->size);

    if (img->size > (size_t)flash_kib * 1024u) {
        fprintf(stderr, "образ не влазить у Flash\n");
        goto out;
    }

    if (erased_by_unprotect) {
        printf("стирання вже зроблено зняттям захисту\n");
    } else {
        printf("масове стирання (до 30 с)...\n");
        st = bl_mass_erase(&port);
        if (st != BL_OK) {
            fprintf(stderr, "Extended Erase: %s\n", bl_status_text(st));
            goto out;
        }
    }

    if (!write_image(&port, img)) {
        goto out;
    }
    if (!verify_image(&port, img)) {
        goto out;
    }

    st = bl_go(&port, BL_FLASH_BASE);
    if (st != BL_OK) {
        fprintf(stderr, "Go: %s (прошивка записана, потрібне ручне скидання)\n", bl_status_text(st));
        goto out;
    }

    printf("готово: керування передано на 0x%08X\n", BL_FLASH_BASE);
    rc = 0;

out:
    serial_close(&port);
    return rc;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "вжиток: %s <порт> <прошивка.bin>\n", argv[0]);
        return 2;
    }

    image img = {NULL, 0};
    if (!image_load(argv[2], &img)) {
        return 1;
    }
    if (!image_looks_like_firmware(&img)) {
        free(img.data);
        return 1;
    }

    int rc = flash(argv[1], &img);
    free(img.data);
    return rc;
}
