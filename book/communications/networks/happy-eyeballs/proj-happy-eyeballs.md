# ⚙️ Реалізація паралельного змагання з'єднань Happy Eyeballs v2

Цей проєкт демонструє покрокову побудову асинхронного рушія встановлення з'єднань за стандартом Happy Eyeballs v2 (RFC 8305) на базі неблокуючих системних сокетів POSIX, циклу опитування дескрипторів та точного таймера змагання.

## Архітектурні виклики та модель потоку подій

У класичному мережевому програмуванні встановлення вихідного TCP-з'єднання виконується через блокуючий системний виклик `connect()`. Якщо цільова IP-адреса належить до непрацездатного маршруту або пакет TCP SYN потрапляє у міжмережеву «чорну діру», виклик зависає в очікуванні відповіді на тривалий час (від 20 до 75 секунд залежно від параметрів ретрансмісії ядра). Якщо клієнтська програма наївно перебирає список отриманих IP-адрес послідовно в одному потоці, сумарна затримка підключення може перевищувати кілька хвилин.

Щоб уникнути подібних зависань, алгоритм Happy Eyeballs v2 реалізує асинхронну модель змагання з'єднань (Connection Racing). Рушій виконує роботу в єдиному неблокуючому циклі подій, координуючи декілька незалежних фаз:

1. **Чергування адрес (Address Interleaving).** Отримані від DNS списки адрес родин IPv6 та IPv4 розгортаються у чергу, де адреси різних родин суворо чергуються між собою. Це унеможливлює ситуацію, коли клієнт послідовно перебирає чотири непрацюючі адреси IPv6, перш ніж спробувати хоча б одну адресу IPv4.
2. **Градуйований запуск спроб (Staggered Connection Scheduling).** Підключення до першої адреси черги (як правило, IPv6) стартує в момент `t = 0`. Одночасно запускається таймер затримки наступної спроби (Connection Attempt Delay), рекомендоване значення якого становить 250 мс. Якщо за цей час перший сокет не встигає завершити тристороннє рукостискання TCP, рушій відкриває другий сокет для наступної адреси зі списку (IPv4) і запускає його підключення паралельно.
3. **Мультиплексування та зняття стану сокетів.** Усі відкриті сокети, які перебувають у стані відправленого SYN-пакета, реєструються в системному опитувачі `poll()` з маскою подій `POLLOUT`.
4. **Визначення переможця та атомарне скасування.** Перший сокет, що успішно переходить у стан встановленого з'єднання (`ESTABLISHED`), негайно оголошується переможцем і повертається додатку. Усі інші активні дескриптори пулу негайно закриваються системним викликом `close()`, що змушує ядро звільнити ресурси та надіслати пакети скидання TCP RST, якщо на них пізніше прийдуть запізнілі пакети SYN-ACK.

## Структури даних та алгоритм чергування адрес

Вхідними даними для рушія є два незалежні масиви адрес, отримані після дозволу DNS-записів AAAA (IPv6) та A (IPv4). За правилами RFC 6724 адреси всередині кожної родини вже відсортовані за спаданням пріоритету (наприклад, пріоритет глобальних адрес над застарілими чи тунельними).

Якщо сформувати список простою конкатенацією `[v6_1, v6_2, v6_3, v4_1, v4_2]`, то у разі системного збою маршрутизації IPv6 клієнт буде змушений чекати таймер затримки 250 мс для кожної з трьох адрес IPv6, що сумарно створить невиправдану затримку в 750 мс перед першою спробою IPv4. 

Алгоритм чергування поєднує списки за принципом «по черзі з кожного кошика»: `[v6_1, v4_1, v6_2, v4_2, v6_3]`. Якщо один зі списків вичерпується раніше за інший, залишок довшого списку дописується в кінець черги.

## Реалізація асинхронного рушія на C та C++

Наведений нижче код реалізує повноцінний автономний рушій Happy Eyeballs v2. Приклад мовою C використовує стандартні структури POSIX та ручне керування пам'яттю, тоді як вкладка C++ демонструє сучасний ідіоматичний підхід: безпечну RAII-обгортку над дескрипторами сокетів, роботу з `std::chrono` для точного монотонного часу та контейнери `std::vector` і `std::span`.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <time.h>

