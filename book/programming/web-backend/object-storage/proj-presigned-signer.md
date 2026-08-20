# ⚙️ Генерація та валідація Presigned URL: автентифікація SigV4 без передачі ключів

Реалізація криптографічного алгоритму підпису AWS Signature Version 4 (SigV4) та перевірки підписаних URL-адрес дозволяє клієнтам безпечно взаємодіяти з об'єктним сховищем напряму, виключаючи передачу секретних ключів та знімаючи транзитний трафік із серверів додатків.

## Архітектурне завдання: прямий обмін даними зі сховищем

У високонавантажених вебсистемах завантаження та роздавання великих двійкових файлів (відеофайлів, фотографій високої роздільності, архівів та резервних копій) створює критичне навантаження на обчислювальні вузли бекенду. Якщо клієнтські програми надсилають файли через стандартний API-контролер застосунку, кожен мегабайт даних двічі проходить через мережевий інтерфейс: спершу від клієнта до бекенду, а потім від бекенду до внутрішнього сховища.

Така транзитна схема призводить до трьох системних проблем:

1. **Вичерпання дескрипторів сокетів та блокування робочих потоків (Socket and Worker Starvation).** Повільні клієнти на мобільних 3G/4G мережах можуть передавати файл розміром 100 МБ протягом кількох хвилин. Увесь цей час робочий потік вебсервера або пул з'єднань асинхронного циклу подій залишається прив'язаним до сокета, вичерпуючи ліміти паралелізму.
2. **Марнотратне споживання оперативної пам'яті.** Буферизація вхідних двійкових потоків на рівні бекенду вимагає виділення гігабайтів RAM, провокуючи спрацьовування механізму аварійного завершення процесів ядра Linux (OOM Killer) у моменти пікових навантажень.
3. **Подвійна вартість мережевого трафіку (Egress Bandwidth).** У хмарних інфраструктурах вихідний трафік між зонами доступності та публічним інтернетом тарифікується окремо. Пропуск терабайтів медіа через проміжні віртуальні машини подвоює рахунки за інфраструктуру.

Архітектурний патерн **Valet Key** (делегований ключ доступу) усуває ці недоліки:

* Клієнт звертається до бекенду з легковаговим JSON-запитом на отримання дозволу (наприклад, метод `POST /api/v1/media/ticket` із зазначенням імені файлу, типу контенту та розміру).
* Бекенд перевіряє права користувача в базі даних, валідує ліміти квот і за допомогою свого довгострокового секретного ключа генерує короткоживуче підписане посилання (**Presigned URL**).
* Клієнт отримує URL і виконує прямий запит до сховища (AWS S3, MinIO або Ceph RGW) методами `PUT` (завантаження) або `GET` (скачування).
* Об'єктне сховище автономно верифікує криптографічний підпис, перевіряє часові обмеження та приймає або віддає потік байтів без участі серверів застосунку.

Щоби реалізувати цей механізм як на боці генератора, так і на боці власного S3-сумісного проксі, шлюзу або тестового сервера, необхідно побудувати дві взаємодоповнюючі операції: формування канонічного підпису за стандартом AWS SigV4 та його сувору верифікацію.

## Анатомія та етапи криптографічного протоколу SigV4

Протокол AWS Signature Version 4 є галузевим стандартом автентифікації розподілених HTTP-систем. На відміну від стандартного підпису через HTTP-заголовок `Authorization`, у підписаних посиланнях (Presigned URL) усі параметри автентифікації та метадані передаються безпосередньо в рядку запиту (query string).

Конвеєр генерації складається з п'яти послідовних математичних перетворень:

```
1. Визначення та нормалізація параметрів запиту:
   - X-Amz-Algorithm     = AWS4-HMAC-SHA256
   - X-Amz-Credential    = <AccessKeyId>/<DateStamp>/<Region>/<Service>/aws4_request
   - X-Amz-Date          = <ISO8601_Timestamp> (формат YYYYMMDDTHHMMSSZ, наприклад 20260820T120000Z)
   - X-Amz-Expires       = <Час життя посилання в секундах, від 1 до 604800>
   - X-Amz-SignedHeaders = host

2. Побудова канонічного запиту (Canonical Request):
   CanonicalRequest =
     HTTPMethod + "\n" +
     CanonicalURI + "\n" +
     CanonicalQueryString + "\n" +
     CanonicalHeaders + "\n" +
     SignedHeaders + "\n" +
     "UNSIGNED-PAYLOAD"

3. Побудова рядка для підпису (String to Sign):
   StringToSign =
     "AWS4-HMAC-SHA256" + "\n" +
     X-Amz-Date + "\n" +
     <DateStamp>/<Region>/<Service>/aws4_request + "\n" +
     Hex(SHA256(CanonicalRequest))

4. Обчислення каскадного похідного ключа підпису (Key Derivation):
   kDate    = HMAC-SHA256("AWS4" + SecretAccessKey, DateStamp)
   kRegion  = HMAC-SHA256(kDate, Region)
   kService = HMAC-SHA256(kRegion, Service)
   kSigning = HMAC-SHA256(kService, "aws4_request")

5. Обчислення фінального підпису (Signature):
   Signature = Hex(HMAC-SHA256(kSigning, StringToSign))
```

