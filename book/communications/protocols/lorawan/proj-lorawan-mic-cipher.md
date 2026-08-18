# ⚙️ Реалізація розрахунку MIC та шифрування корисного навантаження LoRaWAN

Криптографічний захист у мережах LoRaWAN побудований на симетричному блоковому шифрі AES-128, проте кінцеві вузли зазвичай побудовані на надзвичайно обмежених мікроконтролерах (ARM Cortex-M0+, MSP430, AVR) з кількома кілобайтами оперативної пам'яті. Щоб забезпечити надійну автентифікацію та конфіденційність без перевантаження процесора, специфікація LoRaWAN використовує два стандартизовані криптографічні режими:
1. **AES-CMAC (RFC 4493)** для розрахунку 4-байтного коду автентичності повідомлення (англ. *Message Integrity Code*, MIC);
2. **AES-128 у режимі лічильника (CTR)** для потокового шифрування та розшифрування корисного навантаження кадру `FRMPayload`.

Розгляньмо математичний алгоритм формування службових блоків, генерації підключів і покрокову реалізацію повного криптографічного контуру мовами C та C++.

### 1. Математичні основи блокового шифру AES-128 у вбудованих системах

Алгоритм AES (англ. *Advanced Encryption Standard*, Rijndael) оперує матрицею стану розміром 4×4 байти (128 бітів). Процес шифрування складається з 10 раундів послідовних перетворень над полем Галуа `GF(2^8)` за незвідним поліномом `m(x) = x^8 + x^4 + x^3 + x + 1` (шістнадцяткове значення `0x11B`):

1. **SubBytes (Підстановка байтів):** Нелінійне перетворення, де кожен байт замінюється значенням із фіксованої таблиці підстановок S-Box. S-Box будується як мультиплікативна інверсія в полі `GF(2^8)` із подальшим афінним перетворенням над `GF(2)`. Вона забезпечує максимальну конфузію (англ. *Confusion*), унеможливлюючи лінійний та диференційний криптоаналіз.
2. **ShiftRows (Зсув рядків):** Циклічний зсув байтів у рядках матриці стану вліво: нульовий рядок не зсувається, перший зсувається на 1 байт, другий на 2, третій на 3. Це перетворення забезпечує дифузію (англ. *Diffusion*) між стовпчиками стану.
3. **MixColumns (Змішування стовпчиків):** Кожен стовпчик матриці множиться на фіксований поліном `c(x) = {03}x^3 + {01}x^2 + {01}x + {02}` за модулем `x^4 + 1`. Множення на `{02}` у полі `GF(2^8)` реалізується простою операцією зсуву вліво на 1 біт з умовним додаванням константи `0x1B` у разі переповнення (функція `xtime`). У десятому (фінальному) раунді перетворення MixColumns опускається.
4. **AddRoundKey (Додавання раундового ключа):** Побайтове додавання матриці стану з відповідним 128-бітним раундовим ключем за допомогою операції XOR.

#### Процедура розгортання ключа (Key Expansion)

128-бітний базовий ключ розгортається в масив з 11 раундових ключів (загалом 176 байтів або 44 32-бітні слова `W[0..43]`). Перші 4 слова заповнюються байтами вихідного ключа. Кожне наступне слово `W[i]` обчислюється як:

```
W[i] = W[i - 4] ⊕ W[i - 1]                  [для i, не кратних 4]
W[i] = W[i - 4] ⊕ SubWord(RotWord(W[i - 1])) ⊕ Rcon[i / 4]  [для i, кратних 4]
```

Тут операція `RotWord` виконує циклічний зсув 4-байтного слова вліво на 1 байт (`[a0, a1, a2, a3] → [a1, a2, a3, a0]`), `SubWord` застосовує таблицю S-Box до кожного байта, а константа раунду `Rcon[j]` містить значення степеня `x^(j-1)` у полі `GF(2^8)`.

### 2. Формування вхідного блоку `B0` та алгоритм AES-CMAC для розрахунку MIC

Код автентичності MIC розраховується над конкатенацією спеціального службового блоку `B0` та всіх полів кадру MAC (`MHDR | FHDR | FPort | FRMPayload`).

Службовий блок `B0` має фіксовану довжину 16 байтів (128 бітів) і формується за такою структурою:

```
Блок B0 (16 байтів):
[0]      : 0x49 (фіксований прапорець блоку B0)
[1..4]   : 0x00, 0x00, 0x00, 0x00 (зарезервовано)
[5]      : Dir (напрямок: 0x00 для Uplink, 0x01 для Downlink)
[6..9]   : DevAddr (32-бітна адреса пристрою, Little-Endian)
[10..13] : FCnt (32-бітний лічильник кадру FCntUp/FCntDown, Little-Endian)
[14]     : 0x00 (зарезервовано)
[15]     : len (довжина повідомлення: MHDR + FHDR + FPort + FRMPayload)
```

