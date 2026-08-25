# ⚙️ Реалізація автомата станів Double Ratchet мовами C та C++

Протокол Double Ratchet реалізує скінченний автомат станів, що поєднує симетричний ланцюг обчислення одноразових ключів повідомлень та асиметричний храповик Діффі — Геллмана на еліптичній кривій Curve25519. Його головне завдання — гарантувати пряму секретність для кожного окремого кадру та забезпечити автоматичне відновлення таємності після компрометації оперативної пам'яті клієнта.

### 1. Архітектура автомата станів та контури обробки ключів

Програмна модель протоколу базується на трьох взаємопов'язаних контурах обробки криптографічних матеріалів:

1. **Контур ініціалізації (`ratchet_init`):** приймає спільний 32-байтний майстер-секрет (узгоджений протоколом X3DH) та налаштовує первинні значення кореневого ключа `rk` і локальних ключів еліптичної кривої. Для Аліси контур негайно генерує перший відкритий ключ і розгортає ланцюг відправлення `cks`. Для Боба контур зберігає попередньо згенеровану пару ключів і переходить у стан очікування першого вхідного кадру.
2. **Контур відправлення (`ratchet_encrypt_step`):** на кожен виклик операції шифрування виконує один крок симетричного KDF-ланцюга, генерує разовий ключ `mk`, збільшує внутрішній лічильник `ns` та формує 40-байтний відкритий заголовок із поточним відкритим ключем `dhs.pub`, лічильником попереднього ланцюга `pn` та поточним індексом `n`.
3. **Контур отримання (`ratchet_decrypt_step`):** аналізує заголовок вхідного кадру. Якщо відкритий ключ співрозмовника `hdr->dh_pub` відрізняється від збереженого `dhr`, автомат фіксує пропущені ключі попереднього ланцюга до індексу `hdr->pn`, виконує асиметричний крок над кореневим ключем `rk`, генерує нову локальну пару DH для майбутніх відповідей, і лише після цього розгортає новий ланцюг отримання `ckr`.

### 2. Алгоритм обробки затриманих повідомлень та буферизація ключів

Мережевий транспорт може доставляти повідомлення з порушенням первинного порядку. Якщо повідомлення №3 надійде раніше за повідомлення №1 і №2, пряме прокручування ланцюга знищило б проміжні ключі, унеможливлюючи розшифрування запізнілих пакетів.

Функція `skip_message_keys` розв'язує цю проблему шляхом «перемотування» KDF-ланцюга вперед до індексу цільового повідомлення:
- Усі проміжні значення `mk` обчислюються за допомогою `crypto_kdf_ck` і зберігаються у фіксованому масиві `skipped_key_entry_t`.
- Кожен запис містить трійку `(dh_pub, n, mk)` та прапорець зайнятості `used`.
- Для вбудованих систем та мобільних клієнтів лінійний пошук у фіксованому масиві на 64–256 елементів є значно ефективнішим за динамічні хеш-таблиці, оскільки повністю виключає фрагментацію купи та виділення динамічної пам'яті на гарячому шляху дешифрування.
- Коли затримане повідомлення врешті надходить, функція дешифрування спочатку перевіряє таблицю пропущених ключів. Якщо ключ знайдено, він негайно використовується для розшифрування, затирається нулями та звільняє комірку таблиці.

### 3. Покрокове простеження сценарію діалогу (Trace Walkthrough)

Розглянемо послідовність внутрішніх переходів автомата під час реального діалогу між двома учасниками:

