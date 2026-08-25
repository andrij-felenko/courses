# ⚙️ Реалізація клієнта протоколу ssh-agent на C та C++

Цей проект демонструє низькорівневу взаємодію з локальним демоном `ssh-agent` через сокет домену UNIX (`$SSH_AUTH_SOCK`). Програма підключається до сокета, формує бінарний запит на отримання списку відкритих ключів (`SSH_AGENTC_REQUEST_IDENTITIES`), розбирає відповідь і надсилає запит на цифровий підпис довільного блоку даних (`SSH_AGENTC_SIGN_REQUEST`).

---

## 1. Постановка завдання та контекст виконання

Під час автентифікації на віддаленому сервері за відкритим ключем клієнтська програма `ssh` не зчитує закритий ключ із диска безпосередньо, якщо в середовищі запущено агент автентифікації. Замість цього клієнт виступає посередником між віддаленим сервером `sshd` та локальним фоновим процесом `ssh-agent`.

Щоб реалізувати таку взаємодію в автономній утиліті або бібліотеці, програма повинна виконати таку послідовність низькорівневих системних дій:
1. Зчитати змінну середовища оточення `$SSH_AUTH_SOCK`, яка вказує на активний локальний сокет домену UNIX.
2. Створити потоковий сокет сімейства `AF_UNIX` з типом `SOCK_STREAM` і встановити з'єднання через системний виклик `connect()`.
3. Закодувати та надіслати бінарний запит `SSH_AGENTC_REQUEST_IDENTITIES` (числовий код `11`) для отримання списку відкритих ключів, доступних у пам'яті демона.
4. Розібрати структуровану відповідь `SSH_AGENT_IDENTITIES_ANSWER` (код `12`), коректно витягнувши довжини бінарних блобів ключів та їхні текстові коментарі.
5. Для першого знайденого ключа сформувати повідомлення `SSH_AGENTC_SIGN_REQUEST` (код `13`), що містить відкритий ключ, рядок виклику (challenge) та прапорці алгоритму підпису.
6. Отримати та перевірити відповідь `SSH_AGENT_SIGN_RESPONSE` (код `14`), яка містить готовий криптографічний підпис, накладений закритим ключем усередині демона.

Ключовий висновок цієї архітектури полягає в тому, що клієнтська програма отримує валідний цифровий підпис довільного блоку даних, не маючи прямого доступу до приватного ключа й не знаючи парольної фрази, якою цей ключ захищено на диску.

---

## 2. Архітектура протоколу та обрамлення повідомлень

Протокол взаємодії з агентом OpenSSH працює поверх потоку байтів без збереження меж повідомлень. Тому кожне повідомлення має префіксне обрамлення довжиною (Length-Prefixed Framing):

```
+-----------------------------------+--------------------+----------------------------------------+
|  Довжина навантаження (4 байти)   |  Код типу (1 байт) |  Тіло повідомлення (N байтів)          |
|       uint32, Big-Endian          |      uint8         |                                        |
+-----------------------------------+--------------------+----------------------------------------+
```

### Особливості мережевого кодування та системних викликів

1. **Мережевий порядок байтів (Big-Endian):**
   Усі 32-бітні цілі числа передаються від старшого байта до молодшого. Оскільки більшість сучасних процесорів x86_64 та ARM64 використовують прямий порядок (Little-Endian), кожне поле довжини має бути явно перетворене функціями `htonl()` під час пакування та `ntohl()` під час читання.
2. **Гарантоване дочитування потоку (`read_exact`):**
   Системний виклик ядра `read()` на потоковому сокеті не гарантує повернення всієї запитаної структури за один виклик. Наприклад, якщо клієнт запитує 512 байтів відповіді, ядро може повернути спочатку 128 байтів, а решту передати в наступних циклах планувальника. Спроба розібрати неповний буфер призведе до пошкодження пам'яті. Тому реалізація вимагає обов'язкової допоміжної функції `read_exact()`, яка накопичує байти в циклі до досягнення потрібного розміру.
3. **Обробка переривань сигналів (`EINTR`):**
   Якщо під час очікування даних на сокеті процес отримує сигнал операційної системи (наприклад, зміну розміру вікна `SIGWINCH` або сигнал таймера), виклики `read()` та `write()` повертають помилку `-1` зі встановленням `errno = EINTR`. Надійна реалізація зобов'язана перехоплювати цей стан і продовжувати цикл передачі.

---

## 3. Вихідний код реалізації