### Чому використовується чотирирівневий каскад ключів

Замість прямого обчислення HMAC від рядка підпису за допомогою основного секретного ключа (`SecretAccessKey`), алгоритм SigV4 використовує криптографічну схему виведення ключів (англ. *Key Derivation Function, KDF*).

Кожен рівень каскаду звужує область дії згенерованого ключа:
* Ключ `kDate` прив'язаний виключно до конкретної календарної дати за UTC.
* Ключ `kRegion` діє лише в межах одного географічного регіону (наприклад, `eu-central-1`).
* Ключ `kService` обмежений конкретним сервісом (`s3`).
* Фінальний ключ `kSigning` діє виключно для запитів типу `aws4_request`.

Така багаторівнева ізоляція забезпечує високу стійкість до компрометації. Якщо зловмисник якимось чином перехопить внутрішній ключ `kSigning` або скомпрометує пам'ять локального обчислювального вузла в одному регіоні, він не зможе виконати зворотне обчислення головного ключа облікового запису `SecretAccessKey`, а також не зможе підписати запити на наступний день або в інші регіони хмари.

### Канонікалізація рядків та кодування URI

Головне джерело помилок при реалізації підпису полягає в найменших розбіжностях між символами канонічного рядка на стороні клієнта та сервера. Будь-який неврахований пробіл або зміна регістру символів призводить до іншого хешу SHA-256 та помилки `403 SignatureDoesNotMatch`.

Правила канонікалізації вимагають:
* **Канонічний URI (`CanonicalURI`).** Шлях нормалізується за правилами RFC 3986. Якщо шлях порожній, використовується одиночний слеш `/`. Подвійні слеші `//` мають бути збережені або нормалізовані відповідно до конфігурації сховища.
* **Канонічний рядок параметрів (`CanonicalQueryString`).** Усі параметри розділяються символом `&`, а їхні ключі та значення кодуються за схемою percent-encoding. Усі пари `key=value` сортуються у строгому лексикографічному порядку за зростанням байтових кодів ASCII. Сам параметр `X-Amz-Signature` не входить до канонічного рядка, оскільки він є результатом обчислення.
* **Канонічні заголовки (`CanonicalHeaders`).** Назви заголовків переводяться в нижній регістр (`host`), видаляються зайві пробіли на початку та в кінці значень, а рядки сортуються за алфавітом і завершуються символом нового рядка `\n`.

## Покроковий приклад обчислення підпису (Trace Walkthrough)

Щоби простежити кожен крок математичних перетворень, розглянемо тестовий приклад із конкретними даними:

* **HTTP-метод:** `PUT`
* **Хост сховища:** `mybucket.s3.eu-central-1.amazonaws.com`
* **URI шляху:** `/uploads/report.pdf`
* **Ідентифікатор ключа (`AccessKeyId`):** `AKIAIOSFODNN7EXAMPLE`
* **Секретний ключ (`SecretAccessKey`):** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
* **Дата запиту (`X-Amz-Date`):** `20260820T120000Z` (дата `20260820`)
* **Регіон та сервіс:** `eu-central-1`, `s3`
* **Термін дії (`X-Amz-Expires`):** `900` секунд (15 хвилин)

### Крок 1: Побудова Canonical Query String

Параметри кодуються та сортуються за ключами ASCII:

```text
X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20260820%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20260820T120000Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host
```

### Крок 2: Побудова Canonical Request та обчислення його хешу

Тіло канонічного запиту об'єднує метод, шлях, параметри, заголовки та фіксований рядок `UNSIGNED-PAYLOAD`:

```text
PUT
/uploads/report.pdf
X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20260820%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20260820T120000Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host
host:mybucket.s3.eu-central-1.amazonaws.com

host
UNSIGNED-PAYLOAD
```

Обчислення криптографічного дайджесту SHA-256 від цього рядка дає шістнадцятковий хеш `CanonicalRequestHash`.

### Крок 3: Побудова StringToSign

Формується рядок для підпису:

```text
AWS4-HMAC-SHA256
20260820T120000Z
20260820/eu-central-1/s3/aws4_request
<Hex-значення CanonicalRequestHash>
```

### Крок 4: Каскадне виведення ключів та фінальний HMAC

Послідовно обчислюються проміжні двійкові хеші:
1. `kSecret = "AWS4" + "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"`
2. `kDate    = HMAC-SHA256(kSecret, "20260820")`
3. `kRegion  = HMAC-SHA256(kDate, "eu-central-1")`
4. `kService = HMAC-SHA256(kRegion, "s3")`
5. `kSigning = HMAC-SHA256(kService, "aws4_request")`

Фінальний підпис є результатом `HMAC-SHA256(kSigning, StringToSign)`, закодованим у 64 символи нижнього регістру шістнадцяткового формату.

## Робочий код: генерація та перевірка Presigned URL

