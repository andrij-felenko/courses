/* rack-slot — керування одним слотом тестової стійки з CI-джоби.
 *
 *   rack-slot 3 boot            холодний старт і очікування банера
 *   rack-slot 3 flash fw.hex    прошити образ і дочекатися банера
 *   rack-slot 3 unbrick         реанімація через фабричний ROM-завантажувач
 *
 * Коди виходу: 0 — гаразд, 1 — помилка, 2 — слот зайнятий, 3 — плата мовчить.
 */
#include "rack.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "slot.h"

#define LOCK_WAIT_MS    30000u
#define BOOT_TIMEOUT_MS 5000u
#define BOOT_BANNER     "[BOOT]"

volatile sig_atomic_t rack_stop = 0;

/* 256 КіБ логу всередині — такому місце не на стеку. */
static rack_slot_t g_slot;

static void on_signal(int sig)
{
    (void)sig;
    rack_stop = 1;
}

static void install_handlers(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigemptyset(&sa.sa_mask);
    /* Свідомо без SA_RESTART: select у циклі очікування має ВИЙТИ з помилкою
       EINTR, інакше демон досидить до кінця таймауту, тримаючи слот. */
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    /* CI закриває свій кінець пайпа, щойно джоба скасована. Обірваний stdout
       не має вбивати сесію: слот ще треба знеструмити й відпустити. */
    signal(SIGPIPE, SIG_IGN);
}

static void usage(const char *argv0)
{
    fprintf(stderr, "вжиток: %s <слот 1..99> boot | flash <образ> | unbrick\n", argv0);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        usage(argv[0]);
        return 1;
    }

    char *end = NULL;
    long slot_id = strtol(argv[1], &end, 10);
    if (end == argv[1] || *end != '\0' || slot_id < 1 || slot_id > 99) {
        fprintf(stderr, "номер слота має бути числом 1..99, а не \"%s\"\n", argv[1]);
        return 1;
    }

    const char *cmd = argv[2];
    const char *image = NULL;
    if (strcmp(cmd, "flash") == 0) {
        if (argc < 4) {
            usage(argv[0]);
            return 1;
        }
        image = argv[3];
    } else if (strcmp(cmd, "boot") != 0 && strcmp(cmd, "unbrick") != 0) {
        usage(argv[0]);
        return 1;
    }

    install_handlers();

    rack_status_t st = rack_slot_acquire(&g_slot, (int)slot_id, LOCK_WAIT_MS);
    if (st == RACK_BUSY) {
        fprintf(stderr, "слот %02ld зайнятий іншим прогоном\n", slot_id);
        return 2;
    }
    if (st != RACK_OK) {
        return 1;
    }

    int rc = 1;
    if (rack_slot_open_hw(&g_slot, STDOUT_FILENO) != RACK_OK) {
        goto out;
    }

    if (strcmp(cmd, "boot") == 0) {
        st = rack_slot_boot(&g_slot, BOOT_BANNER, BOOT_TIMEOUT_MS);
    } else if (strcmp(cmd, "flash") == 0) {
        st = rack_slot_flash(&g_slot, image);
        if (st == RACK_OK) {
            /* openocd сам пустив плату командою reset — ловимо той самий банер. */
            st = rack_slot_expect(&g_slot, BOOT_BANNER, BOOT_TIMEOUT_MS);
        }
    } else {
        st = rack_slot_unbrick(&g_slot);
        if (st == RACK_OK) {
            /* Після стирання банера не буде — просто показуємо, що каже плата. */
            st = rack_slot_drain(&g_slot, 500u);
        }
    }

    switch (st) {
    case RACK_OK:
        rc = 0;
        break;
    case RACK_TIMEOUT:
        fprintf(stderr, "слот %02ld: за %u мс не діждався \"%s\"%s\n", slot_id, BOOT_TIMEOUT_MS,
                BOOT_BANNER, g_slot.log_trimmed ? " (лог обрізано з початку)" : "");
        rc = 3;
        break;
    default:
        rc = 1;
        break;
    }

out:
    rack_slot_release(&g_slot);
    if (rack_stop && rc != 0) {
        fprintf(stderr, "слот %02ld: сесію обірвано сигналом\n", slot_id);
    }
    return rc;
}