Нижче наведено робочу реалізацію клієнта агента. Вкладка C демонструє роботу з низькорівневими системними викликами POSIX, ручним виділенням пам'яті та вказівниками, а вкладка C++ реалізує ту саму логіку з використанням RAII-обгортки сокета, контейнерів `std::vector`, переглядів `std::span` та строгої обробки винятків.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>

#define SSH_AGENT_FAILURE                 5
#define SSH_AGENT_SUCCESS                 6
#define SSH_AGENTC_REQUEST_IDENTITIES     11
#define SSH_AGENT_IDENTITIES_ANSWER       12
#define SSH_AGENTC_SIGN_REQUEST           13
#define SSH_AGENT_SIGN_RESPONSE           14

/* Гарантоване читання точної кількості байтів із сокета */
static int read_exact(int fd, void *buf, size_t len) {
    uint8_t *p = (uint8_t *)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t r = read(fd, p + total, len - total);
        if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (r == 0) return -1; /* Передчасне закриття з'єднання */
        total += (size_t)r;
    }
    return 0;
}

/* Гарантований запис точної кількості байтів у сокет */
static int write_exact(int fd, const void *buf, size_t len) {
    const uint8_t *p = (const uint8_t *)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t w = write(fd, p + total, len - total);
        if (w < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        total += (size_t)w;
    }
    return 0;
}

/* Підключення до локального сокета агента через $SSH_AUTH_SOCK */
static int connect_agent(void) {
    const char *sock_path = getenv("SSH_AUTH_SOCK");
    if (!sock_path || strlen(sock_path) == 0) {
        fprintf(stderr, "Помилка: змінна $SSH_AUTH_SOCK не встановлена або порожня\n");
        return -1;
    }

    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(fd);
        return -1;
    }
    return fd;
}

