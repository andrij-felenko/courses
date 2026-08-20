# ⚙️ Двигунець TOTP: повний цикл генерації, перевірки та резервних кодів

## Задача

Побудувати надійний, виробничий бекенд-модуль двофакторної автентифікації на базі стандартів RFC 6238 (TOTP — Time-Based One-Time Password) та RFC 4226 (HOTP — HMAC-Based One-Time Password). Модуль повинен забезпечувати повний життєвий цикл другого фактора в системі:
1. Безпечне створення спільного симетричного секрету `K` через криптографічно надійний генератор псевдовипадкових чисел операційної системи (CSPRNG).
2. Кодування секрету у формат RFC 4648 Base32 та формування стандартизованого рядка `otpauth://totp/...` для експорту в QR-код мобільних застосунків.
3. Обчислення лічильника кроків часу `T`, формування 64-бітного бінарного представлення у мережевому порядку байтів (Big-Endian) та підпис через HMAC-SHA-1 / HMAC-SHA-256.
4. Динамічне усікання 20-байтного (або 32-байтного) відбитка (Dynamic Truncation) для вилучення 31-бітного числа та отримання 6 десяткових цифр.
5. Двоетапна активація фактора (Enrollment handshake): новий секрет не активується в профілі користувача, доки клієнт не доведе володіння ним успішною верифікацією першого згенерованого коду.
6. Верифікація вхідного коду з підтримкою вікна розсинхронізації годинників `±1` крок (інтервал валідності 90 секунд).
7. Захист від повторного використання перехопленого коду (Anti-Replay Protection) через фіксацію останнього перевіреного часового кроку.
8. Порівняння кодів суворо за сталий час (Constant-Time Comparison) для запобігання атакам через побічні канали вимірювання часу (Timing Attacks).
9. Генерація набору резервних одноразових кодів відновлення (Emergency Backup Codes), їх безпечне зберігання у вигляді криптографічних хешів та атомарне одноразове списання під час входу.
10. Обробка ручної повторної синхронізації годинника (Resynchronization Protocol) за двома послідовними кодами у разі значного зсуву апаратного часу на пристрої користувача.
11. Захист від перебору 6-значного простору через проміжне програмне забезпечення обмеження частоти запитів (Rate Limiting) з експоненційною затримкою.
12. Безпечне зберігання секретів у стані спокою (Envelope Encryption) та очищення чутливих буферів у оперативній пам'яті (Memory Zeroing).

Нижче розібрано кожен крок алгоритму з детальним аналізом фізики процесу та робочим кодом чотирма мовами бекенду: TypeScript (Node.js), Python, Go та C++ (C++20).

---

## Ідея: час як узгоджений лічильник подій

Складнощі автентифікації за паролем походять від того, що статичний секрет подорожує мережею під час кожного входу. Якщо лінію підслухано або сервер перенаправлено на фішинговий проксі, пароль стає відомим третій стороні. 

Ідея одноразового пароля на основі часу полягає в тому, що **сам секрет `K` ніколи більше не передається каналом зв'язку після початкового налаштування**. Натомість клієнт і сервер використовують узгоджену фізичну величину — поточний час — як аргумент однобічної криптографічної функції.

Узгодженим лічильником виступає кількість цілих 30-секундних інтервалів, що минули від початку доби Unix Epoch (00:00:00 UTC 1 січня 1970 року):

```
T = ⌊ (t - T₀) / X ⌋
```

де:
* `t` — поточний системний час у секундах (Unix timestamp);
* `T₀` — початкова точка відліку (за стандартом RFC 6238 завжди дорівнює `0`);
* `X` — тривалість одного кроку в секундах (за замовчуванням `30` секунд).

Оскільки обидві сторони мають доступ до синхронізованого світового часу (через протокол NTP на серверах та стільникові вежі / GPS на смартфонах), їхні обчислення збігаються без жодної взаємодії по мережі. Клієнт показує людині 6 цифр, людина вводить їх у браузер, а сервер повторює обчислення для поточного інтервалу і перевіряє рівність результатів.

```
Клієнт (телефон):             Сервер (бекенд):
 час t = 1718928015            час t = 1718928017
 T = ⌊1718928015 / 30⌋         T = ⌊1718928017 / 30⌋
 T = 57297600                  T = 57297600
 HMAC-SHA1(K, T)               HMAC-SHA1(K, T)
        ↓                              ↓
 Код: «482 910» ——— надсилає ———→ Код: «482 910» → ЗБІГ!
```

---

## Крок 1. Генерація секрету, кодування Base32 та формування URI

Спільний секретний ключ `K` — це випадковий масив байтів високої ентропії. За рекомендаціями RFC 4226 та RFC 6238 довжина ключа для алгоритму HMAC-SHA-1 має бути щонайменше 160 бітів (20 байтів), а для HMAC-SHA-256 — 256 бітів (32 байти).

