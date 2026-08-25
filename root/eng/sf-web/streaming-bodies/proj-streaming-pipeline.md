# ⚙️ Потоковий тунель із фіксованим буфером і зворотним тиском

Побудова мережевих тунелів, зворотних проксі-вузлів та клієнтських конвеєрів для передавання масивних файлів або нескінченних мультимедійних потоків вимагає суворого дотримання просторового інваріанту: обсяг споживаної оперативної пам'яті програми має бути строго обмеженим і становити величину `O(1)`, яка жодним чином не залежить від сумарного обсягу переданих даних `N`.

У практичній розробці це означає повну відмову від будь-яких проміжних динамічних списків, конкатенації масивів байтів у пам'яті процесу чи завчасного накопичення всього тіла відповіді. Замість цього потік організується як неперервний і замкнений цикл обробки з фіксованим лінійним або кільцевим буфером чітко визначеного розміру (зазвичай від 16 до 64 кілобайтів). У такій схемі швидкість вичитування даних із вхідного сокета джерела безпосередньо регулюється готовністю вихідного сокета споживача прийняти чергову порцію, утворюючи фізичний ланцюг зворотного тиску.

### Архітектура конвеєра та стани парсера блокового кодування

Під час отримання та проміжного транслювання потоку у форматі HTTP/1.1 із заголовком `Transfer-Encoding: chunked` клієнтський парсер функціонує як детермінований скінченний автомат. На відміну від звичайного читання фіксованої кількості байтів за заголовком `Content-Length`, автомат блокового кодування повинен аналізувати структуру транспортних рамок безпосередньо у вхідному потоці октет:

```
[Очікування розміру чанка] ──(Hex + CRLF)──> [Читання тіла чанка]
            ▲                                         │
            │                                  (N байтів прочитано)
            │                                         ▼
            └──(CRLF після даних)───────── [Очікування розділювача]
```

1. **Стан аналізу розміру (`CHUNK_SIZE`):** парсер зчитує вхідні байти до першого символу переведення рядка, виділяє шістнадцяткове число та перетворює його на цілочисельний розмір блоку в байтах. Якщо отримано числове значення `0`, це сигналізує про завершення корисного навантаження та перемикає автомат у режим обробки трейлерів.
2. **Стан читання корисного навантаження (`CHUNK_DATA`):** автомат зчитує рівно `N` байтів сирих даних у виділений робочий буфер. Усі зчитані байти негайно передаються на обробку або записуються у вихідний сокет споживача без збереження в пам'яті.
3. **Стан вичитування розділювача (`CHUNK_CRLF`):** після передавання заявлених `N` байтів парсер очікує обов'язкову термінальну послідовність символів `\r\n` (CRLF), яка відокремлює поточний чанк від наступного префікса розміру.
4. **Стан обробки трейлерів або завершення (`TRAILERS_OR_END`):** після нульового чанка парсер або зчитує фінальні HTTP-заголовки (метадані, розраховані на льоту, як-от контрольні суми), або отримує завершальний порожній рядок `\r\n`, після чого потік вважається коректно закритим.

### Реалізація на Python: потоковий клієнт із генератором

У високорівневому середовищі Python бібліотека `requests` поверх рушія `urllib3` надає механізм потокового читання через прапорець `stream=True`. Якщо цей параметр увімкнено, внутрішній сокет не вичитується до кінця під час виклику методу запиту, а дескриптор з'єднання залишається відкритим під керуванням ітератора `iter_content()`.

Зворотне потокове вивантаження здійснюється передаванням генератора безпосередньо в аргумент `data`. За відсутності явного заголовка `Content-Length` клієнт `urllib3` автоматично перемикається в режим `Transfer-Encoding: chunked`, вичитуючи фрагменти з генератора по мірі їх надсилання у сокет.