Включення полів `DevAddr`, `FCnt` та `Dir` безпосередньо у вхідний блок автентифікації гарантує, що зловмисник не зможе:
- Перенаправити пакет іншому пристрою шляхом підміни заголовка `DevAddr`;
- Повторно надіслати старий записаний пакет (захист від атак повтору через монотонний лічильник `FCnt`);
- Віддзеркалити висхідний пакет у низхідний канал зв'язку (захист від атак відображення через прапорець `Dir`).

#### Алгоритм генерації підключів CMAC (RFC 4493)

Для усунення вразливостей класичного CBC-MAC до атак дописування блоків у кінець повідомлення змінної довжини (англ. *Length Extension Attack*), стандарт AES-CMAC генерує два 128-бітні допоміжні ключі `K1` та `K2` з базового мережевого ключа `NwkSKey`:

1. Обчислюється шифрування нульового блоку: `L = AES128_encrypt(NwkSKey, 0^128)`.
2. Якщо старший біт `L` дорівнює 0 (тобто `(L[0] & 0x80) == 0`):
   `K1 = L << 1`.
   Якщо старший біт `L` дорівнює 1:
   `K1 = (L << 1) ⊕ 0x87` (де константа `0x87` відповідає неприводимому поліному `x^128 + x^7 + x^2 + x + 1` у полі `GF(2^128)`).
3. Аналогічно з ключа `K1` генерується другий допоміжний ключ `K2`:
   Якщо старший біт `K1` дорівнює 0:
   `K2 = K1 << 1`.
   Якщо старший біт `K1` дорівнює 1:
   `K2 = (K1 << 1) ⊕ 0x87`.

Повідомлення `M = B0 | PHYPayload[0 .. len-1]` розбивається на 16-байтні блоки `M_1, M_2, ..., M_n`.
- Якщо останній блок `M_n` є повним (рівно 16 байтів), до нього застосовується операція маскування першим ключем: `M_n = M_n ⊕ K1`.
- Якщо останній блок є неповним (довжина менше 16 байтів), він доповнюється байтом `0x80` (біт `1`), за яким слідують нульові байти до досягнення 16 байтів, після чого застосовується маскування другим ключем: `M_n = M_n ⊕ K2`.

Після маскування виконується стандартне послідовне шифрування блоків у режимі CBC (Cipher Block Chaining) з нульовим вектором ініціалізації:
```
Y_0 = 0^128
Y_i = AES128_encrypt(NwkSKey, Y_(i-1) ⊕ M_i)   [для i = 1 .. n]
```

Перші 4 байти останнього вихідного блоку `Y_n[0..3]` і є шуканим 4-байтним значенням `MIC`.

### 3. Формування блоків `A_i` та потокове шифрування AES-CTR

Корисне навантаження кадру `FRMPayload` шифрується симетричним потоковим шифром на базі AES-128 в режимі лічильника (CTR). Якщо поле `FPort = 0` (кадр містить службові MAC-команди мережевого рівня), шифрування здійснюється за допомогою мережевого сесійного ключа `NwkSKey`. Якщо `FPort ≥ 1` (дані користувача або додатка), використовується сесійний ключ додатку `AppSKey`.

Для кожного 16-байтного блоку корисного навантаження `k ∈ [1, ceil(len / 16)]` генерується унікальний вектор лічильника `A_k`:

```
Блок A_k (16 байтів):
[0]      : 0x01 (фіксований прапорець лічильника A_k)
[1..4]   : 0x00, 0x00, 0x00, 0x00 (зарезервовано)
[5]      : Dir (0x00 для Uplink, 0x01 для Downlink)
[6..9]   : DevAddr (32-бітна адреса пристрою, Little-Endian)
[10..13] : FCnt (32-бітний лічильник кадру, Little-Endian)
[14]     : 0x00 (зарезервовано)
[15]     : k (номер блоку: 1, 2, 3, ...)
```

Кожен вектор `A_k` шифрується базовим ключем AES-128, утворюючи 16-байтний блок псевдовипадкової гами (англ. *Keystream Block*) `S_k`:

```
S_k = AES128_encrypt(Key, A_k)
```

Шифротекст утворюється побайтовим додаванням за модулем 2 (XOR) відкритого тексту корисного навантаження `Payload` та блоку гами `S_k`:

```
Ciphertext[i] = Plaintext[i] ⊕ S_k[i % 16]
```

Оскільки операція додавання за модулем 2 є строгою інволюцією (`(A ⊕ B) ⊕ B = A`), процедура дешифрування є абсолютно тотожною: отриманий шифротекст знову додається через XOR з тотожно згенерованими блоками гами `S_k`. Це виключає потребу в реалізації зворотного перетворення AES (InvSubBytes, InvShiftRows, InvMixColumns), заощаджуючи пам'ять програм мікроконтролера.

