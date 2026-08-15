# 📋 Інтерфейс криптографічної бібліотеки білінійних спарювань

Програмний інтерфейс (API) високопродуктивної криптографічної бібліотеки білінійних спарювань на еліптичних кривих (на прикладі кривої BLS12-381) структуровано у вигляді багаторівневої системи типів і функцій. Вона охоплює базові структури даних, низькорівневі обчислення циклу Міллера, функції хешування у групи, а також високорівневі модулі підписів BLS та поліноміальних зобов'язань KZG.

---

## 1. Концептуальний дизайн та специфікація типів даних

Дизайн даного API опирається на принципи строгої типобезпеки, відсутності прихованого динамічного виділення пам'яті та чіткого алгебраїчного розділення точкових груп `G1`, `G2` та цільової групи `Gt`.

Оскільки в асиметричних спарюваннях Типу 3 (до яких належить крива BLS12-381) не існує ефективного гомоморфізму між `G2` та `G1`, типи даних для точок `G1` (визначених над базовим полем `F_p`) та `G2` (визначених над квадратичним розширенням `F_{p^2}`) є концептуально непідмінними на рівні компілятора. Це унеможливлює випадкову передачу точки `G1` у функцію, що очікує точку `G2`.

### Представлення в пам'яті та форма Монтгомері

Всі елементи полів `F_p` у пам'яті зберігаються у формі Монтгомері (англ. *Montgomery representation*), що перетворює елемент `a ∈ F_p` у `a_R = a · R (mod p)`, де `R = 2^384`. Це дозволяє замінити коштовне класичне ділення за модулем `p` на серію побітових зсувів та множень за алгоритмом Монтгомері (англ. *Montgomery reduction*).

Для забезпечення сумісності з апаратними інструкціями векторної обробки (AVX-512, ARM Neon) всі структури даних мають вирівнювання (англ. *memory alignment*) за межею 64 байтів.

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                          Пам'ять C-структури                           │
 ├──────────────────────────┬─────────────────────────────────────────────┤
 │ bls12_381_g1_t           │ 48 байт (афінна x) + 48 байт (афінна y)      │
 │ (Стиснутий: 48 байт)     │ Базове поле F_p                             │
 ├──────────────────────────┼─────────────────────────────────────────────┤
 │ bls12_381_g2_t           │ 96 байт (афінна x) + 96 байт (афінна y)      │
 │ (Стиснутий: 96 байт)     │ Розширення поля F_{p^2}                     │
 ├──────────────────────────┼─────────────────────────────────────────────┤
 │ bls12_381_gt_t           │ 576 байт (12 елементів по 48 байт)          │
 │ (Елемент F_{p^{12}})     │ Повне розширення вежі полів                 │
 └──────────────────────────┴─────────────────────────────────────────────┘