Нижче наведено повнофункціональну реалізацію генератора та валідатора підписаних посилань мовами C, C++ та Go. Реалізація здійснює коректну канонікалізацію, каскадне обчислення HMAC-SHA256 та перевірку підпису в константному часі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

#define SHA256_HEX_LEN 65
#define MAX_URL_LEN 2048

static void sha256_hex(const unsigned char *data, size_t len, char hex_out[SHA256_HEX_LEN]) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&hex_out[i * 2], "%02x", hash[i]);
    }
    hex_out[64] = '\0';
}

static void hmac_sha256(const unsigned char *key, size_t key_len,
                        const unsigned char *data, size_t data_len,
                        unsigned char out[SHA256_DIGEST_LENGTH]) {
    unsigned int len = SHA256_DIGEST_LENGTH;
    HMAC(EVP_sha256(), key, (int)key_len, data, data_len, out, &len);
}

void derive_signing_key(const char *secret_key, const char *date,
                        const char *region, const char *service,
                        unsigned char k_signing[SHA256_DIGEST_LENGTH]) {
    char k_secret[128];
    snprintf(k_secret, sizeof(k_secret), "AWS4%s", secret_key);

    unsigned char k_date[SHA256_DIGEST_LENGTH];
    unsigned char k_region[SHA256_DIGEST_LENGTH];
    unsigned char k_service[SHA256_DIGEST_LENGTH];

    hmac_sha256((const unsigned char *)k_secret, strlen(k_secret),
                (const unsigned char *)date, strlen(date), k_date);
    hmac_sha256(k_date, SHA256_DIGEST_LENGTH,
                (const unsigned char *)region, strlen(region), k_region);
    hmac_sha256(k_region, SHA256_DIGEST_LENGTH,
                (const unsigned char *)service, strlen(service), k_service);
    hmac_sha256(k_service, SHA256_DIGEST_LENGTH,
                (const unsigned char *)"aws4_request", 12, k_signing);

    // Очищення проміжних секретів у пам'яті
    OPENSSL_cleanse(k_secret, sizeof(k_secret));
    OPENSSL_cleanse(k_date, sizeof(k_date));
    OPENSSL_cleanse(k_region, sizeof(k_region));
    OPENSSL_cleanse(k_service, sizeof(k_service));
}

int generate_presigned_url(const char *http_method, const char *host,
                           const char *uri, const char *access_key,
                           const char *secret_key, const char *region,
                           const char *service, int expires_sec,
                           time_t now_ts, char *url_out, size_t url_out_size) {
    char date_stamp[9];   // YYYYMMDD
    char amz_date[17];    // YYYYMMDDTHHMMSSZ
    struct tm gm_time;
    #ifdef _WIN32
    gmtime_s(&gm_time, &now_ts);
    #else
    gmtime_r(&now_ts, &gm_time);
    #endif

    strftime(date_stamp, sizeof(date_stamp), "%Y%m%d", &gm_time);
    strftime(amz_date, sizeof(amz_date), "%Y%m%dT%H%M%SZ", &gm_time);

    char credential_scope[128];
    snprintf(credential_scope, sizeof(credential_scope), "%s/%s/%s/aws4_request",
             date_stamp, region, service);

    char credential_encoded[256];
    snprintf(credential_encoded, sizeof(credential_encoded), "%s%%2F%s%%2F%s%%2F%s%%2Faws4_request",
             access_key, date_stamp, region, service);

    // Канонічний рядок параметрів, відсортований лексикографічно
    char canonical_qs[1024];
    snprintf(canonical_qs, sizeof(canonical_qs),
             "X-Amz-Algorithm=AWS4-HMAC-SHA256"
             "&X-Amz-Credential=%s"
             "&X-Amz-Date=%s"
             "&X-Amz-Expires=%d"
             "&X-Amz-SignedHeaders=host",
             credential_encoded, amz_date, expires_sec);

    char canonical_headers[256];
    snprintf(canonical_headers, sizeof(canonical_headers), "host:%s\n", host);

    char canonical_req[2048];
    snprintf(canonical_req, sizeof(canonical_req),
             "%s\n%s\n%s\n%s\nhost\nUNSIGNED-PAYLOAD",
             http_method, uri, canonical_qs, canonical_headers);

    char canonical_req_hash[SHA256_HEX_LEN];
    sha256_hex((const unsigned char *)canonical_req, strlen(canonical_req), canonical_req_hash);

    char string_to_sign[1024];
    snprintf(string_to_sign, sizeof(string_to_sign),
             "AWS4-HMAC-SHA256\n%s\n%s\n%s",
             amz_date, credential_scope, canonical_req_hash);

    unsigned char k_signing[SHA256_DIGEST_LENGTH];
    derive_signing_key(secret_key, date_stamp, region, service, k_signing);

    unsigned char raw_signature[SHA256_DIGEST_LENGTH];
    hmac_sha256(k_signing, SHA256_DIGEST_LENGTH,
                (const unsigned char *)string_to_sign, strlen(string_to_sign), raw_signature);
    OPENSSL_cleanse(k_signing, sizeof(k_signing));

    char signature_hex[SHA256_HEX_LEN];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&signature_hex[i * 2], "%02x", raw_signature[i]);
    }
    signature_hex[64] = '\0';

    return snprintf(url_out, url_out_size, "https://%s%s?%s&X-Amz-Signature=%s",
                    host, uri, canonical_qs, signature_hex);
}