### 4. Криптографія процедури активації OTAA та деривація сесійних ключів

Під час бездротової активації OTAA кінцевий вузол та сервер безпеки Join Server узгоджують динамічні сесійні ключі без їх передачі у відкритому радіоефірі.

#### 1. Захист кадру Join-Request
Вузол формує повідомлення активації: `M = MHDR (0x00) | JoinEUI (8 Б) | DevEUI (8 Б) | DevNonce (2 Б)`.
Код автентичності `MIC` для запиту активації розраховується як перші 4 байти AES-CMAC за допомогою кореневого ключа **`AppKey`**:
```
MIC_join = AES_CMAC(AppKey, MHDR | JoinEUI | DevEUI | DevNonce)[0..3]
```

#### 2. Захист та дешифрування відповіді Join-Accept
Якщо автентифікація успішна, Join Server формує відповідь:
`JoinAcceptPayload = AppNonce (3 Б) | NetID (3 Б) | DevAddr (4 Б) | DLSettings (1 Б) | RxDelay (1 Б) | CFList (0 або 16 Б) | MIC (4 Б)`.

Щоб мінімізувати розмір кодової бази на мікроконтролері, творці стандарту LoRaWAN застосували елегантний архітектурний прийом: сервер шифрує корисне навантаження `Join-Accept` за допомогою функції **дешифрування AES-128 (AES Decrypt)** у режимі ECB:
```
JoinAccept_Radio = AES128_decrypt(AppKey, JoinAcceptPayload)
```
Завдяки цьому кінцевий пристрій для розшифрування прийнятого кадру викликає звичайну функцію **прямого шифрування (AES Encrypt)**:
```
JoinAcceptPayload = AES128_encrypt(AppKey, JoinAccept_Radio)
```
Це позбавляє розробника необхідності компілювати громіздкі таблиці зворотного S-Box (InvSBox) та функції InvMixColumns, звільняючи понад 2 КБ дорогоцінної Flash-пам'яті мікроконтролера.

#### 3. Формули деривації сесійних ключів
Після успішного розшифрування `Join-Accept` пристрій та Join Server незалежно генерують два робочі сесійні ключі:

```
NwkSKey = AES128_encrypt(AppKey, 0x01 | AppNonce (3 Б) | NetID (3 Б) | DevNonce (2 Б) | pad7 (7 Б))
AppSKey = AES128_encrypt(AppKey, 0x02 | AppNonce (3 Б) | NetID (3 Б) | DevNonce (2 Б) | pad7 (7 Б))
```
Тут `pad7` — сім нульових байтів (`0x00 * 7`), що доповнюють вхідний блок деривації до стандартних 16 байтів AES.

### 5. Еволюція криптографічної моделі у LoRaWAN 1.1

У версії LoRaWAN 1.1 криптографічний контур зазнав подальшого посилення для запобігання атакам з боку компрометованих операторів базових станцій та підтримки захищеного міжмережевого роумінгу.

Замість єдиного мережевого ключа `NwkSKey` було введено три спеціалізовані сесійні ключі:
1. `FNwkSIntKey` (Forwarding Network Session Integrity Key) — використовується для розрахунку перших 2 байтів коду `MIC` висхідних повідомлень (перевіряється мережею, що безпосередньо прийняла пакет);
2. `SNwkSIntKey` (Serving Network Session Integrity Key) — використовується для розрахунку старших 2 байтів коду `MIC` висхідних повідомлень та повного 4-байтного `MIC` низхідних повідомлень (перевіряється домашнім сервером пристрою);
3. `NwkSEncKey` (Network Session Encryption Key) — використовується виключно для шифрування та дешифрування службових команд керування каналом (MAC-команд) на нульовому порту `FPort = 0`.

Кореневі ключі також розділено: оператор домашньої мережі володіє `NwkKey`, а власник додатка контролює `AppKey`. Це забезпечує повну криптографічну ізоляцію: оператор транзитної мережі здатний лише маршрутизувати зашифровані пакети та перевіряти цілісність радіоканалу, не маючи доступу ані до телеметрії додатка, ані до внутрішніх команд керування.

### 6. Програмна реалізація контуру безпеки LoRaWAN

Нижче наведено повністю робочу, самодостатню реалізацію криптографічного контуру LoRaWAN мовами C та ідіоматичною C++. Реалізація оптимізована для вбудованих систем: вона не використовує динамічного виділення пам'яті (malloc/new), не містить сторонніх залежностей і повністю відповідає вимогам стандарту LoRaWAN Link Layer Specification v1.0.4.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

/* Таблиця нелінійної підстановки S-Box алгоритму AES */
static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

/* Множення на x у полі Галуа GF(2^8) з редукцією за поліномом 0x1B */
static inline uint8_t xtime(uint8_t x) {
    return (uint8_t)((x << 1) ^ (((x >> 7) & 1) * 0x1b));
}

