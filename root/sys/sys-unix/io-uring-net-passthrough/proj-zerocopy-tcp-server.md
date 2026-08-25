# ⚙️ Практична реалізація SendZC/RecvZC сервера в io_uring

Ця вставка містить практичну реалізацію високопродуктивного мережевого TCP-сервера ехо на базі `io_uring` із використанням відправки без копіювання (`IORING_OP_SEND_ZC`), попередньо зареєстрованих буферів пам'яті (`IORING_REGISTER_BUFFERS`) та обробки двофазних сповіщень completion queue (`IORING_CQE_F_NOTIF`). Вона пояснює кожен етап побудови асинхронного циклу обробки з'єднань, керування пулом буферів та синхронізації пам'яті.

## Архітектурний дизайн сервера

Сервер реалізує високоефективну модель обробки мережевих підключень, орієнтовану на повну відсутність системних викликів у гарячому циклі обробки даних (hot path):

1. **Одноразова реєстрація буферів при старті:** Програма ініціалізує вирівняний за межею сторінки (4096 байт) масив пам'яті та реєструє його в ядрі за допомогою `io_uring_register_buffers()`. Це усуває накладні витрати на закріплення сторінок ОЗП (`pin_user_pages()`) під час кожної операції вводу-виводу.
2. **Асинхронний accept без блокування:** Сервер реєструє підготовлений запит `IORING_OP_ACCEPT` у кільці Submission Queue (SQ). Коли нове TCP-з'єднання встановлюється, ядро генерує completion-подію CQE з новим дескриптором сокета і автоматично перевикористовує запит для прийому наступних клієнтів.
3. **Фіксований читальний крок:** Отримання даних здійснюється через операцію `IORING_OP_READ_FIXED`, яка зчитує байти з сокета безпосередньо у зареєстрований буфер пам'яті з індексом `buf_idx`.
4. **Відправка Zero-Copy (SendZC):** Відправка даних здійснюється через `IORING_OP_SEND_ZC` із прапорцем `IORING_RECVSEND_FIXED_BUF`. Ядро формує пакет `sk_buff` зі сторінками пам'яті користувача, минаючи `memcpy()`.
5. **Двофазне керування життєвим циклом буфера:** Сервер обробляє два об'єкти CQE для кожної відправки. Перший CQE підтверджує кількість прийнятих мережевим стеком байтів (`cqe->res > 0`, `cqe->flags & IORING_CQE_F_MORE`). Другий CQE із прапорцем `IORING_CQE_F_NOTIF` підтверджує, що мережева карта закінчила DMA-читання, після чого буфер повертається у пул вільних ресурсів.

## Детальний розбір реалізації коду: C та C++

У наведених прикладах показано фундаментальні відмінності між класичним C-стилем обробки системних ресурсів та сучасним ідіоматичним C++20 із застосуванням концепції RAII, управління пам'яттю через RAII-обгортки та неблокуючих безпечних типів.

