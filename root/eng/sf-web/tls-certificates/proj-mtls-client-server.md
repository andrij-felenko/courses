# ⚙️ Практичний стенд mTLS: генерація PKI та клієнт-серверний зв'язок

Взаємна автентифікація на транспортному рівні (mTLS) вимагає суворого узгодження криптографічних сертифікатів з обох сторін з'єднання. На практиці більшість інженерних збоїв у розподілених системах та мікросервісних архітектурах виникає через тонкі помилки конфігурації: відсутність розширення `Subject Alternative Name` у серверному сертифікаті, пропуск розширення `Extended Key Usage: clientAuth` у клієнтському сертифікаті або некоректні обмеження `Basic Constraints` у проміжних центрах сертифікації.

У цьому практичному стенді ми розгорнемо власний локальний центр сертифікації (CA), згенеруємо валідні сертифікати стандарту X.509 v3 з усіма обов'язковими розширеннями безпеки та створимо повноцінний взаємно автентифікований зв'язок мовами Python та C/C++.

## Крок 1. Проєктування та генерація тестового PKI

Для коректної роботи сучасних TLS-стеків усі сертифікати повинні містити явні метадані версії 3. Якщо серверний сертифікат містить домен лише в застарілому полі `Common Name` (CN), сучасні клієнти (Python 3.7+, OpenSSL 1.1.1+, Chrome) негайно розірвуть з'єднання з помилкою `Hostname mismatch`. Аналогічно, якщо клієнтський сертифікат не має розширення `clientAuth`, сервер відхилить його з кодом `INVALID_PURPOSE`.

Створимо конфігураційний файл `pki.cnf`, який чітко розмежовує профілі для кореневого центру, сервера та клієнта:

```ini
[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = req_distinguished_name
prompt              = no

[ req_distinguished_name ]
C  = UA
O  = TestLab
CN = TestLab Root CA

[ v3_ca ]
# Кореневий CA зобов'язаний бути CA:TRUE з критичним прапорцем
basicConstraints        = critical, CA:TRUE
keyUsage                = critical, digitalSignature, cRLSign, keyCertSign
subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always,issuer

[ v3_server ]
# Кінцевий сервер має CA:FALSE та призначення serverAuth
basicConstraints        = critical, CA:FALSE
keyUsage                = critical, digitalSignature, keyEncipherment
extendedKeyUsage        = serverAuth
subjectAltName          = @alt_names_server

[ alt_names_server ]
DNS.1   = localhost
DNS.2   = server.local
IP.1    = 127.0.0.1

[ v3_client ]
# Клієнтський сертифікат mTLS має призначення clientAuth
basicConstraints        = critical, CA:FALSE
keyUsage                = critical, digitalSignature
extendedKeyUsage        = clientAuth
subjectAltName          = @alt_names_client

[ alt_names_client ]
DNS.1   = client.local
email.1 = client@testlab.local
```

### Покрокове виконання команд OpenSSL

Розглянемо призначення кожного прапорця в процесі генерації криптографічних матеріалів:

1. **Генерація пари ключів та сертифіката Root CA:**
   Прапорець `-x509` вказує утиліті створити самопідписаний кореневий сертифікат замість запиту на підпис (CSR). Опція `-nodes` (англ. *no DES*) створює приватний ключ без парольної фрази для автоматизованого використання на тестовому стенді. Опція `-extensions v3_ca` підключає секцію з розширенням `Basic Constraints: CA: TRUE`, що дає центру право підписувати підлеглі сертифікати.

   ```bash
   openssl genrsa -out ca.key 2048
   openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 \
       -config pki.cnf -extensions v3_ca -out ca.crt
   ```

2. **Створення запиту та підпис сертифіката сервера:**
   Сервер генерує власний приватний ключ `server.key` та запит на підпис `server.csr`. Потім кореневий центр підписує цей запит командою `openssl x509 -req`, підставляючи розширення з секції `v3_server`. Прапорець `-CAcreateserial` створює службовий файл `ca.srl` для відстеження унікальних серійних номерів випущених сертифікатів, що запобігає колізіям серійників у кеші браузерів та OpenSSL.

   ```bash
   openssl genrsa -out server.key 2048
   openssl req -new -key server.key -out server.csr \
       -subj "/C=UA/O=TestLab/CN=localhost"
   openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
       -out server.crt -days 365 -sha256 -extfile pki.cnf -extensions v3_server
   ```

