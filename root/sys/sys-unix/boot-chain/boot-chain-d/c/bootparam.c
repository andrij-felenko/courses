#include "bootparam.h"

#include <stdio.h>
#include <string.h>

const char *bp_strerror(enum bp_status st)
{
    switch (st) {
    case BP_OK:             return "гаразд";
    case BP_ERR_OPEN:       return "не вдалося відкрити образ";
    case BP_ERR_READ:       return "збій читання образу";
    case BP_ERR_SHORT:      return "образ коротший за setup_header";
    case BP_ERR_MAGIC:      return "немає магічного числа \"HdrS\": це не bzImage";
    case BP_ERR_BOOT_FLAG:  return "немає сигнатури 0xAA55";
    case BP_ERR_OLD_PROTO:  return "протокол завантаження старіший за 2.02";
    case BP_ERR_NO_VERSION: return "в образі немає рядка версії ядра";
    case BP_ERR_RANGE:      return "розміщення не влазить у дозволені межі";
    }
    return "невідома помилка";
}

enum bp_status bp_read_header(const char *path, struct setup_header *out)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL)
        return BP_ERR_OPEN;

    if (fseek(f, SETUP_HEADER_OFFSET, SEEK_SET) != 0) {
        fclose(f);
        return BP_ERR_READ;
    }

    size_t got = fread(out, 1, sizeof(*out), f);
    if (ferror(f)) {
        fclose(f);
        return BP_ERR_READ;
    }
    fclose(f);

    if (got != sizeof(*out))
        return BP_ERR_SHORT;

    /* Три перевірки, які завантажувач мусить зробити ДО стрибка в ядро. */
    if (out->header != SETUP_HEADER_MAGIC)
        return BP_ERR_MAGIC;
    if (out->boot_flag != SETUP_BOOT_FLAG)
        return BP_ERR_BOOT_FLAG;
    if (out->version < SETUP_PROTO_MIN)
        return BP_ERR_OLD_PROTO;

    return BP_OK;
}

/*
 * Рядок версії ядра лежить у коді налаштування; kernel_version — це зсув
 * від початку сегмента налаштування, зменшений на 0x200. У файлі, отже,
 * шукати треба за kernel_version + 0x200.
 */
enum bp_status bp_read_kernel_version(const char *path, const struct setup_header *h,
                                      char *buf, size_t buf_size)
{
    if (buf == NULL || buf_size == 0)
        return BP_ERR_RANGE;
    buf[0] = '\0';

    if (h->kernel_version == 0)
        return BP_ERR_NO_VERSION;

    long offset = (long)h->kernel_version + 0x200;
    if ((size_t)offset >= bp_setup_size(h))
        return BP_ERR_RANGE;

    FILE *f = fopen(path, "rb");
    if (f == NULL)
        return BP_ERR_OPEN;
    if (fseek(f, offset, SEEK_SET) != 0) {
        fclose(f);
        return BP_ERR_READ;
    }

    size_t i = 0;
    int c;
    while (i + 1 < buf_size && (c = fgetc(f)) != EOF && c != '\0') {
        /* Рядок закінчується нулем; сміття за межами ASCII обриваємо. */
        if (c < 0x20 || c > 0x7E)
            break;
        buf[i++] = (char)c;
    }
    buf[i] = '\0';
    fclose(f);

    return (i > 0) ? BP_OK : BP_ERR_NO_VERSION;
}

size_t bp_setup_size(const struct setup_header *h)
{
    /* Нуль у setup_sects історично означає чотири сектори. */
    unsigned sects = (h->setup_sects != 0) ? h->setup_sects : 4u;
    return ((size_t)sects + 1u) * 512u;
}

uint64_t bp_protected_size(const struct setup_header *h)
{
    return (uint64_t)h->syssize * 16u;
}

uint32_t bp_initrd_addr_max(const struct setup_header *h)
{
    if (h->version >= SETUP_PROTO_ADDR_MAX && h->initrd_addr_max != 0)
        return h->initrd_addr_max;
    return INITRD_ADDR_MAX_DEFAULT;
}

enum bp_status bp_fill_loader_fields(struct setup_header *h, const struct bp_load_plan *plan)
{
    if (h->version < SETUP_PROTO_MIN)
        return BP_ERR_OLD_PROTO;

    if (plan->initrd_size != 0) {
        if (plan->initrd_phys == 0)
            return BP_ERR_RANGE;
        uint64_t end = (uint64_t)plan->initrd_phys + plan->initrd_size - 1u;
        if (end > (uint64_t)bp_initrd_addr_max(h))
            return BP_ERR_RANGE;  /* ядро не дотягнеться до образу вище стелі */
    } else if (plan->initrd_phys != 0) {
        return BP_ERR_RANGE;      /* адреса без розміру — помилка виклику */
    }

    if (plan->cmdline_phys == 0)
        return BP_ERR_RANGE;

    h->type_of_loader = LOADER_TYPE_UNKNOWN;
    h->loadflags |= LOADFLAG_LOADED_HIGH;  /* ядро лежить за 0x100000 */
    h->loadflags &= (uint8_t)~LOADFLAG_QUIET;
    h->ramdisk_image = plan->initrd_phys;
    h->ramdisk_size  = plan->initrd_size;
    h->cmd_line_ptr  = plan->cmdline_phys;

    /* Купа коду налаштування: кінець задають відносно сегмента + 0x200. */
    if (h->loadflags & LOADFLAG_CAN_USE_HEAP)
        h->heap_end_ptr = (uint16_t)(0xE000 - 0x200);

    return BP_OK;
}

void bp_print_header(const struct setup_header *h, const char *path, const char *kver)
{
    printf("Образ: %s\n", path);
    if (kver != NULL && kver[0] != '\0')
        printf("  версія ядра           : %s\n", kver);
    printf("  протокол завантаження : %u.%02u\n",
           (unsigned)(h->version >> 8), (unsigned)(h->version & 0xFF));
    printf("  код налаштування      : %zu байтів (setup_sects=%u)\n",
           bp_setup_size(h), (unsigned)h->setup_sects);
    printf("  захищений код         : %llu байтів\n",
           (unsigned long long)bp_protected_size(h));
    printf("  точка входу 32-біт    : 0x%08X\n", h->code32_start);
    printf("  стеля для initramfs   : 0x%08X\n", bp_initrd_addr_max(h));
    printf("  корінь read-only      : %s\n", (h->root_flags & 1u) ? "так" : "ні");
    printf("  loadflags             : 0x%02X%s%s\n",
           (unsigned)h->loadflags,
           (h->loadflags & LOADFLAG_LOADED_HIGH) ? " LOADED_HIGH" : "",
           (h->loadflags & LOADFLAG_CAN_USE_HEAP) ? " CAN_USE_HEAP" : "");
    printf("  ramdisk_image/size    : 0x%08X / %u\n", h->ramdisk_image, h->ramdisk_size);
    printf("  cmd_line_ptr          : 0x%08X\n", h->cmd_line_ptr);
    printf("  type_of_loader        : 0x%02X\n", (unsigned)h->type_of_loader);
}