int main(void) {
    int fd = connect_agent();
    if (fd < 0) return 1;

    /* 1. Формуємо запит SSH_AGENTC_REQUEST_IDENTITIES */
    uint32_t req_len = htonl(1);
    uint8_t req_type = SSH_AGENTC_REQUEST_IDENTITIES;
    if (write_exact(fd, &req_len, 4) < 0 || write_exact(fd, &req_type, 1) < 0) {
        perror("Помилка відправки запиту ключів");
        close(fd);
        return 1;
    }

    /* 2. Зчитуємо довжину відповіді */
    uint32_t resp_len_net;
    if (read_exact(fd, &resp_len_net, 4) < 0) {
        perror("Помилка читання довжини відповіді");
        close(fd);
        return 1;
    }
    uint32_t resp_len = ntohl(resp_len_net);
    if (resp_len < 1) {
        fprintf(stderr, "Некоректний розмір відповіді агента\n");
        close(fd);
        return 1;
    }

    uint8_t *resp_buf = malloc(resp_len);
    if (!resp_buf) {
        perror("malloc");
        close(fd);
        return 1;
    }

    if (read_exact(fd, resp_buf, resp_len) < 0) {
        perror("Помилка читання тіла відповіді");
        free(resp_buf);
        close(fd);
        return 1;
    }

    uint8_t resp_type = resp_buf[0];
    if (resp_type != SSH_AGENT_IDENTITIES_ANSWER) {
        fprintf(stderr, "Агент повернув помилку або неочікуваний тип: %u\n", resp_type);
        free(resp_buf);
        close(fd);
        return 1;
    }

    if (resp_len < 5) {
        fprintf(stderr, "Пошкоджена відповідь агента\n");
        free(resp_buf);
        close(fd);
        return 1;
    }

    uint32_t nkeys = 0;
    memcpy(&nkeys, resp_buf + 1, 4);
    nkeys = ntohl(nkeys);
    printf("Завантажено ключів в ssh-agent: %u\n", nkeys);

    size_t offset = 5;
    uint8_t *first_key_blob = NULL;
    uint32_t first_key_len = 0;

    for (uint32_t i = 0; i < nkeys; ++i) {
        if (offset + 4 > resp_len) break;
        uint32_t klen;
        memcpy(&klen, resp_buf + offset, 4);
        klen = ntohl(klen);
        offset += 4;

        if (offset + klen > resp_len) break;
        const uint8_t *key_data = resp_buf + offset;
        offset += klen;

        if (i == 0) {
            first_key_len = klen;
            first_key_blob = malloc(klen);
            if (first_key_blob) memcpy(first_key_blob, key_data, klen);
        }

        if (offset + 4 > resp_len) break;
        uint32_t clen;
        memcpy(&clen, resp_buf + offset, 4);
        clen = ntohl(clen);
        offset += 4;

        if (offset + clen > resp_len) break;
        char *comment = malloc(clen + 1);
        if (comment) {
            memcpy(comment, resp_buf + offset, clen);
            comment[clen] = '\0';
            printf("  [Ключ #%u] Довжина: %u байтів, Коментар: \"%s\"\n", i + 1, klen, comment);
            free(comment);
        }
        offset += clen;
    }

    /* 3. Якщо знайдено хоча б один ключ — виконуємо тестовий підпис */
    if (first_key_blob && first_key_len > 0) {
        const char *challenge = "challenge_session_auth_data_payload_2026";
        uint32_t challenge_len = (uint32_t)strlen(challenge);
        uint32_t flags = 0; /* Прапорці за замовчуванням */

        /* Розрахунок довжини пакета SSH_AGENTC_SIGN_REQUEST:
           1 байт (код) + 4 (key_len) + first_key_len + 4 (data_len) + challenge_len + 4 (flags) */
        uint32_t sign_req_payload_len = 1 + 4 + first_key_len + 4 + challenge_len + 4;
        uint8_t *sign_buf = malloc(4 + sign_req_payload_len);
        if (sign_buf) {
            uint32_t net_sign_len = htonl(sign_req_payload_len);
            memcpy(sign_buf, &net_sign_len, 4);
            sign_buf[4] = SSH_AGENTC_SIGN_REQUEST;

            size_t pos = 5;
            uint32_t net_klen = htonl(first_key_len);
            memcpy(sign_buf + pos, &net_klen, 4); pos += 4;
            memcpy(sign_buf + pos, first_key_blob, first_key_len); pos += first_key_len;

            uint32_t net_dlen = htonl(challenge_len);
            memcpy(sign_buf + pos, &net_dlen, 4); pos += 4;
            memcpy(sign_buf + pos, challenge, challenge_len); pos += challenge_len;

            uint32_t net_flags = htonl(flags);
            memcpy(sign_buf + pos, &net_flags, 4); pos += 4;

            if (write_exact(fd, sign_buf, 4 + sign_req_payload_len) == 0) {
                uint32_t sign_resp_len_net;
                if (read_exact(fd, &sign_resp_len_net, 4) == 0) {
                    uint32_t sign_resp_len = ntohl(sign_resp_len_net);
                    uint8_t *sign_resp_buf = malloc(sign_resp_len);
                    if (sign_resp_buf && read_exact(fd, sign_resp_buf, sign_resp_len) == 0) {
                        if (sign_resp_buf[0] == SSH_AGENT_SIGN_RESPONSE) {
                            uint32_t sig_blob_len;
                            memcpy(&sig_blob_len, sign_resp_buf + 1, 4);
                            sig_blob_len = ntohl(sig_blob_len);
                            printf("Успішний підпис виклику агентом! Розмір підпису: %u байтів\n", sig_blob_len);
                        } else {
                            printf("Агент відхилив запит на підпис (можливо, потрібне підтвердження ssh-add -c)\n");
                        }
                        free(sign_resp_buf);
                    }
                }
            }
            free(sign_buf);
        }
        free(first_key_blob);
    }

    free(resp_buf);
    close(fd);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <stdexcept>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>

namespace ssh {

enum MessageType : uint8_t {
    AgentFailure = 5,
    AgentSuccess = 6,
    AgentcRequestIdentities = 11,
    AgentIdentitiesAnswer = 12,
    AgentcSignRequest = 13,
    AgentSignResponse = 14
};

/* RAII-обгортка дескриптора сокета */
class UnixSocket {
public:
    explicit UnixSocket(int fd) : fd_(fd) {
        if (fd_ < 0) throw std::system_error(errno, std::generic_category(), "Невалідний сокет");
    }

    ~UnixSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    UnixSocket(const UnixSocket&) = delete;
    UnixSocket& operator=(const UnixSocket&) = delete;

    UnixSocket(UnixSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UnixSocket& operator=(UnixSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void writeExact(std::span<const uint8_t> data) const {
        size_t total = 0;
        while (total < data.size()) {
            ssize_t w = ::write(fd_, data.data() + total, data.size() - total);
            if (w < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "write error");
            }
            total += static_cast<size_t>(w);
        }
    }

    void readExact(std::span<uint8_t> buffer) const {
        size_t total = 0;
        while (total < buffer.size()) {
            ssize_t r = ::read(fd_, buffer.data() + total, buffer.size() - total);
            if (r < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "read error");
            }
            if (r == 0) throw std::runtime_error("Передчасний розрив з'єднання з агентом");
            total += static_cast<size_t>(r);
        }
    }

private:
    int fd_{-1};
};

struct KeyIdentity {
    std::vector<uint8_t> blob;
    std::string comment;
};

class AgentClient {
public:
    static AgentClient connect() {
        const char* sockPath = std::getenv("SSH_AUTH_SOCK");
        if (!sockPath || std::strlen(sockPath) == 0) {
            throw std::runtime_error("Змінна середовища $SSH_AUTH_SOCK не встановлена");
        }

        int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        struct sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, sockPath, sizeof(addr.sun_path) - 1);

        if (::connect(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "connect() failed");
        }

        return AgentClient(UnixSocket(fd));
    }

    std::vector<KeyIdentity> requestIdentities() const {
        // Відправляємо запит
        uint32_t reqLen = htonl(1);
        uint8_t reqType = MessageType::AgentcRequestIdentities;

        std::vector<uint8_t> reqPacket(5);
        std::memcpy(reqPacket.data(), &reqLen, 4);
        reqPacket[4] = reqType;
        socket_.writeExact(reqPacket);

        // Читаємо довжину відповіді
        uint32_t respLenNet = 0;
        socket_.readExact(std::span<uint8_t>(reinterpret_cast<uint8_t*>(&respLenNet), 4));
        uint32_t respLen = ntohl(respLenNet);

        if (respLen < 5) throw std::runtime_error("Некоректний розмір відповіді від агента");

        std::vector<uint8_t> respPayload(respLen);
        socket_.readExact(respPayload);

        if (respPayload[0] != MessageType::AgentIdentitiesAnswer) {
            throw std::runtime_error("Агент повернув неочікуваний тип або помилку");
        }

        uint32_t nkeys = 0;
        std::memcpy(&nkeys, respPayload.data() + 1, 4);
        nkeys = ntohl(nkeys);

        std::vector<KeyIdentity> keys;
        keys.reserve(nkeys);

        size_t offset = 5;
        for (uint32_t i = 0; i < nkeys && offset + 4 <= respPayload.size(); ++i) {
            uint32_t klen = 0;
            std::memcpy(&klen, respPayload.data() + offset, 4);
            klen = ntohl(klen);
            offset += 4;

            if (offset + klen > respPayload.size()) break;
            std::vector<uint8_t> keyBlob(respPayload.begin() + offset, respPayload.begin() + offset + klen);
            offset += klen;

            if (offset + 4 > respPayload.size()) break;
            uint32_t clen = 0;
            std::memcpy(&clen, respPayload.data() + offset, 4);
            clen = ntohl(clen);
            offset += 4;

            if (offset + clen > respPayload.size()) break;
            std::string comment(reinterpret_cast<const char*>(respPayload.data() + offset), clen);
            offset += clen;

            keys.push_back({std::move(keyBlob), std::move(comment)});
        }

        return keys;
    }

    std::vector<uint8_t> signData(std::span<const uint8_t> keyBlob, std::span<const uint8_t> data, uint32_t flags = 0) const {
        uint32_t payloadLen = 1 + 4 + keyBlob.size() + 4 + data.size() + 4;
        std::vector<uint8_t> reqPacket;
        reqPacket.reserve(4 + payloadLen);

        uint32_t netPayloadLen = htonl(payloadLen);
        reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netPayloadLen), reinterpret_cast<uint8_t*>(&netPayloadLen) + 4);
        reqPacket.push_back(MessageType::AgentcSignRequest);

        auto appendField = [&reqPacket](std::span<const uint8_t> bytes) {
            uint32_t netLen = htonl(static_cast<uint32_t>(bytes.size()));
            reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netLen), reinterpret_cast<uint8_t*>(&netLen) + 4);
            reqPacket.insert(reqPacket.end(), bytes.begin(), bytes.end());
        };

        appendField(keyBlob);
        appendField(data);

        uint32_t netFlags = htonl(flags);
        reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netFlags), reinterpret_cast<uint8_t*>(&netFlags) + 4);

        socket_.writeExact(reqPacket);

        uint32_t respLenNet = 0;
        socket_.readExact(std::span<uint8_t>(reinterpret_cast<uint8_t*>(&respLenNet), 4));
        uint32_t respLen = ntohl(respLenNet);

        std::vector<uint8_t> respPayload(respLen);
        socket_.readExact(respPayload);

        if (respPayload.empty() || respPayload[0] != MessageType::AgentSignResponse) {
            throw std::runtime_error("Операція підпису була відхилена агентом");
        }

        if (respPayload.size() < 5) throw std::runtime_error("Пошкоджений підпис агента");

        uint32_t sigLen = 0;
        std::memcpy(&sigLen, respPayload.data() + 1, 4);
        sigLen = ntohl(sigLen);

        return std::vector<uint8_t>(respPayload.begin() + 5, respPayload.begin() + 5 + sigLen);
    }

