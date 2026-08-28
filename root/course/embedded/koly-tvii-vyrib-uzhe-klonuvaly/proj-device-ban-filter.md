# ⚙️ Криптографічна фільтрація та відсікання клонів на бекенді

Коли клонований апаратний виріб з'являється на ринку, виробники копій зазвичай намагаються зберегти сумісність із фірмовою інфраструктурою: мобільними застосунками, веб-порталами, серверами оновлення прошивки (OTA) та хмарною аналітикою. Оскільки клонери прагнуть мінімізувати власні витрати на серверні потужності, вони спрямовують трафік клонованого парку на ваші публічні точки входу (API endpoints). Найнадійніший інженерний спосіб захистити сервіси й відсікти такі пристрої без деструктивного втручання в кремній — це взаємна криптографічна атестація на основі асиметричних ключів та ланцюга сертифікатів.

## Архітектура протоколу атестації та розподіл довіри

Захист від несанкціонованого доступу клонованого парку базується на трьох рівнях довіри:

1. **Фабрична персоналізація (Factory Provisioning).** Під час фінального тестування на виробничій лінії кожен оригінальний екземпляр генерує власну ключову пару всередині апаратного криптографічного чипа (Secure Element, наприклад Microchip ATECC608, NXP SE050 або Infineon OPTIGA Trust M). Приватний ключ ніколи не залишає межі захищеного кремнію. Фабричний сервер, підключений до апаратного модуля безпеки (Hardware Security Module, HSM), підписує публічний ключ пристрою за допомогою закритого проміжного сертифіката виробника (Intermediate Device CA).
2. **Сесійний виклик-відповідь (Challenge-Response Handshake).** Клієнт не надсилає постійних паролів чи статичних токенів. Для кожної сесії бекенд генерує свіжий одноразовий криптографічний вектор (`nonce`), який пристрій підписує за допомогою закритого ключа всередині крипточипа.
3. **Хмарний фільтр і керування життєвим циклом.** Серверний шлюз перевіряє ланцюг довіри сертифіката, валідність підпису, звіряє ідентифікатор із базою відкликаних ключів (Certificate Revocation List, CRL) та аналізує поведінкові аномалії підключення.

```
[ Клієнтський пристрій ]                                     [ Хмарний шлюз атестації ]
         |                                                               |
         | 1. Ініціалізація сесії: Hello (Device UUID + Сертифікат X.509)|
         |-------------------------------------------------------------->|
         |                                                               | [1.1 Перевірка ланцюга CA]
         |                                                               | [1.2 Генерація Nonce (32B)]
         | 2. Виклик: Challenge (32-байтний Nonce + Timestamp)           |
         |<--------------------------------------------------------------|
         |                                                               |
         | [2.1 Завантаження Nonce в Secure Element]                     |
         | [2.2 Апаратне обчислення ECDSA-підпису на кривій NIST P-256]  |
         |                                                               |
         | 3. Відповідь: Auth Response (ECDSA Signature R||S)            |
         |-------------------------------------------------------------->|
         |                                                               | [3.1 Верифікація підпису]
         |                                                               | [3.2 Перевірка CRL / банів]
         |                                                               | [3.3 Аналіз колізій IP/UUID]
         | 4. Результат: Session JWT (з правами та рівнем доступу)       |
         |<--------------------------------------------------------------|
```

Якщо клонери скопіювали спільний відкритий сертифікат або дамп флеш-пам'яті одного зразка, вони не мають доступу до унікального закритого ключа, фізично запечатаного в апаратному чипі. У разі, якщо один чип був фізично скомпрометований (наприклад, дорогою декапсуляцією та зчитуванням фокусованим іонним пучком FIB), клонери починають випускати тисячі пристроїв з одним і тим самим відкритим ідентифікатором. Хмарний шлюз фіксує аномальну активність (одночасні сесії з різних провайдерів і континентів) і блокує скомпрометований ключ на рівні CRL за мілісекунди.

## Життєвий цикл фабричної провізії ключів

Безпека всієї системи тримається на регламенті заводської прошивки. Якщо запис ключів відбувається через відкритий інтерфейс зневадження без контролю, недобросовісний контрактний виробник може зберегти базу згенерованих пар ключів і виготовити «третю зміну» плат.

Щоб унеможливити такий витік, генерація приватного ключа виконується самим Secure Element за командою `GENKEY`. Приватний ключ ніколи не з'являється на шині I2C чи SPI в незашифрованому вигляді: назовні віддається лише публічна точка еліптичної кривої. Фабричний стенд надсилає цей публічний ключ на захищений HSM-сервер компанії, де формується підписаний сертифікат пристрою, який потім записується у відкриту зону конфігурації мікросхеми безпеки.

## Реалізація клієнтської частини на мікроконтролері

