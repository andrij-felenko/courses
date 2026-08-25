# Реалізація сесійного перемикання VT і керування режимом клавіатури

Будь-який графічний сервер (Wayland-композитор або Xorg), що працює безпосередньо на апаратному відеоадаптері без проміжного віконного менеджера, стикається з двома критичними системними викликами: перехопленням вводу та узгодженням прав на графічний пристрій при перемиканні віртуальних консолей. Якщо запустити графічний цикл на `/dev/tty1` і не змінити режим клавіатури, кожне натискання клавіш потраплятиме одночасно і в чергу подій підсистеми `evdev`, і в буфер лінійної дисципліни `N_TTY`, провокуючи виконання випадкових команд фоновою оболонкою. Крім того, якщо користувач натисне `Ctrl+Alt+F2` для переходу на текстову консоль, ядро спробує перемалювати текстовий кадровий буфер поверх активних графічних регістрів GPU, що призведе до зависання графічного конвеєра.

## Архітектура сесійного узгодження

Коли кілька графічних або текстових сесій ділять один фізичний дисплей і комплект пристроїв введення, ядро Linux не може автоматично здогадатися, як коректно призупинити роботу складного тривимірного конвеєра рендерингу (Vulkan або OpenGL). Якщо ядро просто перемкне покажчик буфера відеопам'яті на текстову консоль, графічний процесор продовжить записувати кадри в пам'ять, спричиняючи візуальне сміття на екрані іншої сесії або навіть апаратний скид (англ. *GPU hang / TDR*).

Щоб забезпечити безпечну передачу дисплея, ядро надає механізм кооперативного перемикання через структуру `struct vt_mode`. Графічний процес повідомляє ядру, що бажає самостійно керувати фазами перемикання (`VT_PROCESS`), і призначає два сигнали реального часу: сигнал відпускання консолі `relsig` (зазвичай `SIGUSR1`) та сигнал повернення консолі `acqsig` (зазвичай `SIGUSR2`).

Алгоритм роботи сесійного менеджера складається з п'яти обов'язкових кроків:
1. **Ізоляція клавіатури:** перемкнути режим клавіатури віртуальної консолі в `K_OFF` (або `K_RAW`), придушивши генерацію символів у черзі лінійної дисципліни TTY. Введення повністю передається бібліотеці обробки подій `libinput` через вузли `/dev/input/event*`.
2. **Реєстрація обробників перемикання:** перевести віртуальну консоль у режим узгодженого перемикання `VT_PROCESS` викликом `ioctl(tty_fd, VT_SETMODE, &vtm)`.
3. **Обробка запиту на звільнення (`relsig`):** при отриманні `SIGUSR1` процес негайно призупиняє цикл відмальовування, вимикає таймери оновлення екрана, скидає права головного графічного пристрою викликом `drmDropMaster(drm_fd)` і надсилає ядру підтвердження `ioctl(tty_fd, VT_RELDISP, 1)`. Тільки після отримання цього підтвердження ядро активує цільову консоль.
4. **Обробка запиту на повернення (`acqsig`):** при отриманні `SIGUSR2` процес відновлює статус DRM-майстра викликом `drmSetMaster(drm_fd)`, переініціалізує кадровий буфер дисплея (CRTC та площини KMS), відновлює опитування пристроїв вводу й підтверджує ядру готовність викликом `ioctl(tty_fd, VT_RELDISP, VT_ACKACQ)`.
5. **Аварійне та штатне відновлення:** при виході з програми або отриманні сигналів завершення (`SIGINT`, `SIGTERM`) сесійний менеджер зобов'язаний повернути консоль в автоматичний режим `VT_AUTO` та відновити початковий режим клавіатури (`K_UNICODE` або `K_XLATE`), інакше консоль залишиться заблокованою для користувача.

Нижче наведено повну реалізацію сесійного менеджера перемикання консолей, що використовує `signalfd` та `epoll` для асинхронного реагування на події ядра без блокування потоку виконання.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/epoll.h>
#include <linux/vt.h>
#include <linux/kd.h>
#include <xf86drm.h>