```

У стиснутому байтовому форматі (48 байтів для `G1` та 96 байтів для `G2`) найстарші 3 біти першого байта використовуються як метадані кодування:
- **Bit 7 (Compression Flag):** Завжди дорівнює `1` для стиснутих точок (зберігається лише координата `x` та знак `y`).
- **Bit 6 (Infinity Flag):** Дорівнює `1`, якщо точка є точкою на нескінченності `O`.
- **Bit 5 (Lexicographical Y-Bit):** Визначає старшинство (знак) координати `y` у полі `F_p` або `F_{p^2}` для відновлення точки.

### Докладний опис внутрішньої структури елементів полів

Внутрішня організація базових типів даних гарантує коректне представлення числових компонентів у пам'яті:

1. **Елемент базового поля (`bls12_381_fp_t` / `Fp`):** Приймає 381-бітове значення, розбите на шість 64-бітних слів (`uint64_t limbs[6]`). Значення зберігається в інтервалі `[0, p - 1]`. При спробі передати масив із числом, що перевищує модуль `p`, API повертає помилку `BLS12_381_ERROR_INVALID_POINT`.
2. **Елемент розширення поля (`bls12_381_fp2_t` / `Fp2`):** Уособлює елемент квадратичного розширення `F_{p^2} = F_p[u] / (u^2 + 1)`. Складається з двох елементів `c0` та `c1`, що представляють дійсний та уявний коефіцієнти при елементі `u`.
3. **Елемент цільової групи (`bls12_381_gt_t` / `Fp12`):** Представляє елемент мультиплікативної групи `Gt ⊂ F_{p^{12}}*`. Пам'ять організована у вигляді вежі розширень `F_{p^{12}} = F_{p^6}[w] / (w^2 - v)`, де масиви `c0[3]` утримують нижню частину `F_{p^6}`, а `c1[3]` — верхню частину `F_{p^6}`.
4. **Проєктивні координати Якобі (`G1Projective` / `G2Projective`):** Зберігають точки кривої у триплеті `(X : Y : Z)`. Вживання проєктивних координат дозволяє виконувати додавання та подвоєння точок без операцій інверсії у полях `F_p` чи `F_{p^2}`. Точка на нескінченності `O` задається прапорцем `Z = 0`.

### C- та C++-структури полів і точок

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Статуси повернення рішень API
typedef enum {
    BLS12_381_SUCCESS               = 0,
    BLS12_381_ERROR_INVALID_POINT   = 1,
    BLS12_381_ERROR_NOT_IN_GROUP    = 2,
    BLS12_381_ERROR_BUFFER_TOO_SMALL= 3,
    BLS12_381_ERROR_VERIFICATION_FAILED = 4,
    BLS12_381_ERROR_NULL_POINTER    = 5
} bls12_381_status_t;

// Елемент базового поля F_p (381 біт, 48 байт у формі Монтгомері)
typedef struct {
    uint64_t limbs[6]; // 6 * 64 = 384 біти
} bls12_381_fp_t;

// Елемент розширення F_{p^2} = F_p[u] / (u^2 + 1)
typedef struct {
    bls12_381_fp_t c0; // Реальність
    bls12_381_fp_t c1; // Уявність
} bls12_381_fp2_t;

// Елемент цільової групи Gt (поле F_{p^{12}}, 576 байт)
typedef struct {
    bls12_381_fp2_t c0[3]; // Нижня вежа F_{p^6}
    bls12_381_fp2_t c1[3]; // Верхня вежа F_{p^6}
} bls12_381_gt_t;

// Точка групи G1 у проєктивних координатах Якобі (X : Y : Z)
typedef struct {
    bls12_381_fp_t X;
    bls12_381_fp_t Y;
    bls12_381_fp_t Z;
} bls12_381_g1_projective_t;

// Точка групи G1 в афінних координатах (x, y)
typedef struct {
    bls12_381_fp_t x;
    bls12_381_fp_t y;
    bool infinity;
} bls12_381_g1_affine_t;

// Точка групи G2 у проєктивних координатах (X : Y : Z)
typedef struct {
    bls12_381_fp2_t X;
    bls12_381_fp2_t Y;
    bls12_381_fp2_t Z;
} bls12_381_g2_projective_t;

// Точка групи G2 в афінних координатах (x, y)
typedef struct {
    bls12_381_fp2_t x;
    bls12_381_fp2_t y;
    bool infinity;
} bls12_381_g2_affine_t;
```
```cpp
#include <array>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <span >

namespace crypto::pairing {

enum class ErrorCode : std::uint8_t {
    Success = 0,
    InvalidPoint,
    NotInGroup,
    BufferTooSmall,
    VerificationFailed,
    NullPointer
};

// Елемент базового поля F_p (48 байт) у стилі C++20
struct alignas(64) Fp {
    std::array<std::uint64_t, 6> limbs{};
};

// Елемент розширення F_{p^2}
struct alignas(64) Fp2 {
    Fp c0{};
    Fp c1{};
};

// Елемент цільової групи Gt (F_{p^{12}}, 576 байт)
struct alignas(64) Fp12 {
    std::array<Fp2, 3> c0{};
    std::array<Fp2, 3> c1{};
};

// Точка групи G1 в афінних координатах
struct G1Affine {
    Fp x{};
    Fp y{};
    bool infinity{false};
};

// Точка групи G2 в афінних координатах
struct G2Affine {
    Fp2 x{};
    Fp2 y{};
    bool infinity{false};
};

} // namespace crypto::pairing
```
:::

