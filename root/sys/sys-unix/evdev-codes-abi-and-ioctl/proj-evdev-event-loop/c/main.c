/* C Implementation: epoll + evdev reader + uinput injector */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/epoll.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <linux/uinput.h>

#define MAX_EVENTS 10
#define EVENT_BUFFER_SIZE 32

static int setup_uinput_device(void) {
    int ufd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (ufd < 0) {
        perror("Failed to open /dev/uinput");
        return -1;
    }

    if (ioctl(ufd, UI_SET_EVBIT, EV_KEY) < 0 ||
        ioctl(ufd, UI_SET_KEYBIT, KEY_A) < 0 ||
        ioctl(ufd, UI_SET_KEYBIT, KEY_B) < 0 ||
        ioctl(ufd, UI_SET_EVBIT, EV_SYN) < 0) {
        perror("Failed to set uinput capabilities");
        close(ufd);
        return -1;
    }

    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234;
    usetup.id.product = 0x5678;
    snprintf(usetup.name, UINPUT_MAX_NAME_SIZE, "Virtual Test Keyboard");

    if (ioctl(ufd, UI_DEV_SETUP, &usetup) < 0 ||
        ioctl(ufd, UI_DEV_CREATE) < 0) {
        perror("Failed to create uinput device");
        close(ufd);
        return -1;
    }

    return ufd;
}

static void process_input_events(int ev_fd, int ufd) {
    struct input_event ev[EVENT_BUFFER_SIZE];
    ssize_t bytes_read = read(ev_fd, ev, sizeof(ev));

    if (bytes_read < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Read error on evdev node");
        }
        return;
    }

    size_t count = (size_t)bytes_read / sizeof(struct input_event);
    for (size_t i = 0; i < count; ++i) {
        if (ev[i].type == EV_SYN && ev[i].code == SYN_DROPPED) {
            fprintf(stderr, "Warning: Buffer overflow, SYN_DROPPED received!\n");
            /* У реальному коді тут виконується EVIOCGKEY для синхронізації стану */
            continue;
        }

        printf("Event: type=%u, code=%u, value=%d\n", ev[i].type, ev[i].code, ev[i].value);

        /* Якщо натиснуто KEY_A — модифікуємо і відправляємо KEY_B у uinput */
        if (ev[i].type == EV_KEY && ev[i].code == KEY_A) {
            struct input_event mod_ev = ev[i];
            mod_ev.code = KEY_B;
            if (write(ufd, &mod_ev, sizeof(mod_ev)) < 0) {
                perror("Failed to write to uinput");
            }
        } else {
            if (write(ufd, &ev[i], sizeof(ev[i])) < 0) {
                perror("Failed to passthrough event to uinput");
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s /dev/input/eventN\n", argv[0]);
        return EXIT_FAILURE;
    }

    int ev_fd = open(argv[1], O_RDONLY | O_NONBLOCK);
    if (ev_fd < 0) {
        perror("Failed to open input device");
        return EXIT_FAILURE;
    }

    int ufd = setup_uinput_device();
    if (ufd < 0) {
        close(ev_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("Failed to create epoll instance");
        close(ufd);
        close(ev_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev_spec;
    memset(&ev_spec, 0, sizeof(ev_spec));
    ev_spec.events = EPOLLIN;
    ev_spec.data.fd = ev_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, ev_fd, &ev_spec) < 0) {
        perror("Failed to add ev_fd to epoll");
        close(epoll_fd);
        ioctl(ufd, UI_DEV_DESTROY);
        close(ufd);
        close(ev_fd);
        return EXIT_FAILURE;
    }

    printf("Listening for input events on %s...\n", argv[1]);
    struct epoll_event events[MAX_EVENTS];

    for (int loop = 0; loop < 20; ++loop) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 2000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait failed");
            break;
        }

        for (int n = 0; n < nfds; ++n) {
            if (events[n].data.fd == ev_fd) {
                process_input_events(ev_fd, ufd);
            }
        }
    }

    /* Clean exit */
    close(epoll_fd);
    ioctl(ufd, UI_DEV_DESTROY);
    close(ufd);
    close(ev_fd);
    return EXIT_SUCCESS;
}