#define MAX_ENDPOINTS 16
#define CONNECTION_ATTEMPT_DELAY_MS 250
#define TOTAL_TIMEOUT_MS 10000

typedef struct {
    struct sockaddr_storage addr;
    socklen_t addr_len;
    int family; /* AF_INET або AF_INET6 */
} Endpoint;

typedef struct {
    int fd;
    size_t endpoint_idx;
    int is_active;
    int is_connected;
} ConnectionAttempt;

typedef struct {
    Endpoint endpoints[MAX_ENDPOINTS];
    size_t endpoint_count;
    size_t next_endpoint_to_try;
    ConnectionAttempt attempts[MAX_ENDPOINTS];
    size_t active_attempts_count;
    int winner_fd;
} HappyEyeballsEngine;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static long long current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000LL + (ts.tv_nsec / 1000000LL);
}

/* Формування черги адрес зі строгим чергуванням родин IPv6 та IPv4 */
static size_t interleave_endpoints(const Endpoint* v6, size_t v6_cnt,
                                   const Endpoint* v4, size_t v4_cnt,
                                   Endpoint* out) {
    size_t i = 0, j = 0, k = 0;
    while (i < v6_cnt || j < v4_cnt) {
        if (i < v6_cnt && k < MAX_ENDPOINTS) {
            out[k++] = v6[i++];
        }
        if (j < v4_cnt && k < MAX_ENDPOINTS) {
            out[k++] = v4[j++];
        }
    }
    return k;
}

