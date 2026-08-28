# ⚙️ Реалізація апаратного модуля ідентичності та mTLS клієнта

У класичних вбудованих додатках робота з протоколом TLS часто реалізується через завантаження приватного ключа RSA або ECDSA з Flash-пам'яті в масив оперативної пам'яті (RAM) мікроконтролера, звідки криптографічна бібліотека безпосередньо зчитує байти ключа для обчислення підпису. Такий підхід створює критичну вразливість: будь-яке переповнення стека або буфера у мережевому драйвері дозволяє зловмиснику зчитати оперативну пам'ять та назавжди викрасти ідентичність пристрою.

Цей проект демонструє виробничу архітектуру інтеграції апаратного модуля ідентичності (Hardware Root of Trust) та клієнта mTLS на базі бібліотеки mbedTLS. Приватний ключ ніколи не потрапляє в пам'ять процесора: під час взаємної автентифікації TLS операція створення підпису делегується апаратному чипу безпеки через механізм зворотного виклику (callback-функцію для непрозорого контексту відкритого ключа).

---

## 1. Архітектурні рівні та керування пам'яттю

Реалізація організована у вигляді трьох ізольованих рівнів:

1. **Апаратний рівень (Hardware Abstraction Layer — HAL)**: інкапсулює низькорівневу взаємодію з фізичним кремнієм. Зчитує незмінний серійний номер мікроконтролера (Chip UID) з регістрів eFuse та виконує виклики до захищеного елемента (Secure Element, наприклад Microchip ATECC608 або Infineon Optiga Trust M) через шину I2C або SPI.
2. **Криптографічний міст (Opaque PK Driver)**: інтегрує апаратні слоти Secure Element у структуру відкритих ключів `mbedtls_pk_context` із типом `MBEDTLS_PK_OPAQUE`. Бібліотека знає лише відкритий ключ пристрою, а будь-яка спроба підпису гешу перенаправляється на фізичний чип.
3. **Клієнтський рівень сесії TLS**: встановлює захищене TCP-з'єднання з віддаленим шлюзом або сервером EST, виконує обмін сертифікатами X.509 (IDevID або LDevID) та здійснює повноцінне рукостискання mTLS.

---

## 2. Реалізація драйвера та mTLS клієнта

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/asn1write.h"
#include "mbedtls/error.h"

#define SE_SLOT_IDEVID_KEY 0x00
#define SE_SLOT_LDEVID_KEY 0x01

/* Структура представлення апаратного модуля безпеки */
typedef struct {
    uint8_t chip_uid[16];
    size_t  uid_len;
    uint8_t active_slot;
} hardware_security_module_t;

/* Зчитування унікального апаратного ідентифікатора кремнію */
int hsm_read_silicon_uid(hardware_security_module_t *hsm) {
    if (!hsm) return -1;
    /* У реальній системі: зчитування eFuse або регістрів UID мікроконтролера */
    const uint8_t mock_uid[16] = {
        0x53, 0x54, 0x4D, 0x33, 0x32, 0x48, 0x35, 0x30,
        0xAA, 0xBB, 0xCC, 0xDD, 0x01, 0x02, 0x03, 0x04
    };
    memcpy(hsm->chip_uid, mock_uid, sizeof(mock_uid));
    hsm->uid_len = sizeof(mock_uid);
    hsm->active_slot = SE_SLOT_IDEVID_KEY;
    return 0;
}

/* Апаратний підпис гешу: приватний ключ ніколи не виходить за межі чипа */
int hsm_ecdsa_sign_hash(hardware_security_module_t *hsm,
                        const uint8_t *hash, size_t hash_len,
                        uint8_t *sig_r, uint8_t *sig_s,
                        size_t *sig_comp_len) {
    if (!hsm || !hash || hash_len != 32 || !sig_r || !sig_s) return -1;
    
    /* Відправлення команди підпису на Secure Element через шину I2C */
    /* Чип обчислює ECDSA над наданим дайджестом і повертає числа r та s */
    memset(sig_r, 0xA5, 32);
    memset(sig_s, 0x5A, 32);
    *sig_comp_len = 32;
    return 0;
}