:::tabs
```c
/* c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <liburing.h>

#define QUEUE_DEPTH 256
#define BUFFER_SIZE 65536
#define NUM_BUFFERS 64

enum conn_state {
    STATE_ACCEPT,
    STATE_READ,
    STATE_SEND_ZC,
    STATE_WAIT_NOTIF
};

struct client_ctx {
    int fd;
    enum conn_state state;
    int buf_idx;
    size_t bytes_to_send;
    size_t bytes_sent;
};

static char g_buffers[NUM_BUFFERS][BUFFER_SIZE] __attribute__((aligned(4096)));
static int g_buf_freelist[NUM_BUFFERS];
static int g_buf_free_top = NUM_BUFFERS;

static int alloc_buffer(void) {
    if (g_buf_free_top <= 0) return -1;
    return g_buf_freelist[--g_buf_free_top];
}

static void free_buffer(int idx) {
    if (g_buf_free_top < NUM_BUFFERS) {
        g_buf_freelist[g_buf_free_top++] = idx;
    }
}

int main(int argc, char *argv[]) {
    int port = 8080;
    if (argc > 1) port = atoi(argv[1]);

    for (int i = 0; i < NUM_BUFFERS; i++) {
        g_buf_freelist[i] = i;
    }

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int val = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr.s_addr = INADDR_ANY
    };

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }

    if (listen(listen_fd, 128) < 0) {
        perror("listen");
        return 1;
    }

    struct io_uring ring;
    if (io_uring_queue_init(QUEUE_DEPTH, &ring, 0) < 0) {
        fprintf(stderr, "Failed to init io_uring\n");
        return 1;
    }

    /* Реєстрація масиву буферів для Zero-Copy */
    struct iovec iovs[NUM_BUFFERS];
    for (int i = 0; i < NUM_BUFFERS; i++) {
        iovs[i].iov_base = g_buffers[i];
        iovs[i].iov_len = BUFFER_SIZE;
    }

    if (io_uring_register_buffers(&ring, iovs, NUM_BUFFERS) < 0) {
        fprintf(stderr, "Failed to register fixed buffers\n");
        return 1;
    }

    printf("SendZC TCP Echo Server listening on port %d...\n", port);

    /* Додаємо первинний accept у чергу */
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    struct client_ctx accept_ctx = { .fd = listen_fd, .state = STATE_ACCEPT };
    io_uring_prep_accept(sqe, listen_fd, NULL, NULL, 0);
    io_uring_sqe_set_data(sqe, &accept_ctx);
    io_uring_submit(&ring);

    while (1) {
        struct io_uring_cqe *cqe;
        int ret = io_uring_wait_cqe(&ring, &cqe);
        if (ret < 0) break;

        struct client_ctx *ctx = (struct client_ctx *)io_uring_cqe_get_data(cqe);
        int res = cqe->res;
        unsigned int flags = cqe->flags;

        if (ctx->state == STATE_ACCEPT) {
            if (res >= 0) {
                int client_fd = res;
                struct client_ctx *cctx = malloc(sizeof(*cctx));
                cctx->fd = client_fd;
                cctx->buf_idx = alloc_buffer();
                cctx->state = STATE_READ;

                if (cctx->buf_idx >= 0) {
                    sqe = io_uring_get_sqe(&ring);
                    io_uring_prep_read_fixed(sqe, client_fd, g_buffers[cctx->buf_idx], 
                                             BUFFER_SIZE, 0, cctx->buf_idx);
                    io_uring_sqe_set_data(sqe, cctx);
                } else {
                    close(client_fd);
                    free(cctx);
                }
            }
            /* Перепідготовка accept */
            sqe = io_uring_get_sqe(&ring);
            io_uring_prep_accept(sqe, listen_fd, NULL, NULL, 0);
            io_uring_sqe_set_data(sqe, &accept_ctx);
            io_uring_submit(&ring);
        } 
        else if (ctx->state == STATE_READ) {
            if (res > 0) {
                ctx->bytes_to_send = res;
                ctx->bytes_sent = 0;
                ctx->state = STATE_SEND_ZC;

                sqe = io_uring_get_sqe(&ring);
                /* Подаємо IORING_OP_SEND_ZC з зареєстрованим буфером */
                io_uring_prep_send_zc_fixed(sqe, ctx->fd, g_buffers[ctx->buf_idx], 
                                           res, 0, 0, ctx->buf_idx);
                io_uring_sqe_set_data(sqe, ctx);
                io_uring_submit(&ring);
            } else {
                /* Клієнт закрив з'єднання або помилка */
                close(ctx->fd);
                free_buffer(ctx->buf_idx);
                free(ctx);
            }
        }
        else if (ctx->state == STATE_SEND_ZC) {
            /* Обробка першого або другого CQE для SendZC */
            if (flags & IORING_CQE_F_NOTIF) {
                /* Другий CQE: сповіщення про завершення DMA та звільнення пам'яті */
                sqe = io_uring_get_sqe(&ring);
                ctx->state = STATE_READ;
                io_uring_prep_read_fixed(sqe, ctx->fd, g_buffers[ctx->buf_idx], 
                                         BUFFER_SIZE, 0, ctx->buf_idx);
                io_uring_sqe_set_data(sqe, ctx);
                io_uring_submit(&ring);
            } else {
                /* Перший CQE: повернув кількість переданих байт */
                if (res < 0) {
                    close(ctx->fd);
                    free_buffer(ctx->buf_idx);
                    free(ctx);
                } else if (!(flags & IORING_CQE_F_MORE)) {
                    /* Запитів більше немає, чекаємо або читаємо далі */
                }
            }
        }

        io_uring_cqe_seen(&ring, cqe);
    }

    io_uring_queue_exit(&ring);
    close(listen_fd);
    return 0;
}
```

