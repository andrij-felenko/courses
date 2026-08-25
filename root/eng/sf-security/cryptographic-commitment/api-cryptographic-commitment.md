# 📋 Специфікація програмних інтерфейсів зобов'язань (Pedersen & KZG API)

Специфікація API зобов'язань визначає уніфікований криптографічний contract для роботи зі схемами зобов'язання Педерсена, хеш-конвертами та поліноміальними зобов'язаннями KZG. Цей інтерфейс розроблено для забезпечення безпечної інтеграції в розподілені мережі, системи електронного голосування та децентралізовані смарт-контракти.

## 1. C-API бібліотеки зобов'язань Педерсена (`libpedersen_commit`)

C-бібліотека надає низькорівневий апаратний інтерфейс для швидкої генерації та верифікації зобов'язань Педерсена на еліптичних кривих secp256k1 та ed25519.

### 1.1 Структури даних та типи

```c
/* Контекст параметрів циклічної групи еліптичної кривої (наприклад, secp256k1 або ed25519) */
typedef struct pedersen_context_s pedersen_context_t;

/* Структура 256-бітного елемента поля або скаляра (BigEndian) */
typedef struct {
    uint8_t bytes[32];
} pedersen_scalar_t;

/* Структура 33-бітного стиснутого елемента групи / точки кривої */
typedef struct {
    uint8_t bytes[33];
} pedersen_point_t;

/* Коди помилок API */
typedef enum {
    PEDERSEN_SUCCESS = 0,
    PEDERSEN_ERROR_INVALID_PARAM = -1,
    PEDERSEN_ERROR_VERIFICATION_FAILED = -2,
    PEDERSEN_ERROR_RNG_FAILED = -3,
    PEDERSEN_ERROR_BUFFER_TOO_SMALL = -4
} pedersen_error_t;
```

### 1.2 Сигнатури функцій C-API та детальний розбір аргументів

#### `pedersen_context_create`
```c
pedersen_error_t pedersen_context_create(
    pedersen_context_t** ctx,
    const uint8_t* custom_h_label,
    size_t label_len
);
```
- **Призначення:** Ініціалізує глобальний контекст кривої та безпечно генерує незалежний генератор `H` через SHA-256 (Nothing-Up-My-Sleeve point generation).
- **Параметри:** 
  - `ctx`: Вказівник на вихідну адресу контексту. Пам'ять під контекст виділяється всередині функції та потребує звільнення через `pedersen_context_destroy`.
  - `custom_h_label`: Унікальний рядок мітки домену для генерації точки `H = HashToCurve(G || label)`.
  - `label_len`: Довжина масиву байтів мітки домену у байтах.

#### `pedersen_commit`
```c
pedersen_error_t pedersen_commit(
    const pedersen_context_t* ctx,
    pedersen_point_t* commitment_out,
    const pedersen_scalar_t* value,
    const pedersen_scalar_t* blinding
);
```
- **Призначення:** Обчислює зобов'язання `C = value · G + blinding · H` на еліптичній кривій.
- **Параметри:**
  - `ctx`: Валідний ініціалізований контекст кривої.
  - `commitment_out`: Вказівник на буфер розміром 33 байти для збереження стиснутої точки `C`.
  - `value`: Скаляр значення `v ∈ Z_q` у форматі Big-Endian.
  - `blinding`: 256-бітний фактор приховування `r ∈ Z_q`, отриманий з CSPRNG.
- **Повертає:** `PEDERSEN_SUCCESS` (0) у разі успішного обчислення.

#### `pedersen_verify`
```c
pedersen_error_t pedersen_verify(
    const pedersen_context_t* ctx,
    const pedersen_point_t* commitment,
    const pedersen_scalar_t* value,
    const pedersen_scalar_t* blinding
);
```
- **Призначення:** Локально верифікує рівність `commitment == value · G + blinding · H`.
- **Повертає:** `PEDERSEN_SUCCESS` у разі успіху або `PEDERSEN_ERROR_VERIFICATION_FAILED` при розходженні.