---

## 2. Підсистема точкової арифметики та валідації підгруп

У криптографічних протоколах точки, що передаються мережею від недовірених сторін, можуть бути навмисно згенеровані поза правильними підгрупами порядку `r`.

Якщо точка `Q` належить кривій над `F_{p^2}`, але не належить підгрупі `G2` (а належить некоректній підгрупі малого порядку `h2`), зловмисник може здійснити **атаку малого масиву** (англ. *small subgroup attack*) та відновити секретний ключ `sk` за декілька викликів спарювання. З цієї причини дане API вимагає обов'язкової валідації точок перед обчисленнями.

### Функціональний контракт підсистеми

1. **`generator()`:** Вертає канонічний генератор групи (`P1` для `G1` або `P2` для `G2`).
2. **`scalar_mul()`:** Скалярне множення точки на 256-бітовий скаляр `k` у константному часі за допомогою драбини Монтгомері.
3. **`is_in_correct_subgroup()`:** Виконує перевірку належності точок порядку `r`. Для групи `G1` застосовується швидка перевірка за допомогою ендоморфізму GLV `ψ(P) = [λ]P`, що вимагає лише двох множень у полі `F_p`. Для групи `G2` застосовується відображення Фробеніуса `π_p(Q) == [x]Q`.

### C- та C++-сигнатури точкової арифметики

:::tabs
```c
/**
 * @brief Повертає канонічний генератор групи G1.
 * @param[out] out_generator Вказівник на точку G1 для запису результату.
 */
void bls12_381_g1_generator(bls12_381_g1_affine_t* out_generator);

/**
 * @brief Скалярне множення точки G1 на 256-бітовий скаляр [k]P у константному часі.
 * @param[out] result Точка результату [k]P.
 * @param[in] point Вхідна точка P.
 * @param[in] scalar_bytes Масив з 32 байтів скаляра k (big-endian).
 * @return BLS12_381_SUCCESS у разі успіху.
 */
bls12_381_status_t bls12_381_g1_scalar_mul(
    bls12_381_g1_projective_t* result,
    const bls12_381_g1_affine_t* point,
    const uint8_t scalar_bytes[32]
);

/**
 * @brief Перевіряє, чи належить точка P групи G1 до правильної підгрупи порядку r.
 * @param[in] point Точка для перевірки.
 * @return true якщо точка належить G1, інакше false.
 */
bool bls12_381_g1_is_in_correct_subgroup(const bls12_381_g1_affine_t* point);
```
```cpp
namespace crypto::pairing {

class G1Group {
public:
    [[nodiscard]] static G1Affine generator() noexcept;

    [[nodiscard]] static std::expected<G1Affine, ErrorCode> scalar_mul(
        const G1Affine& point,
        std::span<const std::uint8_t, 32> scalar
    ) noexcept;

    [[nodiscard]] static bool is_in_correct_subgroup(const G1Affine& point) noexcept;
};

} // namespace crypto::pairing
```
:::

---

## 3. Модуль кодування та відображення хешу (Hash-to-Curve)

Модуль реалізує детерміноване кодування точок у байтові масиви та криптографічне відображення довільних повідомлень у точки кривої за стандартом **RFC 9380** (Simplified SWU map).

### Кроки відображення Hash-to-Curve (RFC 9380)