1. **Ініціалізація Аліси:** функція `ratchet_init` отримує `sk` та відкритий ключ Боба `peer_pub`. Вона обчислює `dh_secret = X25519(dhs.priv, peer_pub)`, розгортає `rk` і створює перший ключ ланцюга `cks`. Лічильники `ns = 0, nr = 0, pn = 0`.
2. **Аліса відправляє перше повідомлення (n = 0):** функція `ratchet_encrypt_step` виконує крок `crypto_kdf_ck(cks)`, повертає `mk_0` і оновлює `cks` до наступного стану. Лічильник `ns` стає `1`. Заголовок містить `(dh_pub_A1, pn=0, n=0)`.
3. **Боб отримує перше повідомлення:** бачить невідомий `dh_pub_A1`. Оскільки `has_dhr == false`, Боб обчислює `dh_secret = X25519(bob_priv, dh_pub_A1)`, генерує новий `rk` та `ckr`. Потім Боб генерує нову локальну пару `(bob_priv_2, bob_pub_2)`, обчислює другий спільний секрет і генерує свій `cks`. Після цього з ланцюга `ckr` видобувається `mk_0`, і повідомлення розшифровується.
4. **Боб відповідає (n = 0):** Боб викликає `ratchet_encrypt_step`, отримує ключ `mk` зі свого ланцюга `cks`, формує заголовок `(bob_pub_2, pn=0, n=0)` і відправляє кадр Алісі.
5. **Аліса отримує відповідь Боба:** Аліса бачить `bob_pub_2 != peer_pub`. Вона завершує свій старий ланцюг, виконує асиметричний храповик, оновлює `rk` та свій `ckr`, генерує нову пару `dhs_A2` і переходить у повністю оновлений криптографічний простір.

### 4. Захист пам'яті та бар'єри оптимізації компілятора

Критичним аспектом безпеки наскрізного шифрування є своєчасне та надійне видалення тимчасових ключів повідомлень `mk` та проміжних секретів `dh_secret` з оперативної пам'яті. Звичайний виклик `memset(buf, 0, len)` у сучасних компіляторах C та C++ (GCC, Clang, MSVC) оптимізується й повністю видаляється як мертвий код (англ. *Dead Store Elimination*), якщо після виклику пам'ять буфера звільняється або виходить з області видимості.

Для запобігання витоку ключів у дампах пам'яті та swap-файлах код застосовує функцію `secure_memzero`, яка записує нулі через вказівник із кваліфікатором `volatile uint8_t*`. Компілятор не має права видаляти операції запису через `volatile`, оскільки зобов'язаний припускати наявність сторонніх спостерігачів за пам'яттю.

У реалізації мовою C++ управління життєвим циклом ключів додатково інкапсулюється в деструкторах класів та структур (`KeyPair`, `DoubleRatchetSession`) за парадигмою RAII (Resource Acquisition Is Initialization). Це гарантує, що пам'ять ключів буде надійно затерта навіть у разі генерації винятків або аварійного виходу з функції дешифрування.

### 5. Інтеграція з реальними криптографічними бібліотеками

У наведеному навчальному коді операції `crypto_dh`, `crypto_kdf_rk` та `crypto_kdf_ck` реалізовано спрощеними бітовими операціями для наочності структури автомата станів. У промисловому виробничому коді ці заглушки замінюються на виклики перевірених криптографічних бібліотек:
- `crypto_dh` викликає функцію скалярного множення на кривій Curve25519: `crypto_scalarmult_curve25519` (libsodium) або `EVP_PKEY_derive` (OpenSSL).
- `crypto_kdf_rk` та `crypto_kdf_ck` використовують стандартизовані виклики `HKDF-Extract` та `HKDF-Expand` на основі `HMAC-SHA256`.
- Отримані ключі повідомлень `mk` передаються безпосередньо у функцію автентифікованого шифрування `crypto_aead_chacha20poly1305_ietf_encrypt`, де заголовок `msg_header_t` слугує асоційованими даними `AAD`.

У багатопотокових додатках операції над структурою `ratchet_state_t` обов'язково захищаються м'ютексом, оскільки одночасне виконання шифрування вихідного кадру та дешифрування вхідного пакета в різних потоках призведе до стану гонки (*race condition*) та розсинхронізації лічильників сесії.

### 6. Робоча реалізація мовами C та C++

Нижче наведено повну реалізацію автомата Double Ratchet: симетричний крок розгортання ключів, оновлення кореневого ланцюга при зміні відкритого ключа та механізм буферизації пропущених ключів.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define KEY_SIZE           32
#define MAX_SKIPPED_KEYS   64
#define MAX_FORWARD_STEPS  256

typedef struct {
    uint8_t priv[KEY_SIZE];
    uint8_t pub[KEY_SIZE];
} dh_keypair_t;

typedef struct {
    uint8_t  dh_pub[KEY_SIZE];
    uint32_t pn;
    uint32_t n;
} msg_header_t;

typedef struct {
    uint8_t  dh_pub[KEY_SIZE];
    uint32_t n;
    uint8_t  mk[KEY_SIZE];
    bool     used;
} skipped_key_entry_t;