3. **Створення запиту та підпис сертифіката клієнта:**
   Аналогічна процедура виконується для клієнтського ключа, але з використанням секції `v3_client`, яка наділяє сертифікат правом `extendedKeyUsage = clientAuth` та встановлює альтернативне ім'я клієнта `client.local`.

   ```bash
   openssl genrsa -out client.key 2048
   openssl req -new -key client.key -out client.csr \
       -subj "/C=UA/O=TestLab/CN=client.local"
   openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
       -out client.crt -days 365 -sha256 -extfile pki.cnf -extensions v3_client
   ```

## Крок 2. Реалізація mTLS сервера на Python

Сервер створює `ssl.SSLContext`, налаштовує режим обов'язкової клієнтської автентифікації `verify_mode = ssl.CERT_REQUIRED` та завантажує спільний `ca.crt`. 

Під час підключення клієнта функція `wrap_socket` виконує TLS-рукостискання до того, як запит потрапить до обробника HTTP. Якщо клієнт не надав сертифікат або надав недійсний підпис, з'єднання обривається на транспортному рівні без виклику `do_GET`. У разі успіху обробник витягує ідентичність клієнта безпосередньо з розібраної структури X.509 через `getpeercert()`, що дозволяє прив'язати авторизацію користувача до сертифіката.

```python
import socket
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer


class MTLSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отримуємо розібраний сертифікат клієнта відкритого TLS-сокета
        client_cert = self.connection.getpeercert()
        subject = dict(x[0] for x in client_cert.get('subject', []))
        common_name = subject.get('commonName', 'Unknown')

        body = f"mTLS автентифікація успішна! Привіт, {common_name}\n".encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port=8443):
    # Контекст для перевірки клієнтів (SERVER_AUTH для сервера, що приймає з'єднання)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Завантажуємо власний сертифікат сервера та його приватний ключ
    ctx.load_cert_chain(certfile="server.crt", keyfile="server.key")
    # Встановлюємо довірений Root CA для перевірки сертифікатів клієнтів
    ctx.load_verify_locations(cafile="ca.crt")
    # Вимагаємо обов'язкового надання валідного клієнтського сертифіката
    ctx.verify_mode = ssl.CERT_REQUIRED

    server = HTTPServer(('localhost', port), MTLSHandler)
    # Обгортаємо звичайний TCP сокет у захищений TLS шар
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"[*] mTLS HTTPS сервер слухає https://localhost:{port}")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
```

## Крок 3. Реалізація mTLS клієнта (Python та C/C++)

Клієнтська програма повинна одночасно виконати дві задачі: надати власний сертифікат і приватний ключ у відповідь на запит `CertificateRequest` сервера, а також самостійно перевірити сертифікат сервера за допомогою локального кореневого сертифіката `ca.crt`.

### Реалізація на Python (urllib та requests)

У стандартній бібліотеці `urllib.request` клієнтський SSL-контекст передається через параметр `context`. У популярній бібліотеці `requests` для mTLS використовується параметр `cert`, який приймає кортеж зі шляхів до файлу відкритого сертифіката та приватного ключа:

```python
import urllib.request
import ssl
import requests


def mtls_urllib_request(url="https://localhost:8443/"):
    # Створюємо контекст клієнта та завантажуємо кореневий CA для перевірки сервера
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="ca.crt")
    # Завантажуємо клієнтський сертифікат і приватний ключ для mTLS
    ctx.load_cert_chain(certfile="client.crt", keyfile="client.key")
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx) as response:
        print(f"[urllib] Статус: {response.status}")
        print("[urllib] Тіло відповіді:", response.read().decode('utf-8'))


def mtls_requests_client(url="https://localhost:8443/"):
    # Бібліотека requests приймає пару (cert, key) для клієнтської автентифікації
    resp = requests.get(
        url,
        verify="ca.crt",
        cert=("client.crt", "client.key")
    )
    print(f"[requests] Статус: {resp.status_code}")
    print(f"[requests] Тіло: {resp.text}")


if __name__ == '__main__':
    mtls_urllib_request()
    mtls_requests_client()
```

### Системна реалізація клієнта: C та C++ на базі OpenSSL