/* Розгортання 128-бітного ключа на 11 раундових ключів (176 байтів) */
static void aes_key_expansion(const uint8_t key[16], uint8_t round_keys[176]) {
    static const uint8_t rcon[10] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36};
    memcpy(round_keys, key, 16);
    for (int i = 4; i < 44; ++i) {
        uint8_t temp[4];
        memcpy(temp, &round_keys[(i - 1) * 4], 4);
        if (i % 4 == 0) {
            uint8_t k = temp[0];
            temp[0] = sbox[temp[1]] ^ rcon[(i / 4) - 1];
            temp[1] = sbox[temp[2]];
            temp[2] = sbox[temp[3]];
            temp[3] = sbox[k];
        }
        for (int j = 0; j < 4; ++j) {
            round_keys[i * 4 + j] = round_keys[(i - 4) * 4 + j] ^ temp[j];
        }
    }
}

/* Одноблокове шифрування AES-128 над матрицею 16 байтів */
static void aes_encrypt_block(const uint8_t in[16], uint8_t out[16], const uint8_t round_keys[176]) {
    uint8_t state[16];
    for (int i = 0; i < 16; ++i) state[i] = in[i] ^ round_keys[i];

    for (int round = 1; round <= 10; ++round) {
        for (int i = 0; i < 16; ++i) state[i] = sbox[state[i]];

        /* ShiftRows */
        uint8_t t;
        t = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = t;
        t = state[2]; state[2] = state[10]; state[10] = t; t = state[6]; state[6] = state[14]; state[14] = t;
        t = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = state[3]; state[3] = t;

        if (round < 10) {
            /* MixColumns */
            for (int i = 0; i < 4; ++i) {
                int c = i * 4;
                uint8_t a = state[c], b = state[c + 1], c_val = state[c + 2], d = state[c + 3];
                state[c]     = xtime(a ^ b) ^ b ^ c_val ^ d;
                state[c + 1] = xtime(b ^ c_val) ^ c_val ^ d ^ a;
                state[c + 2] = xtime(c_val ^ d) ^ d ^ a ^ b;
                state[c + 3] = xtime(d ^ a) ^ a ^ b ^ c_val;
            }
        }
        for (int i = 0; i < 16; ++i) state[i] ^= round_keys[round * 16 + i];
    }
    memcpy(out, state, 16);
}

/* Зсув 128-бітного масиву вліво на 1 біт з додаванням поліному 0x87 у GF(2^128) */
static void cmac_shift_left(const uint8_t in[16], uint8_t out[16]) {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        out[i] = (uint8_t)((in[i] << 1) | overflow);
        overflow = (in[i] & 0x80) ? 1 : 0;
    }
    if (in[0] & 0x80) {
        out[15] ^= 0x87;
    }
}

/* Генерація додаткових ключів K1 та K2 для алгоритму CMAC */
static void cmac_generate_subkeys(const uint8_t round_keys[176], uint8_t k1[16], uint8_t k2[16]) {
    uint8_t zero[16] = {0};
    uint8_t l[16];
    aes_encrypt_block(zero, l, round_keys);
    cmac_shift_left(l, k1);
    cmac_shift_left(k1, k2);
}

/* Обчислення коду цілісності MIC (4 байти) згідно з RFC 4493 */
uint32_t lorawan_compute_mic(const uint8_t *msg, size_t msg_len,
                             uint32_t dev_addr, uint32_t fcnt,
                             uint8_t dir, const uint8_t nwk_skey[16]) {
    uint8_t round_keys[176];
    uint8_t k1[16], k2[16];
    aes_key_expansion(nwk_skey, round_keys);
    cmac_generate_subkeys(round_keys, k1, k2);

    /* Формування 16-байтного блоку B0 */
    uint8_t b0[16] = {0};
    b0[0] = 0x49;
    b0[5] = dir;
    b0[6] = (uint8_t)(dev_addr & 0xFF);
    b0[7] = (uint8_t)((dev_addr >> 8) & 0xFF);
    b0[8] = (uint8_t)((dev_addr >> 16) & 0xFF);
    b0[9] = (uint8_t)((dev_addr >> 24) & 0xFF);
    b0[10] = (uint8_t)(fcnt & 0xFF);
    b0[11] = (uint8_t)((fcnt >> 8) & 0xFF);
    b0[12] = (uint8_t)((fcnt >> 16) & 0xFF);
    b0[13] = (uint8_t)((fcnt >> 24) & 0xFF);
    b0[15] = (uint8_t)msg_len;

    /* Розрахунок кількості 16-байтних блоків повідомлення */
    size_t total_len = 16 + msg_len;
    size_t n_blocks = (total_len + 15) / 16;
    bool is_last_complete = (total_len % 16 == 0);

    uint8_t x[16] = {0};
    uint8_t y[16] = {0};

    for (size_t i = 0; i < n_blocks; ++i) {
        uint8_t block[16] = {0};
        size_t block_offset = i * 16;

        for (size_t j = 0; j < 16; ++j) {
            size_t idx = block_offset + j;
            if (idx < 16) {
                block[j] = b0[idx];
            } else if (idx < total_len) {
                block[j] = msg[idx - 16];
            } else if (idx == total_len) {
                block[j] = 0x80; /* Додавання біта 1 у разі неповного блоку */
            }
        }

        if (i == n_blocks - 1) {
            const uint8_t *k = is_last_complete ? k1 : k2;
            for (int j = 0; j < 16; ++j) block[j] ^= k[j];
        }

        for (int j = 0; j < 16; ++j) y[j] = x[j] ^ block[j];
        aes_encrypt_block(y, x, round_keys);
    }

    return (uint32_t)x[0] | ((uint32_t)x[1] << 8) | ((uint32_t)x[2] << 16) | ((uint32_t)x[3] << 24);
}