int validate_presigned_url(const char *http_method, const char *host,
                           const char *uri, const char *canonical_qs_no_sig,
                           const char *provided_sig, const char *secret_key,
                           const char *date_stamp, const char *region,
                           const char *service, const char *amz_date,
                           time_t req_time, int expires_sec, time_t current_time) {
    // 1. Перевірка терміну дії (TTL)
    if (current_time < req_time || current_time > (req_time + expires_sec)) {
        return -1; // Посилання прострочене (Request has expired)
    }

    char credential_scope[128];
    snprintf(credential_scope, sizeof(credential_scope), "%s/%s/%s/aws4_request",
             date_stamp, region, service);

    char canonical_headers[256];
    snprintf(canonical_headers, sizeof(canonical_headers), "host:%s\n", host);

    char canonical_req[2048];
    snprintf(canonical_req, sizeof(canonical_req),
             "%s\n%s\n%s\n%s\nhost\nUNSIGNED-PAYLOAD",
             http_method, uri, canonical_qs_no_sig, canonical_headers);

    char canonical_req_hash[SHA256_HEX_LEN];
    sha256_hex((const unsigned char *)canonical_req, strlen(canonical_req), canonical_req_hash);

    char string_to_sign[1024];
    snprintf(string_to_sign, sizeof(string_to_sign),
             "AWS4-HMAC-SHA256\n%s\n%s\n%s",
             amz_date, credential_scope, canonical_req_hash);

    unsigned char k_signing[SHA256_DIGEST_LENGTH];
    derive_signing_key(secret_key, date_stamp, region, service, k_signing);

    unsigned char expected_raw_sig[SHA256_DIGEST_LENGTH];
    hmac_sha256(k_signing, SHA256_DIGEST_LENGTH,
                (const unsigned char *)string_to_sign, strlen(string_to_sign), expected_raw_sig);
    OPENSSL_cleanse(k_signing, sizeof(k_signing));

    char expected_sig_hex[SHA256_HEX_LEN];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&expected_sig_hex[i * 2], "%02x", expected_raw_sig[i]);
    }
    expected_sig_hex[64] = '\0';

    // 2. Порівняння підписів у константному часі для уникнення timing attacks
    if (CRYPTO_memcmp(provided_sig, expected_sig_hex, 64) == 0) {
        return 0; // Підпис автентичний
    }
    return -2; // Невірний підпис (SignatureMismatch)
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <span>
#include <expected>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

class SigV4Signer {
public:
    struct Credentials {
        std::string access_key;
        std::string secret_key;
        std::string region;
        std::string service{"s3"};
    };

    enum class Error {
        Expired,
        SignatureMismatch,
        InvalidFormat
    };

    explicit SigV4Signer(Credentials creds) : creds_(std::move(creds)) {}

    ~SigV4Signer() {
        // Очищення секретного ключа в оперативній пам'яті при знищенні об'єкта
        OPENSSL_cleanse(creds_.secret_key.data(), creds_.secret_key.size());
    }

    [[nodiscard]] std::string generate_presigned_url(
        std::string_view http_method,
        std::string_view host,
        std::string_view uri,
        std::chrono::seconds expires,
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now()) const
    {
        const auto [date_stamp, amz_date] = format_timestamps(now);
        const std::string credential_scope = date_stamp + "/" + creds_.region + "/" + creds_.service + "/aws4_request";
        const std::string credential_encoded = creds_.access_key + "%2F" + date_stamp + "%2F" + creds_.region + "%2F" + creds_.service + "%2Faws4_request";

        const std::string canonical_qs =
            "X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=" + credential_encoded +
            "&X-Amz-Date=" + amz_date +
            "&X-Amz-Expires=" + std::to_string(expires.count()) +
            "&X-Amz-SignedHeaders=host";

        const std::string canonical_headers = "host:" + std::string(host) + "\n";
        const std::string canonical_req = std::string(http_method) + "\n" +
                                          std::string(uri) + "\n" +
                                          canonical_qs + "\n" +
                                          canonical_headers + "\n" +
                                          "host\n" +
                                          "UNSIGNED-PAYLOAD";

        const std::string canonical_req_hash = sha256_hex(canonical_req);
        const std::string string_to_sign = "AWS4-HMAC-SHA256\n" + amz_date + "\n" + credential_scope + "\n" + canonical_req_hash;

        const auto k_signing = derive_signing_key(creds_.secret_key, date_stamp, creds_.region, creds_.service);
        const auto signature = hmac_sha256_hex(k_signing, string_to_sign);

        return "https://" + std::string(host) + std::string(uri) + "?" + canonical_qs + "&X-Amz-Signature=" + signature;
    }

