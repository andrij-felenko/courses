# 📋 Специфікація API транскрипту Фіата — Шаміра: неінтерактивний генератор викликів

Специфікація API транскрипту Фіата — Шаміра визначає уніфікований програмний інтерфейс для управління станом неінтерактивного доводжувача та верифікатора у протоколах доведення з нульовим розголошенням (ZK-SNARKs, ZK-STARKs, Bulletproofs, підписи Шнорра/Ed25519). Модуль транскрипту забезпечує криптографічно безпечну заміну віддаленого верифікатора шляхом каскадного додавання повідомлень до стану криптографічного хешу та генерації псевдовипадкових викликів.

Головна вимога до цього інтерфейсу — унеможливити так звані «атаки вилучення контексту» (Weak Fiat-Shamir attacks) та гарантувати строго однаковий порядок поглинання даних (`absorb`) та генерації викликів (`squeeze`) як на стороні доводжувача, так і на стороні верифікатора. Якщо порядок поглинання полів різниться хоча б на один біт або не містить ідентифікатора домену, верифікація неінтерактивного доказу завершиться відмовою або створить уразливість підробки.

## 1. Архітектура автомата станів та коди помилок

Транскрипт Фіата — Шаміра функціонує як детермінований автомат станів, побудований на базі криптографічної губкової конструкції (Sponge Construction) або криптографічного хешу у режимі ланцюгування (Hash Chaining Mode).

### 1.1 Перелік кодів повернення (`fiat_shamir_status_t`)

Кожна функція C-інтерфейсу повертає явний статус виконання типу `fiat_shamir_status_t`. Використання кодів помилок є обов'язковим для перевірки цілісності стану транскрипту перед генерацією викликів.

| Код помилки | Числове значення | Семантичний опис та причини виникнення |
| :--- | :--- | :--- |
| `FS_SUCCESS` | `0x00` | Операцію успішно виконано; стан транскрипту оновлено. |
| `FS_ERR_INVALID_PARAM` | `0x01` | Передано `NULL`-вказівник, порожню мітку домену або нульову довжину буфера. |
| `FS_ERR_STATE_CORRUPTED` | `0x02` | Спроба згенерувати виклик без початкової ініціалізації контексту `init`. |
| `FS_ERR_OUT_OF_ORDER` | `0x03` | Порушено порядок викликів `absorb` та `squeeze` (розходження між доводжувачем і верифікатором). |
| `FS_ERR_BUFFER_OVERFLOW` | `0x04` | Переповнення внутрішнього накопичувача стану або перевищення максимальної довжини мітки `FS_LABEL_MAX_LEN`. |

## 2. Специфікація інтерфейсу транскрипту на C та C++20