/* Потокове шифрування та розшифрування корисного навантаження (AES-128 CTR) */
void lorawan_cipher_payload(uint8_t *payload, size_t payload_len,
                            uint32_t dev_addr, uint32_t fcnt,
                            uint8_t dir, const uint8_t key[16]) {
    if (payload_len == 0) return;

    uint8_t round_keys[176];
    aes_key_expansion(key, round_keys);

    uint8_t a_block[16] = {0};
    a_block[0] = 0x01;
    a_block[5] = dir;
    a_block[6] = (uint8_t)(dev_addr & 0xFF);
    a_block[7] = (uint8_t)((dev_addr >> 8) & 0xFF);
    a_block[8] = (uint8_t)((dev_addr >> 16) & 0xFF);
    a_block[9] = (uint8_t)((dev_addr >> 24) & 0xFF);
    a_block[10] = (uint8_t)(fcnt & 0xFF);
    a_block[11] = (uint8_t)((fcnt >> 8) & 0xFF);
    a_block[12] = (uint8_t)((fcnt >> 16) & 0xFF);
    a_block[13] = (uint8_t)((fcnt >> 24) & 0xFF);

    size_t n_blocks = (payload_len + 15) / 16;
    for (size_t i = 1; i <= n_blocks; ++i) {
        a_block[15] = (uint8_t)i;
        uint8_t s_block[16];
        aes_encrypt_block(a_block, s_block, round_keys);

        size_t bytes_to_xor = (i == n_blocks && payload_len % 16 != 0) ? (payload_len % 16) : 16;
        for (size_t j = 0; j < bytes_to_xor; ++j) {
            payload[(i - 1) * 16 + j] ^= s_block[j];
        }
    }
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <algorithm>

namespace lorawan::crypto {

// Таблиця підстановок S-Box алгоритму AES
inline constexpr std::array<uint8_t, 256> sbox = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

constexpr uint8_t xtime(uint8_t x) noexcept {
    return static_cast<uint8_t>((x << 1) ^ (((x >> 7) & 1) * 0x1b));
}

// Криптографічний рушій AES-128
class Aes128Engine {
public:
    explicit Aes128Engine(std::span<const uint8_t, 16> key) noexcept {
        expand_key(key);
    }

    void encrypt_block(std::span<const uint8_t, 16> in, std::span<uint8_t, 16> out) const noexcept {
        std::array<uint8_t, 16> state{};
        for (size_t i = 0; i < 16; ++i) state[i] = in[i] ^ round_keys_[i];

        for (int round = 1; round <= 10; ++round) {
            for (size_t i = 0; i < 16; ++i) state[i] = sbox[state[i]];

            // ShiftRows
            uint8_t t = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = t;
            t = state[2]; state[2] = state[10]; state[10] = t; t = state[6]; state[6] = state[14]; state[14] = t;
            t = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = state[3]; state[3] = t;

            if (round < 10) {
                // MixColumns
                for (size_t i = 0; i < 4; ++i) {
                    size_t c = i * 4;
                    uint8_t a = state[c], b = state[c + 1], c_val = state[c + 2], d = state[c + 3];
                    state[c]     = xtime(a ^ b) ^ b ^ c_val ^ d;
                    state[c + 1] = xtime(b ^ c_val) ^ c_val ^ d ^ a;
                    state[c + 2] = xtime(c_val ^ d) ^ d ^ a ^ b;
                    state[c + 3] = xtime(d ^ a) ^ a ^ b ^ c_val;
                }
            }
            for (size_t i = 0; i < 16; ++i) state[i] ^= round_keys_[round * 16 + i];
        }
        std::copy(state.begin(), state.end(), out.begin());
    }

private:
    std::array<uint8_t, 176> round_keys_{};

    void expand_key(std::span<const uint8_t, 16> key) noexcept {
        constexpr std::array<uint8_t, 10> rcon = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36};
        std::copy(key.begin(), key.end(), round_keys_.begin());
        for (size_t i = 4; i < 44; ++i) {
            std::array<uint8_t, 4> temp{};
            std::copy_n(&round_keys_[(i - 1) * 4], 4, temp.begin());
            if (i % 4 == 0) {
                uint8_t k = temp[0];
                temp[0] = sbox[temp[1]] ^ rcon[(i / 4) - 1];
                temp[1] = sbox[temp[2]];
                temp[2] = sbox[temp[3]];
                temp[3] = sbox[k];
            }
            for (size_t j = 0; j < 4; ++j) {
                round_keys_[i * 4 + j] = round_keys_[(i - 4) * 4 + j] ^ temp[j];
            }
        }
    }
};

void cmac_shift_left(std::span<const uint8_t, 16> in, std::span<uint8_t, 16> out) noexcept {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        out[i] = static_cast<uint8_t>((in[i] << 1) | overflow);
        overflow = (in[i] & 0x80) ? 1 : 0;
    }
    if (in[0] & 0x80) {
        out[15] ^= 0x87;
    }
}