    [[nodiscard]] std::expected<void, Error> validate_presigned_url(
        std::string_view http_method,
        std::string_view host,
        std::string_view uri,
        std::string_view canonical_qs_no_sig,
        std::string_view provided_sig,
        std::string_view amz_date,
        std::string_view date_stamp,
        std::chrono::system_clock::time_point req_time,
        std::chrono::seconds expires,
        std::chrono::system_clock::time_point current_time = std::chrono::system_clock::now()) const
    {
        if (current_time < req_time || current_time > (req_time + expires)) {
            return std::unexpected(Error::Expired);
        }

        const std::string credential_scope = std::string(date_stamp) + "/" + creds_.region + "/" + creds_.service + "/aws4_request";
        const std::string canonical_headers = "host:" + std::string(host) + "\n";
        const std::string canonical_req = std::string(http_method) + "\n" +
                                          std::string(uri) + "\n" +
                                          std::string(canonical_qs_no_sig) + "\n" +
                                          canonical_headers + "\n" +
                                          "host\n" +
                                          "UNSIGNED-PAYLOAD";

        const std::string canonical_req_hash = sha256_hex(canonical_req);
        const std::string string_to_sign = "AWS4-HMAC-SHA256\n" + std::string(amz_date) + "\n" + credential_scope + "\n" + canonical_req_hash;

        const auto k_signing = derive_signing_key(creds_.secret_key, date_stamp, creds_.region, creds_.service);
        const auto expected_sig = hmac_sha256_hex(k_signing, string_to_sign);

        if (provided_sig.size() != 64 ||
            CRYPTO_memcmp(provided_sig.data(), expected_sig.data(), 64) != 0) {
            return std::unexpected(Error::SignatureMismatch);
        }

        return {};
    }

private:
    Credentials creds_;

    static std::string sha256_hex(std::string_view input) {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> hash{};
        SHA256(reinterpret_cast<const unsigned char*>(input.data()), input.size(), hash.data());
        return bytes_to_hex(hash);
    }

    static std::array<unsigned char, SHA256_DIGEST_LENGTH> hmac_sha256_raw(
        std::span<const unsigned char> key, std::string_view data)
    {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> out{};
        unsigned int len = SHA256_DIGEST_LENGTH;
        HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size()),
             reinterpret_cast<const unsigned char*>(data.data()), data.size(), out.data(), &len);
        return out;
    }

    static std::string hmac_sha256_hex(std::span<const unsigned char> key, std::string_view data) {
        return bytes_to_hex(hmac_sha256_raw(key, data));
    }

    static std::array<unsigned char, SHA256_DIGEST_LENGTH> derive_signing_key(
        std::string_view secret, std::string_view date, std::string_view region, std::string_view service)
    {
        const std::string k_secret = "AWS4" + std::string(secret);
        auto k_date = hmac_sha256_raw(std::span{reinterpret_cast<const unsigned char*>(k_secret.data()), k_secret.size()}, date);
        auto k_region = hmac_sha256_raw(k_date, region);
        auto k_service = hmac_sha256_raw(k_region, service);
        auto k_signing = hmac_sha256_raw(k_service, "aws4_request");

        OPENSSL_cleanse(k_date.data(), k_date.size());
        OPENSSL_cleanse(k_region.data(), k_region.size());
        OPENSSL_cleanse(k_service.data(), k_service.size());
        return k_signing;
    }

    static std::string bytes_to_hex(std::span<const unsigned char> bytes) {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0');
        for (auto b : bytes) {
            oss << std::setw(2) << static_cast<int>(b);
        }
        return oss.str();
    }

    static std::pair<std::string, std::string> format_timestamps(std::chrono::system_clock::time_point tp) {
        const auto time_t_val = std::chrono::system_clock::to_time_t(tp);
        std::tm gm_tm{};
        #ifdef _WIN32
        gmtime_s(&gm_tm, &time_t_val);
        #else
        gmtime_r(&time_t_val, &gm_tm);
        #endif
        char d_buf[9], dt_buf[17];
        std::strftime(d_buf, sizeof(d_buf), "%Y%m%d", &gm_tm);
        std::strftime(dt_buf, sizeof(dt_buf), "%Y%m%dT%H%M%SZ", &gm_tm);
        return {std::string(d_buf), std::string(dt_buf)};
    }
};
```
```go
package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"net/url"
	"time"
)

type S3Presigner struct {
	AccessKey string
	SecretKey string
	Region    string
	Service   string
}

func hmacSHA256(key []byte, data string) []byte {
	h := hmac.New(sha256.New, key)
	h.Write([]byte(data))
	return h.Sum(nil)
}

func sha256Hex(data string) string {
	h := sha256.Sum256([]byte(data))
	return hex.EncodeToString(h[:])
}

func (p *S3Presigner) deriveSigningKey(dateStamp string) []byte {
	kDate := hmacSHA256([]byte("AWS4"+p.SecretKey), dateStamp)
	kRegion := hmacSHA256(kDate, p.Region)
	kService := hmacSHA256(kRegion, p.Service)
	return hmacSHA256(kService, "aws4_request")
}