/* Зворотний виклик mbedTLS для непрозорого (opaque) ключа */
static int opaque_ecdsa_sign_callback(mbedtls_pk_context *ctx,
                                      mbedtls_md_type_t md_alg,
                                      const unsigned char *hash, size_t hash_len,
                                      unsigned char *sig, size_t *sig_len,
                                      int (*f_rng)(void *, unsigned char *, size_t),
                                      void *p_rng) {
    (void)md_alg; (void)f_rng; (void)p_rng;
    hardware_security_module_t *hsm = (hardware_security_module_t *)ctx->pk_ctx;
    
    uint8_t r[32], s[32];
    size_t comp_len = 0;
    
    if (hsm_ecdsa_sign_hash(hsm, hash, hash_len, r, s, &comp_len) != 0) {
        return MBEDTLS_ERR_PK_BAD_INPUT_DATA;
    }
    
    /* Формування ASN.1 DER структури ECDSA-Sig-Value: SEQUENCE { r INTEGER, s INTEGER } */
    unsigned char *p = sig + 72;
    int len = 0;
    
    mbedtls_mpi r_mpi, s_mpi;
    mbedtls_mpi_init(&r_mpi);
    mbedtls_mpi_init(&s_mpi);
    
    mbedtls_mpi_read_binary(&r_mpi, r, comp_len);
    mbedtls_mpi_read_binary(&s_mpi, s, comp_len);
    
    mbedtls_asn1_write_mpi(&p, sig, &s_mpi);
    mbedtls_asn1_write_mpi(&p, sig, &r_mpi);
    len = (int)(sig + 72 - p);
    mbedtls_asn1_write_len(&p, sig, len);
    mbedtls_asn1_write_tag(&p, sig, MBEDTLS_ASN1_CONSTRUCTED | MBEDTLS_ASN1_SEQUENCE);
    
    *sig_len = (size_t)(sig + 72 - p);
    memmove(sig, p, *sig_len);
    
    mbedtls_mpi_free(&r_mpi);
    mbedtls_mpi_free(&s_mpi);
    return 0;
}

/* Запуск mTLS клієнта з використанням апаратного ключа */
int run_device_mtls_client(const char *server_host, const char *server_port,
                           const char *ca_cert_pem, const char *dev_cert_pem) {
    int ret = 0;
    hardware_security_module_t hsm;
    if (hsm_read_silicon_uid(&hsm) != 0) {
        fprintf(stderr, "Помилка читання UID чипа\n");
        return -1;
    }

    mbedtls_net_context      server_fd;
    mbedtls_ssl_context      ssl;
    mbedtls_ssl_config       conf;
    mbedtls_x509_crt         cacert;
    mbedtls_x509_crt         clicert;
    mbedtls_pk_context       pkey;
    mbedtls_entropy_context  entropy;
    mbedtls_ctr_drbg_context ctr_drbg;

    mbedtls_net_init(&server_fd);
    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    mbedtls_x509_crt_init(&cacert);
    mbedtls_x509_crt_init(&clicert);
    mbedtls_pk_init(&pkey);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_entropy_init(&entropy);

    const char *pers = "device_identity_mtls";
    if (mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                              (const unsigned char *)pers, strlen(pers)) != 0) {
        ret = -1;
        goto cleanup;
    }

    /* Завантаження CA та сертифіката пристрою */
    if (mbedtls_x509_crt_parse(&cacert, (const unsigned char *)ca_cert_pem, strlen(ca_cert_pem) + 1) != 0 ||
        mbedtls_x509_crt_parse(&clicert, (const unsigned char *)dev_cert_pem, strlen(dev_cert_pem) + 1) != 0) {
        ret = -2;
        goto cleanup;
    }

    /* Налаштування непрозорого контексту відкритого ключа */
    pkey.pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
    pkey.pk_ctx  = &hsm;

    if (mbedtls_ssl_config_defaults(&conf, MBEDTLS_SSL_IS_CLIENT,
                                    MBEDTLS_SSL_TRANSPORT_STREAM,
                                    MBEDTLS_SSL_PRESET_DEFAULT) != 0) {
        ret = -3;
        goto cleanup;
    }

    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);
    mbedtls_ssl_conf_own_cert(&conf, &clicert, &pkey);
    mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

    if (mbedtls_ssl_setup(&ssl, &conf) != 0) {
        ret = -4;
        goto cleanup;
    }

    if (mbedtls_ssl_set_hostname(&ssl, server_host) != 0) {
        ret = -5;
        goto cleanup;
    }

    /* Встановлення мережевого TCP з'єднання */
    if (mbedtls_net_connect(&server_fd, server_host, server_port, MBEDTLS_NET_PROTO_TCP) != 0) {
        ret = -6;
        goto cleanup;
    }
    mbedtls_ssl_set_bio(&ssl, &server_fd, mbedtls_net_send, mbedtls_net_recv, NULL);

    /* Виконання TLS рукостискання */
    while ((ret = mbedtls_ssl_handshake(&ssl)) != 0) {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
            fprintf(stderr, "Помилка TLS рукостискання: -0x%04X\n", -ret);
            goto cleanup;
        }
    }

    printf("mTLS сесію успішно встановлено з сервером %s:%s\n", server_host, server_port);
    ret = 0;