/* Ініціалізація спроби асинхронного підключення */
static int start_connection_attempt(HappyEyeballsEngine* engine) {
    if (engine->next_endpoint_to_try >= engine->endpoint_count) {
        return 0; /* Немає більше адрес для спроб */
    }

    size_t ep_idx = engine->next_endpoint_to_try++;
    Endpoint* ep = &engine->endpoints[ep_idx];

    int fd = socket(ep->family, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    if (set_nonblocking(fd) < 0) {
        close(fd);
        return -1;
    }

    int rc = connect(fd, (struct sockaddr*)&ep->addr, ep->addr_len);
    if (rc == 0) {
        /* З'єднання відбулося миттєво (наприклад, loopback) */
        ConnectionAttempt* att = &engine->attempts[engine->active_attempts_count++];
        att->fd = fd;
        att->endpoint_idx = ep_idx;
        att->is_active = 1;
        att->is_connected = 1;
        engine->winner_fd = fd;
        return 1;
    }

    if (rc < 0 && errno == EINPROGRESS) {
        /* Нормальний асинхронний старт тристороннього рукостискання */
        ConnectionAttempt* att = &engine->attempts[engine->active_attempts_count++];
        att->fd = fd;
        att->endpoint_idx = ep_idx;
        att->is_active = 1;
        att->is_connected = 0;
        return 1;
    }

    /* Миттєва помилка (наприклад, ENETUNREACH) — закриваємо сокет */
    close(fd);
    return 0;
}

/* Скасування та закриття всіх невдалих або повільних спроб */
static void cleanup_losing_attempts(HappyEyeballsEngine* engine, int winning_fd) {
    for (size_t i = 0; i < engine->active_attempts_count; ++i) {
        ConnectionAttempt* att = &engine->attempts[i];
        if (att->is_active && att->fd != winning_fd) {
            close(att->fd);
            att->is_active = 0;
            att->fd = -1;
        }
    }
}

/* Головний цикл змагання з'єднань Happy Eyeballs v2 */
int happy_eyeballs_connect(const Endpoint* interleaved_endpoints, size_t count) {
    if (count == 0) return -1;

    HappyEyeballsEngine engine;
    memset(&engine, 0, sizeof(engine));
    memcpy(engine.endpoints, interleaved_endpoints, count * sizeof(Endpoint));
    engine.endpoint_count = count;
    engine.winner_fd = -1;

    long long start_time = current_time_ms();
    long long next_attempt_time = start_time;

    while (engine.winner_fd == -1) {
        long long now = current_time_ms();
        if (now - start_time >= TOTAL_TIMEOUT_MS) {
            cleanup_losing_attempts(&engine, -1);
            return -1; /* Загальний таймаут вичерпано */
        }

        /* Час для запуску наступної паралельної спроби */
        if (now >= next_attempt_time && engine.next_endpoint_to_try < engine.endpoint_count) {
            int res = start_connection_attempt(&engine);
            if (engine.winner_fd != -1) {
                break; /* Миттєве підключення */
            }
            if (res > 0) {
                next_attempt_time = now + CONNECTION_ATTEMPT_DELAY_MS;
            } else {
                /* Якщо спроба зазнала швидкої помилки, пробуємо наступну негайно */
                next_attempt_time = now;
                continue;
            }
        }

        /* Формування списку опитування дескрипторів для poll */
        struct pollfd pfd[MAX_ENDPOINTS];
        int pfd_map[MAX_ENDPOINTS];
        nfds_t nfds = 0;

        for (size_t i = 0; i < engine.active_attempts_count; ++i) {
            if (engine.attempts[i].is_active && !engine.attempts[i].is_connected) {
                pfd[nfds].fd = engine.attempts[i].fd;
                pfd[nfds].events = POLLOUT;
                pfd[nfds].revents = 0;
                pfd_map[nfds] = (int)i;
                nfds++;
            }
        }

        if (nfds == 0 && engine.next_endpoint_to_try >= engine.endpoint_count) {
            /* Усі адреси вичерпані й жоден сокет не активний */
            return -1;
        }

        int poll_timeout = 10; /* мс */
        if (engine.next_endpoint_to_try < engine.endpoint_count) {
            long long time_to_next = next_attempt_time - now;
            if (time_to_next < 0) time_to_next = 0;
            if (time_to_next < poll_timeout) poll_timeout = (int)time_to_next;
        }

        int prc = poll(pfd, nfds, poll_timeout);
        if (prc > 0) {
            for (nfds_t i = 0; i < nfds; ++i) {
                if (pfd[i].revents & (POLLOUT | POLLERR | POLLHUP)) {
                    int att_idx = pfd_map[i];
                    int fd = engine.attempts[att_idx].fd;
                    int sock_err = 0;
                    socklen_t err_len = sizeof(sock_err);

                    if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) == 0 && sock_err == 0) {
                        /* Переможець знайдений! */
                        engine.winner_fd = fd;
                        engine.attempts[att_idx].is_connected = 1;
                        break;
                    } else {
                        /* Помилка з'єднання на цьому дескрипторі */
                        close(fd);
                        engine.attempts[att_idx].is_active = 0;
                        engine.attempts[att_idx].fd = -1;
                    }
                }
            }
        }
    }

    int winner = engine.winner_fd;
    cleanup_losing_attempts(&engine, winner);
    return winner;
}
```
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <span>
#include <algorithm>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace happy_eyeballs {

using namespace std::chrono_literals;

/* Безпечна RAII-обгортка для керування життєвим циклом файлового дескриптора */
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

struct Endpoint {
    sockaddr_storage addr{};
    socklen_t addr_len{sizeof(sockaddr_storage)};
    int family{AF_INET6};
};

struct ConnectionAttempt {
    UniqueFd socket_fd;
    size_t endpoint_index{0};
    bool connected{false};
};

class ConnectionRacer {
public:
    static constexpr auto kAttemptDelay = 250ms;
    static constexpr auto kTotalTimeout = 10000ms;

    /* Створення черги із суворим чергуванням адрес IPv6 та IPv4 */
    static std::vector<Endpoint> interleave(std::span<const Endpoint> v6_addrs,
                                            std::span<const Endpoint> v4_addrs) {
        std::vector<Endpoint> result;
        result.reserve(v6_addrs.size() + v4_addrs.size());

        size_t i = 0, j = 0;
        while (i < v6_addrs.size() || j < v4_addrs.size()) {
            if (i < v6_addrs.size()) {
                result.push_back(v6_addrs[i++]);
            }
            if (j < v4_addrs.size()) {
                result.push_back(v4_addrs[j++]);
            }
        }
        return result;
    }

    /* Запуск гонки з'єднань над чергою адрес */
    static std::optional<UniqueFd> connect(std::span<const Endpoint> endpoints) {
        if (endpoints.empty()) {
            return std::nullopt;
        }

        std::vector<ConnectionAttempt> active_attempts;
        size_t next_idx = 0;

        const auto start_time = std::chrono::steady_clock::now();
        auto next_attempt_time = start_time;

        while (true) {
            const auto now = std::chrono::steady_clock::now();
            if (now - start_time >= kTotalTimeout) {
                return std::nullopt; /* Загальний таймаут вичерпано */
            }

            /* Перевірка потреби запуску наступної паралельної спроби */
            if (now >= next_attempt_time && next_idx < endpoints.size()) {
                const auto& ep = endpoints[next_idx];
                UniqueFd fd{::socket(ep.family, SOCK_STREAM, 0)};

                if (fd.valid()) {
                    set_nonblocking(fd.get());
                    int rc = ::connect(fd.get(), reinterpret_cast<const sockaddr*>(&ep.addr), ep.addr_len);

                    if (rc == 0) {
                        /* Миттєве встановлення зв'язку */
                        return fd;
                    }

                    if (rc < 0 && errno == EINPROGRESS) {
                        active_attempts.push_back(ConnectionAttempt{
                            .socket_fd = std::move(fd),
                            .endpoint_index = next_idx,
                            .connected = false
                        });
                        next_attempt_time = now + kAttemptDelay;
                    } else {
                        /* Швидка помилка маршруту — перехід до наступної адреси без затримки */
                        next_attempt_time = now;
                    }
                }
                next_idx++;
            }

            /* Підготовка списку дескрипторів для системного виклику poll */
            std::vector<pollfd> poll_fds;
            poll_fds.reserve(active_attempts.size());
            for (const auto& att : active_attempts) {
                if (att.socket_fd.valid()) {
                    poll_fds.push_back(pollfd{
                        .fd = att.socket_fd.get(),
                        .events = POLLOUT,
                        .revents = 0
                    });
                }
            }

            if (poll_fds.empty() && next_idx >= endpoints.size()) {
                return std::nullopt; /* Усі варіанти вичерпано без успіху */
            }

            int timeout_ms = 10;
            if (next_idx < endpoints.size()) {
                auto time_left = std::chrono::duration_cast<std::chrono::milliseconds>(next_attempt_time - now).count();
                timeout_ms = std::max(0, static_cast<int>(time_left));
                timeout_ms = std::min(timeout_ms, 25);
            }

            int prc = ::poll(poll_fds.data(), static_cast<nfds_t>(poll_fds.size()), timeout_ms);
            if (prc > 0) {
                for (size_t i = 0; i < poll_fds.size(); ++i) {
                    if (poll_fds[i].revents & (POLLOUT | POLLERR | POLLHUP)) {
                        int current_fd = poll_fds[i].fd;
                        int sock_err = 0;
                        socklen_t len = sizeof(sock_err);

                        if (::getsockopt(current_fd, SOL_SOCKET, SO_ERROR, &sock_err, &len) == 0 && sock_err == 0) {
                            /* Знайдено переможця: повертаємо дескриптор, решта сокетів закривається автоматично деструкторами RAII */
                            for (auto& att : active_attempts) {
                                if (att.socket_fd.get() == current_fd) {
                                    return std::move(att.socket_fd);
                                }
                            }
                        } else {
                            /* Збій на сокеті — скидаємо та закриваємо відповідний дескриптор */
                            for (auto& att : active_attempts) {
                                if (att.socket_fd.get() == current_fd) {
                                    att.socket_fd.reset();
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

private:
    static bool set_nonblocking(int fd) noexcept {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags == -1) return false;
        return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) != -1;
    }
};

} // namespace happy_eyeballs
```
:::