Клієнтський модуль реалізує взаємодію з драйвером крипточипа. Він приймає масив виклику від сервера, викликає апаратну функцію підпису та формує структуру відповіді.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHALLENGE_NONCE_SIZE   32
#define ECDSA_SIG_SIZE          64
#define DEVICE_SERIAL_SIZE      16

typedef struct {
    uint8_t serial[DEVICE_SERIAL_SIZE];
    uint8_t signature[ECDSA_SIG_SIZE];
} device_auth_payload_t;

/* Низькорівневий інтерфейс взаємодії з апаратним крипточипом (I2C/SPI) */
extern bool secure_element_read_serial(uint8_t *out_serial_16b);
extern bool secure_element_sign_challenge(const uint8_t *digest_32b, uint8_t *out_sig_64b);

/**
 * @brief Формування криптографічної відповіді на виклик сервера.
 * @param nonce_32b Одноразовий вектор виклику від бекенду.
 * @param payload_out Вихідна структура для передавання по мережі.
 * @return true у разі успішного підпису апаратним модулем.
 */
bool device_generate_attestation_response(const uint8_t *nonce_32b,
                                          device_auth_payload_t *payload_out) {
    if (!nonce_32b || !payload_out) {
        return false;
    }

    /* Очищення пам'яті для уникнення витоку старих даних */
    memset(payload_out, 0, sizeof(device_auth_payload_t));

    /* Читання фабричного серійного номера */
    if (!secure_element_read_serial(payload_out->serial)) {
        return false;
    }

    /* Апаратне обчислення підпису ECDSA P-256 без вивантаження закритого ключа */
    if (!secure_element_sign_challenge(nonce_32b, payload_out->signature)) {
        memset(payload_out, 0, sizeof(device_auth_payload_t));
        return false;
    }

    return true;
}
```
```cpp
#include <array>
#include <span>
#include <optional>
#include <cstdint>
#include <cstring>

constexpr std::size_t ChallengeNonceSize = 32;
constexpr std::size_t EcdsaSignatureSize = 64;
constexpr std::size_t DeviceSerialSize = 16;

struct DeviceAuthPayload {
    std::array<std::uint8_t, DeviceSerialSize> serial{};
    std::array<std::uint8_t, EcdsaSignatureSize> signature{};
};

class ISecureElementDriver {
public:
    virtual ~ISecureElementDriver() = default;
    [[nodiscard]] virtual bool readSerial(std::span<std::uint8_t, DeviceSerialSize> outSerial) const noexcept = 0;
    [[nodiscard]] virtual bool signChallenge(std::span<const std::uint8_t, ChallengeNonceSize> nonce,
                                             std::span<std::uint8_t, EcdsaSignatureSize> outSignature) const noexcept = 0;
};

class AttestationClient {
public:
    explicit AttestationClient(const ISecureElementDriver& driver) noexcept
        : driver_(driver) {}