// Розрахунок коду цілісності MIC з гарантією відсутності динамічної пам'яті
[[nodiscard]] uint32_t compute_mic(std::span<const uint8_t> msg,
                                   uint32_t dev_addr, uint32_t fcnt,
                                   uint8_t dir, std::span<const uint8_t, 16> nwk_skey) noexcept {
    const Aes128Engine aes(nwk_skey);

    std::array<uint8_t, 16> zero{};
    std::array<uint8_t, 16> l{}, k1{}, k2{};
    aes.encrypt_block(zero, l);
    cmac_shift_left(l, k1);
    cmac_shift_left(k1, k2);

    std::array<uint8_t, 16> b0{};
    b0[0] = 0x49;
    b0[5] = dir;
    b0[6] = static_cast<uint8_t>(dev_addr & 0xFF);
    b0[7] = static_cast<uint8_t>((dev_addr >> 8) & 0xFF);
    b0[8] = static_cast<uint8_t>((dev_addr >> 16) & 0xFF);
    b0[9] = static_cast<uint8_t>((dev_addr >> 24) & 0xFF);
    b0[10] = static_cast<uint8_t>(fcnt & 0xFF);
    b0[11] = static_cast<uint8_t>((fcnt >> 8) & 0xFF);
    b0[12] = static_cast<uint8_t>((fcnt >> 16) & 0xFF);
    b0[13] = static_cast<uint8_t>((fcnt >> 24) & 0xFF);
    b0[15] = static_cast<uint8_t>(msg.size());

    const size_t total_len = 16 + msg.size();
    const size_t n_blocks = (total_len + 15) / 16;
    const bool is_last_complete = (total_len % 16 == 0);

    std::array<uint8_t, 16> x{}, y{};

    for (size_t i = 0; i < n_blocks; ++i) {
        std::array<uint8_t, 16> block{};
        const size_t block_offset = i * 16;

        for (size_t j = 0; j < 16; ++j) {
            size_t idx = block_offset + j;
            if (idx < 16) {
                block[j] = b0[idx];
            } else if (idx < total_len) {
                block[j] = msg[idx - 16];
            } else if (idx == total_len) {
                block[j] = 0x80;
            }
        }

        if (i == n_blocks - 1) {
            const auto& k = is_last_complete ? k1 : k2;
            for (size_t j = 0; j < 16; ++j) block[j] ^= k[j];
        }

        for (size_t j = 0; j < 16; ++j) y[j] = x[j] ^ block[j];
        aes.encrypt_block(y, x);
    }

    return static_cast<uint32_t>(x[0]) |
          (static_cast<uint32_t>(x[1]) << 8) |
          (static_cast<uint32_t>(x[2]) << 16) |
          (static_cast<uint32_t>(x[3]) << 24);
}