Секрет кодується у форматі Base32 (RFC 4648). Вибір Base32 замість звичного Base64 зумовлений людським фактором: алфавіт Base32 містить лише великі літери латиниці `A-Z` та цифри `2-7`. У ньому відсутні символи `0` (нуль) та `O` (велика буква о), а також `1` (одиниця) та `I`/`l` (букви I/l), які легко переплутати при ручному введенні на екрані телефона.

Після кодування секрету сервер формує стандартизований уніфікований ідентифікатор ресурсу (URI) за схемою `otpauth://`, який кодується у графічний QR-код для зручного зчитування камерою:

```
otpauth://totp/AcmeCorp:alice@example.com?secret=JBSWY3DPEHPK3PXP&issuer=AcmeCorp&algorithm=SHA1&digits=6&period=30
```

Параметри URI строго специфіковані:
* `totp` — тип генератора (на основі часу, на відміну від лічильника `hotp`);
* `label` (`AcmeCorp:alice@example.com`) — назва сервісу та обліковий запис користувача;
* `secret` — закодований у Base32 секретний ключ без пробілів та символів доповнення `=`;
* `issuer` — назва організації чи платформи (мусить збігатися з префіксом у label);
* `algorithm` — геш-функція (`SHA1`, `SHA256` або `SHA512`);
* `digits` — кількість цифр у коді (за замовчуванням 6);
* `period` — крок часу в секундах (за замовчуванням 30).

:::tabs
```ts
import crypto from "crypto";

const BASE32_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

export function generateBase32Secret(byteLength: number = 20): string {
  const buffer = crypto.randomBytes(byteLength);
  let bits = 0;
  let value = 0;
  let output = "";

  for (let i = 0; i < buffer.length; i++) {
    value = (value << 8) | buffer[i];
    bits += 8;
    while (bits >= 5) {
      output += BASE32_CHARS[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  if (bits > 0) {
    output += BASE32_CHARS[(value << (5 - bits)) & 31];
  }
  return output;
}

export function decodeBase32(base32: string): Buffer {
  const clean = base32.replace(/[\s=-]/g, "").toUpperCase();
  let bits = 0;
  let value = 0;
  const bytes: number[] = [];

  for (let i = 0; i < clean.length; i++) {
    const idx = BASE32_CHARS.indexOf(clean[i]);
    if (idx === -1) {
      throw new Error(`Недійсний символ Base32: ${clean[i]}`);
    }
    value = (value << 5) | idx;
    bits += 5;
    if (bits >= 8) {
      bytes.push((value >>> (bits - 8)) & 255);
      bits -= 8;
    }
  }
  return Buffer.from(bytes);
}

export function buildTotpUri(
  issuer: string,
  accountName: string,
  secretBase32: string
): string {
  const label = encodeURIComponent(`${issuer}:${accountName}`);
  const params = new URLSearchParams({
    secret: secretBase32,
    issuer: issuer,
    algorithm: "SHA1",
    digits: "6",
    period: "30",
  });
  return `otpauth://totp/${label}?${params.toString()}`;
}
```
```python
import secrets
import base64
import urllib.parse

def generate_base32_secret(byte_length: int = 20) -> str:
    raw_bytes = secrets.token_bytes(byte_length)
    return base64.b32encode(raw_bytes).decode("ascii").rstrip("=")

def decode_base32(secret: str) -> bytes:
    clean = secret.replace(" ", "").replace("-", "").upper()
    padding = (8 - len(clean) % 8) % 8
    clean += "=" * padding
    return base64.b32decode(clean, casefold=True)

def build_totp_uri(issuer: str, account_name: str, secret_base32: str) -> str:
    label = f"{issuer}:{account_name}"
    params = {
        "secret": secret_base32,
        "issuer": issuer,
        "algorithm": "SHA1",
        "digits": 6,
        "period": 30,
    }
    return f"otpauth://totp/{urllib.parse.quote(label)}?{urllib.parse.urlencode(params)}"
```
```go
package totp

import (
	"crypto/rand"
	"encoding/base32"
	"fmt"
	"net/url"
	"strings"
)

var b32Encoding = base32.StdEncoding.WithPadding(base32.NoPadding)

func GenerateBase32Secret(byteLength int) (string, error) {
	buf := make([]byte, byteLength)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	return b32Encoding.EncodeToString(buf), nil
}

func DecodeBase32(secret string) ([]byte, error) {
	clean := strings.ToUpper(strings.ReplaceAll(strings.ReplaceAll(secret, " ", ""), "-", ""))
	return b32Encoding.DecodeString(clean)
}

func BuildTotpURI(issuer, accountName, secretBase32 string) string {
	label := fmt.Sprintf("%s:%s", issuer, accountName)
	v := url.Values{}
	v.Set("secret", secretBase32)
	v.Set("issuer", issuer)
	v.Set("algorithm", "SHA1")
	v.Set("digits", "6")
	v.Set("period", "30")

	return fmt.Sprintf("otpauth://totp/%s?%s", url.PathEscape(label), v.Encode())
}
```
```cpp
#include <vector>
#include <string>
#include <string_view>
#include <stdexcept>
#include <random>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cstdint>