cleanup:
    mbedtls_net_free(&server_fd);
    mbedtls_x509_crt_free(&clicert);
    mbedtls_x509_crt_free(&cacert);
    mbedtls_pk_free(&pkey);
    mbedtls_ssl_free(&ssl);
    mbedtls_ssl_config_free(&conf);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return ret;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <cstring>

#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/error.h"

namespace device_security {

enum class ErrorCode {
    SiliconUidReadFailed,
    DrbgInitFailed,
    CertificateParseFailed,
    ConfigDefaultsFailed,
    SslSetupFailed,
    HostnameSetFailed,
    NetworkConnectFailed,
    HandshakeFailed,
    HardwareSigningFailed
};

enum class KeySlot : uint8_t {
    IDevID = 0x00,
    LDevID = 0x01
};

/* RAII-обгортка апаратного модуля безпеки */
class HardwareSecurityModule {
public:
    HardwareSecurityModule() : active_slot_(KeySlot::IDevID) {
        /* Зчитування 128-бітного апаратного серійника */
        const std::array<uint8_t, 16> mock_uid = {
            0x53, 0x54, 0x4D, 0x33, 0x32, 0x48, 0x35, 0x30,
            0xAA, 0xBB, 0xCC, 0xDD, 0x01, 0x02, 0x03, 0x04
        };
        uid_ = mock_uid;
    }

    [[nodiscard]] std::span<const uint8_t> uid() const noexcept {
        return uid_;
    }

    void select_key_slot(KeySlot slot) noexcept {
        active_slot_ = slot;
    }

    [[nodiscard]] std::expected<std::pair<std::array<uint8_t, 32>, std::array<uint8_t, 32>>, ErrorCode>
    sign_digest(std::span<const uint8_t> hash) const noexcept {
        if (hash.size() != 32) {
            return std::unexpected(ErrorCode::HardwareSigningFailed);
        }
        std::array<uint8_t, 32> r{}, s{};
        r.fill(0xA5);
        s.fill(0x5A);
        return std::make_pair(r, s);
    }

private:
    std::array<uint8_t, 16> uid_{};
    KeySlot active_slot_;
};

/* RAII-керування ресурсами mbedTLS */
struct MbedTlsDeleters {
    void operator()(mbedtls_net_context* p)      const noexcept { mbedtls_net_free(p); delete p; }
    void operator()(mbedtls_ssl_context* p)      const noexcept { mbedtls_ssl_free(p); delete p; }
    void operator()(mbedtls_ssl_config* p)       const noexcept { mbedtls_ssl_config_free(p); delete p; }
    void operator()(mbedtls_x509_crt* p)         const noexcept { mbedtls_x509_crt_free(p); delete p; }
    void operator()(mbedtls_pk_context* p)       const noexcept { mbedtls_pk_free(p); delete p; }
    void operator()(mbedtls_entropy_context* p)  const noexcept { mbedtls_entropy_free(p); delete p; }
    void operator()(mbedtls_ctr_drbg_context* p) const noexcept { mbedtls_ctr_drbg_free(p); delete p; }
};

/* Клієнт mTLS з апаратною автентифікацією */
class DeviceMtlsClient {
public:
    explicit DeviceMtlsClient(std::shared_ptr<HardwareSecurityModule> hsm)
        : hsm_(std::move(hsm)),
          net_(new mbedtls_net_context),
          ssl_(new mbedtls_ssl_context),
          conf_(new mbedtls_ssl_config),
          cacert_(new mbedtls_x509_crt),
          clicert_(new mbedtls_x509_crt),
          pkey_(new mbedtls_pk_context),
          entropy_(new mbedtls_entropy_context),
          drbg_(new mbedtls_ctr_drbg_context) {
        
        mbedtls_net_init(net_.get());
        mbedtls_ssl_init(ssl_.get());
        mbedtls_ssl_config_init(conf_.get());
        mbedtls_x509_crt_init(cacert_.get());
        mbedtls_x509_crt_init(clicert_.get());
        mbedtls_pk_init(pkey_.get());
        mbedtls_entropy_init(entropy_.get());
        mbedtls_ctr_drbg_init(drbg_.get());
    }

