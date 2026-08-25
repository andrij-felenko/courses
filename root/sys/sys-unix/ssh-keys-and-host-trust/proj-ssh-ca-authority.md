# ⚙️ Автоматизація інфраструктури SSH Certificate Authority

Традиційне розгортання публічних ключів у файли `~/.ssh/authorized_keys` на сотнях хостів створює непереборний операційний тягар: звільнення розробника або компрометація ноутбука вимагає виконання синхронізаційних скриптів по всьому парку серверів, а додавання нових віртуальних машин спричиняє шквал попереджень TOFU у користувачів. Архітектура SSH Certificate Authority (SSH CA) розв'язує цю проблему, замінюючи статичні списки ключів криптографічно підписаними сертифікатами з обмеженим часом життя (TTL) та фіксованими іменами облікових записів (principals).

Нижче наведено робочий конвеєр для створення двох незалежних центрів сертифікації (Host CA та User CA), автоматизації випуску короткоживучих сертифікатів інженерів, конфігурації серверів і клієнтів, а також інженерну утиліту аналізу внутрішньої двійкової структури SSH-сертифікатів на мовах C та C++.

## 1. Архітектурні засади та створення ключів Центрів Сертифікації

Центри сертифікації користувачів і хостів мають бути фізично та логічно розділені. Ключ Host CA використовується лише для підпису публічних ключів серверів (виконується рідко, під час введення машини в експлуатацію). Ключ User CA використовується для регулярного підпису ключів розробників (автоматизований сервіс SSO/Vault з жорстким аудитом).

Розділення ключів гарантує, що компрометація сервісу видачі користувацьких сертифікатів не дозволить зловмиснику підробити ідентичність цільових серверів для перехоплення трафіку, і навпаки.

```bash
#!/usr/bin/env bash
set -euo pipefail

CA_DIR="/etc/ssh/ca"
mkdir -p "${CA_DIR}"
chmod 700 "${CA_DIR}"

# 1. Генерація кореневого ключа Host CA
ssh-keygen -t ed25519 -a 100 -f "${CA_DIR}/ssh_host_ca" \
    -C "CA-HOST-INFRASTRUCTURE-PROD" -N ""

# 2. Генерація кореневого ключа User CA
ssh-keygen -t ed25519 -a 100 -f "${CA_DIR}/ssh_user_ca" \
    -C "CA-USER-DEVELOPERS-PROD" -N ""

chmod 600 "${CA_DIR}/ssh_host_ca" "${CA_DIR}/ssh_user_ca"
chmod 644 "${CA_DIR}/ssh_host_ca.pub" "${CA_DIR}/ssh_user_ca.pub"
```

Кореневі закриті ключі CA повинні зберігатися на захищених серверах з обмеженим доступом або в апаратних модулях безпеки (HSM). Для автоматизованого середовища ключ User CA монтується в пам'ять сервісу генерації сертифікатів, тоді як ключ Host CA залишається офлайн і використовується лише адміністраторами інфраструктури під час введення нових нод.

## 2. Підпис хост-ключів серверів (Host CA)

Коли новий сервер розгортається, його публічний хост-ключ передається на CA для підпису. Сертифікат закріплює дозволені доменні імена та IP-адреси машини у полі `principals`.

```bash
#!/usr/bin/env bash
set -euo pipefail

HOST_PUB="/etc/ssh/ssh_host_ed25519_key.pub"
CA_KEY="/etc/ssh/ca/ssh_host_ca"
HOST_ID="srv-db-prod-01"
PRINCIPALS="srv-db-prod-01,srv-db-prod-01.infra.company.com,10.20.0.15"

# Підпис хост-сертифіката (-h вказує тип host certificate)
ssh-keygen -s "${CA_KEY}" \
    -I "${HOST_ID}" \
    -h \
    -n "${PRINCIPALS}" \
    -V "+365d" \
    "${HOST_PUB}"

# Результат: згенеровано файл /etc/ssh/ssh_host_ed25519_key-cert.pub
chmod 644 /etc/ssh/ssh_host_ed25519_key-cert.pub
```

Налаштування на цільовому сервері у `/etc/ssh/sshd_config`:

```text
# Шлях до сертифіката сервера
HostCertificate /etc/ssh/ssh_host_ed25519_key-cert.pub

# Довіра до сертифікатів інженерів, підписаних User CA
TrustedUserCAKeys /etc/ssh/ssh_user_ca.pub
```

Налаштування на клієнтських робочих станціях у `~/.ssh/known_hosts`:

```text
@cert-authority *.infra.company.com,10.20.0.* ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... (вміст ssh_host_ca.pub)
```

