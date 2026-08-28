#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/epoll.h>
#include <linux/vt.h>
#include <linux/kd.h>
#include <xf86drm.h>

#define VT_RELEASE_SIGNAL SIGUSR1
#define VT_ACQUIRE_SIGNAL SIGUSR2

struct vt_session {
    int tty_fd;
    int drm_fd;
    int sfd;
    int epoll_fd;
    long orig_kb_mode;
    struct vt_mode orig_vt_mode;
    bool is_active;
    bool is_running;
};

static int vt_session_init(struct vt_session *s, const char *tty_path, const char *drm_path) {
    memset(s, 0, sizeof(*s));
    s->tty_fd = -1;
    s->drm_fd = -1;
    s->sfd = -1;
    s->epoll_fd = -1;
    s->is_active = true;
    s->is_running = true;

    s->tty_fd = open(tty_path, O_RDWR | O_NOCTTY | O_CLOEXEC);
    if (s->tty_fd < 0) {
        perror("Не вдалося відкрити TTY-консоль");
        return -1;
    }

    /* Зберігаємо поточний режим клавіатури для відновлення при виході */
    if (ioctl(s->tty_fd, KDGKBMODE, &s->orig_kb_mode) < 0) {
        perror("ioctl(KDGKBMODE) зазнав невдачі");
        close(s->tty_fd);
        return -1;
    }

    /* Зберігаємо початковий режим VT */
    if (ioctl(s->tty_fd, VT_GETMODE, &s->orig_vt_mode) < 0) {
        perror("ioctl(VT_GETMODE) зазнав невдачі");
        close(s->tty_fd);
        return -1;
    }

    /* Відкриваємо вузол DRM первинного відеоадаптера */
    s->drm_fd = open(drm_path, O_RDWR | O_CLOEXEC);
    if (s->drm_fd < 0) {
        perror("Не вдалося відкрити вузол DRM");
        close(s->tty_fd);
        return -1;
    }

    /* Блокуємо сигнали перемикання для обробки через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, VT_RELEASE_SIGNAL);
    sigaddset(&mask, VT_ACQUIRE_SIGNAL);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) {
        perror("sigprocmask зазнав невдачі");
        close(s->drm_fd);
        close(s->tty_fd);
        return -1;
    }

    s->sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (s->sfd < 0) {
        perror("signalfd зазнав невдачі");
        close(s->drm_fd);
        close(s->tty_fd);
        return -1;
    }

    s->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (s->epoll_fd < 0) {
        perror("epoll_create1 зазнав невдачі");
        close(s->sfd);
        close(s->drm_fd);
        close(s->tty_fd);
        return -1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = s->sfd;
    if (epoll_ctl(s->epoll_fd, EPOLL_CTL_ADD, s->sfd, &ev) < 0) {
        perror("epoll_ctl(ADD signalfd) зазнав невдачі");
        close(s->epoll_fd);
        close(s->sfd);
        close(s->drm_fd);
        close(s->tty_fd);
        return -1;
    }

    /* Вимикаємо клавіатуру у TTY (K_OFF), щоб символи не потрапляли в оболонку */
    if (ioctl(s->tty_fd, KDSKBMODE, K_OFF) < 0) {
        perror("ioctl(KDSKBMODE, K_OFF) зазнав невдачі");
        /* Продовжуємо, але з попередженням */
    }

    /* Переводимо консоль у режим узгодженого перемикання */
    struct vt_mode vtm = {
        .mode = VT_PROCESS,
        .waitv = 0,
        .relsig = VT_RELEASE_SIGNAL,
        .acqsig = VT_ACQUIRE_SIGNAL,
        .frsig = 0
    };

    if (ioctl(s->tty_fd, VT_SETMODE, &vtm) < 0) {
        perror("ioctl(VT_SETMODE, VT_PROCESS) зазнав невдачі");
        /* Відновлюємо клавіатуру перед виходом */
        ioctl(s->tty_fd, KDSKBMODE, s->orig_kb_mode);
        close(s->epoll_fd);
        close(s->sfd);
        close(s->drm_fd);
        close(s->tty_fd);
        return -1;
    }

    printf("[VT Session] Ініціалізація успішна: VT_PROCESS активний\n");
    return 0;
}

static void vt_session_handle_release(struct vt_session *s) {
    printf("[VT Session] Отримано relsig (SIGUSR1): віддаємо консоль ядру\n");
    s->is_active = false;

    /* 1. Віддаємо статус DRM-майстра */
    if (drmDropMaster(s->drm_fd) < 0) {
        perror("drmDropMaster зазнав невдачі");
    }

    /* 2. Підтверджуємо ядру готовність до зміни консолі */
    if (ioctl(s->tty_fd, VT_RELDISP, 1) < 0) {
        perror("ioctl(VT_RELDISP, 1) зазнав невдачі");
    }
}

static void vt_session_handle_acquire(struct vt_session *s) {
    printf("[VT Session] Отримано acqsig (SIGUSR2): повертаємося на графічну консоль\n");

    /* 1. Повертаємо статус DRM-майстра */
    if (drmSetMaster(s->drm_fd) < 0) {
        perror("drmSetMaster зазнав невдачі");
    }

    /* 2. Підтверджуємо ядру успішне захоплення ресурсів */
    if (ioctl(s->tty_fd, VT_RELDISP, VT_ACKACQ) < 0) {
        perror("ioctl(VT_RELDISP, VT_ACKACQ) зазнав невдачі");
    }

    s->is_active = true;
}

static void vt_session_cleanup(struct vt_session *s) {
    printf("[VT Session] Відновлення початкового стану термінала...\n");

    /* Відновлюємо початковий режим VT (зазвичай VT_AUTO) */
    if (s->tty_fd >= 0) {
        ioctl(s->tty_fd, VT_SETMODE, &s->orig_vt_mode);
        ioctl(s->tty_fd, KDSKBMODE, s->orig_kb_mode);
        close(s->tty_fd);
    }

    if (s->drm_fd >= 0) close(s->drm_fd);
    if (s->sfd >= 0) close(s->sfd);
    if (s->epoll_fd >= 0) close(s->epoll_fd);
}

int main(int argc, char **argv) {
    const char *tty_path = (argc > 1) ? argv[1] : "/dev/tty";
    const char *drm_path = (argc > 2) ? argv[2] : "/dev/dri/card0";

    struct vt_session session;
    if (vt_session_init(&session, tty_path, drm_path) < 0) {
        fprintf(stderr, "Помилка запуску сесійного менеджера VT\n");
        return 1;
    }

    struct epoll_event events[4];
    while (session.is_running) {
        int nfds = epoll_wait(session.epoll_fd, events, 4, 1000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait зазнав помилки");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == session.sfd) {
                struct signalfd_siginfo fdsi;
                ssize_t bytes = read(session.sfd, &fdsi, sizeof(fdsi));
                if (bytes != sizeof(fdsi)) continue;

                if (fdsi.ssi_signo == VT_RELEASE_SIGNAL) {
                    vt_session_handle_release(&session);
                } else if (fdsi.ssi_signo == VT_ACQUIRE_SIGNAL) {
                    vt_session_handle_acquire(&session);
                } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM) {
                    printf("[VT Session] Отримано сигнал зупинки, виходимо...\n");
                    session.is_running = false;
                }
            }
        }

        if (session.is_active) {
            /* Графічний сервер виконує рендеринг кадру */
        }
    }

    vt_session_cleanup(&session);
    return 0;
}