1. **ExpandMessageXMD:** Перетворює байтове повідомлення `msg` та доменний розділювач `dst` у масив псевдовипадкових байтів за допомогою хеш-функції SHA-256 / SHAKE-256.
2. **MapToField:** Перетворює отримані байти у два елементи поля `u0, u1 ∈ F_p` або `F_{p^2}`.
3. **Simplified SWU Map:** Раціональне відображення повертає точки кривої `P0 = SWU(u0)` та `P1 = SWU(u1)`.
4. **Cofactor Clearing:** Результат додається `P = P0 + P1` і множиться на кофактор `h1` або `h2` групи.

### C- та C++-сигнатури кодування та хешування

:::tabs
```c
/**
 * @brief Стискає точку G1 у 48-байтний масив.
 * @param[out] out_bytes Буфер розміром 48 байтів.
 * @param[in] point Точка для кодування.
 */
bls12_381_status_t bls12_381_g1_compress(
    uint8_t out_bytes[48],
    const bls12_381_g1_affine_t* point
);

/**
 * @brief Безпечно відображає довільне повідомлення у точку групи G1 (HashToG1).
 * @param[out] out_point Результат у групі G1.
 * @param[in] msg Вказівник на байтове повідомлення.
 * @param[in] msg_len Довжина повідомлення у байтах.
 * @param[in] dst Доменний розділювач контексту (Domain Separation Tag, DST).
 * @param[in] dst_len Довжина DST.
 */
bls12_381_status_t bls12_381_hash_to_g1(
    bls12_381_g1_projective_t* out_point,
    const uint8_t* msg,
    size_t msg_len,
    const uint8_t* dst,
    size_t dst_len
);
```
```cpp
namespace crypto::pairing {

class HashToCurve {
public:
    [[nodiscard]] static std::expected<std::array<std::uint8_t, 48>, ErrorCode> compress_g1(
        const G1Affine& point
    ) noexcept;

    [[nodiscard]] static std::expected<G1Affine, ErrorCode> hash_to_g1(
        std::span<const std::uint8_t> msg,
        std::span<const std::uint8_t> dst
    ) noexcept;
};

} // namespace crypto::pairing
```
:::

---

## 4. Ядро обчислення спарювань (Pairing Engine Core API)

Ядро спарювань надає низькорівневі інтерфейси для виконання окремого циклу Міллера, фінального піднесення до степеня, обчислення одного спарювання Ате та пакетного (мульти-) спарювання.

### Математичний контракт пакетного спарювання (Multi-Pairing)

При перевірці криптографічних підписів або ZK-доведень часто вимагається перевірка рівняння вигляду:

```
∏_{i=0}^{N-1} e(P_i, Q_i) == 1  у групі Gt
```

Прямий виклик `N` окремих функцій `bls12_381_pairing_ate` вимагав би `N` циклів Міллера та `N` фінальних піднесень до степеня. Функція `bls12_381_multi_pairing` виконує `N` циклів Міллера паралельно, перемножує їхні проміжні результати у повному розширенні `F_{p^{12}}`, після чого здійснює **лише одне** фінальне піднесення до степеня. Це заощаджує до 45% обчислювального часу при `N ≥ 2`.

### C- та C++-сигнатури ядра спарювань

:::tabs
```c
/**
 * @brief Обчислює цикл Міллера f_{T, Q}(P) без фінального піднесення до степеня.
 * @param[out] out_gt Елемент поля F_{p^{12}} для запису накопиченого результату.
 * @param[in] P Точка групи G1 (в афінних координатах).
 * @param[in] Q Точка групи G2 (в афінних координатах).
 */
bls12_381_status_t bls12_381_pairing_miller_loop(
    bls12_381_gt_t* out_gt,
    const bls12_381_g1_affine_t* P,
    const bls12_381_g2_affine_t* Q
);

/**
 * @brief Пакетне (мульти-) спарювання: ∏_{i=0}^{N-1} e(P_i, Q_i).
 * @param[out] out_gt Результальний елемент Gt.
 * @param[in] P_array Масив з N точок групи G1.
 * @param[in] Q_array Масив з N точок групи G2.
 * @param[in] count Кількість пар N.
 */
bls12_381_status_t bls12_381_multi_pairing(
    bls12_381_gt_t* out_gt,
    const bls12_381_g1_affine_t* P_array,
    const bls12_381_g2_affine_t* Q_array,
    size_t count
);
```
```cpp
namespace crypto::pairing {

class PairingEngine {
public:
    [[nodiscard]] static std::expected<Fp12, ErrorCode> miller_loop(
        const G1Affine& P,
        const G2Affine& Q
    ) noexcept;

    [[nodiscard]] static std::expected<Fp12, ErrorCode> multi_pairing(
        std::span<const G1Affine> P_array,
        std::span<const G2Affine> Q_array
    ) noexcept;
};

} // namespace crypto::pairing
```
:::