Тепер кожен інженер без жодного діалогового вікна TOFU безпечно підключається до будь-якого з тисяч серверів домену `infra.company.com`. Якщо зловмисник спробує підробити IP або DNS-запис сервера, клієнт відхилить з'єднання, оскільки сертифікат зловмисника не матиме валідного підпису Host CA або його `principals` не міститимуть імені цільового хоста.

## 3. Генерація короткоживучих сертифікатів для користувачів

Інженер генерує локальну пару ключів `~/.ssh/id_ed25519` та надає публічний ключ `id_ed25519.pub` корпоративному сервісу автентифікації. Сервіс перевіряє право доступу (наприклад, через LDAP/SSO з MFA) і генерує сертифікат з терміном дії 8 годин:

```bash
#!/usr/bin/env bash
set -euo pipefail

USER_PUB="id_ed25519.pub"
CA_KEY="/etc/ssh/ca/ssh_user_ca"
KEY_ID="bohdan.felenko@company.com"
SERIAL="10492"
PRINCIPALS="bohdan,ubuntu,deploy"
VALIDITY="+8h"

ssh-keygen -s "${CA_KEY}" \
    -I "${KEY_ID}" \
    -z "${SERIAL}" \
    -n "${PRINCIPALS}" \
    -V "${VALIDITY}" \
    -O no-agent-forwarding \
    -O no-x11-forwarding \
    "${USER_PUB}"

# Згенеровано файл id_ed25519-cert.pub
```

Користувач підключається як `ssh ubuntu@srv-db-prod-01.infra.company.com`. Клієнт SSH автоматично знаходить `id_ed25519-cert.pub` поруч із приватним ключем, передає сертифікат серверу під час `SSH_MSG_USERAUTH_REQUEST`, і сервер пускає користувача, оскільки сертифікат завірений довіреним `TrustedUserCAKeys`.

### Синхронізація часу та граничні випадки TTL

Використання короткоживучих сертифікатів вимагає точної синхронізації часу на всіх вузлах мережі. Якщо системний годинник на сервері або клієнтській машині відхиляється більш ніж на кілька секунд, сертифікат може вважатися недійсним (`certificate is not yet valid` або `certificate has expired`).

Рекомендації щодо налаштування часу:
1. Усі вузли інфраструктури повинні синхронізуватися за протоколом NTP через локальні демони `chrony` або `systemd-timesyncd`.
2. При підписі сертифіката рекомендується встановлювати час початку дії з невеликим запасом у минуле (наприклад, `-V -5m:+8h`), щоб нівелювати допустимий розсинхрон годинників (clock skew).

## 4. Відкликання сертифікатів (Key Revocation List)

Якщо ноутбук інженера втрачено або зафіксовано підозрілу активність до закінчення 8-годинного терміну дії, CA генерує або оновлює двійковий список відкликаних ключів (KRL):

```bash
#!/usr/bin/env bash
set -euo pipefail

KRL_FILE="/etc/ssh/revoked_keys.krl"

# Створення або оновлення списку KRL за сертифікатом
ssh-keygen -k -f "${KRL_FILE}" -u id_ed25519-cert.pub

# Або відкликання за серійним номером та публічним ключем CA
# ssh-keygen -k -f "${KRL_FILE}" -s /etc/ssh/ca/ssh_user_ca.pub -z 10492
```

У конфігурації `/etc/ssh/sshd_config` сервера активується директива:

```text
RevokedKeys /etc/ssh/revoked_keys.krl
```

Файл KRL є компактною двійковою структурою (біт-вектором), що дозволяє `sshd` виконувати перевірку відкликання за частки мікросекунди без створення мережевих запитів до онлайн-серверів OCSP.

## 5. Програмний розбір двійкової структури SSH-сертифіката

Формат сертифіката OpenSSH описано у специфікації `PROTOCOL.certkeys`. Сертифікат є послідовністю полів у двійковому кодуванні SSH wire format:
- `string`: тип відкритого ключа (`ssh-ed25519-cert-v01@openssh.com`)
- `string`: 32 байти nonce (випадкове число)
- `string`: відкритий ключ суб'єкта (для ed25519 — 32 байти)
- `uint64`: серійний номер сертифіката (Big-Endian)
- `uint32`: тип сертифіката (1 = SSH2_CERT_TYPE_USER, 2 = SSH2_CERT_TYPE_HOST)
- `string`: ідентифікатор ключа (Key ID / опис)
- `string`: вкладений блок дозволених імен (principals)
- `uint64`: valid_after (Unix timestamp)
- `uint64`: valid_before (Unix timestamp)
- `string`: критичні опції (critical options)
- `string`: розширення (extensions)
- `string`: зарезервоване поле
- `string`: відкритий ключ центру сертифікації (CA key)
- `string`: криптографічний підпис сертифіката