## Детальний розбір реалізації та обробка крайових випадків

### 1. Монотонний час проти системного годинника
Для відліку інтервалів таймерів (250 мс між спробами та 10 с загального ліміту) рушій використовує монотонний таймер `CLOCK_MONOTONIC` (або `std::chrono::steady_clock` у C++). 

Використання реального системного часу (`CLOCK_REALTIME` / `gettimeofday()`) у таких алгоритмах є критичною помилкою: якщо під час виконання гонки з'єднань служба синхронізації часу NTP скоригує системний годинник назад або вперед, різниця часу стане від'ємною або гігантською. Це спричинить або передчасне завершення за таймаутом, або повне зависання планувальника спроб.

### 2. Специфіка обробки помилки `EINPROGRESS`
Під час виклику `connect()` на неблокуючому сокеті ядро операційної системи формує пакет TCP SYN, записує його у вихідну чергу мережевого інтерфейсу та негайно повертає керування додатку зі значенням `-1` та кодом помилки `errno = EINPROGRESS`. 

У коді рушія цей стан обробляється як нормальний старт: сокет реєструється у масиві активних спроб `active_attempts`, а час наступної спроби `next_attempt_time` зсувається на 250 мс уперед.

Якщо ж функція `connect()` повертає миттєву системну помилку — наприклад, `ENETUNREACH` (мережа недосяжна через відсутність маршруту за замовчуванням) або `EAFNOSUPPORT` (родина адрес не підтримується ядром чи адаптером) — рушій не чекає 250 мс, а негайно закриває дефектний сокет і пробує наступну адресу з черги на цій самій ітерації циклу.