namespace totp {

inline constexpr std::string_view BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

std::string generate_base32_secret(std::size_t byte_length = 20) {
    std::random_device rd;
    std::vector<std::uint8_t> buffer(byte_length);
    for (auto& b : buffer) {
        b = static_cast<std::uint8_t>(rd());
    }

    std::string result;
    std::uint32_t value = 0;
    int bits = 0;
    for (std::uint8_t b : buffer) {
        value = (value << 8) | b;
        bits += 8;
        while (bits >= 5) {
            result += BASE32_ALPHABET[(value >> (bits - 5)) & 31];
            bits -= 5;
        }
    }
    if (bits > 0) {
        result += BASE32_ALPHABET[(value << (5 - bits)) & 31];
    }
    return result;
}

std::vector<std::uint8_t> decode_base32(std::string_view input) {
    std::vector<std::uint8_t> bytes;
    std::uint32_t value = 0;
    int bits = 0;
    for (char c : input) {
        if (c == ' ' || c == '-' || c == '=') continue;
        char upper = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        auto pos = BASE32_ALPHABET.find(upper);
        if (pos == std::string_view::npos) {
            throw std::runtime_error("Недійсний символ Base32");
        }
        value = (value << 5) | static_cast<std::uint32_t>(pos);
        bits += 5;
        if (bits >= 8) {
            bytes.push_back(static_cast<std::uint8_t>((value >> (bits - 8)) & 0xFF));
            bits -= 8;
        }
    }
    return bytes;
}

} // namespace totp
```
:::

---

## Крок 2 та 3. HMAC та алгоритм динамічного усікання

Отримавши 64-бітне число лічильника `T`, алгоритм виконує такі перетворення за специфікацією RFC 4226 §5.3–5.4:

1. **Бінарна упаковка Big-Endian:** 64-бітне ціле число `T` перетворюється на фіксований 8-байтний масив, де старші байти розташовані попереду. Наприклад, крок `T = 57297600` (шістнадцяткове `0x036A4AC0`) записується як `00 00 00 00 03 6A 4A C0`.
2. **Криптографічне хешування:** Обчислюється HMAC від цих 8 байтів за допомогою секрету `K`. Для SHA-1 результат — 20 байтів: `HS[0 .. 19]`.
3. **Динамічне визначення зміщення (Dynamic Offset):** Останній байт відбитка `HS[19]` маскується побітовим `AND 0x0F` (молодші 4 біти). Це дає зміщення `offset` у діапазоні від `0` до `15`.
4. **Витяг 4 байтів:** Починаючи з позиції `offset`, беруться 4 послідовні байти: `HS[offset], HS[offset+1], HS[offset+2], HS[offset+3]`.
5. **Скидання знакового біта:** 32-бітне число об'єднується операцією `(Byte0 << 24) | (Byte1 << 16) | (Byte2 << 8) | Byte3`, після чого старший біт обнуляється маскою `& 0x7FFFFFFF`. Це робиться для того, щоб результат завжди трактувався як додатне 31-бітне ціле число незалежно від того, як мова програмування чи апаратна платформа працює зі знаковими типами `int32`.
6. **Десяткова редукція:** Число ділиться за модулем `10^d` (де `d = 6`): `OTP = P mod 1 000 000`. Фінальний рядок форматується з фіксованою довжиною 6 цифр з додаванням провідних нулів у разі потреби (наприклад, `742` стає `000742`).

:::tabs
```ts
export function generateTOTPCode(
  secretBytes: Buffer,
  timestampSeconds: number,
  timeStep: number = 30,
  digits: number = 6
): string {
  const counter = Math.floor(timestampSeconds / timeStep);
  
  // 64-бітний лічильник у форматі Big-Endian (8 байтів)
  const counterBuffer = Buffer.alloc(8);
  counterBuffer.writeBigUInt64BE(BigInt(counter), 0);

  const hmac = crypto.createHmac("sha1", secretBytes);
  hmac.update(counterBuffer);
  const digest = hmac.digest();

  // Dynamic Truncation за RFC 4226 §5.4
  const offset = digest[digest.length - 1] & 0x0f;
  const binaryCode =
    ((digest[offset] & 0x7f) << 24) |
    ((digest[offset + 1] & 0xff) << 16) |
    ((digest[offset + 2] & 0xff) << 8) |
    (digest[offset + 3] & 0xff);

  const otp = binaryCode % Math.pow(10, digits);
  return otp.toString().padStart(digits, "0");
}
```
```python
import hmac
import hashlib
import struct

def generate_totp_code(
    secret_bytes: bytes,
    timestamp_seconds: int,
    time_step: int = 30,
    digits: int = 6
) -> str:
    counter = timestamp_seconds // time_step
    # 8 байтів Big-Endian: '>Q' — unsigned long long 64 біти
    counter_bytes = struct.pack(">Q", counter)

    digest = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()
    
    # Dynamic Truncation
    offset = digest[-1] & 0x0F
    binary_code = struct.unpack(">I", digest[offset:offset+4])[0] & 0x7FFFFFFF
    
    otp = binary_code % (10 ** digits)
    return str(otp).zfill(digits)