#### `pedersen_combine`
```c
pedersen_error_t pedersen_combine(
    const pedersen_context_t* ctx,
    pedersen_point_t* combined_out,
    const pedersen_point_t* commitments_array,
    size_t count
);
```
- **Призначення:** Здійснює гомоморфне додавання масиву зобов'язань `C_sum = ∑ C_i` шляхом додавання точок еліптичної кривої.

---

## 2. Інтерфейс поліноміальних зобов'язань KZG (`kzg_proof_api`)

Інтерфейс KZG надає високорівневу абстракцію для завірення поліномів та швидкої перевірки їхніх оцінок у довільних точках.

### 2.1 C++ / Rust API класи специфікації

```cpp
namespace crypto::kzg {

struct Polynomial {
    std::vector<Scalar> coefficients; // f(X) = a0 + a1*X + ... + ad*X^d
};

struct KZGCommitment {
    G1Point point; // C = [f(tau)]1
};

struct KZGProof {
    G1Point proof_point; // pi = [q(tau)]1
};

class KZGScheme {
public:
    // Завантаження Structured Reference String (SRS) з файлу Trusted Setup
    static KZGScheme load_srs(const std::string& srs_file_path, size_t max_degree);

    // Створення зобов'язання C для полінома f(X)
    KZGCommitment commit(const Polynomial& poly) const;

    // Створення доказу оцінки в точці z: f(z) = y
    KZGProof open_eval(const Polynomial& poly, const Scalar& z, const Scalar& y) const;

    // Верифікація доказу через білінійне спарювання e(C - [y]1, [1]2) == e(pi, [tau - z]2)
    bool verify_eval(const KZGCommitment& commitment, 
                     const Scalar& z, 
                     const Scalar& y, 
                     const KZGProof& proof) const;
};

} // namespace crypto::kzg
```

---

## 3. Специфікація CLI-утиліти (`commitment-cli`)

Утиліта командного рядка надає можливість генерувати та верифікувати зобов'язання з термінала.

### 3.1 Команда створення хеш-зобов'язання
```bash
commitment-cli hash commit --input "SecretMessage" --out-file commitment.json
```
**Вихідний JSON (`commitment.json`):**
```json
{
  "scheme": "SHA-256",
  "commitment": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "blinding_factor_hex": "7a8b9c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b"
}
```

### 3.2 Команда верифікації хеш-зобов'язання
```bash
commitment-cli hash verify --commitment-file commitment.json --input "SecretMessage"
```
**Вивід у stdout:**
```
[SUCCESS] Commitment verification PASSED. Value matched.
```

### 3.3 Команда створення зобов'язання Педерсена
```bash
commitment-cli pedersen commit --value 500 --out-file pedersen_commit.json
```

**Таблиця параметрів CLI-утиліти:**

| Прапорець | Опис | Тип даних | За замовчуванням |
| :--- | :--- | :--- | :--- |
| `--input` | Повідомлення для обчислення хеш-зобов'язання | Рядок | Обов'язкове |
| `--value` | Числове значення для зобов'язання Педерсена | Ціле число | Обов'язкове |
| `--blinding` | Власний фактор приховування (hex) | Рядок (hex) | Автогенерація CSPRNG |
| `--curve` | Еліптична крива для Педерсена/KZG | Enum (`secp256k1`, `bls12-381`) | `bls12-381` |
| `--out-file` | Файл збереження результату зобов'язання | Шлях до файлу | stdout |

### 3.4 Детальний розбір помилок та кодів повернення утиліти

Утиліта повертає наступні стандартизовані системні коди завершення (exit codes):

| Код повернення | Назва символу | Опис ситуації |
| :--- | :--- | :--- |
| `0` | `EXIT_SUCCESS` | Операцію обчислення або перевірки зобов'язання завершено успішно. |
| `1` | `EXIT_VERIFY_FAILED` | Фаза верифікації відкриття не пройшла збіг (невірне повідомлення або випадковість). |
| `2` | `EXIT_INVALID_INPUT` | Передано некоректний формат скаляра, точки кривої або hex-рядка. |
| `3` | `EXIT_RNG_ERROR` | Системний криптографічний генератор випадковості (CSPRNG) недоступний. |
| `4` | `EXIT_SRS_LOAD_ERROR` | Помилка зчитування або пошкодження файлу Structured Reference String для KZG. |