---

## 5. Високорівневий модуль підпису BLS12-381 (BLS Signature API)

Модуль реалізує криптографічну схему підпису BLS (Boneh — Lynn — Shacham) з агрегацією підписів у групі `G1` та публічними ключами у групі `G2`.

### Безпека агрегації та захист від атак Rogue Key

При об'єднанні підписів декількох користувачів `σ_agg = ∑ σ_i` виникає загроза атаки підробленим ключем (англ. *rogue key attack*). Якщо зловмисник знає публічний ключ жертви `PK_target`, він може зареєструвати підроблений ключ `PK_adv = PK_real - PK_target` і створити підпис від імені всієї групи.

Дане API підтримує дві схеми захисту:
1. **Proof of Possession (PoP):** Кожен користувач при реєстрації надає підпис-докази володіння ключем `PoP = Sign(sk, PK)`.
2. **Агрегація FastAggregate:** Перевіряє підписи лише тоді, коли всі учасники підписують одне й те саме повідомлення `m`, а публічні ключі попередньо перевірені на унікальність.

### C- та C++-сигнатури підпису BLS

:::tabs
```c
/**
 * @brief Генерує підпис BLS для повідомлення.
 * @param[out] out_signature Підпис σ = [sk] HashToG1(m) у групі G1 (48 байтів стиснуто).
 * @param[in] secret_key Секретний ключ sk (32 байти).
 * @param[in] msg Повідомлення для підпису.
 * @param[in] msg_len Довжина повідомлення.
 */
bls12_381_status_t bls_sign(
    uint8_t out_signature[48],
    const uint8_t secret_key[32],
    const uint8_t* msg,
    size_t msg_len
);

/**
 * @brief Перевіряє один підпис BLS: e(σ, P2) == e(H(m), PK).
 * @param[in] signature_bytes Стиснутий підпис σ (48 байтів).
 * @param[in] public_key_bytes Стиснутий відкритий ключ PK (96 байтів).
 * @param[in] msg Повідомлення.
 * @param[in] msg_len Довжина повідомлення.
 * @return BLS12_381_SUCCESS у разі успішної перевірки підпису.
 */
bls12_381_status_t bls_verify(
    const uint8_t signature_bytes[48],
    const uint8_t public_key_bytes[96],
    const uint8_t* msg,
    size_t msg_len
);
```
```cpp
namespace crypto::pairing {

class BlsSignatureScheme {
public:
    using SignatureBuffer = std::array<std::uint8_t, 48>;
    using PublicKeyBuffer = std::array<std::uint8_t, 96>;
    using SecretKeyBuffer = std::array<std::uint8_t, 32>;

    [[nodiscard]] static std::expected<SignatureBuffer, ErrorCode> sign(
        std::span<const std::uint8_t, 32> secret_key,
        std::span<const std::uint8_t> msg
    ) noexcept;

    [[nodiscard]] static bool verify(
        std::span<const std::uint8_t, 48> signature,
        std::span<const std::uint8_t, 96> public_key,
        std::span<const std::uint8_t> msg
    ) noexcept;
};

} // namespace crypto::pairing
```
:::

---

## 6. Високорівневий модуль KZG зобов'язань (KZG Commitment API)