func (p *S3Presigner) GeneratePresignedURL(method, host, uri string, expiresSec int, now time.Time) string {
	dateStamp := now.UTC().Format("20060102")
	amzDate := now.UTC().Format("20060102T150405Z")
	credScope := fmt.Sprintf("%s/%s/%s/aws4_request", dateStamp, p.Region, p.Service)

	v := url.Values{}
	v.Set("X-Amz-Algorithm", "AWS4-HMAC-SHA256")
	v.Set("X-Amz-Credential", fmt.Sprintf("%s/%s", p.AccessKey, credScope))
	v.Set("X-Amz-Date", amzDate)
	v.Set("X-Amz-Expires", fmt.Sprintf("%d", expiresSec))
	v.Set("X-Amz-SignedHeaders", "host")

	canonicalQS := v.Encode()
	canonicalReq := fmt.Sprintf("%s\n%s\n%s\nhost:%s\n\nhost\nUNSIGNED-PAYLOAD",
		method, uri, canonicalQS, host)

	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%s",
		amzDate, credScope, sha256Hex(canonicalReq))

	signingKey := p.deriveSigningKey(dateStamp)
	signature := hex.EncodeToString(hmacSHA256(signingKey, stringToSign))

	return fmt.Sprintf("https://%s%s?%s&X-Amz-Signature=%s", host, uri, canonicalQS, signature)
}

func (p *S3Presigner) Validate(method, host, uri, canonicalQSNoSig, providedSig, amzDate, dateStamp string, reqTime time.Time, expiresSec int) error {
	now := time.Now().UTC()
	if now.Before(reqTime) || now.After(reqTime.Add(time.Duration(expiresSec)*time.Second)) {
		return fmt.Errorf("URL expired")
	}

	credScope := fmt.Sprintf("%s/%s/%s/aws4_request", dateStamp, p.Region, p.Service)
	canonicalReq := fmt.Sprintf("%s\n%s\n%s\nhost:%s\n\nhost\nUNSIGNED-PAYLOAD",
		method, uri, canonicalQSNoSig, host)

	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%s",
		amzDate, credScope, sha256Hex(canonicalReq))

	signingKey := p.deriveSigningKey(dateStamp)
	expectedSig := hex.EncodeToString(hmacSHA256(signingKey, stringToSign))

	if subtle.ConstantTimeCompare([]byte(providedSig), []byte(expectedSig)) != 1 {
		return fmt.Errorf("signature mismatch")
	}
	return nil
}
```
:::

## Інженерні пастки, вразливості та виробничі обмеження

Під час впровадження Presigned URL у виробничих системах виникає низка специфічних інфраструктурних та безпекових викликів.

### 1. Налаштування міждоменного доступу CORS

Коли браузер виконує прямий виклик `PUT` або `GET` за адресою іншого домену (наприклад, з `app.example.com` до `my-bucket.s3.eu-central-1.amazonaws.com`), рушій браузера автоматично надсилає попередній запит `OPTIONS` (CORS Preflight).

Якщо на рівні бакета не налаштовано конфігурацію CORS, завантаження зазнає невдачі на рівні браузера, навіть якщо підпис SigV4 абсолютно бездоганний:

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>https://app.example.com</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
        <ExposeHeader>ETag</ExposeHeader>
        <MaxAgeSeconds>3600</MaxAgeSeconds>
    </CORSRule>
</CORSConfiguration>
```

Заголовок `<ExposeHeader>ETag</ExposeHeader>` є критично необхідним: без нього скрипт на стороні клієнта не зможе прочитати хеш завантаженого файлу з відповіді S3, щоби передати його на бекенд для підтвердження успішного завершення операції.

### 2. Захист від підміни типу вмісту та розміру файлу

За замовчуванням підпис SigV4 для Query-параметрів підписує лише заголовок `host` та використовує рядок `UNSIGNED-PAYLOAD`. Це означає, що клієнт із валідним підписом теоретично може завантажити файл будь-якого розміру або підмінити тип файлу (наприклад, замість оголошеного зображення `image/png` передати шкідливий виконуваний скрипт або файл обсягом 50 ГБ, що вичерпає квоту дискового простору).

Для нейтралізації цієї загрози застосовують два взаємодоповнюючі механізми:

1. **Явне включення заголовка `Content-Type` до списку `SignedHeaders`.** У цьому разі бекенд фіксує значення типу вмісту при створенні підпису. Якщо клієнт спробує надіслати інший тип контенту, S3 негайно відхилить запит з помилкою валідації підпису.
2. **Політика форми з обмеженням діапазону розміру (S3 POST Policy).** Якщо пряме завантаження здійснюється через HTML-форму методом `POST`, бекенд генерує документ політики у форматі JSON, кодований у Base64, із жорсткою умовою `["content-length-range", 1024, 10485760]`. Сховище автоматично перериває передачу, якщо обсяг даних виходить за межі від 1 КБ до 10 МБ.

### 3. Атаки за часом (Timing Attacks) при перевірці підписів

При самостійній валідації підписів у власних S3-сумісних сервісах або шлюзах суворо заборонено використовувати стандартні бібліотечні функції порівняння рядків (`strcmp`, `memcmp` без захисту або оператор `==`).

Стандартне порівняння переривається на першому ж байті, що не збігся:

```
Спроба 1: "a..."  -> час виконання 12 нс (перший байт хибний)
Спроба 2: "f..."  -> час виконання 48 нс (перший байт вірний, другий хибний)
```

Вимірюючи час відгуку сервера з високою точністю через локальну мережу, атакуючий може побайтово реконструювати коректний 64-символьний підпис SHA-256 за лінійну кількість спроб (`64 · 16 = 1024` запити). Функція `CRYPTO_memcmp` в OpenSSL або `subtle.ConstantTimeCompare` у Go виконує побітову диз'юнкцію результатів над усіма байтами без розгалужень, забезпечуючи суворо константний час виконання незалежно від позиції невідповідності.

### 4. Робота з тимчасовими обліковими даними IAM (AWS STS)

Якщо бекенд запущено у контейнері Kubernetes або віртуальній машині AWS EC2 з призначеною IAM-роллю, застосунок використовує не статичні секретні ключі, а тимчасові маркери безпеки (AWS Security Token Service, STS).

У цьому разі до канонічного рядка параметрів додається обов'язковий параметр `X-Amz-Security-Token=<session_token>`. Якщо цей параметр забути додати до `CanonicalQueryString`, або якщо час життя підписаного посилання перевищить час життя самого маркера сесії STS (зазвичай 1–12 годин), об'єктне сховище поверне помилку `403 ExpiredToken`.

### 5. Потокове підписування фрагментів (Chunked Streaming SigV4)

Для завантаження надвеликих об'єктів без попереднього знання точного розміру протокол SigV4 підтримує режим потокового підписування частин (`STREAMING-AWS4-HMAC-SHA256-PAYLOAD`).

У цьому режимі тіло HTTP-запиту розбивається на чанки фіксованого розміру, де кожен чанк супроводжується власним підписом-трейлером. Підпис попереднього чанка стає вхідним дайджестом для обчислення підпису наступного чанка, утворюючи криптографічний ланцюг хешів. Це гарантує цілісність кожного переданого сегмента в реальному часі без необхідності накопичувати весь файл у пам'яті клієнта.

### 6. Завантаження через HTML-форми (S3 POST Policy)

Крім підписаних посилань для методу `PUT`, хмарні сховища підтримують пряме завантаження через звичайні HTML-форми стандарту `multipart/form-data`. У цьому варіанті клієнт не виконує асинхронних запитів JavaScript, а надсилає стандартну вебформу безпосередньо на адресу бакета.

Щоби авторизувати таке завантаження, сервер генерує документ політики (англ. *Policy Document*) у форматі JSON, який описує допустимі параметри операції:

```json
{
  "expiration": "2026-08-20T12:15:00.000Z",
  "conditions": [
    {"bucket": "mybucket"},
    ["starts-with", "$key", "user-uploads/42/"],
    {"acl": "private"},
    {"success_action_redirect": "https://app.example.com/upload-success"},
    ["content-length-range", 1024, 10485760]
  ]
}
```

Бекенд перетворює цей JSON-документ у рядок Base64 та обчислює підпис `HMAC-SHA256(kSigning, Base64Policy)`. Усі отримані значення вбудовуються у приховані поля форми:

```html
<form action="https://mybucket.s3.eu-central-1.amazonaws.com/" method="post" enctype="multipart/form-data">
  <input type="hidden" name="key" value="user-uploads/42/${filename}" />
  <input type="hidden" name="acl" value="private" />
  <input type="hidden" name="X-Amz-Credential" value="AKIAIOSFODNN7EXAMPLE/20260820/eu-central-1/s3/aws4_request" />
  <input type="hidden" name="X-Amz-Algorithm" value="AWS4-HMAC-SHA256" />
  <input type="hidden" name="X-Amz-Date" value="20260820T120000Z" />
  <input type="hidden" name="Policy" value="eyJl...Base64...==" />
  <input type="hidden" name="X-Amz-Signature" value="a1b2c3...64_hex_digits..." />
  <input type="file" name="file" />
  <input type="submit" value="Завантажити" />
</form>
```

Сховище парсить поля форми за порядком, декодує політику, перевіряє криптографічний підпис і зіставляє фактичний розмір і ключ файлу з умовами `conditions`. Якщо користувач спробував підмінити префікс шляху або перевищив ліміт 10 МБ, S3 повертає помилку `400 Bad Request` або `403 Access Denied` без збереження пошкоджених даних.

### 7. Нормалізація заголовка Host та адресація віртуальних хостів

При роботі з S3 існують дві схеми адресації ресурсів:

* **Стиль віртуального хосту (Virtual-Hosted-Style):** `https://mybucket.s3.eu-central-1.amazonaws.com/image.png`. У цьому разі заголовок `Host` дорівнює `mybucket.s3.eu-central-1.amazonaws.com`, а `CanonicalURI` містить лише `/image.png`.
* **Стиль шляху (Path-Style):** `https://s3.eu-central-1.amazonaws.com/mybucket/image.png`. Тут заголовок `Host` дорівнює `s3.eu-central-1.amazonaws.com`, а `CanonicalURI` починається з імені бакета: `/mybucket/image.png`.