### 3. Двокрокова перевірка готовності сокета через `POLLOUT` та `SO_ERROR`
Коли ядро завершує обробку вихідного SYN-пакета, сокет стає доступним для запису, що активує прапорець `POLLOUT` у виклику `poll()`. Проте стандарт POSIX визначає, що подія `POLLOUT` сигналізується у двох діаметрально протилежних випадках:
* Сервер відповів пакетом SYN-ACK, тристороннє рукостискання завершено, сокет перейшов у стан `ESTABLISHED` і готовий приймати дані додатку.
* Сервер відповів пакетом скидання TCP RST, або проміжний маршрутизатор надіслав ICMP Port Unreachable, або вичерпано внутрішній таймаут SYN-ретрансмісій ядра. У цьому разі з'єднання зазнало збою.

Щоб розрізнити ці стани, рушій зобов'язаний виконати системний запит параметрів сокета:

:::tabs
```c
int sock_err = 0;
socklen_t err_len = sizeof(sock_err);
if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) < 0) {
    /* Системна помилка виклику */
}
```
```cpp
int sock_err = 0;
socklen_t err_len = sizeof(sock_err);
if (::getsockopt(fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) < 0) {
    /* Системна помилка виклику */
}
```
:::

Якщо виклик `getsockopt` повертає нуль і значення `sock_err == 0`, з'єднання встановлено бездоганно. Якщо змінна `sock_err` містить ненульовий код помилки (наприклад, `ECONNREFUSED` = 111 або `ETIMEDOUT` = 110), сокет вважається зламаним і негайно видаляється з пулу.

### 4. Запобігання витоку ресурсів на стороні сервера (TCP RST Cleanup)
У класичній гонці декілька сокетів одночасно надсилають запити TCP SYN до різних IP-адрес сервера. Щойно перший сокет завершує рукостискання, усі інші дескриптори закриваються системним викликом `close()`.

Поведінка ядра при закритті сокета залежить від його поточного внутрішнього стану:
* **Сокет у стані `SYN_SENT`:** Ядро операційної системи видаляє структуру TCB (Transmission Control Block) зі своєї пам'яті. Якщо віддалений сервер пізніше все ж надішле пакет SYN-ACK, клієнтський стек TCP не знайде відповідного локального порту і автоматично надішле у відповідь пакет TCP RST.
* **Сокет у стані `ESTABLISHED` (другий сокет встиг завершити handshake на частку мілісекунди пізніше за першого):** Виклик `close()` над сокетом із непорожніми чергами або скиданням викликає генерацію RST, інформуючи сервер про негайне завершення сесії без переходу в тривалий стан `TIME_WAIT`.