// Потокове шифрування корисного навантаження (AES-128 CTR)
void cipher_payload(std::span<uint8_t> payload,
                    uint32_t dev_addr, uint32_t fcnt,
                    uint8_t dir, std::span<const uint8_t, 16> key) noexcept {
    if (payload.empty()) return;

    const Aes128Engine aes(key);

    std::array<uint8_t, 16> a_block{};
    a_block[0] = 0x01;
    a_block[5] = dir;
    a_block[6] = static_cast<uint8_t>(dev_addr & 0xFF);
    a_block[7] = static_cast<uint8_t>((dev_addr >> 8) & 0xFF);
    a_block[8] = static_cast<uint8_t>((dev_addr >> 16) & 0xFF);
    a_block[9] = static_cast<uint8_t>((dev_addr >> 24) & 0xFF);
    a_block[10] = static_cast<uint8_t>(fcnt & 0xFF);
    a_block[11] = static_cast<uint8_t>((fcnt >> 8) & 0xFF);
    a_block[12] = static_cast<uint8_t>((fcnt >> 16) & 0xFF);
    a_block[13] = static_cast<uint8_t>((fcnt >> 24) & 0xFF);

    const size_t n_blocks = (payload.size() + 15) / 16;
    for (size_t i = 1; i <= n_blocks; ++i) {
        a_block[15] = static_cast<uint8_t>(i);
        std::array<uint8_t, 16> s_block{};
        aes.encrypt_block(a_block, s_block);

        const size_t bytes_to_xor = (i == n_blocks && payload.size() % 16 != 0) ? (payload.size() % 16) : 16;
        for (size_t j = 0; j < bytes_to_xor; ++j) {
            payload[(i - 1) * 16 + j] ^= s_block[j];
        }
    }
}

} // namespace lorawan::crypto
```
:::

### 7. Повний розбір структури кадру та тестова валідація

Для перевірки коректності криптографічного контуру розглянемо повний цикл формування висхідного пакета телеметрії (Uplink):
- Мережевий сесійний ключ `NwkSKey`: `44 55 66 77 88 99 AA BB CC DD EE FF 00 11 22 33`;
- Сесійний ключ додатку `AppSKey`: `11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00`;
- 32-бітна адреса пристрою `DevAddr`: `0x01234567` (послідовність байтів у Little-Endian: `67 45 23 01`);
- 32-бітний лічильник кадрів `FCnt`: `0x00000001` (`01 00 00 00`);
- Напрямок передачі `Dir`: `0` (Uplink);
- Відкритий текст корисного навантаження `FRMPayload`: `48 65 6C 6C 6F` ("Hello", 5 байтів);
- Номер порту додатка `FPort`: `1`.

#### Етап 1: Шифрування корисного навантаження
Для першого 16-байтного блоку даних формується вектор лічильника:
`A_1 = 01 00 00 00 00 00 67 45 23 01 01 00 00 00 00 01`.
Вектор `A_1` шифрується ключем `AppSKey`. Отриманий блок гами `S_1` накладається на 5 байтів "Hello" операцією XOR, утворюючи зашифроване корисне навантаження `FRMPayload`.

#### Етап 2: Збирання кадру MACPayload
Формуються заголовки кадру:
- `MHDR = 0x40` (непідтверджений висхідний кадр Unconfirmed Data Up, версія Major = 0);
- `FHDR`: `DevAddr` (4 байти), `FCtrl = 0x00` (1 байт, прапорці ADR/ACK скинуті, довжина FOpts = 0), `FCnt = 0x0001` (2 байти у радіоефірі);
- `FPort = 0x01` (1 байт);
- `FRMPayload` (5 зашифрованих байтів).
Сумарна довжина заголовків та корисного навантаження становить `1 + 7 + 1 + 5 = 14` байтів.

#### Етап 3: Розрахунок коду цілісності MIC
Формується 16-байтний блок `B0`:
`B0 = 49 00 00 00 00 00 67 45 23 01 01 00 00 00 00 0E` (довжина повідомлення `len = 14 = 0x0E`).
Алгоритм AES-CMAC обчислює підпис над масивом `B0 | MHDR | FHDR | FPort | FRMPayload` (загалом `16 + 14 = 30` байтів) за допомогою ключа `NwkSKey`. Отримані 4 байти додаються в кінець кадру, утворюючи фінальний радіопакет `PHYPayload` довжиною 18 байтів.

### 8. Апаратні прискорювачі та енергетична оптимізація

На сучасних 32-бітних мікроконтролерах програмна реалізація AES-128 потребує від 1500 до 3500 процесорних тактів на один 16-байтний блок. За тактової частоти ядра 16 МГц час обчислення одного блоку становить близько 100–220 мкс, що за струму споживання ядра 4–8 мА додає до загального енергетичного бюджету близько 3–7 мкДж на блок.

Використання вбудованих апаратних криптографічних блоків (наприклад, апаратного модулю AES у мікроконтролерах STM32L4/STM32WLE5 або периферійного прискорювача ESP32) скорочує час шифрування до 160–200 тактів (близько 10–12 мкс) на блок зі зниженням витрат енергії ядра більш ніж у 15 разів.

#### Інтеграція з апаратними реєстрами STM32 (LL Driver)

При роботі з апаратним блоком AES мікроконтролера STM32WLE5 (інтегрований SoC з ядром Cortex-M4 та трансивером Semtech SX126x) процедура ініціалізації полягає у записі ключів безпосередньо в регістри `AES_KEYRx` та виборі режиму ECB або CTR:

```
1. Тактування: LL_AHB3_GRP1_EnableClock(LL_AHB3_GRP1_PERIPH_AES);
2. Конфігурація режиму: LL_AES_SetOperationMode(AES, LL_AES_OPERATION_MODE_ENCRYPT);
3. Запис 128-бітного ключа в регістри:
   LL_AES_WriteKey(AES, nwk_skey_words);