typedef struct {
    dh_keypair_t        dhs;             // власна пара ключів DH
    uint8_t             dhr[KEY_SIZE];   // відкритий ключ DH співрозмовника
    uint8_t             rk[KEY_SIZE];    // Root Key
    uint8_t             cks[KEY_SIZE];   // Chain Key для відправлення
    uint8_t             ckr[KEY_SIZE];   // Chain Key для отримання
    uint32_t            ns;              // лічильник відправлених
    uint32_t            nr;              // лічильник отриманих
    uint32_t            pn;              // розмір попереднього ланцюга
    bool                has_dhr;         // чи отримано перший ключ
    skipped_key_entry_t skipped[MAX_SKIPPED_KEYS];
} ratchet_state_t;

// Безпечне затирання пам'яті, захищене від оптимізацій компілятора
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

// Заглушки криптографічних примітивів для демонстрації автомата станів
// У промисловому коді: libsodium (crypto_scalarmult_curve25519, crypto_auth_hmacsha256)
static void crypto_dh(uint8_t out[KEY_SIZE], const uint8_t priv[KEY_SIZE], const uint8_t pub[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) out[i] = (uint8_t)(priv[i] ^ pub[i]); // X25519
}

static void crypto_kdf_rk(uint8_t next_rk[KEY_SIZE], uint8_t next_ck[KEY_SIZE],
                          const uint8_t rk[KEY_SIZE], const uint8_t dh_out[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) {
        next_rk[i] = (uint8_t)(rk[i] ^ dh_out[i] ^ 0x01);
        next_ck[i] = (uint8_t)(rk[i] ^ dh_out[i] ^ 0x02);
    }
}

static void crypto_kdf_ck(uint8_t next_ck[KEY_SIZE], uint8_t mk[KEY_SIZE], const uint8_t ck[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) {
        mk[i]      = (uint8_t)(ck[i] ^ 0x11); // HMAC(ck, 0x01)
        next_ck[i] = (uint8_t)(ck[i] ^ 0x22); // HMAC(ck, 0x02)
    }
}

void ratchet_init(ratchet_state_t *s, const uint8_t sk[KEY_SIZE], const uint8_t peer_pub[KEY_SIZE], bool is_alice) {
    memset(s, 0, sizeof(*s));
    memcpy(s->rk, sk, KEY_SIZE);

    // Ініціалізація локальної пари ключів DH
    for (int i = 0; i < KEY_SIZE; ++i) {
        s->dhs.priv[i] = (uint8_t)(i + (is_alice ? 1 : 2));
        s->dhs.pub[i]  = (uint8_t)(s->dhs.priv[i] ^ 0xAA);
    }

    if (is_alice && peer_pub != NULL) {
        memcpy(s->dhr, peer_pub, KEY_SIZE);
        s->has_dhr = true;

        uint8_t dh_secret[KEY_SIZE];
        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->cks, s->rk, dh_secret);
        secure_memzero(dh_secret, sizeof(dh_secret));
    }
}

// Збереження пропущеного ключа
static int save_skipped_key(ratchet_state_t *s, const uint8_t dhr[KEY_SIZE], uint32_t n, const uint8_t mk[KEY_SIZE]) {
    for (int i = 0; i < MAX_SKIPPED_KEYS; ++i) {
        if (!s->skipped[i].used) {
            memcpy(s->skipped[i].dh_pub, dhr, KEY_SIZE);
            s->skipped[i].n = n;
            memcpy(s->skipped[i].mk, mk, KEY_SIZE);
            s->skipped[i].used = true;
            return 0;
        }
    }
    return -1; // буфер переповнено
}

// Перемотування ланцюга вперед для збереження ключів
static int skip_message_keys(ratchet_state_t *s, uint32_t until) {
    if (s->nr + MAX_FORWARD_STEPS < until) return -1;

    while (s->nr < until) {
        uint8_t mk[KEY_SIZE];
        crypto_kdf_ck(s->ckr, mk, s->ckr);
        if (save_skipped_key(s, s->dhr, s->nr, mk) != 0) {
            secure_memzero(mk, sizeof(mk));
            return -1;
        }
        secure_memzero(mk, sizeof(mk));
        s->nr++;
    }
    return 0;
}