Це запобігає накопиченню завислих напіввідкритих сесій у таблицях з'єднань серверів та балансувальників навантаження.

## Двофазне змагання: розширення гонки на криптографічний рівень TLS

У сучасних протоколах прикладного рівня (HTTPS, gRPC, DoH) успішне завершення тристороннього рукостискання TCP ще не гарантує безперешкодної передачі корисних даних. У реальних мережах трапляються несправні проміжні вузли (Middleboxes) або системи глибокої інспекції пакетів (DPI), які без перешкод пропускають базові пакети TCP SYN, проте мовчки блокують або скидають пакети `ClientHello` протоколу TLS через наявність розширень SNI (Server Name Indication) чи невідомих шифронаборів.

У такій ситуації класичний одноетапний рушій Happy Eyeballs стає жертвою «хибної перемоги»:
1. Дескриптор IPv6 успішно завершує TCP 3-way handshake за 10 мс.
2. Рушій негайно оголошує IPv6 переможцем і закриває паралельну спробу IPv4.
3. Клієнт розпочинає TLS-рукостискання на сокеті IPv6 і надсилає запит `ClientHello`.
4. Проміжний фаєрвол блокує TLS-пакет, і сесія зависає на таймауті TLS (15–30 секунд), попри те, що шлях IPv4 забезпечив би безперешкодне проходження криптографічного сеансу.

Для захисту від таких збоїв розвинені мережеві бібліотеки застосовують **двофазне змагання (Two-Stage Racing)**:

```
Фаза 1: Трьохстороннє рукостискання TCP (TCP Handshake)
  IPv6 TCP SYN  ──────────>  SYN-ACK  [t = 10 мс]  ──> TCP OK
  IPv4 TCP SYN  ──────────>  (очікування затримки 250 мс)

Фаза 2: Рукостискання TLS (TLS Handshake)
  IPv6 ClientHello  ──────>  [Блокування фаєрволом / Чорна діра]
  (таймер 250 мс спливає)
  IPv4 TCP Handshake ─────>  TCP OK  [t = 290 мс]
  IPv4 ClientHello  ──────>  ServerHello + Certificate  [t = 330 мс] ──> ПЕРЕМОГА TLS!
  IPv6 сокет остаточно анулюється та закривається.
```

При двофазному змаганні сокет не вважається остаточним переможцем доти, доки криптографічний рівень TLS не отримає коректний пакет `ServerHello` та валідний ланцюжок сертифікатів. Якщо перший сокет завершив TCP-рукостискання, але завис на фазі TLS, таймер затримки наступної спроби продовжує відлік і дозволяє паралельному сокету IPv4 випередити дефектний канал зв'язку.

## Інтеграція з асинхронним DNS-резолвером

У представленому вище прикладі передбачалося, що списки адрес IPv6 та IPv4 вже завантажені у пам'ять. Проте у реальних додатках сам процес отримання адрес через DNS також є джерелом небезпечних затримок.

Стандартний блокуючий системний виклик POSIX `getaddrinfo()` виконує запити послідовно або паралельно у внутрішньому потоці бібліотеки C (glibc / musl), повертаючи єдиний пов'язаний список `struct addrinfo`. Якщо авторитетний DNS-сервер для запису AAAA відповідає із затримкою у 2 секунди, а для запису A — за 10 мс, виклик `getaddrinfo()` буде заблокований на всі 2 секунди, утримуючи клієнт у стані очікування.

Промислові рушії Happy Eyeballs вирішують цю проблему шляхом асинхронного розв'язання DNS через неблокуючі бібліотеки (наприклад, c-ares, ldns або системний виклик Linux `getaddrinfo_a`):

1. **Асинхронний старт:** Клієнт одночасно надсилає два незалежні неблокуючі UDP/DoH запити для типів `AAAA` та `A`.
2. **Таймер Resolution Delay (50 мс):** Якщо відповідь для IPv4 (запис A) приходить першою, рушій не починає підключення негайно. Замість цього він запускає таймер очікування AAAA на 50 мс. Якщо за ці 50 мс відповідь AAAA надходить, черга починається з адреси IPv6, зберігаючи пріоритет протоколу нового покоління. Якщо ж таймер 50 мс вичерпується, рушій негайно розпочинає підключення через IPv4, не чекаючи запізнілої відповіді IPv6.
3. **Динамічне оновлення черги:** Якщо запити на підключення через IPv4 вже тривають, а пакет AAAA надходить пізніше (наприклад, на 120-й мілісекунді), нові адреси IPv6 динамічно додаються на початок списку майбутніх спроб.