    [[nodiscard]] std::optional<DeviceAuthPayload> generateResponse(
        std::span<const std::uint8_t, ChallengeNonceSize> nonce) const noexcept {
        DeviceAuthPayload payload{};

        if (!driver_.readSerial(payload.serial)) {
            return std::nullopt;
        }

        if (!driver_.signChallenge(nonce, payload.signature)) {
            return std::nullopt;
        }

        return payload;
    }

private:
    const ISecureElementDriver& driver_;
};
```
:::

## Реалізація сервера перевірки та аналітики клонів (Backend Gateway)

Серверний компонент перевіряє валідність підпису, контролює час життя виклику (таймаут для запобігання replay-атакам), веде чорний список скомпрометованих пристроїв та виявляє аномалії паралельних сесій.

```python
import hmac
import time
import secrets
from typing import Dict, Optional, Tuple, Set
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class AttestationSecurityGateway:
    def __init__(self, hmac_signing_key: bytes, challenge_ttl_sec: float = 30.0):
        self._hmac_key = hmac_signing_key
        self._challenge_ttl = challenge_ttl_sec
        
        # Реєстр публічних ключів (серійний номер -> public key object)
        self._device_registry: Dict[str, ec.EllipticCurvePublicKey] = {}
        
        # Чорний список серійних номерів (Revocation Blocklist)
        self._revocation_list: Set[str] = set()
        
        # Активні виклики: session_id -> (nonce, timestamp, client_ip)
        self._pending_challenges: Dict[str, Tuple[bytes, float, str]] = {}
        
        # Трекер географії та підключень для детекції копіювання: serial -> set(ips)
        self._device_ip_history: Dict[str, Set[str]] = {}

    def register_device(self, serial: str, public_key_pem: bytes) -> None:
        """Реєстрація фабричного публічного ключа оригінального пристрою."""
        pub_key = load_pem_public_key(public_key_pem)
        if isinstance(pub_key, ec.EllipticCurvePublicKey):
            self._device_registry[serial] = pub_key

    def issue_challenge(self, session_id: str, client_ip: str) -> bytes:
        """Генерація унікального криптографічного виклику CSPRNG."""
        nonce = secrets.token_bytes(32)
        self._pending_challenges[session_id] = (nonce, time.time(), client_ip)
        return nonce

    def authenticate_device(self, session_id: str, serial: str, 
                             signature_raw: bytes, client_ip: str) -> Tuple[bool, str, Optional[str]]:
        """Повна перевірка виклику, підпису, списку відкликання та аномалій."""
        challenge = self._pending_challenges.pop(session_id, None)
        if not challenge:
            return False, "ERR_SESSION_NOT_FOUND", None

        nonce, issued_at, initial_ip = challenge

        # 1. Перевірка актуальності виклику за часом
        if (time.time() - issued_at) > self._challenge_ttl:
            return False, "ERR_CHALLENGE_EXPIRED", None

        # 2. Перевірка знаходження в реєстрі відкликаних ключів
        if serial in self._revocation_list:
            return False, "ERR_DEVICE_REVOKED", None

        # 3. Пошук зареєстрованого публічного ключа
        pub_key = self._device_registry.get(serial)
        if not pub_key:
            return False, "ERR_UNREGISTERED_DEVICE", None

        # 4. Перевірка підпису ECDSA (NIST P-256 / SHA-256)
        try:
            pub_key.verify(signature_raw, nonce, ec.ECDSA(hashes.SHA256()))
        except Exception:
            return False, "ERR_INVALID_SIGNATURE", None

        # 5. Детекція клонування: аналіз одночасних географічних підключень
        ip_set = self._device_ip_history.setdefault(serial, set())
        ip_set.add(client_ip)
        if len(ip_set) > 8:
            # Зафіксовано підозрілу кількість унікальних IP-адрес для одного чипа
            self._revocation_list.add(serial)
            return False, "ERR_CLONE_COLLISION_DETECTED", None

        # 6. Формування авторизаційного токена доступу до сервісів
        expiry = int(time.time()) + 3600
        payload = f"{serial}:{expiry}:verified".encode("utf-8")
        token_mac = hmac.new(self._hmac_key, payload, "sha256").hexdigest()
        session_token = f"{payload.decode('utf-8')}.{token_mac}"

        return True, "AUTH_SUCCESS", session_token
```

## Обробка помилок автентифікації на боці пристрою

Коли сервер відхиляє запит атестації (наприклад, повертає `ERR_DEVICE_REVOKED` або `ERR_UNREGISTERED_DEVICE`), прошивка повинна перейти в регламентований режим обмеженої функціональності:

1. **Діагностичне сповіщення користувача.** На екран пристрою або у супутній мобільний застосунок передається зрозуміле повідомлення: «Апаратна автентифікація не пройдена. Хмарні сервіси та автоматичні оновлення недоступні для цього екземпляра. Зверніться до служби підтримки».
2. **Збереження локального функціоналу.** Пристрій продовжує виконувати свої базові фізичні завдання (керування реле, обробку сигналів сенсорів, відображення даних на локальному дисплеї). Неприпустимо викликати циклічне перезавантаження (Watchdog reset) або блокувати інтерфейси введення-виведення.
3. **Експоненційне уповільнення повторних запитів (Exponential Backoff).** Щоб запобігти перевантаженню серверного шлюзу запитами від мільйонного парку клонів, прошивка при відмові збільшує інтервал між спробами автентифікації від 1 хвилини до 24 годин.

## Типові інженерні пастки та крайові випадки

- **Атаки повторного відтворення (Replay Attacks).** Якщо сервер надсилає передбачуваний лічильник або статичний рядок замість криптографічно випадкового `nonce` (CSPRNG), перехоплений підпис може використовуватися нескінченно. Nonce має генеруватися наново для кожного запиту та інвалідуватися одразу після перевірки або після вичерпання таймауту.
- **Синхронізація списків відкликання (CRL Latency).** У розподілених хмарних архітектурах із багатьма регіональними шлюзами затримка розповсюдження інформації про відкликання скомпрометованого серійного номера може складати хвилини. Це створює часове вікно для зловмисників. Для критичних сервісів оновлення бази відкликань має транслюватися через швидкі шини повідомлень (In-memory Pub/Sub, Redis Cluster).
- **Помилки локального годинника (Clock Skew) на кінцевих пристроях.** Вбудовані системи часто не мають резервного живлення годинника реального часу (RTC) або доступу до протоколу NTP на старті. Пристрій не повинен самостійно приймати рішення про простроченість сертифікатів на основі власного часу — часова валідація покладається виключно на бекенд.
- **Стратегія поведінки в автономному режимі (Offline Fallback).** Пристрій не повинен блокувати базові локальні функції (наприклад, зчитування датчиків, локальний екран, керування двигунами), якщо мережа відсутня або бекенд недоступний. Відсікання клону стосується виключно захищених хмарних функцій, оновлень ПЗ та фірмової аналітики.