```cpp
/* cpp */
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <stdexcept>
#include <system_error>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <liburing.h>

namespace net {

constexpr size_t QueueDepth = 256;
constexpr size_t BufferSize = 65536;
constexpr size_t NumBuffers = 64;

class IoUringRing {
    struct io_uring ring_{};
public:
    explicit IoUringRing(unsigned entries) {
        if (int ret = io_uring_queue_init(entries, &ring_, 0); ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_queue_init failed");
        }
    }

    ~IoUringRing() noexcept {
        io_uring_queue_exit(&ring_);
    }

    IoUringRing(const IoUringRing&) = delete;
    IoUringRing& operator=(const IoUringRing&) = delete;

    struct io_uring* get() noexcept { return &ring_; }

    void register_fixed_buffers(std::span<const iovec> iovs) {
        if (int ret = io_uring_register_buffers(&ring_, iovs.data(), iovs.size()); ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "io_uring_register_buffers failed");
        }
    }
};

class SocketOwner {
    int fd_{-1};
public:
    explicit SocketOwner(int fd) noexcept : fd_(fd) {}
    ~SocketOwner() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketOwner(SocketOwner&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketOwner& operator=(SocketOwner&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct BufferPool {
    alignas(4096) std::array<std::array<char, BufferSize>, NumBuffers> storage;
    std::vector<uint16_t> free_indices;

    BufferPool() {
        free_indices.reserve(NumBuffers);
        for (uint16_t i = 0; i < NumBuffers; ++i) {
            free_indices.push_back(i);
        }
    }

    int acquire() {
        if (free_indices.empty()) return -1;
        int idx = free_indices.back();
        free_indices.pop_back();
        return idx;
    }

    void release(uint16_t idx) {
        free_indices.push_back(idx);
    }
};

enum class State { Accept, Read, SendZCWaitNotif };

struct ClientContext {
    SocketOwner client_sock;
    uint16_t buffer_index{0};
    State state{State::Read};

    ClientContext(int fd, uint16_t buf_idx) 
        : client_sock(fd), buffer_index(buf_idx), state(State::Read) {}
};

} // namespace net

int main(int argc, char* argv[]) {
    uint16_t port = 8080;
    if (argc > 1) port = static_cast<uint16_t>(std::atoi(argv[1]));

    net::SocketOwner listen_sock(::socket(AF_INET, SOCK_STREAM, 0));
    if (listen_sock.get() < 0) {
        perror("socket");
        return 1;
    }

    int val = 1;
    ::setsockopt(listen_sock.get(), SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(listen_sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }

    if (::listen(listen_sock.get(), 128) < 0) {
        perror("listen");
        return 1;
    }

    try {
        net::IoUringRing ring(net::QueueDepth);
        auto pool = std::make_unique<net::BufferPool>();

        std::vector<iovec> iovs(net::NumBuffers);
        for (size_t i = 0; i < net::NumBuffers; ++i) {
            iovs[i].iov_base = pool->storage[i].data();
            iovs[i].iov_len = net::BufferSize;
        }

        ring.register_fixed_buffers(iovs);
        std::cout << "C++20 SendZC Server running on port " << port << "...\n";

        // Початкова підготовка accept
        auto* sqe = io_uring_get_sqe(ring.get());
        io_uring_prep_accept(sqe, listen_sock.get(), nullptr, nullptr, 0);
        io_uring_sqe_set_data(sqe, nullptr); // null означає підключення слухаючого сокета
        io_uring_submit(ring.get());

        while (true) {
            io_uring_cqe* cqe{nullptr};
            if (io_uring_wait_cqe(ring.get(), &cqe) < 0) break;

            auto* ctx = static_cast<net::ClientContext*>(io_uring_cqe_get_data(cqe));
            int res = cqe->res;
            unsigned int flags = cqe->flags;

            if (ctx == nullptr) {
                // Подія від listen_sock
                if (res >= 0) {
                    int client_fd = res;
                    int buf_idx = pool->acquire();
                    if (buf_idx >= 0) {
                        auto client_ctx = std::make_unique<net::ClientContext>(client_fd, static_cast<uint16_t>(buf_idx));
                        auto* read_sqe = io_uring_get_sqe(ring.get());
                        io_uring_prep_read_fixed(read_sqe, client_fd, 
                                                 pool->storage[buf_idx].data(), 
                                                 net::BufferSize, 0, buf_idx);
                        io_uring_sqe_set_data(read_sqe, client_ctx.release());
                    } else {
                        ::close(client_fd);
                    }
                }
                // Перереєстрація accept
                sqe = io_uring_get_sqe(ring.get());
                io_uring_prep_accept(sqe, listen_sock.get(), nullptr, nullptr, 0);
                io_uring_sqe_set_data(sqe, nullptr);
                io_uring_submit(ring.get());
            } else {
                if (ctx->state == net::State::Read) {
                    if (res > 0) {
                        ctx->state = net::State::SendZCWaitNotif;
                        auto* send_sqe = io_uring_get_sqe(ring.get());
                        // Ініціалізація SendZC з зареєстрованим буфером
                        io_uring_prep_send_zc_fixed(send_sqe, ctx->client_sock.get(), 
                                                   pool->storage[ctx->buffer_index].data(), 
                                                   res, 0, 0, ctx->buffer_index);
                        io_uring_sqe_set_data(send_sqe, ctx);
                        io_uring_submit(ring.get());
                    } else {
                        pool->release(ctx->buffer_index);
                        delete ctx;
                    }
                } else if (ctx->state == net::State::SendZCWaitNotif) {
                    if (flags & IORING_CQE_F_NOTIF) {
                        // Отримано Notification CQE: DMA відправку повністю завершено
                        auto* read_sqe = io_uring_get_sqe(ring.get());
                        ctx->state = net::State::Read;
                        io_uring_prep_read_fixed(read_sqe, ctx->client_sock.get(), 
                                                 pool->storage[ctx->buffer_index].data(), 
                                                 net::BufferSize, 0, ctx->buffer_index);
                        io_uring_sqe_set_data(read_sqe, ctx);
                        io_uring_submit(ring.get());
                    } else if (res < 0) {
                        pool->release(ctx->buffer_index);
                        delete ctx;
                    }
                }
            }

            io_uring_cqe_seen(ring.get(), cqe);
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal Server Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Покроковий розбір циклу обробки з'єднань

Для кращого розуміння функціонування коду розглянемо порядок проходження даних у C++ реалізації:

1. **Ініціалізація кільця `net::IoUringRing`:** Клас-обгортка `IoUringRing` бере на себе відповідальність за виклики `io_uring_queue_init()` та `io_uring_queue_exit()`. Конструктор перевіряє код повернення ядра та викидає об'єкт `std::system_error` у разі браку ресурсів.
2. **Аллокація та реєстрація буферного пулу:** Пул `BufferPool` виділяє масив розміром 64 буфери по 64 КБ кожен. Атрибут `alignas(4096)` гарантує, що кожен буфер починається з нової фізичної сторінки пам'яті. Виклик `ring.register_fixed_buffers(iovs)` запікає ці сторінки у ядрі.
3. **Обробка виклику `accept`:** Коли у слухаючий сокет надходить нове TCP-з'єднання, `io_uring_wait_cqe()` повертає `cqe` з `user_data == nullptr`. Програма забирає новий сокет `res`, виділяє буфер через `pool->acquire()` і подає запит `io_uring_prep_read_fixed()`.
4. **Обробка `STATE_READ`:** Після прочитання даних (`res > 0`) стан контексту переходить у `State::SendZCWaitNotif`. Програма готує SQE відправки через `io_uring_prep_send_zc_fixed()`, передаючи індекс запеченого буфера `buffer_index`.
5. **Обробка `STATE_SEND_ZC_WAIT_NOTIF`:** Програма отримує події completion queue. Перша подія підтверджує прийняття байтів мережевим стеком. Програма продовжує чекати другої події. Коли надходить друга подія з прапорцем `IORING_CQE_F_NOTIF`, програма знає, що DMA завершено, і подає новий запит на читання `io_uring_prep_read_fixed()`.

## Ключові аспекти вирівнювання та оптимізації продуктивності

При розробці SendZC серверів необхідно зважати на кілька важливих вимог щодо пам'яті та системної конфігурації:

1. **Вирівнювання пам'яті за межею 4096 байт:** Буфери, що реєструються через `io_uring_register_buffers()`, повинні бути вирівняні за межею сторінки (Page Boundary, `alignas(4096)` або `posix_memalign`). Якщо буфер перетинає межу сторінки без вирівнювання, ядро змушене буде обробляти додатковий фрагмент `skb_frag_t`, що знижує ефективність DMA-трансферу на рівнях контролера PCIe.
2. **Керування переповненням CQ-кільця:** Оскільки `IORING_OP_SEND_ZC` генерує два об'єкти CQE на кожен відправлений пакет (перший з результати байтів, другий — нотифікацію), кільце завершень CQ заповнюється у два рази швидше, ніж при звичайному `send`. Якщо програма не встигає вибирати CQE, виникає стан CQ Ring Overflow, при якому ядро змушене скидати нові події. Для відвернення цього слід конфігурувати `cq_entries` зі збільшеним коефіцієнтом (наприклад, у 2–4 рази більшим за `sq_entries`).
3. **Управління лімітом optmem_max:** Кожна нотифікація SendZC вимагає тимчасової пам'яті ядра під об'єкт `struct io_notif_slot`. При інтенсивному паралельному відправленні тисяч пакетів системна пам'ять може вичерпатися, і виклики `io_uring_prep_send_zc` завершуватимуться з помилкою `-ENOBUFS`. Налаштування параметрів ядра через `sysctl -w net.core.optmem_max=4194304` усуває це обмеження під високим навантаженням.

## Пастки реалізації та поради з налагодження

При написанні SendZC серверів розробники найчастіше припустиються трьох типових помилок:

1. **Передчасне перевикористання буфера:** Звільнення буфера у пам'яті або повторне перезаписування даних після першого CQE призводить до пошкодження даних (data corruption) прямо у мережевому каналі, оскільки мережева карта все ще може читати сторінку через DMA. Ресурс можна звільняти або перевикористовувати **виключно** після отримання CQE з прапорцем `IORING_CQE_F_NOTIF`.
2. **Переповнення кільця CQE (CQ Ring Overflow):** Оскільки SendZC на кожен SQE генерує два CQE, швидкість заповнення Completion Queue подвоюється. При інтенсивному навантаженні необхідно збільшувати параметр `cq_entries` при ініціалізації `io_uring_queue_init_params` або використовувати прапорець `IORING_SETUP_CQSIZE`.
3. **Недостатній optmem_max:** Якщо ядро повертає `-ENOBUFS` при спробі подати `IORING_OP_SEND_ZC`, слід збільшити ліміт пам'яті нотифікацій сокета через `sysctl -w net.core.optmem_max=2097152`.