## Масштабування: від poll() до epoll() та kqueue()

Для невеликої кількості паралельних з'єднань (від 2 до 4 активних сокетів) системний виклик `poll()` є оптимальним завдяки простоті використання та нульовим накладним витратам на реєстрацію дескрипторів. Проте у високонавантажених серверах, проксі-вузлах та шлюзах API, де одночасно обслуговуються тисячі клієнтських підключень, перебір масивів `struct pollfd` створює навантаження на процесор масштабу `O(N)`.

У таких архітектурах застосовують механізми готовності масштабу `O(1)`:
* **Linux `epoll` (`epoll_create1`, `epoll_ctl`, `epoll_pwait`):** Реєстрація сокетів із прапорцями `EPOLLOUT | EPOLLONESHOT | EPOLLET`. Використання прапорця `EPOLLONESHOT` гарантує, що подія готовності буде доставлена лише одному робочому потоку, виключаючи стан гонки між ядрами процесора під час визначення переможця.
* **FreeBSD/macOS `kqueue` (`EVFILT_WRITE`, `EV_ONESHOT`):** Високоефективний фільтр подій ядра, що дозволяє поєднувати таймери `EVFILT_TIMER` та події запису сокетів в єдиному черговому масиві системних подій, усуваючи необхідність ручного розрахунку інтервалів `timeout_ms`.

## Взаємодія з оптимізацією TCP Fast Open (TFO)

Технологія TCP Fast Open (RFC 7413) дозволяє передавати дані першого прикладного запиту (наприклад, HTTP GET) безпосередньо всередині корисного навантаження початкового пакета TCP SYN, заощаджуючи один повний круговий інтервал RTT.

Під час використання TCP Fast Open у поєднанні з Happy Eyeballs виникає специфічний ризик: якщо дані прикладного запиту надсилаються в SYN-пакетах декількох паралельних сокетів, сервер отримає корисне навантаження двічі (якщо обидва SYN дійдуть до сервера).

Правило безпеки TFO в Happy Eyeballs регламентує:
* Для **ідемпотентних запитів** (HTTP GET, HEAD), які не змінюють стан сервера, використання TCP Fast Open дозволено для всіх паралельних сокетів пулу.
* Для **неідемпотентних запитів** (HTTP POST, PUT, фінансові транзакції) TCP Fast Open дозволяється використовувати **лише на першій спробі IPv6**. Якщо через 250 мс запускається паралельна спроба IPv4, вона зобов'язана виконувати класичне рукостискання без відправки прикладних даних у SYN, щоб унеможливити подвійне виконання операції на сервері у разі затримки першого пакета.

## Кросплатформні відмінності: Windows Winsock проти POSIX

Під час перенесення алгоритму Happy Eyeballs на платформу Microsoft Windows мережевий розробник стикається з низкою специфічних відмінностей системного API Winsock:

* **Дефекти `WSAPoll()`:** Функція `WSAPoll()` у системі Windows має давню задокументовану проблему з обробкою неуспішних неблокуючих підключень: у разі збою з'єднання вона не завжди коректно встановлює біти `POLLERR` або `POLLHUP`, через що сокет залишається заблокованим у невідомому стані.
* **Асинхронний виклик `ConnectEx()`:** Для високоефективних клієнтів на базі портів завершення вводу-виводу IOCP (I/O Completion Ports) замість `connect()` використовується виклик `ConnectEx()`. Особливість цієї функції полягає в тому, що перед її викликом сокет обов'язково має бути попередньо прив'язаний до локальної адреси за допомогою функції `bind()`.
* **Оновлення контексту сокета `SO_UPDATE_CONNECT_CONTEXT`:** Після успішного завершення операції через `ConnectEx()` сокет не успадковує властивості стандартного з'єднання доти, доки над ним не буде виконано виклик:

:::tabs
```c
setsockopt(socket_fd, SOL_SOCKET, SO_UPDATE_CONNECT_CONTEXT, NULL, 0);
```
```cpp
::setsockopt(socket_fd, SOL_SOCKET, SO_UPDATE_CONNECT_CONTEXT, nullptr, 0);
```
:::

Без цього виклику будь-які подальші операції `getpeername()`, `shutdown()` або передачі даних через TLS зазнаватимуть невдачі з системною помилкою `WSAENOTCONN`.

## Налаштування параметрів сокета після перемоги в гонці

Щойно дескриптор-переможець визначений, а всі інші конкуруючі сокети закриті, критично важливо оптимізувати параметри переможного сокета перед початком передачі прикладного трафіку:

1. **Вимкнення алгоритму Нейгла (`TCP_NODELAY`):** За замовчуванням стек TCP буферизує дрібні пакети для зменшення кількості службових заголовків. Для інтерактивних протоколів (HTTP/2, WebSocket, gRPC) цю затримку необхідно вимкнути викликом `setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag))`, що дозволяє надсилати криптографічні фрейми TLS негайно.
2. **Активація періодичної перевірки зв'язку (`SO_KEEPALIVE`):** Дозволяє виявляти розриви зв'язку та мовчазне зникнення NAT-трансляцій у тривалих з'єднаннях.
3. **Повернення в блокуючий режим (опціонально):** Якщо прикладний шар працює за класичною моделлю потоків (Thread-per-Connection) або використовує синхронний TLS-рушій OpenSSL / mbedTLS, дескриптор-переможець можна повернути в блокуючий стан, знявши прапорець `O_NONBLOCK` за допомогою `fcntl()`.

## Покроковий розбір поведінки рушія на практичному прикладі

Розглянемо проходження алгоритму під час підключення до веб-сервера, для якого DNS повернув дві адреси IPv6 (`2001:db8::1`, `2001:db8::2`) та дві адреси IPv4 (`198.51.100.1`, `198.51.100.2`). Припустимо, що шлях до першої адреси IPv6 заблоковано фаєрволом, а IPv4 працює із затримкою RTT = 40 мс:

1. **t = 0 мс:** Функція `interleave_endpoints` формує чергу спроб: `[2001:db8::1, 198.51.100.1, 2001:db8::2, 198.51.100.2]`.
2. **t = 0 мс:** Створюється неблокуючий сокет `fd_0` для адреси `2001:db8::1`. Виклик `connect()` повертає `EINPROGRESS`. Відправлено TCP SYN [IPv6]. Час наступної спроби встановлюється на `t = 250 мс`.
3. **t = 0..250 мс:** Виклик `poll()` спить короткими інтервалами, очікуючи подій на `fd_0`. Пакет SYN губиться у чорній дірі, жодних подій не відбувається.
4. **t = 250 мс:** Спливає таймер 250 мс. Рушій створює сокет `fd_1` для наступної адреси черги — `198.51.100.1` (IPv4). Виклик `connect()` повертає `EINPROGRESS`. Відправлено TCP SYN [IPv4]. Час наступної спроби планується на `t = 500 мс`. Тепер у масиві `poll` одночасно перебувають два дескриптори: `fd_0` та `fd_1`.
5. **t = 290 мс (через 40 мс після старту IPv4):** Мережевий адаптер отримує TCP SYN-ACK від адреси `198.51.100.1`. Виклик `poll()` прокидається з прапорцем `POLLOUT` на дескрипторі `fd_1`.
6. **t = 290 мс:** Виклик `getsockopt(fd_1, ...)` повертає `SO_ERROR == 0`. Дескриптор `fd_1` оголошується абсолютним переможцем!
7. **t = 290 мс:** Функція очищення `cleanup_losing_attempts` закриває дескриптор `fd_0`. Рушій повертає `fd_1` клієнтському додатку для надсилання HTTPS-запиту.
8. **Результат:** З'єднання встановлено за 290 мс замість 30 секунд аварійного очікування.