// Крок шифрування
int ratchet_encrypt_step(ratchet_state_t *s, msg_header_t *hdr, uint8_t mk_out[KEY_SIZE]) {
    crypto_kdf_ck(s->cks, mk_out, s->cks);

    memcpy(hdr->dh_pub, s->dhs.pub, KEY_SIZE);
    hdr->pn = s->pn;
    hdr->n  = s->ns++;
    return 0;
}

// Крок дешифрування
int ratchet_decrypt_step(ratchet_state_t *s, const msg_header_t *hdr, uint8_t mk_out[KEY_SIZE]) {
    // 1. Перевірка таблиці збережених ключів
    for (int i = 0; i < MAX_SKIPPED_KEYS; ++i) {
        if (s->skipped[i].used && s->skipped[i].n == hdr->n &&
            memcmp(s->skipped[i].dh_pub, hdr->dh_pub, KEY_SIZE) == 0) {
            memcpy(mk_out, s->skipped[i].mk, KEY_SIZE);
            secure_memzero(s->skipped[i].mk, KEY_SIZE);
            s->skipped[i].used = false;
            return 0;
        }
    }

    // 2. Якщо отримано новий відкритий ключ DH — виконуємо асиметричний храповик
    if (!s->has_dhr || memcmp(hdr->dh_pub, s->dhr, KEY_SIZE) != 0) {
        if (s->has_dhr) {
            if (skip_message_keys(s, hdr->pn) != 0) return -1;
        }

        // Крок DH з новим ключем отримувача
        memcpy(s->dhr, hdr->dh_pub, KEY_SIZE);
        s->has_dhr = true;

        uint8_t dh_secret[KEY_SIZE];
        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->ckr, s->rk, dh_secret);

        // Генерація нової пари DH для наших наступних відповідей
        for (int i = 0; i < KEY_SIZE; ++i) s->dhs.priv[i] = (uint8_t)(s->dhs.priv[i] + 1);
        for (int i = 0; i < KEY_SIZE; ++i) s->dhs.pub[i] = (uint8_t)(s->dhs.priv[i] ^ 0xAA);

        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->cks, s->rk, dh_secret);
        secure_memzero(dh_secret, sizeof(dh_secret));

        s->pn = s->ns;
        s->ns = 0;
        s->nr = 0;
    }

    // 3. Перемотування поточного ланцюга отримання
    if (skip_message_keys(s, hdr->n) != 0) return -1;

    // 4. Отримання шуканого ключа повідомлення
    crypto_kdf_ck(s->ckr, mk_out, s->ckr);
    s->nr++;
    return 0;
}
```
```cpp
#include <array>
#include <vector>
#include <optional>
#include <span>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <utility>

class DoubleRatchetSession {
public:
    static constexpr size_t KeySize = 32;
    static constexpr size_t MaxSkippedKeys = 64;
    static constexpr size_t MaxForwardSteps = 256;

    using Key = std::array<uint8_t, KeySize>;

    struct Header {
        Key      dh_pub{};
        uint32_t pn{0};
        uint32_t n{0};
    };

    struct KeyPair {
        Key priv{};
        Key pub{};

        ~KeyPair() {
            volatile uint8_t *p = priv.data();
            for (size_t i = 0; i < KeySize; ++i) p[i] = 0;
        }
    };

    DoubleRatchetSession(const Key &shared_key, const std::optional<Key> &peer_dh_pub, bool is_alice)
        : rk_(shared_key) {
        for (size_t i = 0; i < KeySize; ++i) {
            dhs_.priv[i] = static_cast<uint8_t>(i + (is_alice ? 1 : 2));
            dhs_.pub[i]  = static_cast<uint8_t>(dhs_.priv[i] ^ 0xAA);
        }

        if (is_alice && peer_dh_pub.has_value()) {
            dhr_ = *peer_dh_pub;
            auto dh_secret = dh(dhs_.priv, *dhr_);
            auto [new_rk, new_cks] = kdf_rk(rk_, dh_secret);
            rk_  = new_rk;
            cks_ = new_cks;
        }
    }

    ~DoubleRatchetSession() {
        wipe(rk_);
        wipe(cks_);
        wipe(ckr_);
    }

    // Шифрування повідомлення
    std::pair<Header, Key> encrypt_step() {
        auto [next_cks, mk] = kdf_ck(cks_);
        cks_ = next_cks;

        Header hdr{
            .dh_pub = dhs_.pub,
            .pn     = pn_,
            .n      = ns_++
        };
        return {hdr, mk};
    }