    [[nodiscard]] std::expected<void, ErrorCode>
    connect(std::string_view host, std::string_view port,
            std::string_view ca_pem, std::string_view dev_cert_pem) {
        
        constexpr std::string_view pers = "device_identity_mtls_cpp";
        if (mbedtls_ctr_drbg_seed(drbg_.get(), mbedtls_entropy_func, entropy_.get(),
                                  reinterpret_cast<const unsigned char*>(pers.data()),
                                  pers.size()) != 0) {
            return std::unexpected(ErrorCode::DrbgInitFailed);
        }

        if (mbedtls_x509_crt_parse(cacert_.get(),
                                   reinterpret_cast<const unsigned char*>(ca_pem.data()),
                                   ca_pem.size() + 1) != 0 ||
            mbedtls_x509_crt_parse(clicert_.get(),
                                   reinterpret_cast<const unsigned char*>(dev_cert_pem.data()),
                                   dev_cert_pem.size() + 1) != 0) {
            return std::unexpected(ErrorCode::CertificateParseFailed);
        }

        /* Прив'язка апаратного HSM до контексту відкритого ключа */
        pkey_->pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
        pkey_->pk_ctx  = hsm_.get();

        if (mbedtls_ssl_config_defaults(conf_.get(), MBEDTLS_SSL_IS_CLIENT,
                                        MBEDTLS_SSL_TRANSPORT_STREAM,
                                        MBEDTLS_SSL_PRESET_DEFAULT) != 0) {
            return std::unexpected(ErrorCode::ConfigDefaultsFailed);
        }

        mbedtls_ssl_conf_authmode(conf_.get(), MBEDTLS_SSL_VERIFY_REQUIRED);
        mbedtls_ssl_conf_ca_chain(conf_.get(), cacert_.get(), nullptr);
        mbedtls_ssl_conf_own_cert(conf_.get(), clicert_.get(), pkey_.get());
        mbedtls_ssl_conf_rng(conf_.get(), mbedtls_ctr_drbg_random, drbg_.get());

        if (mbedtls_ssl_setup(ssl_.get(), conf_.get()) != 0) {
            return std::unexpected(ErrorCode::SslSetupFailed);
        }

        if (mbedtls_ssl_set_hostname(ssl_.get(), std::string(host).c_str()) != 0) {
            return std::unexpected(ErrorCode::HostnameSetFailed);
        }

        if (mbedtls_net_connect(net_.get(), std::string(host).c_str(),
                                std::string(port).c_str(), MBEDTLS_NET_PROTO_TCP) != 0) {
            return std::unexpected(ErrorCode::NetworkConnectFailed);
        }

        mbedtls_ssl_set_bio(ssl_.get(), net_.get(), mbedtls_net_send, mbedtls_net_recv, nullptr);

        int ret = 0;
        while ((ret = mbedtls_ssl_handshake(ssl_.get())) != 0) {
            if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
                return std::unexpected(ErrorCode::HandshakeFailed);
            }
        }

