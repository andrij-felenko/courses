# ⚙️ Розбір та валідація дескрипторів кабелю на C та C++

<preknowlist>
- [USB Power Delivery](topic:electronics/usb-pd) — протокол цифрових переговорів по лінії CC, пакети керування та стани шини.
- [📋 Дескриптори Structured VDM та VDO](topic:electronics/e-marker/api-vdm-descriptors.md) — карти бітових полів, коди команд та числові значення VDO.
- [Кодування BMC у Type-C](topic:electronics/bmc-encoding) — структура кадру, порядок бітів та контроль цілісності CRC-32.
</preknowlist>

Коли контролер порту джерела (DFP) або дворольового пристрою (DRP) завершує аналогове розпізнавання підтяжки `Ra` і подає живлення на шину VCONN, протокольний рушій (*Policy Engine*) ініціює транзакцію опитування кабелю `SOP' Discover Identity`. Фізичний трансивер BMC приймає напівдуплексний цифровий потік, верифікує апаратну контрольну суму CRC-32 і передає у мікропрограмне забезпечення буфер необроблених 32-бітових слів.

Завдання парсера полягає у тому, щоб із сирого масиву бітових полів виділити параметри кабельної збірки, перевірити відповідність стандартам USB-IF і сформувати остаточний безпечний профіль лімітів. Помилка у декодуванні дескриптора неприпустима: якщо мікроконтролер хибно розпізнає 3-амперний кабель як 5-амперний, джерело живлення дозволить споживачу споживати струм 5 А, що за умов тривалого навантаження спричинить небезпечний перегрів тонких мідних жил, оплавлення оболонки та руйнування контактної групи роз'єму.

## Архітектурні вимоги до парсера дескрипторів

При розробці низькорівневого модуля розбору VDO для вбудованих систем необхідно дотримуватися суворих інженерних обмежень:

1. **Відмова від бітових полів компілятора (`bitfields`).** Використання стандартних бітових полів мови C (`struct { unsigned int field : 3; }`) у драйверах зв'язку є небезпечним, оскільки порядок упаковки бітів (*bit-endianness*) та вирівнювання не стандартизовані стандартом ANSI C і залежать від конкретного компілятора (GCC, Clang, IAR, Keil) та архітектури процесора (ARM Cortex-M, RISC-V, Xtensa). Єдиним надійним промисловим підходом є явне зсунення та маскування бітів константами.
2. **Порядок байтів (Little-Endian).** Згідно зі специфікацією USB PD, усі багатобайтові поля в пакетах BMC передаються молодшим байтом уперед. Якщо мікроконтролер працює в іншому порядку байтів, необхідне явне перетворення.
3. **Суворий контроль розміру вхідного буфера.** Відповідь `Discover Identity ACK` повинна містити щонайменше п'ять 32-бітових слів (VDM Header, ID Header, Cert Stat, Product VDO, Cable VDO 1). Доступ до елементів масиву без попередньої перевірки лічильника слів `word_count` створює вразливість виходу за межі пам'яті (*out-of-bounds read*).
4. **Нульове динамічне виділення пам'яті.** Усі структури даних повинні розміщуватися виключно на стеку або у статичній пам'яті, що гарантує детермінований час виконання та унеможливлює фрагментацію купи (*heap fragmentation*) у критичних сценаріях керування живленням.
5. **Асинхронне виконання в операційних системах реального часу (RTOS).** Функція парсера є чистою та ревхідною (*reentrant*), вона не виконує блокувальних очікувань чи звернень до шин вводу/виводу, що дозволяє викликати її як у контексті переривань, так і всередині окремої задачі FreeRTOS чи потоку Zephyr OS.

## Програмна реалізація парсера мовами C та C++