    // Дешифрування повідомлення
    Key decrypt_step(const Header &hdr) {
        // 1. Пошук у таблиці пропущених ключів
        auto it = std::find_if(skipped_keys_.begin(), skipped_keys_.end(), [&](const SkippedKey &sk) {
            return sk.n == hdr.n && sk.dh_pub == hdr.dh_pub;
        });

        if (it != skipped_keys_.end()) {
            Key mk = it->mk;
            wipe(it->mk);
            skipped_keys_.erase(it);
            return mk;
        }

        // 2. Асиметричний крок при новому відкритому ключі
        if (!dhr_.has_value() || *dhr_ != hdr.dh_pub) {
            if (dhr_.has_value()) {
                skip_keys(hdr.pn);
            }

            dhr_ = hdr.dh_pub;
            auto dh_secret = dh(dhs_.priv, *dhr_);
            auto [rk1, ckr_new] = kdf_rk(rk_, dh_secret);
            rk_  = rk1;
            ckr_ = ckr_new;

            // Оновлюємо нашу локальну пару для наступних відповідей
            for (size_t i = 0; i < KeySize; ++i) {
                dhs_.priv[i] = static_cast<uint8_t>(dhs_.priv[i] + 1);
                dhs_.pub[i]  = static_cast<uint8_t>(dhs_.priv[i] ^ 0xAA);
            }

            auto dh_secret_send = dh(dhs_.priv, *dhr_);
            auto [rk2, cks_new] = kdf_rk(rk_, dh_secret_send);
            rk_  = rk2;
            cks_ = cks_new;

            pn_ = ns_;
            ns_ = 0;
            nr_ = 0;
        }

        // 3. Перемотування поточного ланцюга
        skip_keys(hdr.n);

        // 4. Отримання ключа
        auto [next_ckr, mk] = kdf_ck(ckr_);
        ckr_ = next_ckr;
        nr_++;
        return mk;
    }

private:
    struct SkippedKey {
        Key      dh_pub;
        uint32_t n;
        Key      mk;
    };

    KeyPair               dhs_{};
    std::optional<Key>    dhr_{std::nullopt};
    Key                   rk_{};
    Key                   cks_{};
    Key                   ckr_{};
    uint32_t              ns_{0};
    uint32_t              nr_{0};
    uint32_t              pn_{0};
    std::vector<SkippedKey> skipped_keys_{};

    static void wipe(Key &k) {
        volatile uint8_t *p = k.data();
        for (size_t i = 0; i < KeySize; ++i) p[i] = 0;
    }

    static Key dh(const Key &priv, const Key &pub) {
        Key out{};
        for (size_t i = 0; i < KeySize; ++i) out[i] = static_cast<uint8_t>(priv[i] ^ pub[i]);
        return out;
    }

    static std::pair<Key, Key> kdf_rk(const Key &rk, const Key &dh_out) {
        Key next_rk{}, next_ck{};
        for (size_t i = 0; i < KeySize; ++i) {
            next_rk[i] = static_cast<uint8_t>(rk[i] ^ dh_out[i] ^ 0x01);
            next_ck[i] = static_cast<uint8_t>(rk[i] ^ dh_out[i] ^ 0x02);
        }
        return {next_rk, next_ck};
    }

    static std::pair<Key, Key> kdf_ck(const Key &ck) {
        Key next_ck{}, mk{};
        for (size_t i = 0; i < KeySize; ++i) {
            mk[i]      = static_cast<uint8_t>(ck[i] ^ 0x11);
            next_ck[i] = static_cast<uint8_t>(ck[i] ^ 0x22);
        }
        return {next_ck, mk};
    }

    void skip_keys(uint32_t until) {
        if (nr_ + MaxForwardSteps < until) {
            throw std::runtime_error("Message jump exceeds MaxForwardSteps");
        }
        while (nr_ < until) {
            auto [next_ckr, mk] = kdf_ck(ckr_);
            ckr_ = next_ckr;
            if (skipped_keys_.size() >= MaxSkippedKeys) {
                throw std::runtime_error("Skipped keys table overflow");
            }
            skipped_keys_.push_back({*dhr_, nr_, mk});
            nr_++;
        }
    }
};
```
:::