```python
import os
import sys
import time
import requests
from typing import Generator, Iterable

CHUNK_SIZE = 64 * 1024  # Фіксований буфер 64 КБ


def generate_large_stream(total_bytes: int, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """Генератор, що віддає масивний потік даних порціями без завантаження всього об'єму в RAM."""
    sent = 0
    pattern = b"0123456789ABCDEF" * (chunk_size // 16)
    while sent < total_bytes:
        to_send = min(chunk_size, total_bytes - sent)
        if to_send < chunk_size:
            yield pattern[:to_send]
        else:
            yield pattern
        sent += to_send


def streaming_download_and_transform(src_url: str, dst_url: str) -> int:
    """Потоковий тунель: викачує дані з джерела та відразу транслює на інший сервер."""
    total_piped = 0

    # stream=True запобігає завантаженню response.content у пам'ять
    with requests.get(src_url, stream=True, timeout=30.0) as resp:
        resp.raise_for_status()

        def stream_consumer() -> Generator[bytes, None, None]:
            nonlocal total_piped
            # iter_content зчитує сирі байти з внутрішнього сокета urllib3
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                total_piped += len(chunk)
                # Передаємо оброблений фрагмент безпосередньо у вихідний потік
                yield chunk

        # Передавання генератора в data активує Transfer-Encoding: chunked у запиті
        upload_resp = requests.post(dst_url, data=stream_consumer(), timeout=60.0)
        upload_resp.raise_for_status()

    return total_piped
```

### Низькорівневий сокетний тунель на C та C++

На рівні системних викликів операційної системи надійне потокове пересилання вимагає прямого контролю над частковими записами та станом блокування сокетів. Виклик `send()` у разі заповнення мережевого буфера ядра відправляє менше байтів, ніж було передано в аргументі довжини. Якщо дескриптор налаштовано в неблокуючому режимі, операційна система сигналізує про неможливість запису поверненням коду `-1` із встановленням значення `errno` у `EAGAIN` або `EWOULDBLOCK`.

Щоб потік працював без втрати даних та без розриву з'єднання, передавач зобов'язаний перейти в режим очікування готовності дескриптора на запис через системний виклик `poll()` або `epoll()`, утримуючи лише поточний невідправлений залишок чанка без додаткових динамічних алокацій у купі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/types.h>

#define BUFFER_SIZE (64 * 1024)

/* Надійне відправлення всього буфера крізь сокет з урахуванням часткових записів */
static int send_all(int fd, const char *buf, size_t len) {
    size_t total_sent = 0;
    while (total_sent < len) {
        ssize_t n = send(fd, buf + total_sent, len - total_sent, 0);
        if (n > 0) {
            total_sent += (size_t)n;
            continue;
        }
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd = { .fd = fd, .events = POLLOUT, .revents = 0 };
                int res = poll(&pfd, 1, 5000);
                if (res > 0 && (pfd.revents & POLLOUT)) continue;
                return -1;
            }
            return -1;
        }
        return -1; /* З'єднання закрито віддаленим вузлом */
    }
    return 0;
}

/* Перенаправлення потоку між сокетами з фіксованим буфером O(1) пам'яті */
int pipe_stream_fixed_buffer(int src_fd, int dst_fd, size_t *out_bytes) {
    char *buffer = malloc(BUFFER_SIZE);
    if (!buffer) return -1;

    size_t total_transferred = 0;
    int status = 0;

    for (;;) {
        ssize_t bytes_read = recv(src_fd, buffer, BUFFER_SIZE, 0);
        if (bytes_read > 0) {
            if (send_all(dst_fd, buffer, (size_t)bytes_read) != 0) {
                status = -2; /* Помилка запису у вихідний сокет */
                break;
            }
            total_transferred += (size_t)bytes_read;
            continue;
        }
        if (bytes_read == 0) {
            /* Досягнуто кінця вхідного потоку (EOF) */
            status = 0;
            break;
        }
        if (errno == EINTR) continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            struct pollfd pfd = { .fd = src_fd, .events = POLLIN, .revents = 0 };
            int res = poll(&pfd, 1, 5000);
            if (res > 0 && (pfd.revents & POLLIN)) continue;
            status = -3; /* Таймаут читання */
            break;
        }
        status = -1; /* Помилка читання */
        break;
    }

    free(buffer);
    if (out_bytes) *out_bytes = total_transferred;
    return status;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>

