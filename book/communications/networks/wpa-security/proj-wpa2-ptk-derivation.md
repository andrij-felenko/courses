# ⚙️ Обчислення ключів WPA2: розгортання PTK та верифікація EAPOL MIC

У протоколі захисту бездротових мереж WPA2 автентифікація клієнта та створення сеансового шифру виконуються за допомогою чотириетапного рукостискання (4-Way Handshake). Під час цього процесу клієнт (Supplicant) і точка доступу (Authenticator) доводять один одному знання попередньо узгодженого пароля (Pre-Shared Key, PSK), не передаючи сам пароль або його хеш через радіоефір. Замість цього сторони обмінюються випадковими числами (ANonce та SNonce), незалежно розраховують 512-бітний блок сеансових ключів (Pairwise Transient Key, PTK) та перевіряють автентичність повідомлень за допомогою коду цілісності (Message Integrity Code, MIC).

Нижче наведено повний розбір бінарної структури керуючих кадрів EAPOL-Key, алгоритмічний конвеєр розгортання ключів WPA2, реалізацію мовами C та C++ з використанням сучасних безпечних практик програмування, а також детальний аналіз крайових випадків, захисту від витоків інформації за побічними каналами часу, механізму доставки групових ключів AES Key Wrap (RFC 3394), архітектури багатопотокового підбору через відображення пам'яті (Memory-Mapped I/O), побайтового аналізу дампів pcap у Wireshark та оптимізації алгоритму в інструментах аудиту безпеки на графічних процесорах (GPU) і векторних інструкціях CPU (AVX-512).

---

### 1. Бінарна структура дескриптора EAPOL-Key (IEEE 802.11i / 802.1X)

Усі повідомлення чотириетапного рукостискання передаються у вигляді спеціальних кадрів автентифікації на рівні керування доступом до середовища (MAC) стандарту IEEE 802.1X. Формат кадру EAPOL-Key має суворо фіксовану бінарну розкладку:

```
+──────────────────────────┬──────────┬─────────────────────────────────────────────+
| Поле дескриптора         | Довжина  | Призначення та бінарний зміст               |
+──────────────────────────┼──────────┼─────────────────────────────────────────────+
| Protocol Version         | 1 байт   | Версія протоколу EAPOL (зазвичай 0x01 або   |
|                          |          | 0x02 для 802.11i RSN)                       |
| Packet Type              | 1 байт   | Тип кадру (0x03 — EAPOL-Key)                |
| Packet Body Length       | 2 байти  | Довжина тіла дескриптора (Big-Endian)       |
| Key Descriptor Type      | 1 байт   | Тип дескриптора (0x02 — RSN / WPA2, 0x01 —  |
|                          |          | застарілий WPA1, 0x03 — WAPI)               |
| Key Information          | 2 байти  | Бітові прапорці стану та версії ключів      |
| Key Length               | 2 байти  | Довжина сеансового шифру (16 байтів для     |
|                          |          | AES-128-CCMP, 32 байти для TKIP)            |
| Key Replay Counter       | 8 байтів | Монотонний 64-бітний лічильник точки        |
|                          |          | доступу проти атак повторного відтворення   |
| Key Nonce                | 32 байти | Псевдовипадкове число (ANonce у кадрах 1/3, |
|                          |          | SNonce у кадрі 2)                           |
| Key IV                   | 16 байтів| Вектор ініціалізації (заповнений нулями у   |
|                          |          | WPA2 CCMP)                                  |
| Key RSC                  | 8 байтів | Receive Sequence Counter (лічильник пакетів |
|                          |          | для групового ключа GTK)                    |
| Reserved                 | 8 байтів | Зарезервовано стандартом (нулі)             |
| Key MIC                  | 16 байтів| Код цілісності кадру (зміщення 81..96)      |
| Key Data Length          | 2 байти  | Довжина додаткових інформаційних елементів  |
| Key Data                 | Змінна   | RSN Information Element у кадрі 2, або      |
|                          |          | зашифрований за допомогою KEK ключ GTK у M3 |
+──────────────────────────┴──────────┴─────────────────────────────────────────────+
```

