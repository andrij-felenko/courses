/*
 * Дві половини ланцюга в одному інструменті:
 *   bootchain header <vmlinuz> [initramfs] — розбір протоколу завантаження
 *   bootchain switch-root <новий-корінь> <init> [аргументи…]
 */
#include "bootparam.h"
#include "switchroot.h"

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static void usage(const char *prog)
{
    fprintf(stderr,
            "Використання:\n"
            "  %s header <vmlinuz> [initramfs]\n"
            "  %s switch-root <новий-корінь> <init> [аргументи…]\n",
            prog, prog);
}

/* Так само, як реальний завантажувач: кладемо initramfs якомога вище під стелю. */
static uint32_t plan_initrd_base(uint32_t addr_max, uint64_t size)
{
    uint64_t top = (uint64_t)addr_max + 1u;
    if (size == 0 || size > top)
        return 0;
    return (uint32_t)((top - size) & ~0xFFFULL);  /* вирівнювання на сторінку */
}

static int cmd_header(const char *kernel_path, const char *initrd_path)
{
    struct setup_header h;
    enum bp_status st = bp_read_header(kernel_path, &h);
    if (st != BP_OK) {
        fprintf(stderr, "%s: %s\n", kernel_path, bp_strerror(st));
        return 1;
    }

    char kver[128];
    if (bp_read_kernel_version(kernel_path, &h, kver, sizeof(kver)) != BP_OK)
        kver[0] = '\0';
    bp_print_header(&h, kernel_path, kver);

    struct bp_load_plan plan = { 0, 0, 0 };
    /* Рядок параметрів кладемо в умовний буфер під самим initramfs. */
    if (initrd_path != NULL) {
        struct stat sb;
        if (stat(initrd_path, &sb) != 0) {
            fprintf(stderr, "%s: не вдалося визначити розмір\n", initrd_path);
            return 1;
        }
        plan.initrd_size = (uint32_t)sb.st_size;
        plan.initrd_phys = plan_initrd_base(bp_initrd_addr_max(&h), (uint64_t)sb.st_size);
        if (plan.initrd_phys == 0) {
            fprintf(stderr, "%s: образ не влазить під стелю initrd_addr_max\n", initrd_path);
            return 1;
        }
        plan.cmdline_phys = plan.initrd_phys - 0x1000u;
    } else {
        plan.cmdline_phys = 0x20000u;
    }

    st = bp_fill_loader_fields(&h, &plan);
    if (st != BP_OK) {
        fprintf(stderr, "заповнення полів завантажувача: %s\n", bp_strerror(st));
        return 1;
    }

    printf("\nПісля заповнення полів завантажувачем:\n");
    bp_print_header(&h, kernel_path, kver);
    return 0;
}

static int cmd_switch_root(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "switch-root: потрібні новий корінь і шлях до init\n");
        return 2;
    }
    if (geteuid() != 0) {
        fprintf(stderr, "switch-root: потрібні права root\n");
        return 1;
    }
    if (getpid() != 1)
        fprintf(stderr, "switch-root: попередження — це не PID 1, "
                        "справжній перехід робить лише перший процес\n");

    /* argv[0] нового образу — його власний шлях, далі аргументи як є. */
    enum sr_status st = sr_switch_root(argv[0], argv[1], &argv[1]);
    fprintf(stderr, "switch-root: %s\n", sr_strerror(st));
    return 1;  /* за успіху сюди вже не повертаються */
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    if (strcmp(argv[1], "header") == 0) {
        if (argc < 3) {
            usage(argv[0]);
            return 2;
        }
        return cmd_header(argv[2], argc > 3 ? argv[3] : NULL);
    }
    if (strcmp(argv[1], "switch-root") == 0)
        return cmd_switch_root(argc - 2, argv + 2);

    usage(argv[0]);
    return 2;
}