:::tabs
```c
#ifndef FIAT_SHAMIR_TRANSCRIPT_H
#define FIAT_SHAMIR_TRANSCRIPT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define FS_STATE_BYTES 32
#define FS_LABEL_MAX_LEN 64

typedef enum {
    FS_SUCCESS = 0,
    FS_ERR_INVALID_PARAM = 1,
    FS_ERR_STATE_CORRUPTED = 2,
    FS_ERR_OUT_OF_ORDER = 3,
    FS_ERR_BUFFER_OVERFLOW = 4
} fiat_shamir_status_t;

typedef struct {
    uint8_t state[FS_STATE_BYTES]; /* Поточний хеш-стан (SHA-256 / BLAKE3 / Sponge) */
    uint64_t counter;              /* Лічильник згенерованих викликів */
    bool is_initialized;           /* Прапорець ініціалізації контексту */
} fiat_shamir_transcript_t;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Ініціалізація транскрипту з розділювачем домену (Domain Separator).
 * @param ctx Вказівник на контекст транскрипту.
 * @param protocol_label Рядок ідентифікації протоколу (наприклад, "Schnorr-Ed25519-v1").
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_init(
    fiat_shamir_transcript_t *ctx,
    const char *protocol_label
);

/**
 * @brief Поглинання повідомлення або комітменту в стан транскрипту (Absorb).
 * @param ctx Вказівник на контекст.
 * @param label Текстова мітка елемента (наприклад, "commitment_alpha").
 * @param data Послідовність байтів елемента.
 * @param len Довжина даних у байтах.
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_absorb(
    fiat_shamir_transcript_t *ctx,
    const char *label,
    const uint8_t *data,
    size_t len
);

/**
 * @brief Генерація детермінованого виклику (Squeeze Challenge).
 * @param ctx Вказівник на контекст.
 * @param label Текстова мітка виклику (наприклад, "challenge_beta").
 * @param out_challenge Буфер для запису згенерованого виклику.
 * @param challenge_len Необхідний розмір виклику у байтах.
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_squeeze(
    fiat_shamir_transcript_t *ctx,
    const char *label,
    uint8_t *out_challenge,
    size_t challenge_len
);

/**
 * @brief Скинути стан транскрипту та очистити секрети з пам'яті.
 * @param ctx Вказівник на контекст.
 */
void fiat_shamir_clear(fiat_shamir_transcript_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* FIAT_SHAMIR_TRANSCRIPT_H */
```
```cpp
#ifndef FIAT_SHAMIR_TRANSCRIPT_HPP
#define FIAT_SHAMIR_TRANSCRIPT_HPP

#include <span>
#include <string_view>
#include <vector>
#include <array>
#include <expected>
#include <cstdint>

namespace crypto::fiat_shamir {

enum class TranscriptError {
    InvalidParameter,
    StateCorrupted,
    SequenceMismatch
};

class Transcript {
public:
    explicit Transcript(std::string_view protocol_label) noexcept;
    ~Transcript() noexcept;

    Transcript(const Transcript&) = delete;
    Transcript& operator=(const Transcript&) = delete;
    Transcript(Transcript&&) noexcept = default;
    Transcript& operator=(Transcript&&) noexcept = default;

    /**
     * @brief Додати публічний контекст або комітмент до транскрипту.
     */
    std::expected<void, TranscriptError> absorb(
        std::string_view label,
        std::span<const uint8_t> data
    ) noexcept;

    /**
     * @brief Згенерувати випадковий виклик фіксованої довжини.
     */
    template <size_t N>
    std::expected<std::array<uint8_t, N>, TranscriptError> squeeze(
        std::string_view label
    ) noexcept;

    /**
     * @brief Згенерувати скалярний виклик у формі вектору байтів.
     */
    std::expected<std::vector<uint8_t>, TranscriptError> squeeze_bytes(
        std::string_view label,
        size_t count
    ) noexcept;

private:
    std::array<uint8_t, 32> state_{0};
    uint64_t counter_{0};
    bool initialized_{false};

    void update_hash(std::span<const uint8_t> input) noexcept;
};

} // namespace crypto::fiat_shamir

#endif // FIAT_SHAMIR_TRANSCRIPT_HPP
```
:::

## 3. Переходи станів та схема роботи автомата

Перехід між станами транскрипту строго детермінований і підпорядковується правилам криптографічного накопичення:

```
       [Uninitialized]
              │
              │  fiat_shamir_init("Protocol-Label")
              ▼
        [Absorb State] ───(fiat_shamir_absorb)───┐
              │                                   │
              │                                   ▼
              │                             [Absorb State]
              │ fiat_shamir_squeeze()             │
              ▼                                   │
       [Squeeze State] ◄──────────────────────────┘
              │
              │  fiat_shamir_squeeze() / absorb()
              ▼
       [Active Protocol State]
              │
              │  fiat_shamir_clear()
              ▼
        [Cleared / Terminated]
```

### 3.1 Детальний опис семантики методів

1. **Ініціалізація (`fiat_shamir_init`):**
   Приймає рядок розділення домену `protocol_label`. Метод обчислює початкове значення стану `S_0 = H("DOM_SEP" || protocol_label)` та скидає лічильник викликів `counter` у 0. Якщо доводжувач і верифікатор передадуть різні рядки ініціалізації (наприклад, "Ed25519-v1" та "Ed25519-v2"), їхні стани `S_0` відразу розійдуться, унеможливлюючи крос-протокольні атаки підробки.

2. **Поглинання даних (`fiat_shamir_absorb`):**
   Приймає текстову мітку `label` та масив байтів `data`. Метод виконує каскадне оновлення хешу:
   ```
   S_{i+1} = H( S_i || "absorb" || label || len(data) || data )
   ```
   Включення довжини `len(data)` та мітки `label` запобігає атакам склеювання (Ambiguity Attacks), коли два послідовні масиви байтів `(A, B)` могли б мати таке ж побітове представлення, як і `(A', B')`.

3. **Генерація викликів (`fiat_shamir_squeeze`):**
   Обчислює псевдовипадковий виклик `β` для поточного стану:
   ```
   challenge = H( S_i || "squeeze" || label || counter )
   S_{i+1}   = H( S_i || "state_update" || challenge )
   counter++
   ```
   Автоматичне оновлення стану `S_{i+1}` після кожного виходу `squeeze` гарантує, що наступні виклики будуть псевдовипадково незалежними від попередніх, навіть якщо мітка `label` повториться.

4. **Очищення секретів (`fiat_shamir_clear`):**
   Заповнює оперативну пам'ять структури `fiat_shamir_transcript_t` нулями за допомогою функцій гарантованого стирання (`memset_s` у C або `std::fill` у C++), що запобігає витоку залишків транскрипту з дампів пам'яті (RAM dumps).