namespace vt {

constexpr int ReleaseSignal = SIGUSR1;
constexpr int AcquireSignal = SIGUSR2;

class UniqueFd {
    int m_fd = -1;
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.m_fd);
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }
};

class VtSessionManager {
    UniqueFd m_ttyFd;
    UniqueFd m_drmFd;
    UniqueFd m_signalFd;
    UniqueFd m_epollFd;

    long m_origKbMode = K_XLATE;
    struct vt_mode m_origVtMode{};
    bool m_isActive = true;
    bool m_isRunning = true;

public:
    VtSessionManager(std::string_view ttyPath, std::string_view drmPath) {
        m_ttyFd.reset(::open(ttyPath.data(), O_RDWR | O_NOCTTY | O_CLOEXEC));
        if (!m_ttyFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити TTY");
        }

        if (::ioctl(m_ttyFd.get(), KDGKBMODE, &m_origKbMode) < 0) {
            throw std::system_error(errno, std::generic_category(), "KDGKBMODE помилка");
        }

        if (::ioctl(m_ttyFd.get(), VT_GETMODE, &m_origVtMode) < 0) {
            throw std::system_error(errno, std::generic_category(), "VT_GETMODE помилка");
        }

        m_drmFd.reset(::open(drmPath.data(), O_RDWR | O_CLOEXEC));
        if (!m_drmFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити DRM пристрій");
        }

        setupSignalHandling();
        setupConsoleModes();
    }

    ~VtSessionManager() noexcept {
        restoreConsole();
    }

    void runLoop() {
        struct epoll_event events[4];
        std::cout << "[VT C++] Головний цикл сесії запущено\n";

        while (m_isRunning) {
            int nfds = ::epoll_wait(m_epollFd.get(), events, 4, 1000);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                break;
            }

            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == m_signalFd.get()) {
                    handleSignalEvent();
                }
            }

            if (m_isActive) {
                // Відмальовування графіки композитором
            }
        }
    }

private:
    void setupSignalHandling() {
        sigset_t mask;
        ::sigemptyset(&mask);
        ::sigaddset(&mask, ReleaseSignal);
        ::sigaddset(&mask, AcquireSignal);
        ::sigaddset(&mask, SIGINT);
        ::sigaddset(&mask, SIGTERM);

        if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigprocmask помилка");
        }

        m_signalFd.reset(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
        if (!m_signalFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "signalfd помилка");
        }

        m_epollFd.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!m_epollFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 помилка");
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = m_signalFd.get();
        if (::epoll_ctl(m_epollFd.get(), EPOLL_CTL_ADD, m_signalFd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl помилка");
        }
    }

    void setupConsoleModes() {
        // Вимикаємо трансляцію клавіатури у TTY
        ::ioctl(m_ttyFd.get(), KDSKBMODE, K_OFF);

        struct vt_mode mode{
            .mode = VT_PROCESS,
            .waitv = 0,
            .relsig = static_cast<short>(ReleaseSignal),
            .acqsig = static_cast<short>(AcquireSignal),
            .frsig = 0
        };

        if (::ioctl(m_ttyFd.get(), VT_SETMODE, &mode) < 0) {
            throw std::system_error(errno, std::generic_category(), "VT_SETMODE помилка");
        }
    }

    void handleSignalEvent() {
        struct signalfd_siginfo fdsi{};
        ssize_t s = ::read(m_signalFd.get(), &fdsi, sizeof(fdsi));
        if (s != sizeof(fdsi)) return;

        if (fdsi.ssi_signo == ReleaseSignal) {
            std::cout << "[VT C++] Звільнення консолі: drmDropMaster\n";
            m_isActive = false;
            ::drmDropMaster(m_drmFd.get());
            ::ioctl(m_ttyFd.get(), VT_RELDISP, 1);
        } else if (fdsi.ssi_signo == AcquireSignal) {
            std::cout << "[VT C++] Захоплення консолі: drmSetMaster\n";
            ::drmSetMaster(m_drmFd.get());
            ::ioctl(m_ttyFd.get(), VT_RELDISP, VT_ACKACQ);
            m_isActive = true;
        } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM) {
            std::cout << "[VT C++] Завершення сесії...\n";
            m_isRunning = false;
        }
    }

    void restoreConsole() noexcept {
        if (m_ttyFd.valid()) {
            ::ioctl(m_ttyFd.get(), VT_SETMODE, &m_origVtMode);
            ::ioctl(m_ttyFd.get(), KDSKBMODE, m_origKbMode);
        }
    }
};

} // namespace vt