Усі цілочисельні поля кодуються у мережевому порядку байтів (Big-Endian). Часові позначки `valid_after` та `valid_before` представлені 64-бітними беззнаковими цілими числами секунд від початку епохи Unix (1970-01-01 00:00:00 UTC), що унеможливлює проблему 2038 року (Y2038).

Поле `principals` містить вкладений серіалізований блок: перші 4 байти задають загальну довжину блоку, після чого йдуть послідовні рядки формату `[uint32_len][bytes]`. Парсер зобов'язаний виконувати строгу перевірку меж пам'яті перед кожним читанням, запобігаючи вразливостям виходу за межі буфера (buffer over-read).

Нижче наведено утиліту для декодування та інспекції двійкового сертифіката OpenSSH на мовах C та C++. Реалізація на C використовує структуру `BufferReader` з суворою перевіркою меж буфера, а реалізація на C++ демонструє сучасний ідіоматичний підхід стандарту C++20 на базі `std::span`, `std::string_view` та `std::expected`.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>

typedef struct {
    const uint8_t *data;
    size_t len;
    size_t offset;
} BufferReader;

static int read_uint32(BufferReader *r, uint32_t *out) {
    if (r->offset + 4 > r->len) return 0;
    uint32_t val;
    memcpy(&val, r->data + r->offset, 4);
    *out = ntohl(val);
    r->offset += 4;
    return 1;
}

static int read_uint64(BufferReader *r, uint64_t *out) {
    if (r->offset + 8 > r->len) return 0;
    uint32_t high, low;
    memcpy(&high, r->data + r->offset, 4);
    memcpy(&low, r->data + r->offset + 4, 4);
    *out = ((uint64_t)ntohl(high) << 32) | ntohl(low);
    r->offset += 8;
    return 1;
}

static int read_string(BufferReader *r, const char **str_out, uint32_t *len_out) {
    uint32_t length;
    if (!read_uint32(r, &length)) return 0;
    if (r->offset + length > r->len) return 0;
    *str_out = (const char *)(r->data + r->offset);
    *len_out = length;
    r->offset += length;
    return 1;
}