## 4. Контракт інтерфейсу смарт-контрактів Solidity / EVM (`IPedersenVerifier.sol`)

Для розробників децентралізованих додатків у мережі Ethereum надається специфікація EVM-інтерфейсу верифікації зобов'язань Педерсена та KZG через прекомпілятори кривої BN254 / alt_bn128:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPedersenVerifier {
    struct CommitmentPoint {
        uint256 x;
        uint256 y;
    }

    /// @notice Верифікує зобов'язання Педерсена через прекомпілят еліптичної кривої (0x07 ecMul та 0x06 ecAdd)
    /// @param comm Точка зобов'язання C
    /// @param value Відкрите значення v
    /// @param blinding Відкрита випадковість r
    /// @return true якщо C == v*G + r*H
    function verifyPedersen(
        CommitmentPoint calldata comm,
        uint256 value,
        uint256 blinding
    ) external view returns (bool);

    /// @notice Верифікує KZG доказ оцінки f(z) = y через прекомпілят білінійного спарювання (0x08 ecPairing)
    /// @param commitment Зобов'язання полінома C у групі G1
    /// @param z Точка оцінювання z
    /// @param y Значення полінома y
    /// @param proof Доказ оцінки pi у групі G1
    /// @return true якщо e(C - y*G1, G2) == e(proof, tau*G2 - z*G2)
    function verifyKZGEval(
        CommitmentPoint calldata commitment,
        uint256 z,
        uint256 y,
        CommitmentPoint calldata proof
    ) external view returns (bool);
}
```

## 5. Діаграма обміну даними та послідовності функціональних викликів

Послідовність взаємодії клієнтського додатка з мобільною бібліотекою та мережею смарт-контрактів EVM зображено на наступному конвеєрі викликів:

```
[Клієнтський додаток]         [C-Library libpedersen]         [EVM Smart Contract]
         │                               │                              │
         ├────── pedersen_commit() ─────►│                              │
         │◄───── returns (C_point) ──────┤                              │
         │                               │                              │
         │────────────────────── send Transaction(C_point) ────────────►│
         │                                                              │
         │────────────────────── reveal (v, r) ────────────────────────►│
         │                                                              │ verifyPedersen()
         │                                                              ├──────────┐
         │                                                              │          │ ecMul & ecAdd
         │                                                              │◄─────────┘
         │◄───────────────────── Verification Event(Success) ───────────┤