Поле **Key Information** (2 байти) містить критичні бітові прапорці, що визначають стан скінченного автомата рукостискання:
- `Bits 0..2 (Key Descriptor Version)`: версія алгоритму цілісності. Значення `1` позначає `HMAC-MD5` (застарілий WPA1/TKIP), значення `2` — `HMAC-SHA1-128` (WPA2/CCMP), значення `3` — `AES-128-CMAC` (WPA2/WPA3 з активованим захистом кадрів керування 802.11w PMF).
- `Bit 3 (Key Type)`: встановлений в `1` для індивідуальних парних ключів (Pairwise Key) та `0` для групових ключів (Group Key).
- `Bit 6 (Install)`: наказ клієнту завантажити отриманий ключ `TK` в апаратний модуль шифрування радіоадаптера.
- `Bit 7 (Key Ack)`: вимога підтвердження від приймача (AP встановлює цей біт у повідомленнях 1 і 3).
- `Bit 8 (Key MIC)`: вказує, що поле `Key MIC` містить валідний криптографічний підпис (обов'язково в повідомленнях 2, 3 та 4).
- `Bit 9 (Secure)`: встановлюється в `1`, коли початкова автентифікація завершена.
- `Bit 12 (Encrypted Key Data)`: вказує, що поле `Key Data` зашифроване ключем `KEK` за допомогою алгоритму AES Key Wrap (RFC 3394).

У перехопленому радіокадрі тіло EAPOL інкапсулюється в кадр даних 802.11 через заголовок логічного зв'язку IEEE 802.2 SNAP (Subnetwork Access Protocol) з кодом типу протоколу `0x888E` (802.1X Authentication):
```
[Заголовок кадру 802.11 MAC: 24-30 байтів]
[Заголовок LLC/SNAP: AA AA 03 00 00 00 88 8E: 8 байтів]
[Дескриптор EAPOL-Key: від 95 байтів і більше]
```

---

### 2. Криптографічний конвеєр розгортання ключів WPA2

Процес розрахунку та валідації складається з чотирьох послідовних математичних етапів:

```
+-----------------------------------------------------------------------------------+
|                        КОНВЕЄР РОЗГОРТАННЯ КЛЮЧІВ WPA2-PSK                        |
|                                                                                   |
|  1. Генерація Pairwise Master Key (PMK):                                          |
|     Пароль (Passphrase) + SSID ──► [PBKDF2-HMAC-SHA1, 4096 ітерацій] ──► PMK (32B)|
|                                                                                   |
|  2. Канонічне впорядкування параметрів зв'язку:                                   |
|     A_MAC, S_MAC ──► Min(A_MAC, S_MAC) || Max(A_MAC, S_MAC)  (12 байтів)           |
|     ANonce, SNonce ──► Min(ANonce, SNonce) || Max(ANonce, SNonce)  (64 байти)     |
|                                                                                   |
|  3. Псевдовипадкова функція розширення PRF-512:                                   |
|     Дані = "Pairwise key expansion\0" || MACs || Nonces || Лічильник (0..3)        |
|     PTK = HMAC-SHA1(PMK, Дані||0) || HMAC-SHA1(PMK, Дані||1) || ... (64 байти)    |
|                                                                                   |
|  4. Розщеплення блоку PTK (512 бітів / 64 байти):                                 |
|     [00..15] KCK (Key Confirmation Key, 128 біт) ──► Обчислення EAPOL-Key MIC    |
|     [16..31] KEK (Key Encryption Key, 128 біт)   ──► Розшифрування GTK у кадрі 3  |
|     [32..47] TK  (Temporal Key, 128 біт)         ──► Шифрування даних AES-CCMP    |
|     [48..63] Reserved / TK-MIC (для TKIP)        ──► Не використовується в CCMP   |
+-----------------------------------------------------------------------------------+
```

#### Крок 1. Обчислення майстер-ключа PMK
Майстер-ключ `PMK` формується зі змінного рядка пароля користувача (довжиною від 8 до 63 символів ASCII) та назви бездротової мережі `SSID` (до 32 байтів), яка виступає криптографічною сіллю (Salt):
```
PMK = PBKDF2(HMAC-SHA1, Passphrase, SSID, Iterations = 4096, OutputLength = 32 байти)
```
Фіксація 4096 ітерацій була обрана у 2004 році як компроміс між навантаженням на слабкі вбудовані процесори точок доступу та стійкістю до атак повного перебору. Оскільки сіль `SSID` транслюється відкрито у Beacon-кадрах, попереднє створення глобальних райдужних таблиць (Rainbow Tables) для всіх мереж одночасно стає неможливим: таблиці доводиться розраховувати під кожен окремий SSID індивідуально.

#### Крок 2. Канонічне впорядкування MAC-адрес та випадкових чисел Nonce
Щоб обидві сторони отримали повністю ідентичний вхідний масив для псевдовипадкової функції незалежно від того, хто є передавачем або отримувачем конкретного кадру, адреси та випадкові числа впорядковуються за числовою величиною:
```
Sorted_MACs   = min(AP_MAC, STA_MAC)   || max(AP_MAC, STA_MAC)    (12 байтів)
Sorted_Nonces = min(ANonce, SNonce)     || max(ANonce, SNonce)     (64 байти)
```
Порівняння виконується побайтово від старшого до молодшого розряду (лексикографічно).

#### Крок 3. Псевдовипадкова функція розширення PRF-512
Функція `PRF-512` розгортає 256-бітний `PMK` у 512-бітний сеансовий блок `PTK`. Вона працює в режимі лічильника на базі `HMAC-SHA1`:
```
Дані_i = "Pairwise key expansion" || 0x00 || Sorted_MACs || Sorted_Nonces || i
Блок_i = HMAC-SHA1(PMK, Дані_i)
PTK = Блок_0 || Блок_1 || Блок_2 || Блок_3   (беруться перші 64 байти)
```

#### Крок 4. Обчислення та перевірка коду цілісності EAPOL-Key MIC
Для перевірки коректності кандидатського пароля на перехопленому повідомленні 2 (M2) виконуються такі операції:
1. З кадру вилучається оригінальне 16-байтне значення поля `Key MIC` (зміщення 81 байт).
2. Поле `Key MIC` у робочому буфері кадру заповнюється 16 нулями `0x00`.
3. Розраховується хеш `HMAC-SHA1(KCK, Модифікований_EAPOL_Кадр)`.
4. Перші 16 байтів розрахованого дайджесту порівнюються з оригінальним перехопленим значенням у константному часі.

---

### 3. Програмна реалізація мовами C та C++

У наведеній нижче реалізації показано повний цикл: виведення `PMK`, генерацію `PTK` та верифікацію кадру EAPOL Message 2.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

#define PMK_LEN 32
#define PTK_LEN 64
#define MAC_LEN 6
#define NONCE_LEN 32
#define MIC_LEN 16
#define EAPOL_MIC_OFFSET 81

typedef struct {
    uint8_t kck[16]; /* Key Confirmation Key (перевірка MIC) */
    uint8_t kek[16]; /* Key Encryption Key (шифрування ключів) */
    uint8_t tk[16];  /* Temporal Key (шифрування трафіку CCMP) */
} wpa2_ptk_t;

/* Генерація PMK через PBKDF2(HMAC-SHA1, Passphrase, SSID, 4096, 32) */
bool wpa2_derive_pmk(const char *passphrase, const char *ssid, uint8_t pmk_out[PMK_LEN]) {
    if (!passphrase || !ssid || !pmk_out) return false;
    return PKCS5_PBKDF2_HMAC(passphrase, (int)strlen(passphrase),
                             (const uint8_t *)ssid, (int)strlen(ssid),
                             4096, EVP_sha1(), PMK_LEN, pmk_out) == 1;
}

/* Псевдовипадкова функція PRF-512 для генерації 64 байтів PTK */
bool wpa2_derive_ptk(const uint8_t pmk[PMK_LEN],
                     const uint8_t ap_mac[MAC_LEN], const uint8_t sta_mac[MAC_LEN],
                     const uint8_t anonce[NONCE_LEN], const uint8_t snonce[NONCE_LEN],
                     wpa2_ptk_t *ptk_out) {
    if (!pmk || !ap_mac || !sta_mac || !anonce || !snonce || !ptk_out) return false;

    /* 1. Префікс мітки стандарту IEEE 802.11i */
    const char *label = "Pairwise key expansion";
    size_t label_len = strlen(label) + 1; /* Включаючи нуль-термінатор */

    /* 2. Канонічне впорядкування MAC-адрес та Nonce */
    uint8_t mac_block[12];
    if (memcmp(ap_mac, sta_mac, MAC_LEN) < 0) {
        memcpy(mac_block, ap_mac, MAC_LEN);
        memcpy(mac_block + MAC_LEN, sta_mac, MAC_LEN);
    } else {
        memcpy(mac_block, sta_mac, MAC_LEN);
        memcpy(mac_block + MAC_LEN, ap_mac, MAC_LEN);
    }

    uint8_t nonce_block[64];
    if (memcmp(anonce, snonce, NONCE_LEN) < 0) {
        memcpy(nonce_block, anonce, NONCE_LEN);
        memcpy(nonce_block + NONCE_LEN, snonce, NONCE_LEN);
    } else {
        memcpy(nonce_block, snonce, NONCE_LEN);
        memcpy(nonce_block + NONCE_LEN, anonce, NONCE_LEN);
    }

    /* 3. Збирання префікса даних для PRF: Label || 0x00 || MACs || Nonces */
    uint8_t data_prefix[128];
    size_t offset = 0;
    memcpy(data_prefix + offset, label, label_len);
    offset += label_len;
    memcpy(data_prefix + offset, mac_block, sizeof(mac_block));
    offset += sizeof(mac_block);
    memcpy(data_prefix + offset, nonce_block, sizeof(nonce_block));
    offset += sizeof(nonce_block);

    /* 4. Ітеративне розширення через HMAC-SHA1 (4 блоки по 20 байтів для отримання 64 байтів) */
    uint8_t ptk_raw[80];
    for (uint8_t i = 0; i < 4; i++) {
        data_prefix[offset] = i; /* Додавання лічильника наприкінці */
        unsigned int md_len = 20;
        HMAC(EVP_sha1(), pmk, PMK_LEN, data_prefix, offset + 1, ptk_raw + (i * 20), &md_len);
    }

    /* 5. Розподіл ключів PTK */
    memcpy(ptk_out->kck, ptk_raw, 16);
    memcpy(ptk_out->kek, ptk_raw + 16, 16);
    memcpy(ptk_out->tk,  ptk_raw + 32, 16);

    /* Очищення чутливих тимчасових буферів у пам'яті */
    OPENSSL_cleanse(ptk_raw, sizeof(ptk_raw));
    OPENSSL_cleanse(data_prefix, sizeof(data_prefix));
    return true;
}

/* Верифікація EAPOL-Key Message 2 MIC */
bool wpa2_verify_eapol_mic(const uint8_t kck[16], const uint8_t *eapol_frame, size_t frame_len) {
    if (!kck || !eapol_frame || frame_len < EAPOL_MIC_OFFSET + MIC_LEN) return false;

    /* 1. Зчитування оригінального MIC із кадру */
    uint8_t original_mic[MIC_LEN];
    memcpy(original_mic, eapol_frame + EAPOL_MIC_OFFSET, MIC_LEN);

    /* 2. Копіювання кадру та обнулення поля MIC */
    uint8_t frame_copy[1024];
    if (frame_len > sizeof(frame_copy)) return false;
    memcpy(frame_copy, eapol_frame, frame_len);
    memset(frame_copy + EAPOL_MIC_OFFSET, 0, MIC_LEN);

    /* 3. Розрахунок HMAC-SHA1 над модифікованим кадром (WPA2 Key Descriptor v2) */
    uint8_t calculated_digest[20];
    unsigned int digest_len = sizeof(calculated_digest);
    HMAC(EVP_sha1(), kck, 16, frame_copy, frame_len, calculated_digest, &digest_len);

    /* 4. Порівняння перших 16 байтів у константному часі */
    bool match = (CRYPTO_memcmp(original_mic, calculated_digest, MIC_LEN) == 0);

    OPENSSL_cleanse(frame_copy, sizeof(frame_copy));
    OPENSSL_cleanse(calculated_digest, sizeof(calculated_digest));
    return match;
}

int main(void) {
    const char *ssid = "Office_Secure_WiFi";
    const char *passphrase = "CorrectHorseBatteryStaple99";

    uint8_t ap_mac[6]  = {0x00, 0x14, 0x6C, 0x7E, 0x40, 0x80};
    uint8_t sta_mac[6] = {0x00, 0x25, 0xD3, 0x11, 0x22, 0x33};

    uint8_t anonce[32] = {
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F
    };

    uint8_t snonce[32] = {
        0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7,
        0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF,
        0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
        0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF
    };

    uint8_t pmk[PMK_LEN];
    wpa2_derive_pmk(passphrase, ssid, pmk);

    wpa2_ptk_t ptk;
    wpa2_derive_ptk(pmk, ap_mac, sta_mac, anonce, snonce, &ptk);

    printf("=== WPA2 РОЗРАХУНОК КЛЮЧІВ ===\n");
    printf("SSID:       %s\n", ssid);
    printf("Passphrase: %s\n", passphrase);
    printf("KCK (Key Confirmation Key): ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.kck[i]);
    printf("\nKEK (Key Encryption Key):   ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.kek[i]);
    printf("\nTK  (Temporal CCMP Key):    ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.tk[i]);
    printf("\n\n");

    /* Тестовий кадр EAPOL-Key Message 2 (довжина 121 байт) */
    uint8_t test_eapol[121] = {0};
    test_eapol[0] = 0x02; /* EAPOL Version 2 */
    test_eapol[1] = 0x03; /* EAPOL-Key Type */
    test_eapol[4] = 0x02; /* Key Descriptor Type: RSN / WPA2 */
    test_eapol[6] = 0x01; /* Key Info: Pairwise + MIC встановлено */
    test_eapol[7] = 0x0A;

    /* Обчислення еталонного MIC */
    unsigned int len = 20;
    uint8_t full_digest[20];
    HMAC(EVP_sha1(), ptk.kck, 16, test_eapol, sizeof(test_eapol), full_digest, &len);
    memcpy(test_eapol + EAPOL_MIC_OFFSET, full_digest, 16);

    /* Перевірка верифікатора */
    bool valid = wpa2_verify_eapol_mic(ptk.kck, test_eapol, sizeof(test_eapol));
    printf("Результат верифікації EAPOL MIC: %s\n", valid ? "ПРАВИЛЬНИЙ (УСПІХ)" : "НЕПРАВИЛЬНИЙ (ПОМИЛКА)");

    OPENSSL_cleanse(pmk, sizeof(pmk));
    OPENSSL_cleanse(&ptk, sizeof(ptk));
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <array>
#include <span>
#include <string_view>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

namespace wifi::security {

constexpr size_t PmkSize = 32;
constexpr size_t PtkSize = 64;
constexpr size_t MacSize = 6;
constexpr size_t NonceSize = 32;
constexpr size_t MicSize = 16;
constexpr size_t EapolMicOffset = 81;

struct PtkKeys {
    std::array<uint8_t, 16> kck{}; // Key Confirmation Key (перевірка MIC)
    std::array<uint8_t, 16> kek{}; // Key Encryption Key (доставка GTK)
    std::array<uint8_t, 16> tk{};  // Temporal Key (шифрування CCMP)

    ~PtkKeys() noexcept {
        OPENSSL_cleanse(kck.data(), kck.size());
        OPENSSL_cleanse(kek.data(), kek.size());
        OPENSSL_cleanse(tk.data(), tk.size());
    }
};

// RAII обгортка для безпечного очищення чутливих буферів
template <size_t N>
struct SecureBuffer : public std::array<uint8_t, N> {
    ~SecureBuffer() noexcept {
        OPENSSL_cleanse(this->data(), this->size());
    }
};

// Генерація PMK через PBKDF2
[[nodiscard]] SecureBuffer<PmkSize> derivePmk(std::string_view passphrase, std::string_view ssid) {
    SecureBuffer<PmkSize> pmk{};
    int res = PKCS5_PBKDF2_HMAC(passphrase.data(), static_cast<int>(passphrase.size()),
                                reinterpret_cast<const uint8_t*>(ssid.data()), static_cast<int>(ssid.size()),
                                4096, EVP_sha1(), static_cast<int>(pmk.size()), pmk.data());
    if (res != 1) {
        throw std::runtime_error("Помилка генерації PMK через PBKDF2");
    }
    return pmk;
}

// Генерація PTK за алгоритмом PRF-512
[[nodiscard]] PtkKeys derivePtk(std::span<const uint8_t, PmkSize> pmk,
                                std::span<const uint8_t, MacSize> apMac,
                                std::span<const uint8_t, MacSize> staMac,
                                std::span<const uint8_t, NonceSize> aNonce,
                                std::span<const uint8_t, NonceSize> sNonce) {
    constexpr std::string_view label = "Pairwise key expansion";

    // 1. Канонічне впорядкування MAC-адрес
    std::array<uint8_t, MacSize * 2> macBlock{};
    if (std::lexicographical_compare(apMac.begin(), apMac.end(), staMac.begin(), staMac.end())) {
        std::copy(apMac.begin(), apMac.end(), macBlock.begin());
        std::copy(staMac.begin(), staMac.end(), macBlock.begin() + MacSize);
    } else {
        std::copy(staMac.begin(), staMac.end(), macBlock.begin());
        std::copy(apMac.begin(), apMac.end(), macBlock.begin() + MacSize);
    }

    // 2. Канонічне впорядкування Nonce
    std::array<uint8_t, NonceSize * 2> nonceBlock{};
    if (std::lexicographical_compare(aNonce.begin(), aNonce.end(), sNonce.begin(), sNonce.end())) {
        std::copy(aNonce.begin(), aNonce.end(), nonceBlock.begin());
        std::copy(sNonce.begin(), sNonce.end(), nonceBlock.begin() + NonceSize);
    } else {
        std::copy(sNonce.begin(), sNonce.end(), nonceBlock.begin());
        std::copy(aNonce.begin(), aNonce.end(), nonceBlock.begin() + NonceSize);
    }

    // 3. Формування вхідного буфера: Label || 0x00 || MACs || Nonces || Counter
    std::vector<uint8_t> dataPrefix;
    dataPrefix.reserve(label.size() + 1 + macBlock.size() + nonceBlock.size() + 1);
    dataPrefix.insert(dataPrefix.end(), label.begin(), label.end());
    dataPrefix.push_back(0x00);
    dataPrefix.insert(dataPrefix.end(), macBlock.begin(), macBlock.end());
    dataPrefix.insert(dataPrefix.end(), nonceBlock.begin(), nonceBlock.end());
    dataPrefix.push_back(0x00); // Позиція для лічильника ітерацій

    // 4. Ітеративне розширення PRF-512 (4 блоки по 20 байтів)
    SecureBuffer<80> ptkRaw{};
    for (uint8_t counter = 0; counter < 4; ++counter) {
        dataPrefix.back() = counter;
        unsigned int mdLen = 20;
        HMAC(EVP_sha1(), pmk.data(), static_cast<int>(pmk.size()),
             dataPrefix.data(), dataPrefix.size(),
             ptkRaw.data() + (counter * 20), &mdLen);
    }

    PtkKeys ptk;
    std::copy_n(ptkRaw.begin(), 16, ptk.kck.begin());
    std::copy_n(ptkRaw.begin() + 16, 16, ptk.kek.begin());
    std::copy_n(ptkRaw.begin() + 32, 16, ptk.tk.begin());

    OPENSSL_cleanse(dataPrefix.data(), dataPrefix.size());
    return ptk;
}

// Верифікація EAPOL MIC у константному часі
[[nodiscard]] bool verifyEapolMic(std::span<const uint8_t, 16> kck,
                                  std::span<const uint8_t> eapolFrame) noexcept {
    if (eapolFrame.size() < EAPOL_MICOffset + MicSize) {
        return false;
    }

    // 1. Копіювання отриманого MIC
    std::array<uint8_t, MicSize> originalMic{};
    std::copy_n(eapolFrame.begin() + EapolMicOffset, MicSize, originalMic.begin());

    // 2. Створення робочої копії кадру з обнуленим MIC
    std::vector<uint8_t> frameCopy(eapolFrame.begin(), eapolFrame.end());
    std::fill_n(frameCopy.begin() + EapolMicOffset, MicSize, 0x00);

    // 3. Обчислення HMAC-SHA1 над кадром
    std::array<uint8_t, 20> digest{};
    unsigned int digestLen = static_cast<unsigned int>(digest.size());
    HMAC(EVP_sha1(), kck.data(), static_cast<int>(kck.size()),
         frameCopy.data(), frameCopy.size(), digest.data(), &digestLen);

    // 4. Порівняння в константному часі
    int cmp = CRYPTO_memcmp(originalMic.data(), digest.data(), MicSize);

    OPENSSL_cleanse(frameCopy.data(), frameCopy.size());
    OPENSSL_cleanse(digest.data(), digest.size());
    return (cmp == 0);
}

} // namespace wifi::security

namespace {
void printHex(std::string_view label, std::span<const uint8_t> data) {
    std::cout << std::left << std::setw(28) << label << ": ";
    for (uint8_t b : data) {
        std::cout << std::hex << std::uppercase << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << std::dec << "\n";
}
}

int main() {
    using namespace wifi::security;

    const std::string_view ssid = "Office_Secure_WiFi";
    const std::string_view passphrase = "CorrectHorseBatteryStaple99";

    const std::array<uint8_t, 6> apMac  = {0x00, 0x14, 0x6C, 0x7E, 0x40, 0x80};
    const std::array<uint8_t, 6> staMac = {0x00, 0x25, 0xD3, 0x11, 0x22, 0x33};

    const std::array<uint8_t, 32> aNonce = {
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F
    };

    const std::array<uint8_t, 32> sNonce = {
        0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7,
        0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF,
        0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
        0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF
    };

    try {
        auto pmk = derivePmk(passphrase, ssid);
        auto ptk = derivePtk(pmk, apMac, staMac, aNonce, sNonce);

        std::cout << "=== WPA2 C++ РОЗРАХУНОК КЛЮЧІВ ===\n";
        std::cout << "SSID:       " << ssid << "\n";
        std::cout << "Passphrase: " << passphrase << "\n";
        printHex("KCK (Key Confirmation)", ptk.kck);
        printHex("KEK (Key Encryption)",   ptk.kek);
        printHex("TK  (Temporal CCMP Key)", ptk.tk);
        std::cout << "\n";

        // Синтез валідного EAPOL кадру для тестування
        std::vector<uint8_t> eapolFrame(121, 0x00);
        eapolFrame[0] = 0x02; // Version
        eapolFrame[1] = 0x03; // Type Key
        eapolFrame[4] = 0x02; // RSN Descriptor
        eapolFrame[6] = 0x01; // Key Info
        eapolFrame[7] = 0x0A;

        // Генерація еталонного підпису
        unsigned int len = 20;
        std::array<uint8_t, 20> digest{};
        HMAC(EVP_sha1(), ptk.kck.data(), static_cast<int>(ptk.kck.size()),
             eapolFrame.data(), eapolFrame.size(), digest.data(), &len);
        std::copy_n(digest.begin(), 16, eapolFrame.begin() + EapolMicOffset);

        bool isValid = verifyEapolMic(ptk.kck, eapolFrame);
        std::cout << "Результат верифікації: " << (isValid ? "ПРАВИЛЬНИЙ (УСПІХ)" : "ПОМИЛКА") << "\n";

    } catch (const std::exception &ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

### 4. Зіставлення ідіом розробки мовами C та C++

Порівняння двох реалізацій демонструє фундаментальну різницю між низькорівневим процедурним підходом мови C та безпечним об'єктно-орієнтованим дизайном сучасного C++:

1. **Безпека меж пам'яті (Bounds Safety):**
   У реалізації на C передача масивів виконується через «сирі» покажчики `uint8_t*` із явною передачею розміру `size_t frame_len`. Якщо викликач помилиться у передачі довжини, виникає критична вразливість виходу за межі буфера (Buffer Overflow / Out-of-bounds Read). У C++ застосовано концепцію `std::span` з фіксованими та динамічними екстентами (`std::span<const uint8_t, 16>`). Компілятор автоматично контролює розмірності масивів на етапі компіляції, унеможливлюючи передачу блоків некоректної довжини без жодних накладних витрат у рантаймі.

2. **Керування ресурсами та зачищення пам'яті (RAII):**
   У C зачищення криптографічних ключів виконується вручну через багаторазові виклики `OPENSSL_cleanse`. Якщо функція містить кілька гілок повернення помилок (`return false`), розробник ризикує пропустити очищення пам'яті в одній із гілок, залишаючи секретні байти в пам'яті стека. У C++ структури `PtkKeys` та `SecureBuffer` мають деструктори, які автоматично викликають гарантоване затирання пам'яті під час виходу зі скоупу (навіть у разі виникнення виняткових ситуацій `throw std::runtime_error`).

3. **Обробка помилок та семантика типів:**
   Функція на C повертає булевий прапорець успіху, а результат записує через вихідний покажчик `wpa2_ptk_t *ptk_out`. У C++ функція повертає готовий об'єкт за значенням (із застосуванням оптимізації копіювання RVO / Move Semantics), що робить інтерфейс чистим, строгим та самодокументованим.

---

### 5. Доставка групових ключів: алгоритм AES Key Wrap (RFC 3394)

У повідомленні 3 чотириетапного рукостискання точка доступу передає клієнту спільний груповий ключ **GTK** (Group Temporal Key, 128 або 256 бітів), призначений для розшифрування широкомовного трафіку (Broadcast / Multicast). Оскільки цей ключ передається через незахищений радіоефір, він попередньо зашифровується за допомогою сеансового ключа шифрування ключів **`KEK`** (Key Encryption Key, байти 16..31 блоку PTK).

Стандарт IEEE 802.11i використовує для цього стандартизований алгоритм **NIST AES Key Wrap (RFC 3394)**:

```
Вхід:
  K = KEK (128-бітний ключ обгортання)
  P = GTK (відкриті блоки P₁, P₂, ... P_n довжиною по 64 біти)
  IV = Фіксований вектор ініціалізації: A₀ = 0xA6A6A6A6A6A6A6A6

Алгоритм обгортання (Key Wrap):
  Для раундів r від 0 до 5:
      Для блоків i від 1 до n:
          t = n · r + i
          B = AES_Encrypt(K, A ⊕ t || R[i])
          A = перші 64 біти блоку B
          R[i] = другі 64 біти блоку B

Вихід:
  C = A || R₁ || R₂ || ... || R_n (зашифровані дані для поля Key Data кадру M3)
```

Під час розпакування (Key Unwrap) на боці клієнта операції виконуються у зворотному порядку за допомогою блоку `AES_Decrypt`. На фінальному кроці клієнт перевіряє значення результуючого регістра `A`: якщо воно строго дорівнює масці `0xA6A6A6A6A6A6A6A6`, ключ вважається цілісним та автентичним. Будь-яка модифікація зашифрованих байтів у радіоефірі призводить до повної руйнації контрольного значення `A`, що спричиняє негайне відхилення кадру M3.

---

### 6. Еволюція версій дескриптора ключів (Key Descriptor Versions)

Протокол EAPOL-Key розвивався разом із поправками до стандарту IEEE 802.11, утворюючи чотири криптографічні версії:

1. **Version 1 (WPA1 / TKIP):**
   Використовує хеш-функцію `HMAC-MD5` для обчислення поля Key MIC та потоковий шифр RC4 для обгортання ключів. Повністю застаріла через наявність практичних колізій у функції MD5 та математичних вразливостей шифру RC4.
2. **Version 2 (WPA2 / AES-CCMP):**
   Використовує `HMAC-SHA1-128` (перші 16 байтів дайджесту SHA-1) для розрахунку MIC та алгоритм AES Key Wrap (RFC 3394) для шифрування GTK. Є найпоширенішим промисловим стандартом останніх двох десятиліть.
3. **Version 3 (WPA2/WPA3 з захистом PMF / IEEE 802.11w):**
   Використовує симетричний блоковий алгоритм `AES-128-CMAC` (Cipher-based Message Authentication Code, NIST SP 800-38B) замість застарілого SHA-1. Повністю усуває вразливості, пов'язані з розширенням повідомлень за структурою Меркла — Дамґорда.
4. **Version 4 (WPA3-Enterprise 192-bit CNSA Suite):**
   Використовує `HMAC-SHA384` для генерації ключів, розширення PRF-384 та захист трафіку за допомогою 256-бітного автентифікованого блокового шифру `GCMP-256` (Galois/Counter Mode Protocol).

---

### 7. Архітектурні вимоги до безпеки та захист від побічних каналів

1. **Гарантоване зачищення криптографічних ключів у пам'яті (Zeroization):**
   Ключі `PMK`, `PTK`, `KCK` та проміжні масиви розширення ніколи не повинні залишатися в оперативній пам'яті після завершення розрахунків. Звичайний виклик `memset` може бути оптимізований і повністю видалений компілятором як «мертвий код» (Dead Store Elimination), якщо буфер більше не читається перед звільненням стекового кадру. Для запобігання оптимізації застосовуються спеціалізовані бар'єри пам'яті: `OPENSSL_cleanse`, `memset_s` або використання `volatile`-покажчиків. Це захищає систему від вилучення ключів під час аналізу аварійних дампів процесу (Core Dumps), повторного використання пам'яті купи (Heap Reuse) або атак апаратного зчитування залишкового заряду транзисторів після раптового вимкнення живлення (Cold Boot Attacks).

2. **Захист від атак за часом виконання (Constant-Time Verification):**
   Стандартна бібліотечна функція `memcmp` повертає результат негайно після виявлення першого байта, що не збігається. Якщо атакуючий надсилає тестові кадри з різними варіантами MIC через мережевий інтерфейс, час відповіді процесора відрізняється на кілька десятків тактів залежно від того, скільки перших байтів зійшлося. Використання функції `CRYPTO_memcmp` (яка побайтово підсумовує різницю через порозрядне бітове `OR` і перевіряє фінальний акумулятор лише після проходу всього 16-байтного масиву) гарантує строго однаковий час виконання незалежно від вхідних даних, повністю блокуючи побічні канали витоку інформації.

---

### 8. Оптимізація підбору на GPU та векторних інструкціях CPU (AVX-512)

Алгоритм верифікації EAPOL MIC є обчислювальним ядром усіх сучасних утиліт аудиту бездротової безпеки (таких як Hashcat, John the Ripper та Aircrack-ng). Оскільки 99.9% усього процесорного часу витрачається на розрахунок 4096 раундів `PBKDF2-HMAC-SHA1`, оптимізація цього вузького місця виконується двома шляхами:

1. **Векторизація SIMD та апаратні інструкції CPU (Intel SHA Extensions / ARMv8 Crypto):**
   Сучасні процесори x86-64 (начиная з мікроархітектур Intel Goldmont / Ice Lake та AMD Zen) містять спеціалізовані апаратні інструкції для прискорення гешування: `SHA1MSG1`, `SHA1MSG2`, `SHA1NEXTE` та `SHA1RNDS4`. На відміну від універсальних векторних інструкцій AVX2, ці інструкції виконують 4 повні раунди SHA-1 за 1 такт процесора безпосередньо у спеціалізованому конвеєрі кремнію. На мобільних та вбудованих платформах ARMv8-A аналогічну роль відіграють апаратні криптографічні команди `SHA1C`, `SHA1P`, `SHA1M` та `SHA1H`. 
   
   Поєднання апаратних інструкцій із паралельним виконанням на 16–32 ядрах процесора дозволяє досягти швидкості у понад 450 000–600 000 ітерацій перевірки паролів на секунду на звичайному серверному CPU без залучення дискретних графічних прискорювачів.

2. **Масивно-паралельні обчислення на GPU (CUDA / OpenCL):**
   Сучасна відеокарта високого класу (наприклад, NVIDIA RTX 4090 з понад 16 000 обчислювальних ядер CUDA) здатна розраховувати від 1.5 до 2.5 мільйона хешів `PMK` на секунду.

```
+-----------------------------------------------------------------------------------+
|                        ПРИСКОРЕННЯ ПЕРЕБОРУ В HASHCAT (MODE 22000)                |
|                                                                                   |
|  Оптимізація 1 (Early Reject на першому блоці PRF):                               |
|  Шейдер розраховує лише перший 20-байтний блок PRF-512 (який формує KCK).          |
|  Обчислюється перший 32-бітний фрагмент EAPOL MIC. Якщо перші 4 байти не           |
|  збігаються з оригіналом (ймовірність відсіювання 1 - 2⁻³² ≈ 99.99999998%),       |
|  потік CUDA негайно припиняє роботу з цим кандидатом, не витрачаючи такти на     |
|  решту 12 байтів MIC та генерацію ключів KEK і TK.                               |
|                                                                                   |
|  Оптимізація 2 (Попереднє гешування SSID):                                        |
|  Початковий стан масиву стану SHA-1 (H0..H4) після обробки внутрішнього префікса   |
|  iPad / oPad для фіксованого SSID розраховується один раз для всієї сесії перебору|
|  та завантажується в надшвидку розділювану пам'ять (Shared Memory) кристала GPU.  |
+-----------------------------------------------------------------------------------+
```

#### Атака через PMKID (2018)
У 2018 році розробник Hashcat Йенс Штойбе (Jens Steube) відкрив метод зламу WPA2 без необхідності перехоплювати повний 4-Way Handshake та без присутності активних клієнтів у радіоефірі.

Багато маршрутизаторів із підтримкою швидкого безшовного роумінгу стандарту IEEE 802.11r включають поле `PMKID` безпосередньо в перший відкритий кадр EAPOL (Message 1), який точка доступу відправляє у відповідь на звичайний запит асоціації:
```
PMKID = HMAC-SHA1(PMK, "PMK Name" || AP_MAC || STA_MAC)[0..15]
```

#### Формат запису гешів Hashcat Mode 22000
Сучасні утиліти аудиту (hcxdumptool / hcxtools) зберігають витягнуті дані рукостискання у стандартизованому рядковому форматі `mode 22000`:
```
WPA*02*MIC_HEX*MAC_AP*MAC_STA*ESSID_HEX*ANONCE_HEX*EAPOL_FRAME_HEX*MESSAGE_PAIR
```
де прапорець `MESSAGE_PAIR` інформує рушій про якість перехоплення:
- `0x00`: пара повідомлень M1+M2 (ініційована точкою доступу, підтверджена клієнтом, стандартна пара).
- `0x01`: пара повідомлень M2+M3 (підтверджує, що точка доступу прийняла SNonce клієнта).
- `0x02`: пара повідомлень M3+M4 (завершення сесії).

Формат `mode 22000` об'єднав у єдину структуру як класичні дампи 4-Way Handshake, так і одиночні вектори атак `PMKID`, що дозволило аналізаторам перевіряти комбіновані бази захоплених точок доступу за один прохід словника.

---

### 9. Архітектура багатопотокового рушія перевірки на C++

Для створення високопродуктивних утиліт аудиту на CPU застосовується системний патерн відображення файлів у пам'ять (Memory-Mapped Files, `mmap` у POSIX або `CreateFileMapping` у Windows). Словник розміром у десятки гігабайтів (наприклад, rockyou.txt) не зчитується посторінково через дорогі системні виклики `read`, а відображається безпосередньо у віртуальний адресний простір процесу як єдиний суцільний масив `std::string_view`.

```
[Файл словника на SSD (mmap)] ──► [Zero-Copy масив рядків std::string_view]
                                          │
       ┌──────────────────────────────────┴──────────────────────────────────┐
       ▼                                  ▼                                  ▼
[Воркер 1 (std::jthread)]      [Воркер 2 (std::jthread)]          [Воркер N (std::jthread)]
  Chunk: 0 .. 100 000            Chunk: 100 001 .. 200 000          Chunk: (N-1)·K .. N·K
  PBKDF2 ──► PRF ──► MIC         PBKDF2 ──► PRF ──► MIC             PBKDF2 ──► PRF ──► MIC
       │                                  │                                  │
       └──────────────────────────────────┼──────────────────────────────────┘
                                          ▼
                         [std::atomic<bool> password_found]
```

Кожен потік `std::jthread` отримує фіксований діапазон зміщень у відображеній пам'яті. Коли один із потоків виявляє збіг поля MIC, він записує знайдений пароль у захищений буфер результату та переводить атомарний прапорець `password_found` у стан `true`. Решта потоків перевіряють цей прапорець на кожній ітерації та негайно завершують виконання, вивільняючи ресурси процесора.

---

### 10. Розшифрування радіотрафіку у Wireshark за допомогою сеансового TK

Коли пароль мережі відомий або відновлений за словником, мережеві аналізатори (наприклад, Wireshark або `tshark`) розшифровують весь сеансовий трафік користувача. 

Для цього користувач відкриває меню налаштувань Wireshark (`Edit` ──► `Preferences` ──► `Protocols` ──► `IEEE 802.11` ──► `Decryption Keys`), обирає тип ключа `wpa-pwd` та вказує значення у форматі `Passphrase:SSID` (наприклад, `CorrectHorseBatteryStaple99:Office_Secure_WiFi`). За допомогою фільтра відображення `eapol` дослідник ізолює кадри рукостискання, переконуючись у наявності всіх чотирьох повідомлень або пари M1+M2.

Wireshark відстежує чотири кадри EAPOL-Key конкретної сесії, зчитує `ANonce`, `SNonce`, MAC-адреси та розраховує сеансовий ключ `TK` за алгоритмом, наведеним у нашому коді. Отриманий 128-бітний ключ `TK` завантажується у внутрішній дешифратор CCMP. Кожен наступний кадр даних із відповідними адресами та монотонно зростаючим `PN` розшифровується в реальному часі через режим AES-CTR, відкриваючи повний вміст заголовків IPv4/IPv6, TCP-сесій та корисного навантаження прикладного рівня.