int inspect_ssh_certificate(const uint8_t *raw_cert, size_t cert_len) {
    BufferReader reader = { .data = raw_cert, .len = cert_len, .offset = 0 };

    const char *cert_type_str;
    uint32_t cert_type_len;
    if (!read_string(&reader, &cert_type_str, &cert_type_len)) {
        fprintf(stderr, "Помилка читання типу сертифіката\n");
        return -1;
    }
    printf("Тип сертифіката: %.*s\n", (int)cert_type_len, cert_type_str);

    const char *nonce;
    uint32_t nonce_len;
    if (!read_string(&reader, &nonce, &nonce_len)) return -1;

    const char *pubkey_bytes;
    uint32_t pubkey_len;
    if (!read_string(&reader, &pubkey_bytes, &pubkey_len)) return -1;

    uint64_t serial;
    if (!read_uint64(&reader, &serial)) return -1;
    printf("Серійний номер: %llu\n", (unsigned long long)serial);

    uint32_t cert_kind;
    if (!read_uint32(&reader, &cert_kind)) return -1;
    printf("Призначення: %s (%u)\n", 
           (cert_kind == 1) ? "USER CERTIFICATE" : 
           (cert_kind == 2) ? "HOST CERTIFICATE" : "UNKNOWN", cert_kind);

    const char *key_id;
    uint32_t key_id_len;
    if (!read_string(&reader, &key_id, &key_id_len)) return -1;
    printf("Key ID: %.*s\n", (int)key_id_len, key_id);

    const char *principals_blob;
    uint32_t principals_blob_len;
    if (!read_string(&reader, &principals_blob, &principals_blob_len)) return -1;

    printf("Principals (дозволені облікові записи):\n");
    BufferReader princ_reader = {
        .data = (const uint8_t *)principals_blob,
        .len = principals_blob_len,
        .offset = 0
    };
    while (princ_reader.offset < princ_reader.len) {
        const char *p_str;
        uint32_t p_len;
        if (!read_string(&princ_reader, &p_str, &p_len)) break;
        printf("  - %.*s\n", (int)p_len, p_str);
    }

    uint64_t valid_after, valid_before;
    if (!read_uint64(&reader, &valid_after) || !read_uint64(&reader, &valid_before)) return -1;

    time_t t_after = (time_t)valid_after;
    time_t t_before = (time_t)valid_before;
    char buf_after[64], buf_before[64];
    strftime(buf_after, sizeof(buf_after), "%Y-%m-%d %H:%M:%S UTC", gmtime(&t_after));
    strftime(buf_before, sizeof(buf_before), "%Y-%m-%d %H:%M:%S UTC", gmtime(&t_before));

    printf("Діє з: %s (ts=%llu)\n", buf_after, (unsigned long long)valid_after);
    printf("Діє до: %s (ts=%llu)\n", buf_before, (unsigned long long)valid_before);

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <cstdint>
#include <chrono>
#include <format>
#include <expected>
#include <bit>

enum class ParseError {
    UnexpectedEndOfBuffer,
    InvalidCertificateFormat,
};

class WireReader {
public:
    explicit WireReader(std::span<const uint8_t> buffer) : buffer_(buffer), offset_(0) {}

    std::expected<uint32_t, ParseError> read_uint32() {
        if (offset_ + 4 > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);
        uint32_t val = (static_cast<uint32_t>(buffer_[offset_]) << 24) |
                       (static_cast<uint32_t>(buffer_[offset_ + 1]) << 16) |
                       (static_cast<uint32_t>(buffer_[offset_ + 2]) << 8) |
                       static_cast<uint32_t>(buffer_[offset_ + 3]);
        offset_ += 4;
        return val;
    }

    std::expected<uint64_t, ParseError> read_uint64() {
        auto high = read_uint32();
        if (!high) return std::unexpected(high.error());
        auto low = read_uint32();
        if (!low) return std::unexpected(low.error());
        return (static_cast<uint64_t>(*high) << 32) | static_cast<uint64_t>(*low);
    }

    std::expected<std::string_view, ParseError> read_string() {
        auto len = read_uint32();
        if (!len) return std::unexpected(len.error());
        if (offset_ + *len > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);
        
        std::string_view view(reinterpret_cast<const char*>(buffer_.data() + offset_), *len);
        offset_ += *len;
        return view;
    }

    std::expected<std::span<const uint8_t>, ParseError> read_blob() {
        auto len = read_uint32();
        if (!len) return std::unexpected(len.error());
        if (offset_ + *len > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);

        std::span<const uint8_t> sub(buffer_.data() + offset_, *len);
        offset_ += *len;
        return sub;
    }

    [[nodiscard]] bool empty() const noexcept { return offset_ >= buffer_.size(); }

private:
    std::span<const uint8_t> buffer_;
    size_t offset_;
};

struct SshCertificate {
    std::string_view key_type;
    uint64_t serial{};
    uint32_t cert_type{};
    std::string_view key_id;
    std::vector<std::string_view> principals;
    std::chrono::system_clock::time_point valid_after;
    std::chrono::system_clock::time_point valid_before;
};

std::expected<SshCertificate, ParseError> parse_ssh_certificate(std::span<const uint8_t> raw_bytes) {
    WireReader reader(raw_bytes);
    SshCertificate cert;

    auto key_type = reader.read_string();
    if (!key_type) return std::unexpected(key_type.error());
    cert.key_type = *key_type;

    if (!reader.read_blob()) return std::unexpected(ParseError::UnexpectedEndOfBuffer); // nonce
    if (!reader.read_blob()) return std::unexpected(ParseError::UnexpectedEndOfBuffer); // pubkey

    auto serial = reader.read_uint64();
    if (!serial) return std::unexpected(serial.error());
    cert.serial = *serial;

    auto ctype = reader.read_uint32();
    if (!ctype) return std::unexpected(ctype.error());
    cert.cert_type = *ctype;

    auto kid = reader.read_string();
    if (!kid) return std::unexpected(kid.error());
    cert.key_id = *kid;

    auto princ_blob = reader.read_blob();
    if (!princ_blob) return std::unexpected(princ_blob.error());

    WireReader princ_reader(*princ_blob);
    while (!princ_reader.empty()) {
        auto p = princ_reader.read_string();
        if (!p) break;
        cert.principals.push_back(*p);
    }

    auto after = reader.read_uint64();
    auto before = reader.read_uint64();
    if (!after || !before) return std::unexpected(ParseError::UnexpectedEndOfBuffer);

    cert.valid_after = std::chrono::system_clock::time_point(std::chrono::seconds(*after));
    cert.valid_before = std::chrono::system_clock::time_point(std::chrono::seconds(*before));

    return cert;
}

void print_certificate_info(const SshCertificate& cert) {
    std::cout << "Тип сертифіката: " << cert.key_type << "\n"
              << "Серійний номер: " << cert.serial << "\n"
              << "Призначення: " << (cert.cert_type == 1 ? "USER" : "HOST") << "\n"
              << "Key ID: " << cert.key_id << "\n"
              << "Principals:\n";
    for (const auto& p : cert.principals) {
        std::cout << "  - " << p << "\n";
    }
}
```
:::