```
```go
package totp

import (
	"crypto/hmac"
	"crypto/sha1"
	"encoding/binary"
	"fmt"
	"math"
)

func GenerateTOTPCode(secret []byte, timestamp int64, timeStep int64, digits int) string {
	counter := uint64(timestamp / timeStep)
	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, counter)

	mac := hmac.New(sha1.New, secret)
	mac.Write(buf)
	digest := mac.Sum(nil)

	offset := digest[len(digest)-1] & 0x0f
	binaryCode := binary.BigEndian.Uint32(digest[offset:offset+4]) & 0x7fffffff

	mod := uint32(math.Pow10(digits))
	otp := binaryCode % mod

	format := fmt.Sprintf("%%0%dd", digits)
	return fmt.Sprintf(format, otp)
}
```
```cpp
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <span>

namespace totp {

std::string generate_totp_code(
    std::span<const std::uint8_t> secret,
    std::int64_t timestamp_seconds,
    std::int64_t time_step = 30,
    int digits = 6
) {
    std::uint64_t counter = static_cast<std::uint64_t>(timestamp_seconds / time_step);
    std::uint8_t counter_bytes[8];
    for (int i = 7; i >= 0; --i) {
        counter_bytes[i] = static_cast<std::uint8_t>(counter & 0xFF);
        counter >>= 8;
    }

    unsigned int len = 20;
    std::uint8_t digest[EVP_MAX_MD_SIZE];
    HMAC(EVP_sha1(), secret.data(), static_cast<int>(secret.size()),
         counter_bytes, sizeof(counter_bytes), digest, &len);

    std::uint8_t offset = digest[len - 1] & 0x0F;
    std::uint32_t binary_code =
        ((static_cast<std::uint32_t>(digest[offset]) & 0x7F) << 24) |
        ((static_cast<std::uint32_t>(digest[offset + 1]) & 0xFF) << 16) |
        ((static_cast<std::uint32_t>(digest[offset + 2]) & 0xFF) << 8) |
        (static_cast<std::uint32_t>(digest[offset + 3]) & 0xFF);

    std::uint32_t mod = static_cast<std::uint32_t>(std::pow(10, digits));
    std::uint32_t otp = binary_code % mod;

    std::ostringstream ss;
    ss << std::setw(digits) << std::setfill('0') << otp;
    return ss.str();
}

} // namespace totp
```
:::

---

## Крок 4 та 5. Вікно зсуву часу, стійкість до повторів та константний час

У реальному житті годинники пристроїв не є абсолютно ідеальними. Затримка передачі пакета мережею, повільний набір цифр користувачем або розсинхронізація системного часу смартфона на 5–10 секунд можуть призвести до того, що код буде згенеровано на кроці `T`, а сервер отримає його вже на початку кроку `T+1`.

Для компенсації сервер реалізує **вікно валідації (Validation Window)**. Зазвичай перевіряються 3 послідовні кроки: `[T-1, T, T+1]` (вікно `window = 1`), що охоплює 90 секунд фізичного часу.

### Небезпека повторного входу (Replay Attack)

Вікно у 90 секунд створює критичну вразливість: якщо зловмисник сидить у тій самій локальній мережі й перехопив 6-значний код жертви або підгледів його через плече, він має до 90 секунд, щоб ввести той самий код і пройти авторизацію на паралельному пристрої.

**Архітектурне вирішення:** Сервер зобов'язаний зберігати маркер успішності входу. Це реалізується одним із двох способів:
1. **Водяний знак у базі даних (`last_verified_step`):** В обліковому записі користувача оновлюється поле цілого числа, що зберігає номер кроку `step`, на якому було здійснено успішний вхід. Будь-який наступний запит із `step <= last_verified_step` негайно відхиляється.
2. **Блокування хешу в розподіленому кеші (Redis):** Після успішного входу ключ `mfa_consumed:<user_id>:<step>` записується в Redis із TTL 180 секунд. Повторна спроба використати той самий крок блокується атомарною операцією `SET ... NX`.

### Захист від атак за часом виконання (Timing Attacks)

Звичайний оператор порівняння рядків (`===` у JS, `==` у Python або C++) оптимізований для швидкості: він порівнює символи зліва направо і перериває виконання в мікросекунду знаходження першої невідповідності. Якщо перша цифра коду правильна, порівняння триває на кілька наносекунд довше, ніж якщо неправильна перша.

Зловмисник, що відправляє тисячі запитів і точно вимірює час відповіді HTTP-сервера, може відновити всі 6 цифр одну за одною. Тому порівняння здійснюється виключно за допомогою криптографічних константних функцій (`crypto.timingSafeEqual`, `hmac.compare_digest`, `subtle.ConstantTimeCompare`), які завжди проходять по всіх байтах масиву незалежно від результату.

:::tabs
```ts
export interface VerificationResult {
  valid: boolean;
  verifiedStep?: number;
}

