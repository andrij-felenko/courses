// xsk_app.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <poll.h>
#include <sys/mman.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <xdp/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE 2048
#define BATCH_SIZE 64

static volatile int global_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    global_running = 0;
}

struct xsk_app {
    struct xsk_umem *umem;
    struct xsk_ring_prod fill;
    struct xsk_ring_cons comp;
    struct xsk_ring_cons rx;
    struct xsk_ring_prod tx;
    struct xsk_socket *xsk;
    void *buffer;
};

static int init_xsk_app(struct xsk_app *app, const char *ifname, uint32_t queue_id) {
    size_t umem_size = NUM_FRAMES * FRAME_SIZE;
    if (posix_memalign(&app->buffer, getpagesize(), umem_size) != 0) {
        perror("posix_memalign failed");
        return -1;
    }

    struct xsk_umem_config umem_cfg = {
        .fill_size = NUM_FRAMES,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = XSK_UMEM__DEFAULT_FRAME_HEADROOM,
        .flags = 0
    };

    if (xsk_umem__create(&app->umem, app->buffer, umem_size,
                         &app->fill, &app->comp, &umem_cfg) < 0) {
        perror("xsk_umem__create failed");
        free(app->buffer);
        return -1;
    }

    struct xsk_socket_config xsk_cfg = {
        .rx_size = NUM_FRAMES,
        .tx_size = NUM_FRAMES,
        .libbpf_flags = XSK_LIBBPF_FLAGS__INHIBIT_PROG_LOAD,
        .xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST,
        .bind_flags = XDP_ZEROCOPY | XDP_USE_NEED_WAKEUP
    };

    if (xsk_socket__create(&app->xsk, ifname, queue_id,
                           app->umem, &app->rx, &app->tx, &xsk_cfg) < 0) {
        // Якщо Zero-Copy не підтримується, спробуємо XDP_COPY
        xsk_cfg.bind_flags = XDP_COPY | XDP_USE_NEED_WAKEUP;
        if (xsk_socket__create(&app->xsk, ifname, queue_id,
                               app->umem, &app->rx, &app->tx, &xsk_cfg) < 0) {
            perror("xsk_socket__create failed");
            xsk_umem__delete(app->umem);
            free(app->buffer);
            return -1;
        }
    }

    // Первинне поповнення Fill Ring вільними адресами
    uint32_t idx = 0;
    if (xsk_ring_prod__reserve(&app->fill, NUM_FRAMES / 2, &idx) == NUM_FRAMES / 2) {
        for (int i = 0; i < NUM_FRAMES / 2; i++) {
            *xsk_ring_prod__fill_addr(&app->fill, idx + i) = i * FRAME_SIZE;
        }
        xsk_ring_prod__submit(&app->fill, NUM_FRAMES / 2);
    }

    return 0;
}

static void process_packets(struct xsk_app *app) {
    uint32_t rx_idx = 0, tx_idx = 0, comp_idx = 0, fill_idx = 0;
    
    uint32_t rcvd = xsk_ring_cons__peek(&app->rx, BATCH_SIZE, &rx_idx);
    if (!rcvd) {
        if (xsk_ring_prod__needs_wakeup(&app->fill)) {
            struct pollfd fds = { .fd = xsk_socket__fd(app->xsk), .events = POLLIN };
            poll(&fds, 1, 10);
        }
        return;
    }

    // Резервуємо місця в TX кільці для ехо-відповіді
    uint32_t tx_reserved = xsk_ring_prod__reserve(&app->tx, rcvd, &tx_idx);
    while (tx_reserved < rcvd) {
        if (xsk_ring_prod__needs_wakeup(&app->tx)) {
            xsk_socket__wakeup(app->xsk, XDP_WAKEUP_TX);
        }
        tx_reserved = xsk_ring_prod__reserve(&app->tx, rcvd, &tx_idx);
    }

    for (uint32_t i = 0; i < rcvd; i++) {
        const struct xdp_desc *desc = xsk_ring_cons__rx_desc(&app->rx, rx_idx + i);
        uint64_t addr = desc->addr;
        uint32_t len = desc->len;

        // Отримуємо вказівник на кадр
        uint8_t *pkt = (uint8_t *)xsk_umem__get_data(app->buffer, addr);

        // Переставляємо MAC-адреси місцями (L2 Swap Echo)
        uint8_t tmp_mac[6];
        memcpy(tmp_mac, pkt, 6);
        memcpy(pkt, pkt + 6, 6);
        memcpy(pkt + 6, tmp_mac, 6);

        // Вміщуємо в TX кільце
        struct xdp_desc *tx_desc = xsk_ring_prod__tx_desc(&app->tx, tx_idx + i);
        tx_desc->addr = addr;
        tx_desc->len = len;
    }

    xsk_ring_cons__release(&app->rx, rcvd);
    xsk_ring_prod__submit(&app->tx, rcvd);

    // Звільнення повернених кадрів з Completion Ring
    uint32_t completed = xsk_ring_cons__peek(&app->comp, BATCH_SIZE, &comp_idx);
    if (completed > 0) {
        uint32_t fill_res = xsk_ring_prod__reserve(&app->fill, completed, &fill_idx);
        if (fill_res == completed) {
            for (uint32_t i = 0; i < completed; i++) {
                uint64_t freed_addr = *xsk_ring_cons__comp_addr(&app->comp, comp_idx + i);
                *xsk_ring_prod__fill_addr(&app->fill, fill_idx + i) = freed_addr;
            }
            xsk_ring_prod__submit(&app->fill, completed);
        }
        xsk_ring_cons__release(&app->comp, completed);
    }
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s <ifname> <queue_id>\n", argv[0]);
        return 1;
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    struct xsk_app app;
    memset(&app, 0, sizeof(app));

    if (init_xsk_app(&app, argv[1], atoi(argv[2])) < 0) {
        return 1;
    }

    printf("AF_XDP Echo Server running on %s queue %s...\n", argv[1], argv[2]);

    while (global_running) {
        process_packets(&app);
    }

    printf("Shutting down...\n");
    xsk_socket__delete(app.xsk);
    xsk_umem__delete(app.umem);
    free(app.buffer);

    return 0;
}