class SocketHandle {
    int fd_ = -1;
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class StreamPipeTunnel {
    static constexpr size_t kBufferSize = 64 * 1024;

public:
    static std::expected<size_t, std::error_code> pipe_data(int src_fd, int dst_fd) {
        std::array<std::byte, kBufferSize> buffer{};
        size_t total_transferred = 0;

        for (;;) {
            ssize_t bytes_read = ::recv(src_fd, buffer.data(), buffer.size(), 0);
            if (bytes_read > 0) {
                auto send_res = write_all(dst_fd, std::span{buffer.data(), static_cast<size_t>(bytes_read)});
                if (!send_res) {
                    return std::unexpected(send_res.error());
                }
                total_transferred += static_cast<size_t>(bytes_read);
                continue;
            }
            if (bytes_read == 0) {
                break; // Успішний EOF
            }
            if (errno == EINTR) {
                continue;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd{.fd = src_fd, .events = POLLIN, .revents = 0};
                int p_res = ::poll(&pfd, 1, 5000);
                if (p_res > 0 && (pfd.revents & POLLIN)) {
                    continue;
                }
                return std::unexpected(std::make_error_code(std::errc::timed_out));
            }
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        return total_transferred;
    }

private:
    static std::expected<void, std::error_code> write_all(int fd, std::span<const std::byte> data) {
        size_t total_written = 0;
        while (total_written < data.size()) {
            ssize_t n = ::send(fd, data.data() + total_written, data.size() - total_written, 0);
            if (n > 0) {
                total_written += static_cast<size_t>(n);
                continue;
            }
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    struct pollfd pfd{.fd = fd, .events = POLLOUT, .revents = 0};
                    int p_res = ::poll(&pfd, 1, 5000);
                    if (p_res > 0 && (pfd.revents & POLLOUT)) continue;
                    return std::unexpected(std::make_error_code(std::errc::timed_out));
                }
                return std::unexpected(std::make_error_code(std::errc::broken_pipe));
            }
            return std::unexpected(std::make_error_code(std::errc::connection_aborted));
        }
        return {};
    }
};
```
:::

### Пастки та інженерні нюанси реалізації

1. **Передчасний вихід без вичитування фінального чанка:** Якщо клієнт закриває сокет або перериває читання до того, як парсер отримав нульовий блок `0\r\n\r\n` та кінцевий перехід рядка, сервер вважає запит обірваним і примусово закриває все TCP-з'єднання. Це унеможливлює повторне використання сокета в пулі з'єднань `Keep-Alive` і призводить до марнування ресурсів на повторне проходження рукостискань TLS та TCP.
2. **Неузгодженість тайм-аутів активності (Idle Timeout):** Потокове передавання масивного масиву даних може тривати хвилинами або годинами. Якщо джерело даних чи генератор витрачає занадто багато часу на обчислення чергового фрагмента, проміжний проксі-сервер або балансувальник навантаження розірве з'єднання через спрацювання тайм-ауту бездіяльності сокета (socket read timeout). Для запобігання цьому генератор повинен забезпечувати регулярне надсилання фрагментів або порожніх службових блоків (якщо протокол верхнього рівня це підтримує).
3. **Оптимізація нульового копіювання (Zero-Copy) в Linux:** Для досягнення максимальної пропускної здатності на рівні гігабітних мережевих інтерфейсів пересилання байтів між сокетами або з файлу на диску можна реалізувати без копіювання сторінок пам'яті в простір користувача. Системний виклик `sendfile()` дозволяє транслювати файли безпосередньо в мережевий сокет ядра, а системний виклик `splice()` організовує пряме перекачування сторінок між дескрипторами сокетів через кільцевий буфер каналу (pipe buffer), цілком оминаючи копіювання в оперативну пам'ять процесу.
4. **Обробка розриву зв'язку (Broken Pipe):** Під час запису у вихідний сокет, який уже закритий віддаленим споживачем, операційна система за замовчуванням генерує сигнал `SIGPIPE`, що призводить до негайного завершення процесу. Надійний потоковий сервер або клієнт зобов'язаний або блокувати цей сигнал через виклик `signal(SIGPIPE, SIG_IGN)`, або використовувати прапорець `MSG_NOSIGNAL` під час виклику `send()`, що дозволяє коректно отримати код помилки `EPIPE` та акуратно звільнити ресурси конвеєра.