4. Запис вхідного блоку в регістр даних:
   LL_AES_WriteData(AES, input_block_words);
5. Очікування прапорця завершення: while(!LL_AES_IsActiveFlag_CCF(AES));
6. Читання зашифрованого блоку з регістрів AES_DOUTR.
```

Такий прямий апаратний виклик звільняє пам'ять Flash від таблиць S-Box (256 байтів) та коду розгортання ключів, а також забезпечує константний час виконання операцій, що є базовим захистом від атак за часом виконання (англ. *Timing Attacks*).

### 9. Енергонезалежне збереження лічильників та знос пам'яті Flash

Критичним аспектом безпеки LoRaWAN є збереження монотонності 32-бітного лічильника `FCntUp`. Якщо пристрій зазнає раптового перезавантаження (скидання живлення, спрацьовування сторожового таймера Watchdog), скидання `FCntUp` у нуль призведе до того, що сервер Network Server відхилятиме всі наступні пакети через захист від повторів (Replay Protection).

Проте прямий запис `FCntUp` у внутрішню енергонезалежну пам'ять Flash або EEPROM після кожної передачі є фатальною інженерною помилкою:
- Ресурс секторів Flash-пам'яті мікроконтролера зазвичай становить 10 000 – 100 000 циклів стирання/запису;
- Датчик, що передає дані кожні 15 секунд (240 пакетів на годину), повністю зруйнує сектор Flash за `100000 / (240 · 24) ≈ 17 днів`.

#### Стратегія блокового збереження з інтервалом квантування

Для вирішення цієї дилеми застосовують двоетапну стратегію збереження лічильника:

1. **Квантування збереження у Flash:** Значення `FCntUp` записується у Flash-пам'ять із кроком у `K` відліків (наприклад, `K = 32` або `K = 64`). Тобто у Flash зберігається значення `FCnt_saved = FCnt + K`.
2. **Оперативна робота в RAM:** Поточний лічильник інкрементується виключно в оперативній пам'яті (SRAM).
3. **Відновлення після збою:** У разі перезавантаження пристрій зчитує з Flash значення `FCnt_saved` і починає передачу з цього числа. Сервер Network Server фіксує стрибок лічильника на кілька десятків відліків уперед (що дозволено стандартом LoRaWAN, якщо різниця не перевищує поріг `MAX_FCNT_GAP = 16384`), і продовжує прийом пакетів без розриву сесії.

Такий підхід знижує кількість циклів запису у Flash у `K` разів, продовжуючи ресурс пам'яті мікроконтролера до десятків років.

### 10. Типові інженерні пастки та правила гігієни безпеки

1. **Порядок байтів у лічильниках та адресах (Endianness):** Поля `DevAddr` та `FCnt` у структурі кадрів LoRaWAN та службових блоках `B0` й `A_i` повинні записуватися в порядку **Little-Endian** (молодший байт за меншою адресою пам'яті). Помилка у прямому копіюванні `uint32_t` на архітектурах Big-Endian або невірне перетворення байтів призводить до повної розбіжності MIC та відхилення пакета сервером Network Server.
2. **Розмір лічильника кадрів у розрахунку MIC:** У радіоефірі поле `FCnt` передається як 16-бітне число (2 байти), проте блок `B0` вимагає повного **32-бітного значення** `FCnt`. Якщо пристрій перевищив 65535 передач, старші 16 бітів лічильника зберігаються в пам'яті вузла та сервера і обов'язково беруть участь у розрахунку `B0[12..13]`.
3. **Вибір ключа за номером порту `FPort`:** Якщо кадр містить MAC-команди у полі корисного навантаження (`FPort = 0`), шифрування `FRMPayload` зобов'язане виконуватися за допомогою **`NwkSKey`**, а не `AppSKey`. Переплутування ключів для нульового порту унеможливлює обробку мережевих команд сервером Network Server.
4. **Захист від атак по сторонніх каналах (Side-Channel Attacks):** Якщо пристрій розміщено у фізично доступному місці, час виконання програмного AES може витокувати інформацію про біти ключа через коливання струму споживання (DPA, Differential Power Analysis). Для захищених лічильників рекомендується використовувати апаратні криптографічні прискорювачі з маскуванням живлення (наприклад, криптографічні модулі ATECC608A або вбудовані апаратні блоки AES мікроконтролерів STM32L4/ESP32).
5. **Очищення оперативної пам'яті перед переходом у сон:** Сесійні ключі `NwkSKey` та `AppSKey` повинні захищатися в оперативній пам'яті. У разі використання режиму глибокого сну зі збереженням стану RAM, тимчасові буфери раундових ключів `round_keys` повинні обов'язково затиратися нулями за допомогою функцій гарантованого очищення пам'яті (наприклад, `explicit_bzero` або запис через покажчик `volatile uint8_t*`), щоб запобігти зчитуванню залишкового заряду комірок SRAM при апаратному зломі.