Якщо ваш бекенд або проксі працює на локальному порту (наприклад, локальний MinIO на `localhost:9000`), заголовок `Host` зобов'язаний містити номер порту (`localhost:9000`) як у вихідному HTTP-запиті, так і в `CanonicalHeaders`. Будь-яка невідповідність між портом у заголовку сокета та портом у канонічному рядку призводить до відхилення запиту через незбіг підписів.

### 8. Клієнтська інтеграція та відновлюване завантаження великих блобів

Під час виконання прямих викликів `PUT` із клієнтського браузера за допомогою `fetch()` або `XMLHttpRequest` розробники стикаються з проблемою відображення прогресу та обробки обривів зв'язку.

Стандартний API `fetch()` у сучасних браузерах не надає подій відстеження прогресу передачі тіла запиту (`Upload Progress Streams` досі мають обмежену підтримку). Для відображення точного індикатора завантаження клієнтський код використовує об'єкт `XMLHttpRequest`, який надає подію `xhr.upload.onprogress`:

```javascript
function uploadDirect(presignedUrl, file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('PUT', presignedUrl, true);
        xhr.setRequestHeader('Content-Type', file.type);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const etag = xhr.getResponseHeader('ETag');
                resolve({ etag: etag ? etag.replace(/"/g, '') : null });
            } else {
                reject(new Error(`Upload failed with status ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.send(file);
    });
}
```

Якщо розмір файлу перевищує 100 МБ, пряме завантаження через єдиний Presigned URL стає вразливим до мережевих збоїв: при обриві з'єднання клієнт змушений починати завантаження з нульового байта.

У таких сценаріях бекенд поєднує патерн Valet Key з протоколом **Multipart Upload**:
1. Бекенд ініціює багаточастинну сесію та генерує масив окремих Presigned URL для кожного чанка розміром 10–50 МБ (`partNumber=1`, `partNumber=2`...).
2. Клієнт паралельно завантажує чанки безпосередньо в S3 через виділені посилання.
3. У разі збою одного чанка клієнт повторює запит лише для пошкодженого фрагмента.
4. Після отримання всіх ETag клієнт викликає бекенд, який фіналізує сесію в об'єктному сховищі.

### 9. Динамічне перевизначення заголовків відповіді (Response Overrides у Presigned GET)

Коли бекенд генерує Presigned URL для приватного завантаження файлу (`GET`), виникає потреба керувати тим, як браузер користувача інтерпретує отриманий файл, не змінюючи вихідні метадані самого об'єкта в сховищі.

Наприклад, PDF-звіт у сховищі збережено зі стандартним ключем `reports/2026/uuid_987654321.dat`, проте користувач під час натискання кнопки «Завантажити» повинен отримати файл із читабельним ім'ям `Квартальний_звіт_2026.pdf` та примусовим збереженням на диск замість відкриття у вбудованому переглядачі.

Протокол S3 надає спеціальні параметри запиту для динамічного перевизначення вихідних HTTP-заголовків відповіді:

* `response-content-disposition`: встановлює значення `attachment; filename="filename.pdf"` або `inline`.
* `response-content-type`: примусово задає MIME-тип (наприклад, `application/pdf` замість `binary/octet-stream`).
* `response-cache-control`: встановлює значення `no-cache, no-store` для конфіденційних фінансових документів.
* `response-content-language`: перевизначає мову документа.

Усі ці параметри включаються до `CanonicalQueryString` при підписанні. Якщо зловмисник спробує вручну змінити заголовок `response-content-disposition` у згенерованому URL, щоби змусити браузер виконати шкідливий скрипт замість завантаження файлу, сховище відхилить запит через порушення криптографічного підпису.

### 10. Захист кінцевих точок генерації квитків від вичерпання ресурсів (Rate Limiting)

Хоча підписані посилання знімають навантаження з передачі сирих двійкових байтів, сам контролер генерації квитків на боці бекенду (наприклад, `POST /api/v1/files/ticket`) залишається класичною HTTP-точкою входу.

Якщо авторизований користувач або скомпрометований клієнт почне генерувати мільйони Presigned URL за секунду, це створить ризик вичерпання ресурсів бази даних та переповнення сховища «сміттєвими» незавершеними ключами.

Щоб запобігти зловживанням, архітектура видачі посилань обов'язково оснащується трьома захисними бар'єрами:
* **Обмеження частоти запитів (Rate Limiting за алгоритмом Token Bucket).** На рівні шлюзу API фіксується ліміт генерації посилань (наприклад, не більше 10 посилань на хвилину для одного користувача).
* **Створення попереднього запису в базі даних (Pending State).** Перед видачею підписаного посилання бекенд створює запис у таблиці метаданих зі статусом `pending_upload` та фіксує очікуваний розмір у квоті користувача.
* **Таймаут очищення (Garbage Collection).** Якщо протягом 30 хвилин після генерації посилання від сховища не надійшло повідомлення про успішне збереження файлу, фоновий прибиральник скидає тимчасову квоту та позначає запис як анульований.