        return {};
    }

private:
    std::shared_ptr<HardwareSecurityModule> hsm_;
    std::unique_ptr<mbedtls_net_context, MbedTlsDeleters>      net_;
    std::unique_ptr<mbedtls_ssl_context, MbedTlsDeleters>      ssl_;
    std::unique_ptr<mbedtls_ssl_config, MbedTlsDeleters>       conf_;
    std::unique_ptr<mbedtls_x509_crt, MbedTlsDeleters>         cacert_;
    std::unique_ptr<mbedtls_x509_crt, MbedTlsDeleters>         clicert_;
    std::unique_ptr<mbedtls_pk_context, MbedTlsDeleters>       pkey_;
    std::unique_ptr<mbedtls_entropy_context, MbedTlsDeleters>  entropy_;
    std::unique_ptr<mbedtls_ctr_drbg_context, MbedTlsDeleters> drbg_;
};

} // namespace device_security
```
:::

---

## 3. Критичні підводні камені та правила інженерної реалізації

Під час практичної розробки вбудованих драйверів крипточипів та клієнтів mTLS необхідно враховувати п'ять фундаментальних аспектів інженерної безпеки та надійності:

### 3.1. Пакування підпису в ASN.1 DER та правило знакового біта

Апаратний чип повертає два 32-байтних беззнакових числа `r` та `s`. Проте стандарт X.509 та протокол TLS вимагають, щоб підпис ECDSA передавався як структура ASN.1 DER `ECDSA-Sig-Value`:

```asn1
ECDSA-Sig-Value ::= SEQUENCE {
    r   INTEGER,
    s   INTEGER
}
```

В ASN.1 DER тип `INTEGER` є знаковим у доповняльному коді до двох. Якщо старший біт числа `r` або `s` дорівнює одиниці (значення байта `≥ 0x80`), парсер інтерпретує його як від'ємне число. Щоб уникнути цього, перед таким числом обов'язково додається нульовий префіксний байт `0x00`. Функція `mbedtls_asn1_write_mpi()` виконує це додавання автоматично. Якщо формувати ASN.1 послідовність вручну без урахування цього правила, приблизно кожне друге рукостискання TLS завершуватиметься аварійною помилкою перевірки підпису (`Bad Signature Alert`).

### 3.2. Багатопотоковість в операційних системах реального часу (RTOS)

У середовищі FreeRTOS або Zephyr кілька завдань (наприклад, фоновий MQTT клієнт, потік телеметрії та сервіс EST онбордингу) можуть одночасно звертатися до Secure Element. Оскільки фізична шина I2C/SPI є спільним ресурсом, а сам крипточип є однопотоковим автоматом станів, усі звернення до драйвера HSM мають захищатися м'ютексом із успадкуванням пріоритетів (Priority Inheritance Mutex). Нехтування синхронізацією призводить до переривання транзакцій та зависання внутрішнього криптографічного процесора чипа.

### 3.3. Обробка таймаутів та застрягання шини (Bus Hang Recovery)

Криптографічні операції з еліптичними кривими (особливо генерація пари ключів або перевірка сертифіката) вимагають від 20 до 120 мілісекунд апаратного часу Secure Element. Протягом цього інтервалу мікросхема використовує механізм утримання тактової лінії (I2C Clock Stretching). Драйвер мікроконтролера повинен мати коректно налаштований апаратний таймаут, що перевищує максимальний час обчислень чипа, а також процедуру аварійного скидання шини (генерацію 9 імпульсів SCL) у разі апаратного збою або стрибка напруги.

### 3.4. Очищення буферів та безпека оперативної пам'яті

Незважаючи на те, що довгоживучі асиметричні ключі ніколи не потрапляють в оперативну пам'ять мікроконтролера, у процесі рукостискання TLS у RAM утворюються чутливі проміжні дані: симетричні сесійні ключі (Master Secret, Client/Server Traffic Secrets), вектор ініціалізації та проміжні геш-образи. Після завершення або аварійного розриву TLS-сесії всі структури контексту повинні обов'язково обнулятися викликом `mbedtls_platform_zeroize()` або через RAII-деструктори, щоб запобігти витоку ключів через механізми перегляду неініціалізованої пам'яті (Use-After-Free).

### 3.5. Переваги ідіоматичного C++ для вбудованих систем

Представлена C++ реалізація демонструє сучасний підхід до безпечного системного програмування без накладних витрат:
- **`std::span<const uint8_t>`** замість небезпечних пар «вказівник + довжина» гарантує перевірку меж буферів під час компіляції та усуває ризик виходу за межі пам'яті при роботі з гешами;
- **`std::expected<T, ErrorCode>`** забезпечує детерміновану обробку помилок без використання механізму винятків C++ (C++ Exceptions), які часто заборонені в прошивках реального часу через непередбачуване споживання стека;
- **`std::unique_ptr` із кастомними делетерами** гарантує автоматичне та своєчасне звільнення дескрипторів сокетів та структур mbedTLS у разі будь-якого дострокового виходу з функції, усуваючи класичні для C витоки ресурсів у ланцюжках `goto cleanup`.