private:
    explicit AgentClient(UnixSocket socket) : socket_(std::move(socket)) {}
    UnixSocket socket_;
};

} // namespace ssh

int main() {
    try {
        auto client = ssh::AgentClient::connect();
        auto keys = client.requestIdentities();

        std::cout << "Завантажено ключів в ssh-agent: " << keys.size() << "\n";
        for (size_t i = 0; i < keys.size(); ++i) {
            std::cout << "  [Ключ #" << (i + 1) << "] Розмір: " << keys[i].blob.size()
                      << " байтів, Коментар: \"" << keys[i].comment << "\"\n";
        }

        if (!keys.empty()) {
            std::string challenge = "challenge_session_auth_data_payload_2026";
            std::span<const uint8_t> challengeData(reinterpret_cast<const uint8_t*>(challenge.data()), challenge.size());

            auto signature = client.signData(keys[0].blob, challengeData);
            std::cout << "Успішний цифровий підпис отримано! Довжина підпису: " << signature.size() << " байтів.\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 4. Збирання, виконання та інспекція сокета

Для компіляції та перевірки роботи програми в системі Linux скористайтеся стандартними компіляторами GCC або Clang:

```bash
# Збирання версії на C:
gcc -Wall -Wextra -O2 proj-agent-client.c -o agent-client-c

# Збирання версії на C++ (стандарт C++20):
g++ -std=c++20 -Wall -Wextra -O2 proj-agent-client.cpp -o agent-client-cpp
```

### Перевірка активного стану агента

Перед запуском програми переконайтеся, що демон `ssh-agent` запущено, змінна `$SSH_AUTH_SOCK` доступна, а в пам'ять завантажено тестовий ключ:

```bash
# 1. Перевірка сокета
ls -la "$SSH_AUTH_SOCK"

# 2. Додавання ключа Ed25519
ssh-add ~/.ssh/id_ed25519

# 3. Запуск зібраного клієнта
./agent-client-cpp
```

Приклад очікуваного термінального виводу:

```
Завантажено ключів в ssh-agent: 1
  [Ключ #1] Розмір: 51 байтів, Коментар: "andrij@laptop-2026"
Успішний цифровий підпис отримано! Довжина підпису: 83 байтів.
```

---

## 5. Підводні камені та типові помилки реалізації

Під час проектування клієнтів протоколу агента інженери найчастіше стикаються з трьома критичними крайовими випадками:

1. **Фрагментація потоку та зміщення вказівників:**
   Ніколи не припускайте, що один системний виклик `read()` поверне весь кадр відповіді. Завжди використовуйте суворий цикл накопичення байтів `read_exact()`, який перевіряє лічильник прочитаних даних і повторює читання до вичерпання очікуваного розміру пакета.
2. **Мережевий порядок байтів і переповнення буферів:**
   Усі числові поля довжини (`uint32_t`) повинні обов'язково конвертуватися функціями `htonl()` при формуванні запиту та `ntohl()` при розборі. Якщо на архітектурі x86 пропустити виклик `ntohl()`, числове значення довжини `1` буде сприйнято як `16777216` байтів, що призведе до спроби виділення гігабайтних буферів через `malloc()` або падіння програми з помилкою `std::bad_alloc`.
3. **Обробка таймаутів та інтерактивного підтвердження (`SSH_ASKPASS`):**
   Якщо ключ було завантажено з прапорцем `ssh-add -c`, демон `ssh-agent` не повертає підпис негайно, а блокує читання сокета доти, доки користувач не натисне кнопку згоди в діалоговому вікні. Клієнтська програма не повинна встановлювати надто агресивні короткі сокетні таймаути (`SO_RCVTIMEO`), інакше операція буде розірвана до того, як людина встигне підтвердити дію. Якщо користувач відхилить підтвердження, агент поверне байт `SSH_AGENT_FAILURE` (`5`), який необхідно обробляти як відхилення авторизації, а не як мережевий збій.