У системному програмуванні життєвий цикл захищеного з'єднання будується з чіткої послідовності кроків:
1. Ініціалізація та налаштування `SSL_CTX`: завантаження бандла довірених CA через `SSL_CTX_load_verify_locations` та встановлення клієнтського сертифіката й ключа.
2. Валідація зв'язку між ключем і сертифікатом: виклик `SSL_CTX_check_private_key(ctx)` перевіряє, чи дійсно відкритий ключ у сертифікаті збігається з наданим приватним ключем, запобігаючи падінням під час виконання рукостискання.
3. Створення сокета `socket()`, резолв DNS та підключення `connect()` до віддаленої IP-адреси.
4. Асоціація файлового дескриптора з об'єктом `SSL` через `SSL_set_fd()` та встановлення імені хоста для SNI через `SSL_set_tlsext_host_name()`.
5. Виконання рукостискання `SSL_connect()`: обмін повідомленнями, верифікація сертифіката сервера, надсилання клієнтського сертифіката та підтвердження `CertificateVerify`.
6. Зашифрований обмін через `SSL_write()` та `SSL_read()`.
7. Коректне завершення через `SSL_shutdown()` (надсилання TLS Alert `close_notify`) та звільнення ресурсів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

int main(void) {
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();

    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        fprintf(stderr, "Помилка створення SSL_CTX\n");
        return 1;
    }

    /* Вмикаємо перевірку сервера та завантажуємо CA бандл */
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, NULL);
    if (!SSL_CTX_load_verify_locations(ctx, "ca.crt", NULL)) {
        fprintf(stderr, "Помилка завантаження ca.crt\n");
        SSL_CTX_free(ctx);
        return 1;
    }

    /* Завантажуємо клієнтський сертифікат та приватний ключ для mTLS */
    if (SSL_CTX_use_certificate_chain_file(ctx, "client.crt") <= 0 ||
        SSL_CTX_use_PrivateKey_file(ctx, "client.key", SSL_FILETYPE_PEM) <= 0 ||
        !SSL_CTX_check_private_key(ctx)) {
        fprintf(stderr, "Помилка завантаження клієнтського сертифіката чи ключа\n");
        SSL_CTX_free(ctx);
        return 1;
    }

    /* Встановлюємо перевірку імені хоста в SAN */
    X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx);
    X509_VERIFY_PARAM_set1_host(param, "localhost", 0);

    /* Створення TCP-з'єднання */
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8443);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("Помилка підключення TCP");
        close(sock);
        SSL_CTX_free(ctx);
        return 1;
    }

    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);
    SSL_set_tlsext_host_name(ssl, "localhost");

    if (SSL_connect(ssl) <= 0) {
        fprintf(stderr, "Помилка TLS Handshake: %s\n",
                ERR_error_string(ERR_get_error(), NULL));
        SSL_free(ssl);
        close(sock);
        SSL_CTX_free(ctx);
        return 1;
    }

    printf("TLS-з'єднання встановлено з шифром: %s\n", SSL_get_cipher(ssl));

    const char *http_req = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n";
    SSL_write(ssl, http_req, (int)strlen(http_req));

    char buf[512];
    int bytes = SSL_read(ssl, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("Отримано відповідь:\n%s\n", buf);
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    SSL_CTX_free(ctx);
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
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

// RAII обгортки для C-ресурсів OpenSSL та файлових дескрипторів
struct SslCtxDeleter { void operator()(SSL_CTX *ctx) const noexcept { SSL_CTX_free(ctx); } };
struct SslDeleter    { void operator()(SSL *ssl) const noexcept { SSL_free(ssl); } };
struct SocketCloser  { void operator()(int *fd) const noexcept { if (fd && *fd >= 0) { close(*fd); delete fd; } } };

using UniqueSslCtx = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using UniqueSsl    = std::unique_ptr<SSL, SslDeleter>;
using UniqueSocket = std::unique_ptr<int, SocketCloser>;

class MtlsClient {
public:
    MtlsClient(std::string_view ca_file, std::string_view cert_file, std::string_view key_file) {
        ctx_.reset(SSL_CTX_new(TLS_client_method()));
        if (!ctx_) {
            throw std::runtime_error("Не вдалося створити SSL_CTX");
        }

        SSL_CTX_set_verify(ctx_.get(), SSL_VERIFY_PEER, nullptr);
        if (SSL_CTX_load_verify_locations(ctx_.get(), ca_file.data(), nullptr) != 1) {
            throw std::runtime_error("Не вдалося завантажити CA бандл");
        }

        if (SSL_CTX_use_certificate_chain_file(ctx_.get(), cert_file.data()) <= 0 ||
            SSL_CTX_use_PrivateKey_file(ctx_.get(), key_file.data(), SSL_FILETYPE_PEM) <= 0 ||
            SSL_CTX_check_private_key(ctx_.get()) != 1) {
            throw std::runtime_error("Помилка завантаження клієнтського сертифіката/ключа");
        }

        X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx_.get());
        X509_VERIFY_PARAM_set1_host(param, "localhost", 0);
    }

    void execute_get(std::string_view host, uint16_t port) {
        int raw_sock = socket(AF_INET, SOCK_STREAM, 0);
        if (raw_sock < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення сокета");
        }
        UniqueSocket sock(new int(raw_sock));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (connect(*sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка TCP-з'єднання");
        }

        UniqueSsl ssl(SSL_new(ctx_.get()));
        SSL_set_fd(ssl.get(), *sock);
        SSL_set_tlsext_host_name(ssl.get(), host.data());

        if (SSL_connect(ssl.get()) <= 0) {
            char err_buf[256];
            ERR_error_string_n(ERR_get_error(), err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("TLS Handshake failed: ") + err_buf);
        }

        std::cout << "[+] Встановлено mTLS сесію (" << SSL_get_version(ssl.get())
                  << ", шифр " << SSL_get_cipher(ssl.get()) << ")\n";

        std::string req = "GET / HTTP/1.1\r\nHost: " + std::string(host) + "\r\nConnection: close\r\n\r\n";
        SSL_write(ssl.get(), req.data(), static_cast<int>(req.size()));

        char resp_buf[1024];
        int bytes = SSL_read(ssl.get(), resp_buf, sizeof(resp_buf) - 1);
        if (bytes > 0) {
            resp_buf[bytes] = '\0';
            std::cout << "[+] Відповідь сервера:\n" << resp_buf << "\n";
        }

        SSL_shutdown(ssl.get());
    }

private:
    UniqueSslCtx ctx_;
};

int main() {
    try {
        MtlsClient client("ca.crt", "client.crt", "client.key");
        client.execute_get("localhost", 8443);
    } catch (const std::exception &ex) {
        std::cerr << "[!] Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Крок 4. Тестування за допомогою curl та діагностика крайових випадків

Для швидкої ізоляції мережевих проблем утиліта `curl` дозволяє перевірити взаємодію з mTLS-сервером безпосередньо з командного рядка:

```bash
# Успішний запит із передаванням CA, клієнтського сертифіката й ключа
curl -v --cacert ca.crt --cert client.crt --key client.key https://localhost:8443/

# Запит без клієнтського сертифіката (провокує відмову сервера)
curl -v --cacert ca.crt https://localhost:8443/
```

Під час експлуатації mTLS у розподілених сервісах виникають характерні сценарії відмови:

1. **Клієнт не передав сертифікат:**
   - *Симптом:* сервер повертає фатальну помилку `ssl.SSLError: [SSL: PEER_DID_NOT_RETURN_A_CERTIFICATE]`, а утиліта `curl` виводить TLS Alert 42 (`bad_certificate`).
   - *Діагностика:* сервер виставив `verify_mode = ssl.CERT_REQUIRED`, але клієнтський контекст не налаштував `load_cert_chain()` або не має доступу до файлу приватного ключа через обмеження прав файлової системи (POSIX permissions).

2. **Клієнтський сертифікат підписаний стороннім CA:**
   - *Симптом:* клієнт отримує TLS Alert `unknown_ca` (код 48).
   - *Діагностика:* сертифікат клієнта коректний, але його ланцюжок не сходиться до `ca.crt`, який було передано серверу у виклику `load_verify_locations()`. У Service Mesh це свідчить про розсинхронізацію кореневих сертифікатів між подами Kubernetes.

3. **Невідповідність приватного ключа та відкритого сертифіката:**
   - *Симптом:* виклик `SSL_CTX_use_PrivateKey_file` повертає помилку `key values mismatch`.
   - *Діагностика:* випадково переплутано пари файлів під час ротації секретів. Для швидкої перевірки відповідності порівнюють модуль RSA або геш відкритого ключа:
     ```bash
     openssl x509 -noout -modulus -in client.crt | openssl md5
     openssl rsa -noout -modulus -in client.key | openssl md5
     ```
     Збіг MD5-гешів доводить, що приватний ключ і сертифікат належать одній криптографічній парі.

4. **Відсутність розширення `Extended Key Usage: clientAuth`:**
   - *Симптом:* помилка валідації `X509_V_ERR_INVALID_PURPOSE`.
   - *Діагностика:* сертифікат було випущено виключно для `serverAuth` (як веб-сервер), тому суворий верифікатор OpenSSL відхиляє його використання клієнтом. Перевірте вміст сертифіката командою `openssl x509 -in client.crt -text -noout` і переконайтеся у наявності поля `TLS Web Client Authentication`.