export function verifyTOTPCode(
  secretBase32: string,
  userInputCode: string,
  currentTimestampSeconds: number,
  lastVerifiedStep: number = 0,
  window: number = 1,
  timeStep: number = 30
): VerificationResult {
  const cleanCode = userInputCode.trim();
  if (!/^\d{6}$/.test(cleanCode)) {
    return { valid: false };
  }

  const secretBytes = decodeBase32(secretBase32);
  const currentStep = Math.floor(currentTimestampSeconds / timeStep);

  for (let offset = -window; offset <= window; offset++) {
    const step = currentStep + offset;

    // Захист від повтору: крок уже використовувався в минулому
    if (step <= lastVerifiedStep) {
      continue;
    }

    const expectedCode = generateTOTPCode(secretBytes, step * timeStep, timeStep);
    
    // Безпечне порівняння за сталий час
    const a = Buffer.from(cleanCode);
    const b = Buffer.from(expectedCode);
    if (a.length === b.length && crypto.timingSafeEqual(a, b)) {
      return { valid: true, verifiedStep: step };
    }
  }

  return { valid: false };
}
```
```python
import hmac

def verify_totp_code(
    secret_base32: str,
    user_input_code: str,
    current_timestamp: int,
    last_verified_step: int = 0,
    window: int = 1,
    time_step: int = 30
) -> tuple[bool, int | None]:
    clean_code = user_input_code.strip()
    if len(clean_code) != 6 or not clean_code.isdigit():
        return False, None

    secret_bytes = decode_base32(secret_base32)
    current_step = current_timestamp // time_step

    for offset in range(-window, window + 1):
        step = current_step + offset
        
        # Anti-Replay захист
        if step <= last_verified_step:
            continue

        expected = generate_totp_code(secret_bytes, step * time_step, time_step)
        
        # hmac.compare_digest захищає від Timing Attack
        if hmac.compare_digest(clean_code, expected):
            return True, step

    return False, None
```
```go
package totp

import (
	"crypto/subtle"
	"strings"
)

type VerificationResult struct {
	Valid        bool
	VerifiedStep int64
}

func VerifyTOTPCode(
	secretBase32 string,
	userInputCode string,
	currentTimestamp int64,
	lastVerifiedStep int64,
	window int,
	timeStep int64,
) VerificationResult {
	cleanCode := strings.TrimSpace(userInputCode)
	if len(cleanCode) != 6 {
		return VerificationResult{Valid: false}
	}

	secretBytes, err := DecodeBase32(secretBase32)
	if err != nil {
		return VerificationResult{Valid: false}
	}

	currentStep := currentTimestamp / timeStep

	for offset := -window; offset <= window; offset++ {
		step := currentStep + int64(offset)

		if step <= lastVerifiedStep {
			continue
		}

		expected := GenerateTOTPCode(secretBytes, step*timeStep, timeStep, 6)

		if subtle.ConstantTimeCompare([]byte(cleanCode), []byte(expected)) == 1 {
			return VerificationResult{Valid: true, VerifiedStep: step}
		}
	}

	return VerificationResult{Valid: false}
}
```
```cpp
#include <string>
#include <string_view>
#include <cstdint>
#include <span>

namespace totp {

bool constant_time_equals(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) return false;
    unsigned char result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        result |= static_cast<unsigned char>(a[i]) ^ static_cast<unsigned char>(b[i]);
    }
    return result == 0;
}

struct VerificationResult {
    bool valid;
    std::int64_t verified_step;
};