```

## 6. Контрольний чек-лист перевірки інтеграції API

При інтеграції специфікації API зобов'язань у промислове програмне забезпечення розробники зобов'язані перевірити наступні вимоги безпеки:

1. **Валідація меж скаляра:** Усі вхідні скаляри `v` та `r` перевіряються на належність інтервалу `[0, q - 1]`. При виході за межі поля функція повертає `PEDERSEN_ERROR_INVALID_PARAM`.
2. **Очищення секретів у пам'яті:** Буфери пам'яті, що містять вихідні скаляри `v` та factors `r`, очищаються функцією `memset_s` або `explicit_bzero` відразу після обчислення зобов'язання.
3. **Захист від атак за побічними каналами (Side-Channel Protection):** Скалярне множення точок `v · G` та `r · H` реалізовано з використанням алгоритмів сталого часу (Constant-Time Multiplication) для унеможливлення витоку ключів через час виконання процесора.

## 7. Простеження викликів та профілювання продуктивності (Tracepoints / Sysfs)

Для налагодження криптографічних модулів зобов'язань у ядрах ОС Linux та системних службах надається серія статичних точок простеження (tracepoints):

- `crypto_commit:pedersen_start` — спрацьовує на початку скалярного множення точок.
- `crypto_commit:pedersen_end` — спрацьовує після завершення додавання точок у групі.
- `crypto_commit:kzg_pairing_eval` — фіксує тривалість обчислення білінійного спарювання.

Моніторинг через sysfs здійснюється зчитуванням лічильників продуктивності:
```bash
cat /sys/kernel/debug/tracing/events/crypto_commit/pedersen_start/enable
```

## 8. Сумісність та стандартифікація RFC / ISO

Специфікація узгоджується з міжнародними криптографічними стандартами:
- **IETF RFC 9380:** Hash-to-Curve algorithms for EC points (означення точок `H`).
- **ISO/IEC 18033-2:** Asymmetric Ciphers and Commitment primitives.
- **EIP-4844:** KZG commitment specifications for consensus headers.

## 9. Розробка мовних прив'язок (Language Bindings: Python / Rust / WASM)

Для забезпечення багатоплатформності інтерфейс надає офіційні обгортки (bindings):

- **Python CFFI binding:** дозволяє здійснювати виклики `pedersen_commit` безпосередньо з високорівневих скриптів аналізу даних.
- **WebAssembly (WASM) Module:** дозволяє виконувати фазу відкриття зобов'язань безпосередньо у веб-браузері клієнта з апаратною швидкістю.
- **Rust Safe Wrapper:** надає макрос `pedersen_commit!` із строгими гарантіями володіння пам'яттю (ownership semantics).

## 10. Інтеграція з системами виявлення вторгнень (SIEM / Audit Logging)

Виклики верифікації зобов'язань у корпоративних мережах генерують структуровані події аудиту у форматі JSON-Line:
```json
{
  "timestamp": "2026-08-15T14:38:15Z",
  "event": "COMMITMENT_VERIFY",
  "scheme": "PEDERSEN_SECP256K1",
  "result": "SUCCESS",
  "execution_time_us": 142.5
}
```

## 11. Сумісність із мережевими протоколами gRPC та OpenAPI

Для розподілених мікросервісів специфікація надає Protobuf-контракт:

```protobuf
syntax = "proto3";

package crypto.commitment.v1;

message CommitRequest {
  bytes message_or_value = 1;
  bytes blinding_factor = 2;
  string scheme_type = 3;
}

message CommitResponse {
  bytes commitment_bytes = 1;
  uint32 status_code = 2;
}

service CommitmentService {
  rpc CreateCommitment (CommitRequest) returns (CommitResponse);
}
```

## 12. Специфікація форматів серіалізації даних (JSON / CBOR / Binary)

Для обміну зобов'язаннями між heterogenous системами стандартизовано двійковий формат CBOR (Concise Binary Object Representation). Двійкова структура зобов'язання містить 1-байтний ідентифікатор алгоритму (`0x01` SHA256, `0x02` Pedersen, `0x03` KZG), за яким слідує довжина payload та самі байти стиснутої точки або хешу.

## 13. Тестові вектори для незалежної перевірки реалізацій (Test Vectors)

Для верифікації сумісності сторонніх бібліотек наведено офіційний тестовий вектор для зобов'язань Педерсена на кривій secp256k1:
- `value (v)`: `0x0000000000000000000000000000000000000000000000000000000000000001`
- `blinding (r)`: `0x0000000000000000000000000000000000000000000000000000000000000002`
- `Expected Commitment (C)`: `0x03a34b99f22c7d237621161f731ad59475e182371275965f32a7cb6f4b666d3a82`

## 14. Специфікація обробки виняткових ситуацій та таймаутів мережі

При виконанні мережевих викликів верифікації зобов'язань у розподілених кластерах застосовуються наступні правила таймаутів:

- **Таймаут створення зобов'язання (Commit Timeout):** 500 мілісекунд.
- **Таймаут верифікації KZG спарювання (Verify Timeout):** 2000 мілісекунд.
- **Повторні спроби (Retry policy):** До трьох повторних спроб із експоненційним запізненням (Exponential Backoff).

Розробники смарт-контрактів повинні враховувати споживання газу (Gas costs): виклик `verifyPedersen` потребує ~9,000 gas, тоді як верифікація KZG через `ecPairing` вимагає ~115,000 gas на один доказ.