Нижче наведено дві повноцінні, функціонально еквівалентні реалізації парсера: процедурну мовою C (для класичних вбудованих мікроконтролерів без динамічного виділення пам'яті) та об'єктну мовою C++20 (із використанням безпечних зрізів `std::span`, строгих переліків `enum class` та монадичного повернення результатів через `std::expected`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define USBPD_SVID_STANDARD          0xFF00U
#define VDM_TYPE_STRUCTURED          1U
#define VDM_CMD_DISCOVER_IDENTITY    0x01U
#define VDM_CMD_TYPE_ACK             0x01U

#define PROD_TYPE_PASSIVE_CABLE      0x03U
#define PROD_TYPE_ACTIVE_CABLE       0x04U

typedef enum {
    VDM_PARSE_OK = 0,
    VDM_ERR_BUFFER_TOO_SHORT,
    VDM_ERR_INVALID_SVID,
    VDM_ERR_NOT_STRUCTURED,
    VDM_ERR_WRONG_COMMAND,
    VDM_ERR_NOT_ACK,
    VDM_ERR_NOT_A_CABLE,
    VDM_ERR_INVALID_CURRENT_FIELD
} vdm_parse_result_t;

typedef enum {
    CABLE_SPEED_USB2_ONLY = 0,
    CABLE_SPEED_USB32_GEN1,
    CABLE_SPEED_USB32_GEN2_OR_USB4_GEN2,
    CABLE_SPEED_USB4_GEN3,
    CABLE_SPEED_USB4_GEN4,
    CABLE_SPEED_UNKNOWN
} cable_speed_t;

typedef struct {
    uint16_t vid;
    uint16_t pid;
    uint32_t xid;
    uint8_t  hw_version;
    uint8_t  fw_version;
    bool     is_active_cable;
    bool     is_epr_capable;
    uint16_t max_voltage_mv;
    uint16_t max_current_ma;
    cable_speed_t max_speed;
    uint8_t  max_temperature_c;
    bool     has_thermal_sensor;
} cable_descriptor_t;

vdm_parse_result_t vdm_decode_cable_identity(
    const uint32_t *vdo_buffer,
    size_t word_count,
    cable_descriptor_t *out_desc
) {
    if (vdo_buffer == NULL || out_desc == NULL || word_count < 5) {
        return VDM_ERR_BUFFER_TOO_SHORT;
    }

    uint32_t vdm_header = vdo_buffer[0];
    uint16_t svid = (uint16_t)(vdm_header >> 16);
    uint8_t vdm_type = (uint8_t)((vdm_header >> 15) & 0x01U);
    uint8_t cmd_type = (uint8_t)((vdm_header >> 6) & 0x03U);
    uint8_t cmd_code = (uint8_t)(vdm_header & 0x1FU);

    if (svid != USBPD_SVID_STANDARD) {
        return VDM_ERR_INVALID_SVID;
    }
    if (vdm_type != VDM_TYPE_STRUCTURED) {
        return VDM_ERR_NOT_STRUCTURED;
    }
    if (cmd_code != VDM_CMD_DISCOVER_IDENTITY) {
        return VDM_ERR_WRONG_COMMAND;
    }
    if (cmd_type != VDM_CMD_TYPE_ACK) {
        return VDM_ERR_NOT_ACK;
    }

    uint32_t id_header = vdo_buffer[1];
    uint8_t prod_type = (uint8_t)((id_header >> 27) & 0x07U);
    if (prod_type != PROD_TYPE_PASSIVE_CABLE && prod_type != PROD_TYPE_ACTIVE_CABLE) {
        return VDM_ERR_NOT_A_CABLE;
    }

    out_desc->vid = (uint16_t)(id_header & 0xFFFFU);
    out_desc->is_active_cable = (prod_type == PROD_TYPE_ACTIVE_CABLE);
    out_desc->xid = vdo_buffer[2];

    uint32_t prod_vdo = vdo_buffer[3];
    out_desc->pid = (uint16_t)(prod_vdo >> 16);

    uint32_t cable_vdo1 = vdo_buffer[4];
    out_desc->hw_version = (uint8_t)((cable_vdo1 >> 28) & 0x0FU);
    out_desc->fw_version = (uint8_t)((cable_vdo1 >> 24) & 0x0FU);

    uint8_t volt_bits = (uint8_t)((cable_vdo1 >> 17) & 0x03U);
    switch (volt_bits) {
        case 0x00: out_desc->max_voltage_mv = 20000; break;
        case 0x01: out_desc->max_voltage_mv = 30000; break;
        case 0x02: out_desc->max_voltage_mv = 40000; break;
        case 0x03: out_desc->max_voltage_mv = 50000; break;
    }

    uint8_t curr_bits = (uint8_t)((cable_vdo1 >> 5) & 0x03U);
    if (curr_bits == 0x01) {
        out_desc->max_current_ma = 3000;
    } else if (curr_bits == 0x02) {
        out_desc->max_current_ma = 5000;
    } else {
        return VDM_ERR_INVALID_CURRENT_FIELD;
    }

    uint8_t speed_bits = (uint8_t)(cable_vdo1 & 0x07U);
    switch (speed_bits) {
        case 0x00: out_desc->max_speed = CABLE_SPEED_USB2_ONLY; break;
        case 0x01: out_desc->max_speed = CABLE_SPEED_USB32_GEN1; break;
        case 0x02: out_desc->max_speed = CABLE_SPEED_USB32_GEN2_OR_USB4_GEN2; break;
        case 0x03: out_desc->max_speed = CABLE_SPEED_USB4_GEN3; break;
        case 0x04: out_desc->max_speed = CABLE_SPEED_USB4_GEN4; break;
        default:   out_desc->max_speed = CABLE_SPEED_UNKNOWN; break;
    }

    out_desc->is_epr_capable = (out_desc->max_voltage_mv >= 50000 && out_desc->max_current_ma == 5000);
    out_desc->max_temperature_c = 0;
    out_desc->has_thermal_sensor = false;

    if (word_count >= 6) {
        uint32_t cable_vdo2 = vdo_buffer[5];
        out_desc->max_temperature_c = (uint8_t)((cable_vdo2 >> 24) & 0xFFU);
        uint8_t thermal_sensor = (uint8_t)((cable_vdo2 >> 12) & 0x0FU);
        out_desc->has_thermal_sensor = (thermal_sensor != 0);

        uint8_t epr_flag = (uint8_t)((cable_vdo2 >> 8) & 0x0FU);
        if (epr_flag == 0x01) {
            out_desc->is_epr_capable = true;
            out_desc->max_voltage_mv = 50000;
        }
    }

    return VDM_PARSE_OK;
}
```
```cpp
#include <cstdint>
#include <span>
#include <expected>
#include <string_view>

namespace usbpd {

inline constexpr uint16_t SVID_STANDARD = 0xFF00U;

enum class ParseError {
    BufferTooShort,
    InvalidSvid,
    NotStructuredVdm,
    WrongCommand,
    NotAck,
    NotACable,
    InvalidCurrentField
};

enum class Speed : uint8_t {
    Usb2Only,
    Usb32Gen1,
    Usb32Gen2OrUsb4Gen2,
    Usb4Gen3,
    Usb4Gen4,
    Unknown
};

struct CableDescriptor {
    uint16_t vid{0};
    uint16_t pid{0};
    uint32_t xid{0};
    uint8_t  hw_version{0};
    uint8_t  fw_version{0};
    bool     is_active{false};
    bool     is_epr_capable{false};
    uint16_t max_voltage_mv{20000};
    uint16_t max_current_ma{3000};
    Speed    speed{Speed::Usb2Only};
    uint8_t  max_temperature_c{0};
    bool     has_thermal_sensor{false};

    [[nodiscard]] constexpr std::string_view speed_string() const noexcept {
        switch (speed) {
            case Speed::Usb2Only:             return "USB 2.0 (480 Mbps)";
            case Speed::Usb32Gen1:            return "USB 3.2 Gen1 (5 Gbps)";
            case Speed::Usb32Gen2OrUsb4Gen2:  return "USB 3.2 Gen2 / USB4 Gen2 (10 Gbps)";
            case Speed::Usb4Gen3:             return "USB4 Gen3 (40 Gbps)";
            case Speed::Usb4Gen4:             return "USB4 Gen4 (80/120 Gbps)";
            default:                          return "Unknown";
        }
    }
};

[[nodiscard]] constexpr std::expected<CableDescriptor, ParseError> decode_cable_identity(
    std::span<const uint32_t> vdo_buffer
) noexcept {
    if (vdo_buffer.size() < 5) {
        return std::unexpected(ParseError::BufferTooShort);
    }

    const uint32_t vdm_header = vdo_buffer[0];
    const auto svid = static_cast<uint16_t>(vdm_header >> 16);
    const auto vdm_type = static_cast<uint8_t>((vdm_header >> 15) & 0x01U);
    const auto cmd_type = static_cast<uint8_t>((vdm_header >> 6) & 0x03U);
    const auto cmd_code = static_cast<uint8_t>(vdm_header & 0x1FU);

    if (svid != SVID_STANDARD) {
        return std::unexpected(ParseError::InvalidSvid);
    }
    if (vdm_type != 1U) {
        return std::unexpected(ParseError::NotStructuredVdm);
    }
    if (cmd_code != 0x01U) {
        return std::unexpected(ParseError::WrongCommand);
    }
    if (cmd_type != 0x01U) {
        return std::unexpected(ParseError::NotAck);
    }

    const uint32_t id_header = vdo_buffer[1];
    const auto prod_type = static_cast<uint8_t>((id_header >> 27) & 0x07U);
    if (prod_type != 0x03U && prod_type != 0x04U) {
        return std::unexpected(ParseError::NotACable);
    }

    CableDescriptor desc{};
    desc.vid = static_cast<uint16_t>(id_header & 0xFFFFU);
    desc.is_active = (prod_type == 0x04U);
    desc.xid = vdo_buffer[2];

    const uint32_t prod_vdo = vdo_buffer[3];
    desc.pid = static_cast<uint16_t>(prod_vdo >> 16);

    const uint32_t cable_vdo1 = vdo_buffer[4];
    desc.hw_version = static_cast<uint8_t>((cable_vdo1 >> 28) & 0x0FU);
    desc.fw_version = static_cast<uint8_t>((cable_vdo1 >> 24) & 0x0FU);

    const auto volt_bits = static_cast<uint8_t>((cable_vdo1 >> 17) & 0x03U);
    switch (volt_bits) {
        case 0x00: desc.max_voltage_mv = 20000; break;
        case 0x01: desc.max_voltage_mv = 30000; break;
        case 0x02: desc.max_voltage_mv = 40000; break;
        case 0x03: desc.max_voltage_mv = 50000; break;
    }

    const auto curr_bits = static_cast<uint8_t>((cable_vdo1 >> 5) & 0x03U);
    if (curr_bits == 0x01) {
        desc.max_current_ma = 3000;
    } else if (curr_bits == 0x02) {
        desc.max_current_ma = 5000;
    } else {
        return std::unexpected(ParseError::InvalidCurrentField);
    }

    const auto speed_bits = static_cast<uint8_t>(cable_vdo1 & 0x07U);
    switch (speed_bits) {
        case 0x00: desc.speed = Speed::Usb2Only; break;
        case 0x01: desc.speed = Speed::Usb32Gen1; break;
        case 0x02: desc.speed = Speed::Usb32Gen2OrUsb4Gen2; break;
        case 0x03: desc.speed = Speed::Usb4Gen3; break;
        case 0x04: desc.speed = Speed::Usb4Gen4; break;
        default:   desc.speed = Speed::Unknown; break;
    }

    desc.is_epr_capable = (desc.max_voltage_mv >= 50000 && desc.max_current_ma == 5000);

    if (vdo_buffer.size() >= 6) {
        const uint32_t cable_vdo2 = vdo_buffer[5];
        desc.max_temperature_c = static_cast<uint8_t>((cable_vdo2 >> 24) & 0xFFU);
        const auto thermal_sensor = static_cast<uint8_t>((cable_vdo2 >> 12) & 0x0FU);
        desc.has_thermal_sensor = (thermal_sensor != 0);

        const auto epr_flag = static_cast<uint8_t>((cable_vdo2 >> 8) & 0x0FU);
        if (epr_flag == 0x01) {
            desc.is_epr_capable = true;
            desc.max_voltage_mv = 50000;
        }
    }

    return desc;
}

} // namespace usbpd
```
:::

## Покроковий розбір логіки та обробки критичних станів

Розроблений алгоритм реалізує послідовну фільтрацію та багаторівневу перевірку коректності отриманих даних:

1. **Валідація типу протоколу та SVID.** Парсер перевіряє, що у старших двох байтах першого слова встановлено значення `0xFF00`. Будь-які запити з іншими SVID (наприклад, вендорними `0x04B4` або `0x1057`) не повинні оброблятися цим парсером, оскільки їхній внутрішній формат визначається закритими специфікаціями виробників.
2. **Перевірка адресата (`Product Type`).** Біти B29..B27 у дескрипторі `ID Header VDO` повинні строго містити значення `011b` (пасивний кабель) або `100b` (активний кабель). Якщо пристрій на іншому кінці помилково надіслав у відповідь дескриптор концентратора (*Hub*) чи периферійного пристрою (*UFP/Device*), функція повертає помилку `VDM_ERR_NOT_A_CABLE`.
3. **Контроль заборонених бітових комбінацій струму.** У полі `VBUS Current Capability` значення `00b` та `11b` зарезервовані консорціумом USB-IF. Якщо мікросхема повертає такі біти, це свідчить про пошкодження пам'яті OTP або збій шини даних. Функція миттєво повертає статус `VDM_ERR_INVALID_CURRENT_FIELD`, унеможливлюючи довільне тлумачення струму.
4. **Двофакторна верифікація режиму EPR 240 Вт.** Прапорець `is_epr_capable` активується лише тоді, коли кабель одночасно декларує підтримку напруги 50 В (у бітах B18..B17 дескриптора `Cable VDO 1` або у бітах B11..B8 дескриптора `Cable VDO 2`) та максимальний струм 5 А (значення `10b` у бітах B6..B5). Якщо напруга становить 50 В, але струм обмежено 3 А, або навпаки — струм 5 А, але напруга лише 20 В, режим EPR не дозволяється.
5. **Інтеграція в кінцевий автомат Policy Engine.** Отриманий після виконання функції об'єкт `cable_descriptor_t` передається безпосередньо у планувальник силових контрактів джерела. Якщо `max_current_ma == 3000`, джерело відкидає всі силові об'єкти даних (PDO), що вимагають 5 А, і обмежує список доступних профілів у пакеті `Source_Capabilities` безпечним рівнем 60 Вт (20 В / 3 А).

## Взаємодія з апаратними регістрами контролера порту (TCPCI)

У сучасних вбудованих архітектурах фізичний рівень реалізується окремою мікросхемою контролера порту (*Type-C Port Controller*, TCPC — наприклад, Texas Instruments TPS65987, ON Semiconductor FUSB302 або NXP PTN5110), яка підключається до головного мікроконтролера (*Type-C Port Manager*, TCPM) через шину I2C за стандартним інтерфейсом TCPCI (*Type-C Port Controller Interface Specification*).

Процес відправки запиту `Discover Identity` та вичитування дескрипторів складається з таких апаратних кроків:

1. **Конфігурація передавача TCPC.** Головний мікроконтролер записує у регістр `TRANSMIT` (адреса `0x50`) команду передачі кадру з типом маркування `SOP'` (значення поля `TRANSMIT = 0x01` для SOP_PRIME).
2. **Завантаження корисного навантаження.** У вихідний буфер передачі `TX_BUFFER` (адреса `0x51`) записується 16-бітовий заголовок повідомлення PD Header (де прапорець `NumDataObjects` встановлюється в `1`, тип повідомлення — `Structured VDM`), а слідом за ним — 32-бітове слово заголовка `VDM Header` (`0xFF008001`, де `Command = 0x01` / Discover Identity).
3. **Очікування апаратного переривання.** Після відправки пакета мікроконтролер переводить свій кінцевий автомат у стан очікування переривання від лінії `ALERT` (вивід низького рівня активності). При отриманні відповіді від чипа E-Marker контролер TCPC генерує переривання та встановлює біт `ReceiveSOPPrimeMessage` у регістрі `ALERT` (адреса `0x10`).
4. **Вичитування результату.** Драйвер TCPM зчитує лічильник прийнятих байтів із регістра `RX_BYTE_CNT` (адреса `0x30`) та копіює прийняті 32-бітові слова даних безпосередньо у буфер `vdo_buffer`, після чого викликає функцію `vdm_decode_cable_identity()`.

## Керування таймерами та обробка виняткових станів

Обмін повідомленнями VDM підпорядковується суворим часовим рамкам реального часу. Під час очікування відповіді на запит `SOP' Discover Identity` мікроконтролер запускає апаратний таймер `tVDMResponse` з лімітом 30 мс:

- **Таймаут відповіді (30 мс):** Якщо за 30 мс лінія `ALERT` не сигналізувала про надходження кадру, лічильник повторів `retry_counter` збільшується на одиницю. Після трьох невдалих спроб (`nCapsCount = 3`) порт фіксує статус «кабель без маркера» і переходить до надсилання профілів `Source_Capabilities` зі струмом не більше 3 А.
- **Отримання негативної відповіді (`NAK`):** Якщо кабель відповів кадром `NAK` (наприклад, старий кабель стандарту USB PD 2.0, який не підтримує запит у версії VDM 2.0), стек виконує повторний запит у режимі сумісності зі структурою VDM 1.0.
- **Отримання статусу зайнятості (`BUSY`):** Якщо чип E-Marker повертає статус `BUSY` (через калібрування внутрішнього АЦП або затримку завантаження з OTP), стек призупиняє опитування на інтервал `tVDMBusy` (50 мс) і повторює запит пізніше, не обриваючи силове з'єднання.

## Розширення для аналізу альтернативних режимів (Alternate Modes)

Універсальність розробленого парсера дозволяє легко адаптувати його для вичитування дескрипторів альтернативних режимів. Після успішного виконання `Discover Identity` стек надсилає запит `SOP' Discover SVIDs` для отримання переліку протоколів, підтримуваних кабелем.

Якщо відповідь містить SVID `0xFF01` (VESA DisplayPort), стек викликає підпроцедуру `Discover Modes`, яка зчитує 32-бітовий дескриптор `DisplayPort Cable VDO`:

- Біти **B2..B0 (`DP Signalling Rate`):** `001b` — DP 1.4 HBR3 (8.1 Гбіт/с); `010b` — DP 2.1 UHBR10 (10 Гбіт/с); `011b` — DP 2.1 UHBR20 (20 Гбіт/с);
- Біти **B9..B8 (`Cable Type`):** `00b` — пасивний мідний кабель; `01b` — активний кабель із лінійним редрайвером; `10b` — оптичний кабель із повною гальванічною розв'язкою;
- Біти **B17..B16 (`Pin Assignment`):** декларують підтримку розкладок контактів `Pin Assignment C` (повні 4 канали DisplayPort для передачі відеопотоку 8K) або `Pin Assignment D` (гібридний режим: 2 канали відео 4K плюс двонапрямний потік USB 3.2 Gen2 зі швидкістю 10 Гбіт/с).

Ця інформація передається у відеопідсистему комп'ютера (GPU Display Engine), що дозволяє динамічно обрати роздільну здатність екрана без ризику артефактів чи зриву синхронізації.

## Динамічний розподіл потужності у багатопортових зарядних станціях

У сучасних багатопортових мережевих зарядних пристроях на основі GaN-транзисторів (наприклад, 2×USB-C потужністю 100–240 Вт) парсер дескрипторів відіграє вирішальну роль в алгоритмах динамічного розподілу потужності (*Smart Power Sharing*):

1. Кожен порт має власний незалежний екземпляр кінцевого автомата Policy Engine.
2. При підключенні навантаження до Порту 1 парсер перевіряє кабель: якщо виявлено 5-амперний кабель EPR, порт резервує в загальному енергетичному бюджеті станції 140 Вт (28 В / 5 А).
3. Якщо на Порт 2 згодом підключають другий пристрій зі звичайним 3-амперним кабелем, парсер повідомляє про ліміт 60 Вт (20 В / 3 А). Головний супервізор станції перераховує доступний баланс потужності (140 Вт + 60 Вт = 200 Вт із загальних 240 Вт) і безконфліктно оновлює `Source_Capabilities` на обох портах, запобігаючи спрацьовуванню захисту від перевантаження загального первинного перетворювача.

## Енергозбереження та вимкнення VCONN у сплячому режимі

У портативних пристроях із живленням від акумулятора (павербанки, планшети, смартфони) утримання активної лінії VCONN створює постійне паразитне споживання струму близько 5–15 мА (25–75 мВт потужності).

Для оптимізації автономності протокольний рушій застосовує алгоритм динамічного керування живленням маркера (*VCONN Power Gating*):
1. Одразу після підключення кабель опитується один раз, і його паспортний дескриптор зберігається в оперативній пам'яті порту `current_cable_desc`.
2. Якщо узгоджений контракт не вимагає високих струмів (наприклад, пристрій споживає стандартні 5 В / 0.9 А або перебуває в режимі очікування USB Suspend), контролер порту може тимчасово зняти напругу 5 В із піна VCONN.
3. Перед будь-якою зміною контракту або переходом на режим підвищеної потужності контролер завчасно відновлює живлення VCONN за 10 мс до надсилання нових пакетів переговорів.

## Налагоджувальний інтерфейс та логування телеметрії (CLI)

Для інженерної діагностики під час лабораторних випробувань та налагодження прошивки мікроконтролера модуль декодера зазвичай інтегрується з інтерфейсом командного рядка (CLI) через UART або віртуальний COM-порт.

При введенні налагоджувальної команди `usbpd cable show` діагностичний модуль транслює поля структури `cable_descriptor_t` у зручний людинозчитуваний формат:

```
[USB-PD Port 1 Cable Telemetry]:
  * Vendor ID (VID)       : 0x04B4 (Infineon / Cypress)
  * Product ID (PID)      : 0x1234
  * Test ID (XID)         : 0x00001A2B (USB-IF Compliance Passed)
  * Hardware / FW Rev     : HW: 1, FW: 0
  * Cable Architecture    : Passive Copper Assembly
  * Current Limit         : 5000 mA (5.0 A High-Current Cable)
  * Voltage Rating        : 50000 mV (50 V EPR Capable)
  * Max Safe Power        : 240 W (48 V @ 5 A)
  * Signal Bandwidth      : USB4 Gen3 (40 Gbps Bi-directional)
  * Max Operating Temp    : 105 °C (Thermal Sensor Active in Plug 1)
```

Така прозора телеметрія дозволяє розробникам швидко верифікувати коректність монтажу контактів Paddle Card, перевірити якість прошивки OTP-пам'яті E-Marker та виключити аномалії узгодження контрактів під час сертифікаційних випробувань.

## Практичний розбір лабораторних дампів протоколу

Для всебічної перевірки стійкості алгоритму розглянемо чотири контрольні сценарії дампів, зафіксованих апаратним аналізатором шини:

### Сценарій 1: Сертифікований кабель USB4 240 Вт (EPR)

```
[SOP' Discover Identity ACK Raw Buffer]:
Word 0 (VDM Header)  : 0xFF008041  -> SVID: 0xFF00, Structured VDM 2.0, ACK, Cmd: 0x01
Word 1 (ID Header)   : 0x180004B4  -> Passive Cable, USB-C to USB-C, VID: 0x04B4 (Cypress)
Word 2 (Cert Stat)   : 0x00001A2B  -> XID: 0x00001A2B (Офіційний сертифікат USB-IF)
Word 3 (Product VDO) : 0x12340100  -> PID: 0x1234, Ревізія: v1.0
Word 4 (Cable VDO 1) : 0x10060043  -> Latency <10ns, 50V Max, 5A Max, USB4 Gen3 (40 Gbps)
Word 5 (Cable VDO 2) : 0x69001100  -> Max Temp: 105°C, Термодатчик у Штекері 1, EPR=1
```

Результат розбору: функція повертає `VDM_PARSE_OK`. Поля `max_voltage_mv = 50000`, `max_current_ma = 5000`, `is_epr_capable = true`, `has_thermal_sensor = true`. Джерело дозволяє активацію профілів 140 Вт, 180 Вт та 240 Вт.

### Сценарій 2: Пасивний кабель 100 Вт SPR (USB 3.2 Gen2, 20 В / 5 А)

```
[SOP' Discover Identity ACK Raw Buffer]:
Word 0 (VDM Header)  : 0xFF008041  -> SVID: 0xFF00, Structured VDM 2.0, ACK
Word 1 (ID Header)   : 0x180005AC  -> Passive Cable, VID: 0x05AC (Apple Inc.)
Word 2 (Cert Stat)   : 0x000045F1  -> XID: 0x000045F1
Word 3 (Product VDO) : 0x02010100  -> PID: 0x0201, Ревізія: v1.0
Word 4 (Cable VDO 1) : 0x00000042  -> Latency <10ns, 20V Max (SPR), 5A Max, USB 3.2 Gen2 (10 Gbps)
```

Результат розбору: функція повертає `VDM_PARSE_OK`. Значення `max_voltage_mv = 20000`, `max_current_ma = 5000`, `is_epr_capable = false`. Джерело дозволяє 100-ватні профілі живлення (20 В / 5 А), проте повністю блокує видачу високовольтних щаблів EPR (28 В, 36 В, 48 В).

### Сценарій 3: Кабель без електронного маркера (Timeout)

Якщо користувач підключає стандартний недорогий кабель без мікросхеми E-Marker, спроба надсилання запиту `SOP' Discover Identity` завершується апаратним таймаутом `tVDMResponse` (30 мс). Керівний стек фіксує відсутність відповіді та формує базовий безпечний дескриптор за замовчуванням:
- `max_voltage_mv = 20000` (20 В);
- `max_current_ma = 3000` (3 А);
- `max_speed = CABLE_SPEED_USB2_ONLY` (480 Мбіт/с);
- `is_epr_capable = false`.

### Сценарій 4: Фальсифікований або пошкоджений кабель

```
[SOP' Discover Identity ACK Raw Buffer]:
Word 0 (VDM Header)  : 0xFF008041  -> SVID: 0xFF00, Structured, ACK
Word 1 (ID Header)   : 0x18000000  -> Passive Cable, Невідомий VID: 0x0000
Word 2 (Cert Stat)   : 0x00000000  -> XID: 0 (Сертифікація відсутня)
Word 3 (Product VDO) : 0x00000000  -> PID: 0
Word 4 (Cable VDO 1) : 0x00000060  -> Помилка: біти струму B6..B5 встановлені в 11b (Заборонено!)
```

Результат розбору: функція виявляє заборонену комбінацію бітів струму `11b` і повертає код помилки `VDM_ERR_INVALID_CURRENT_FIELD`. Менеджер політики негайно блокує видачу струму 5 А і переводить інтерфейс у безпечний режим 5 В / 3 А, усуваючи ризик аварії.

## Модульне тестування алгоритму (Unit Testing)

Для забезпечення безвідмовної роботи вбудованого ПЗ стек тестується за допомогою ізольованого тестового набору (*Test Harness*), що перевіряє реакцію алгоритму на всі види спотворень вхідних даних:

1. **Тест нульового вказівника та нульового розміру буфера.** Виклик `vdm_decode_cable_identity(NULL, 0, &desc)` повинен негайно повертати `VDM_ERR_BUFFER_TOO_SHORT`, не викликаючи апаратного виключення ядра (*HardFault / Segmentation Fault*).
2. **Тест обрізаного буфера.** Передача масивів розміром 1, 2, 3 та 4 слова перевіряє коректність роботи захисного бар'єра довжини.
3. **Тест вендорного SVID.** Передача слова заголовка з SVID `0x1234` перевіряє ізоляцію стандартного парсера від чужих протокольних розширень.
4. **Тест заборонених значень струму.** Почергова передача буферів із бітами струму `00b` та `11b` підтверджує захист від несертифікованих або пошкоджених мікросхем.
5. **Тест сумісності з розширенням PD 3.1.** Перевірка правильної обробки буферів із 5 словами (формат PD 3.0 без Cable VDO 2) та з 6 словами (формат PD 3.1 із розширеними полями EPR).

Така модульна архітектура гарантує цілісність енергетичної політики контролера в реальних умовах промислової експлуатації та захищає споживачів від аварійних ситуацій.

У промисловому циклі розробки прошивок цей набір модульних тестів інтегрується в систему неперервної інтеграції (CI/CD). Будь-яка зміна у протокольному рушії автоматично верифікується на тестових векторах стандартних кабелів SPR, EPR 240 Вт та навмисно спотворених пакетів, що повністю унеможливлює потрапляння регресійних помилок у серійні пристрої.