VerificationResult verify_totp_code(
    std::string_view secret_base32,
    std::string_view user_input_code,
    std::int64_t current_timestamp,
    std::int64_t last_verified_step = 0,
    int window = 1,
    std::int64_t time_step = 30
) {
    if (user_input_code.size() != 6) {
        return {false, 0};
    }

    auto secret_bytes = decode_base32(secret_base32);
    std::int64_t current_step = current_timestamp / time_step;

    for (int offset = -window; offset <= window; ++offset) {
        std::int64_t step = current_step + offset;
        if (step <= last_verified_step) {
            continue;
        }

        std::string expected = generate_totp_code(secret_bytes, step * time_step, time_step, 6);
        if (constant_time_equals(user_input_code, expected)) {
            return {true, step};
        }
    }

    return {false, 0};
}

} // namespace totp
```
:::

---

## Крок 6. Ручна синхронізація розсинхронізованого годинника

Якщо клієнтський пристрій тривалий час перебував без доступу до інтернету (наприклад, у подорожі чи авіарежимі), кварцовий генератор телефона міг накопичити зсув у 2–5 хвилин (`offset = 4..10` кроків). Звичайне вікно перевірки `window = 1` відхилятиме коди такого користувача, блокуючи йому вхід.

Просте розширення вікна до 10 кроків (±5 хвилин) неприпустиме, бо це відкриває 21 одночасно дійсний код для зловмисника, збільшуючи ймовірність підбору в 21 раз.

**Рішення RFC 6238:** Спеціальний протокол синхронізації (Resynchronization Protocol), що вимагає введення **двох послідовних кодів одночасно**:
1. Користувач вводить `Code1` (поточний) і `Code2` (який з'являється через 30 секунд).
2. Сервер шукає таке зміщення `offset` у розширеному вікні (наприклад, до `±50` кроків), де `Code1` збігається на кроці `T + offset`, а `Code2` — на кроці `T + offset + 1`.
3. Оскільки ймовірність випадкового збігу двох послідовних 6-значних чисел становить `(1/10⁶)² = 10⁻¹²`, підібрати таку пару неможливо.
4. Знайдене зміщення `offset` зберігається в профілі користувача як постійна поправка часу (`drift_offset`).

:::tabs
```ts
export function resynchronizeClock(
  secretBase32: string,
  code1: string,
  code2: string,
  currentTimestampSeconds: number,
  maxDriftSteps: number = 50,
  timeStep: number = 30
): { success: boolean; driftOffset?: number } {
  const secretBytes = decodeBase32(secretBase32);
  const currentStep = Math.floor(currentTimestampSeconds / timeStep);

  for (let drift = -maxDriftSteps; drift <= maxDriftSteps; drift++) {
    const expected1 = generateTOTPCode(secretBytes, (currentStep + drift) * timeStep, timeStep);
    const expected2 = generateTOTPCode(secretBytes, (currentStep + drift + 1) * timeStep, timeStep);

    const a1 = Buffer.from(code1.trim());
    const b1 = Buffer.from(expected1);
    const a2 = Buffer.from(code2.trim());
    const b2 = Buffer.from(expected2);

    if (
      a1.length === b1.length && crypto.timingSafeEqual(a1, b1) &&
      a2.length === b2.length && crypto.timingSafeEqual(a2, b2)
    ) {
      return { success: true, driftOffset: drift };
    }
  }

  return { success: false };
}
```
```python
def resynchronize_clock(
    secret_base32: str,
    code1: str,
    code2: str,
    current_timestamp: int,
    max_drift_steps: int = 50,
    time_step: int = 30
) -> tuple[bool, int | None]:
    secret_bytes = decode_base32(secret_base32)
    current_step = current_timestamp // time_step
    c1, c2 = code1.strip(), code2.strip()

    for drift in range(-max_drift_steps, max_drift_steps + 1):
        exp1 = generate_totp_code(secret_bytes, (current_step + drift) * time_step, time_step)
        exp2 = generate_totp_code(secret_bytes, (current_step + drift + 1) * time_step, time_step)

        if hmac.compare_digest(c1, exp1) and hmac.compare_digest(c2, exp2):
            return True, drift

    return False, None
```
```go
package totp

import (
	"crypto/subtle"
	"strings"
)

func ResynchronizeClock(
	secretBase32 string,
	code1, code2 string,
	currentTimestamp int64,
	maxDriftSteps int,
	timeStep int64,
) (bool, int) {
	secretBytes, err := DecodeBase32(secretBase32)
	if err != nil {
		return false, 0
	}

	currentStep := currentTimestamp / timeStep
	c1, c2 := strings.TrimSpace(code1), strings.TrimSpace(code2)

	for drift := -maxDriftSteps; drift <= maxDriftSteps; drift++ {
		exp1 := GenerateTOTPCode(secretBytes, (currentStep+int64(drift))*timeStep, timeStep, 6)
		exp2 := GenerateTOTPCode(secretBytes, (currentStep+int64(drift)+1)*timeStep, timeStep, 6)

		m1 := subtle.ConstantTimeCompare([]byte(c1), []byte(exp1))
		m2 := subtle.ConstantTimeCompare([]byte(c2), []byte(exp2))

		if m1 == 1 && m2 == 1 {
			return true, drift
		}
	}

	return false, 0
}
```
```cpp
#include <string_view>
#include <cstdint>

namespace totp {

struct ResyncResult {
    bool success;
    int drift_offset;
};

ResyncResult resynchronize_clock(
    std::string_view secret_base32,
    std::string_view code1,
    std::string_view code2,
    std::int64_t current_timestamp,
    int max_drift_steps = 50,
    std::int64_t time_step = 30
) {
    auto secret_bytes = decode_base32(secret_base32);
    std::int64_t current_step = current_timestamp / time_step;

    for (int drift = -max_drift_steps; drift <= max_drift_steps; ++drift) {
        std::string exp1 = generate_totp_code(secret_bytes, (current_step + drift) * time_step, time_step, 6);
        std::string exp2 = generate_totp_code(secret_bytes, (current_step + drift + 1) * time_step, time_step, 6);

        if (constant_time_equals(code1, exp1) && constant_time_equals(code2, exp2)) {
            return {true, drift};
        }
    }

    return {false, 0};
}

} // namespace totp
```
:::

---

## Крок 7. Одноразові резервні коди відновлення (Backup Codes)

Якщо телефон із застосунком розбився або втрачений, користувач ризикує втратити доступ назавжди. Тому під час налаштування 2FA сервер генерує набір із 8–10 одноразових резервних кодів (Emergency Backup Codes).

Вимоги до архітектури резервних кодів:
1. **Висока ентропія:** Кожен код генерується через CSPRNG (наприклад, 10–12 шістнадцяткових символів).
2. **Зберігання тільки у вигляді хешів:** Сервер ніколи не тримає відкриті резервні коди в базі даних. Вони хешуються алгоритмом SHA-256 із сіллю або argon2id, аналогічно до паролів.
3. **Атомарне списання:** Використання резервного коду мусить виконуватися в одній транзакції бази даних: якщо хеш збігся і поле `used == false`, статус змінюється на `used = true` або запис видаляється. Це запобігає повторному використанню коду при паралельних запитах (Race Condition).

:::tabs
```ts
export interface BackupCodeEntry {
  hash: string;
  used: boolean;
  createdAt: Date;
}