## 4. Простеження станів та діагностика в системі

У ядрах операційних систем (Linux Kernel Crypto API) та високопродуктивних криптографічних серверах простеження стану транскриптів Фіата — Шаміра здійснюється через системні інтерфейси профілювання:

- **Інспекція драйверів через procfs:** Файл `/proc/crypto` відображає зареєстровані алгоритми хешування та стан їхніх контекстів (`crypto_tfm`). Модуль транскрипту ініціалізує хеш-трансформацію `crypto_alloc_shash("sha256", 0, 0)` та відстежує внутрішні буфери.
- **Діагностика вирівнювання пам'яті (Memory Alignment):** Для оптимальної роботи інструкцій SIMD (AVX-512 / ARM Neon) структура `fiat_shamir_transcript_t` вирівнюється на межу кеш-рядка процесора (`alignas(64)`). Невирівняний доступ до буфера `state` при поглинанні великих масивів поліноміальних коефіцієнтів у ZK-STARKs призводить до зниження швидкодії верифікатора у 2–3 рази.
- **Налаγονження порядку викликів (Trace Log):** При виникненні помилки `FS_ERR_OUT_OF_ORDER` транскрипт формує діагностичний лог, що містить відбитки всіх попередньо поглинутих міток `label`. Збіг двох послідовних відбитків дозволяє локалізувати раунд, на якому верифікатор розійшовся з доводжувачем.

## 5. Порівняння специфікацій транскриптів у сучасних бібліотеках

Сучасні криптографічні бібліотеки застосовують специфічні варіації описуваної API-специфікації:

- **Бібліотека Merlin (Rust / Dalek Ecosystem):** Використовує хеш-функцію STROBE на базі Keccak-f[1600]. Дозволяє створювати ієрархічні дочірні транскрипти за допомогою методів `build_transcript()` та відстежувати залежності у підпротоколах.
- **Транскрипт PlonK (zkSync / Aztec):** Застосовує алгебраїчний хеш Poseidon. Поглинання перестановок `wire_commitments` та вижимка скалярів викликів `beta`, `gamma`, `alpha`, `zeta` виконуються над елементами скінченного поля `F_p`.
- **Транскрипт STARKnet (Cairo / FRI):** Використовує двофазне ланцюгування: Merkle-комітменти поглинаються як root-хеші, після чого транскрипт витискає вектори коефіцієнтів для вибіркової перевірки поліноміального ступеня (Queries).

## 6. Протокольні межі та обробка виняткових станів

При інтеграції модуля транскрипту в апаратні модулі безпеки (HSM) або апаратні ізольовані анклави (Intel SGX, ARM TrustZone) розробники повинні враховувати наступні граничні випадки:

- **Спроба зчитування виклику без поглинання даних:** Якщо метод `squeeze` викликається відразу після `init` до передачі зобов’язань `absorb`, транскрипт повертає помилку `FS_ERR_STATE_CORRUPTED`. Виклик без зобов’язання перетворює неінтерактивний доказ на детерміновану константу.
- **Порожні масиви байтів (`len = 0`):** Передача `data = NULL` при `len = 0` вважається припустимою лише у випадку, якщо мітка `label` явно описує порожню подійну мітку (Empty Event Marker). У всіх інших випадках повертається `FS_ERR_INVALID_PARAM`.
- **Ізоляція анклавів пам'яті:** У середовищі HSM стан `fiat_shamir_transcript_t` зберігається у захищеній регістровій пам’яті, а стирання `fiat_shamir_clear` виконується апаратним сигналом після завершення циклу верифікації.

## 7. Захисні гарантії та правила інтеграції

1. **Строга послідовність операцій:** 
   Доводжувач і верифікатор зобов'язані викликати `absorb` та `squeeze` у строго однаковій послідовності. Якщо доводжувач поглине комітменти у порядку `(α1, α2)`, а верифікатор — у порядку `(α2, α1)`, верифікація неінтерактивного доказу гарантовано завершиться помилкою.

2. **Канонічна бінарна сереалізація (Canonical Encoding):**
   Усі математичні об'єкти (елементи скінченних полів, точки на еліптичних кривих, поліноми) повинні кодуватися у потік байтів `data` у єдиному канонічному форматі (наприклад, Little-Endian кодування з фіксованою довжиною байтів). Неканонічне кодування дозволяє атакуючому передавати різні побітові представлення одного й того самого елемента, обходячи верифікацію.

3. **Багатопотокова ізоляція (Thread Safety):**
   Об'єкт `fiat_shamir_transcript_t` є локальним для кожного конкретного сеансу підписання або верифікації і не підлягає одночасному модифікуванню з різних потоків без зовнішньої синхронності через м'ютекс.