Модуль надає функціонал для роботи з зобов'язаннями KZG (Kate — Zaverucha — Goldberg), що використовуються у протоколах ZK-SNARKs (PLONK, Groth16) та блокчейн-схемах EIP-4844 (Proto-Danksharding у мережі Ethereum).

### Математичний процес створення та перевірки зобов'язання

1. **Ініціалізація (SRS):** Завантажує довідкову структуру точок `[s^i]P1 ∈ G1` та `[s]P2 ∈ G2`.
2. **Зобов'язання (Commitment):** Обчислює баритоцентричну суму точок `C = ∑ a_i · ([s^i]P1)`.
3. **Відкриття (Open):** Формує частку `Q(X) = (A(X) - y) / (X - z)` та будує доведення `π = [Q(s)]P1`.
4. **Верифікація (Verify):** За допомогою спарювання перевіряє тотожність `e(π, [s - z]P2) == e(C - [y]P1, P2)`.

### C- та C++-сигнатури KZG

:::tabs
```c
// Структура довідкової строки (Structured Reference String, SRS / Trusted Setup)
typedef struct {
    bls12_381_g1_affine_t* g1_powers; // [P1, [s]P1, [s^2]P1, ..., [s^d]P1]
    bls12_381_g2_affine_t g2_s;       // [s]P2
    size_t max_degree;
} kzg_srs_t;

/**
 * @brief Обчислює зобов'язання C = [A(s)]P1 до многочлена A(X).
 * @param[out] out_commitment Точка зобов'язання C у групі G1 (48 байтів стиснуто).
 * @param[in] srs Вказівник на структуровані параметри SRS.
 * @param[in] coeffs Масив коефіцієнтів многочлена (скаляри Fr).
 * @param[in] degree Ступінь многочлена d.
 */
bls12_381_status_t kzg_commit(
    uint8_t out_commitment[48],
    const kzg_srs_t* srs,
    const uint8_t* coeffs,
    size_t degree
);
```
```cpp
namespace crypto::pairing {

struct KzgSrs {
    std::span<const G1Affine> g1_powers;
    G2Affine g2_s;
};

class KzgScheme {
public:
    [[nodiscard]] static std::expected<std::array<std::uint8_t, 48>, ErrorCode> commit(
        const KzgSrs& srs,
        std::span<const std::uint8_t> coeffs
    ) noexcept;
};

} // namespace crypto::pairing
```
:::

---

## 7. Рекомендації щодо потокобезпечності та обробки помилок

При практичному застосуванні даного API розробники повинні дотримуватися п'яти фундаментальних правил безпеки:

1. **Потокобезпечність (Thread Safety):** Всі функції API є чистими (англ. *reentrant*) і не містять прихованого глобального стану. Об'єкти параметрів `KzgSrs` є незмінними (англ. *read-only*) після завантаження і можуть безпечно розділятися між паралельними потоками обробки.
2. **Константність часу виконання (Constant-Time Execution):** Функції `sign`, `scalar_mul` гарантовано виконуються за однакову кількість тактів процесора незалежно від ваги Геммінга секретного скаляра `sk`, що унеможливлює таймінгові атаки по сторонніх каналах.
3. **Очищення секретів у пам'яті (Secret Zeroization):** Буфери, що містять секретні ключі `secret_key`, перед звільненням пам'яті зобов'язані перезаписуватися за допомогою системних функцій затирання `explicit_bzero` або `memset_s`.
4. **Валідація вхідних буферів:** Усі функції перевіряють вказівники на `NULL` та межі векторів `std::span`. Передавання невалідного буфера повертає статус `ErrorCode::NullPointer` без виклику збою аварійного завершення.
5. **Обробка помилок верифікації:** Якщо підпис або KZG-доведення є недійсними, функції повертають код `ErrorCode::VerificationFailed`, що дозволяє застосункам обробляти некоректні дані у звичайному коді без переривань.