export function generateBackupCodes(count: number = 8): string[] {
  const codes: string[] = [];
  for (let i = 0; i < count; i++) {
    const raw = crypto.randomBytes(5).toString("hex");
    const formatted = `${raw.slice(0, 5)}-${raw.slice(5)}`;
    codes.push(formatted);
  }
  return codes;
}

export function hashBackupCode(plainCode: string): string {
  const clean = plainCode.replace(/[\s-]/g, "").toLowerCase();
  return crypto.createHash("sha256").update(clean).digest("hex");
}

export function verifyAndConsumeBackupCode(
  userInput: string,
  storedCodes: BackupCodeEntry[]
): { success: boolean; updatedCodes: BackupCodeEntry[] } {
  const inputHash = hashBackupCode(userInput);
  let found = false;

  const updatedCodes = storedCodes.map((entry) => {
    if (!entry.used && entry.hash === inputHash && !found) {
      found = true;
      return { ...entry, used: true };
    }
    return entry;
  });

  return { success: found, updatedCodes };
}
```
```python
import secrets
import hashlib

def generate_backup_codes(count: int = 8) -> list[str]:
    codes = []
    for _ in range(count):
        raw = secrets.token_hex(5)
        codes.append(f"{raw[:5]}-{raw[5:]}")
    return codes

def hash_backup_code(plain_code: str) -> str:
    clean = plain_code.replace("-", "").replace(" ", "").lower()
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()

def verify_and_consume_code(
    user_input: str,
    stored_hashes: list[dict]
) -> tuple[bool, list[dict]]:
    input_hash = hash_backup_code(user_input)
    
    for item in stored_hashes:
        if not item.get("used", False) and hmac.compare_digest(item["hash"], input_hash):
            item["used"] = True
            return True, stored_hashes
            
    return False, stored_hashes
```
```go
package totp

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"strings"
)

type BackupCodeRecord struct {
	Hash string
	Used bool
}

func GenerateBackupCodes(count int) ([]string, error) {
	codes := make([]string, count)
	for i := 0; i < count; i++ {
		b := make([]byte, 5)
		if _, err := rand.Read(b); err != nil {
			return nil, err
		}
		raw := hex.EncodeToString(b)
		codes[i] = fmt.Sprintf("%s-%s", raw[:5], raw[5:])
	}
	return codes, nil
}

func HashBackupCode(plain string) string {
	clean := strings.ToLower(strings.ReplaceAll(strings.ReplaceAll(plain, "-", ""), " ", ""))
	h := sha256.Sum256([]byte(clean))
	return hex.EncodeToString(h[:])
}

func VerifyAndConsumeBackupCode(input string, records []BackupCodeRecord) (bool, []BackupCodeRecord) {
	inputHash := HashBackupCode(input)
	for i := range records {
		if !records[i].Used {
			if subtle.ConstantTimeCompare([]byte(records[i].Hash), []byte(inputHash)) == 1 {
				records[i].Used = true
				return true, records
			}
		}
	}
	return false, records
}
```
```cpp
#include <string>
#include <vector>
#include <iomanip>
#include <sstream>
#include <random>
#include <algorithm>
#include <openssl/sha.h>

namespace totp {

struct BackupRecord {
    std::string hash_hex;
    bool used{false};
};

std::string hash_backup_code(std::string_view plain) {
    std::string clean;
    for (char c : plain) {
        if (c != '-' && c != ' ') {
            clean += static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        }
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(clean.data()), clean.size(), hash);

    std::ostringstream ss;
    for (unsigned char b : hash) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    return ss.str();
}

std::vector<std::string> generate_backup_codes(int count = 8) {
    std::random_device rd;
    std::vector<std::string> codes;
    codes.reserve(count);

    for (int i = 0; i < count; ++i) {
        std::ostringstream ss;
        for (int j = 0; j < 5; ++j) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (rd() & 0xFF);
        }
        std::string raw = ss.str();
        codes.push_back(raw.substr(0, 5) + "-" + raw.substr(5));
    }
    return codes;
}