int main(int argc, char** argv) {
    const char* ttyPath = (argc > 1) ? argv[1] : "/dev/tty";
    const char* drmPath = (argc > 2) ? argv[2] : "/dev/dri/card0";

    try {
        vt::VtSessionManager manager(ttyPath, drmPath);
        manager.runLoop();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка VT сесії: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Аналіз життєвого циклу, пастки та крайові випадки

У цій архітектурі є кілька критичних деталей реалізації, порушення яких призводить до зависання всієї системи або блокування вводу:

1. **Синхронізація сигналів через `signalfd`:** звичайні асинхронні обробники сигналів (POSIX `sigaction`) мають жорсткі обмеження: у них дозволено викликати лише вузький перелік функцій, безпечних для сигналів (англ. *async-signal-safe functions*). Виклики `ioctl`, `drmDropMaster` або виділення динамічної пам'яті всередині класичного обробника сигналів можуть призвести до взаємного блокування (англ. *deadlock*). Використання `signalfd` перетворює доставку сигналів ядра на звичайне читання дескриптора у головному циклі `epoll`.
2. **Обов'язковість своєчасної відповіді на `VT_RELDISP`:** якщо процес отримав сигнал `relsig`, але затримав виклик `ioctl(tty_fd, VT_RELDISP, 1)` (наприклад, виконує довгу операцію вводу-виводу на диск або очікує блокування м'ютекса), ядро запустить внутрішній таймер очікування. Якщо відповіді немає понад кілька секунд, ядро примусово скине режим і активує нову консоль, що спричинить стан гонитви за регістри дисплея.
3. **Гарантоване відновлення режиму клавіатури (RAII):** якщо процес графічного сервера аварійно завершується (через помилку сегментації `SIGSEGV` або примусовий `SIGKILL`), деструктор не встигне виконатися, а термінал залишиться в режимі `K_OFF`. У результаті користувач бачитиме запрошення командної оболонки, але клавіатура не реагуватиме на жодні натискання. Для відновлення працездатності в такій ситуації користувачеві доводиться або заходити через SSH і виконувати команду `kbd_mode -u`, або надсилати системну команду SysRq (`Alt+SysRq+R`), яка примусово скидає режим клавіатури активної консолі в `K_XLATE`.
4. **Сучасний поділ обов'язків із `systemd-logind`:** у сучасних Linux-дистрибутивах графічні сервери не запускаються з правами `root` і не відкривають `/dev/tty0` напряму. Замість цього сесійний менеджер `logind` бере на себе монопольне володіння TTY, а композитор взаємодіє з ним через D-Bus API (`TakeControl`, `TakeDevice`, `ReleaseDevice`), отримуючи вже відкриті дескриптори DRM та evdev.
5. **Динамічне виділення нової консолі через `VT_OPENQRY`:** якщо графічний сервер запускається з дисплейного менеджера (GDM, SDDM, LightDM), йому не передається фіксований номер консолі. Менеджер виконує виклик `ioctl(tty0_fd, VT_OPENQRY, &vt_num)`, знаходить першу невідкриту консоль (наприклад, `/dev/tty7`), відкриває її вузол і перемикає фокус викликом `VT_ACTIVATE`.
6. **Діагностика перемикань через ftrace:** для відстеження черги перемикання консолей у ядрі використовується системний трейсер: активація події `tracepoint` за адресою `/sys/kernel/debug/tracing/events/vt/vt_switch/enable` фіксує переходи між номерами консолей разом із точними часовими мітками та ідентифікаторами процесів.