bool verify_and_consume(std::string_view input, std::vector<BackupRecord>& records) {
    std::string target_hash = hash_backup_code(input);
    for (auto& rec : records) {
        if (!rec.used && constant_time_equals(rec.hash_hex, target_hash)) {
            rec.used = true;
            return true;
        }
    }
    return false;
}

} // namespace totp
```
:::

---

## Крок 8. Захист від масового підбору та Rate Limiting

Простір значень 6-значного коду становить рівно один мільйон комбінацій (`000000..999999`). При вікні перевірки `window = 1` дійсними є 3 коди одночасно. Ймовірність успішного вгадування за одну спробу:

```
P = 3 / 1 000 000 = 0.000003  (0.0003%)
```

Проте якщо бекенд обробляє тисячі запитів на секунду без обмеження швидкості, зловмисник може перебрати потрібний діапазон за лічені хвилини.

Правила побудови захисного прошарку Rate Limiting для TOTP:
1. **Жорсткий ліміт помилок на сесію `mfa_ticket`:** Максимум 3–5 невдалих спроб введення коду. Після 5 помилки тимчасовий жетон `mfa_ticket` повністю анулюється, змушуючи зловмисника заново починати з першого кроку введення пароля.
2. **Експоненційна затримка (Exponential Backoff):** Перша помилка — затримка 1 секунда, друга — 2 секунди, третя — 4 секунди.
3. **Блокування за IP-адресою та ідентифікатором акаунта:** Використання алгоритму Token Bucket або Sliding Window у Redis з лімітом не більше 10 запитів на 15 хвилин для одного облікового запису.

---

## Крок 9. Безпека пам'яті та шифрування у стані спокою

Симетричний ключ `K` — це критичний актив безпеки. Якщо зловмисник викраде дамп бази даних, усі незашифровані TOTP-секрети скомпрометують другий фактор усіх користувачів одночасно (як це сталося під час зламу RSA Security 2011 року).

**1. Конвертне шифрування (Envelope Encryption):**
Секрет `K` ніколи не зберігається відкритим текстом у колонках PostgreSQL або MongoDB. Він шифрується симетричним ключем даних (DEK — Data Encryption Key) за алгоритмом AES-256-GCM або ChaCha20-Poly1305. Ключ DEK, у свою чергу, шифрується апаратним майстер-ключем сервісу керування ключами (KMS — Key Management Service / HashiCorp Vault).

**2. Безпечне стирання буферів у пам'яті (Memory Zeroing):**
Після завершення обчислення HMAC масив байтів сирого секрету в оперативній пам'яті сервера мусить бути негайно перезаписаний нулями. У мовах C та C++ звичайний виклик `memset(buf, 0, len)` може бути повністю викинутий оптимізатором компілятора (Dead Code Elimination), якщо буфер далі не читається. Тому застосовуються спеціальні неоптимізовані функції безпечного затирання пам'яті на кшталт `explicit_bzero` (POSIX) або `SecureZeroMemory` (Windows).

---

## Наскрізний життєвий цикл запиту на бекенді

Зведемо всі компоненти в єдину послідовність обробки HTTP-запитів:

1. **Реєстрація 2FA (`POST /api/auth/mfa/setup`):**
   * Бекенд перевіряє активну сесію користувача.
   * Генерується новий секрет `K` та резервні коди.
   * Секрет зберігається в тимчасовій таблиці зі статусом `pending_verification` та TTL 10 хвилин.
   * Клієнту повертається рядок `otpauth://...` (для малювання QR-коду) та список резервних кодів для друку / збереження.

2. **Підтвердження активації (`POST /api/auth/mfa/confirm`):**
   * Користувач сканує QR-код та надсилає перший 6-значний код із додатка.
   * Бекенд перевіряє код за функцією `verifyTOTPCode`.
   * У разі успіху секрет `K` переноситься в основну таблицю профілю (у зашифрованому вигляді через KMS), статус змінюється на `mfa_enabled = true`, а відкриті резервні коди видаляються з пам'яті сервера після збереження їхніх хешів.

3. **Вхід у систему (`POST /api/auth/login` → `POST /api/auth/mfa/verify`):**
   * Крок 1: Користувач надсилає логін та пароль. Сервер перевіряє пароль через `argon2id.verify`. Якщо 2FA увімкнено, замість повної сесії видається короткоживучий підписаний токен `mfa_ticket` (TTL 3–5 хвилин) з обмеженим доступом.
   * Крок 2: Користувач надсилає `mfa_ticket` та 6-значний код на маршрут `/api/auth/mfa/verify`.
   * Сервер перевіряє код з урахуванням захисту від повтору (`last_verified_step`).
   * Якщо перевірка успішна, `mfa_ticket` анулюється, а клієнту встановлюється повноцінне сесійне cookie або видається фінальний Access/Refresh JWT з міткою `amr: ["pwd", "totp"]`.

Таке розділення гарантує, що жоден запит не отримає доступу до захищених ресурсів доти, доки обидва фактори не будуть повністю перевірені за всіма криптографічними правилами.
