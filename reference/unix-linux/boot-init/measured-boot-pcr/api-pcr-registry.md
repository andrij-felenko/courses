# 📋 Довідник розподілу регістрів PCR у специфікації TCG PC Client

Цей довідник містить повну специфікацію розподілу Platform Configuration Registers (PCR) для архітектури PC Client, регламентовану консорціумом Trusted Computing Group (TCG), а також розширення, прийняті в екосистемі Linux (systemd та IMA). Він необхідний системним інженерам та розробникам засобів захисту для точного проектування політик запечатування ключів (Sealing Policies) та аналізу журналів вимірюваного завантаження.

Принцип роботи PCR базується на фіксованому розподілі обов'язків між ланками завантаження. Кожна ланка відповідає за вимірювання строго визначеної підмножини регістрів. Порушення цієї послідовності або спроба оновити "чужий" регістр призводить до розходження підсумкового хешу та відмови у видачі ключів шифрування.

## Стандартний розподіл регістрів PCR (0–15)

Згідно зі специфікацією TCG PC Client Specific Platform Firmware Profile Specification, перші 16 регістрів PCR є стаційними (Static Root of Trust for Measurement, SRTM) і заповнюються послідовно на етапах ініціалізації прошивки, завантажувача та операційної системи.

| Номер PCR | Стандартна назва TCG | Що саме вимірюється в регістр | Компонент, який виконує `Extend` |
|---|---|---|---|
| **PCR 0** | Core Root of Trust for Measurement (CRTM), BIOS Code | Код базової прошивки (CRTM), головний модуль UEFI/BIOS, оновлення мікрокоду процесора (CPU Microcode), системна плата ROM. | CRTM / UEFI Firmware |
| **PCR 1** | Platform Configuration | Налаштування прошивки, таблиці SMBIOS, конфігурація обладнання, енергонезалежні змінні налаштувань плати. | UEFI Firmware |
| **PCR 2** | Option ROM Code | Код розширень адаптерів (Option ROM): EFI-драйвери відеокарт, мережевих карт, RAID-контролерів. | UEFI Firmware / Driver Execution Environment (DXE) |
| **PCR 3** | Option ROM Configuration | Конфігурація та дані налаштувань Option ROM адаптерів. | UEFI Firmware / DXE |
| **PCR 4** | Boot Manager Code | Код завантажувача операційної системи: MBR/VBR або виконуваний файл UEFI Boot Manager (`bootx64.efi`, `grubx64.efi`, `systemd-boot`). | UEFI Boot Manager |
| **PCR 5** | Boot Manager Data | Дані завантажувача: таблиця розділів диска (GPT), змінні завантаження UEFI (`BootOrder`, `BootNext`, `Boot0000`). | UEFI Boot Manager |
| **PCR 6** | State Transitions | Події зміни стану системи: вихід із режимів енергозбереження S3 (Suspend-to-RAM) та S4 (Hibernate). | UEFI Firmware / ACPI |
| **PCR 7** | Secure Boot Policy | Політика та стан Secure Boot: вміст баз ключів `PK`, `KEK`, `db`, `dbx`, а також статус увімкнення `SecureBoot`. | UEFI Firmware |
| **PCR 8** | OS / Bootloader Specific (GRUB Cmdline) | Командний рядок ядра Linux (`/proc/cmdline`), сформований класичним завантажувачем (GRUB/LILO), текстові конфігурації. | GRUB / systemd-boot |
| **PCR 9** | OS / Bootloader Specific (Initramfs) | Вміст та цілісність початкового образу операційної системи у пам'яті (`initrd` / `initramfs`). | GRUB / systemd-boot |
| **PCR 10** | IMA (Integrity Measurement Architecture) | Журнал вимірювання файлів у просторі користувача: виконувачі бінарники, динамічні бібліотеки, скрипти. | Підсистема Linux Kernel IMA |
| **PCR 11** | Unified Kernel Image (systemd-stub) | Комбінований виміряний завантажувачем `systemd-stub` образ UKI: ядро, initrd, cmdline, os-release, splash-екран. | systemd-stub / UKI |
| **PCR 12** | systemd Credentials / Add-ons | Додаткові аргументи ядра, сформовані завантажувачем, зашифровані облікові дані systemd (Credentials), devicetree розширення. | systemd-boot / systemd-stub |
| **PCR 13** | systemd System Extensions (sysext) | Образи розширень системи `systemd-sysext` та накладені файлові системи `/usr` / `/opt`. | systemd-sysext |
| **PCR 14** | systemd Portable Services | Образи портативних служб `systemd-portabled` та конфігураційні накладання. | systemd-portabled |
| **PCR 15** | Application / System Specific | Резервний регістр для системних застосувань та користувацьких служб локальної атестації. | Простір користувача |

## Детальний опис груп регістрів та їхніх функціональних особливостей

### Група апаратури та прошивки (PCR 0–3)

Регістри з 0 по 3 перебувають під повним контролем прошивки UEFI материнської плати. Звичайний завантажувач чи операційна система не можуть запобігти зміні цих регістрів, якщо на материнській платі оновився BIOS або додалася нова відеокарта.

- **PCR 0 (Код прошивки):** Будь-яке оновлення BIOS, прошивки контролера Intel ME / AMD PSP або патчів мікрокоду процесора змінює PCR 0. Якщо ваша політика LUKS2 запечатана на PCR 0, після Flash оновлення материнської плати диск вимагатиме пароль відновлення.
- **PCR 1 (Конфігурація прошивки):** Зміна налаштувань у меню BIOS (наприклад, увімкнення/вимкнення послідовного порту, зміна режиму SATA з AHCI на RAID або редагування SMBIOS) змінює значення PCR 1.
- **PCR 2 та 3 (Option ROM):** Збереження відбитків коду та конфігурації додаткових плат розширення PCI Express. Наприклад, додавання нової дискової плати з власним RAID-контролером або відеокарти з EFI-драйвером модифікує PCR 2.

### Група завантаження та Secure Boot (PCR 4–7)

Регістри цієї групи відповідають за зв'язок між прошивкою плати та завантажувачем ОС на диску:

- **PCR 4 (Завантажувальний код):** Вимірює хеш першого виконуваного файлу на EFI System Partition (ESP), наприклад `/EFI/BOOT/BOOTX64.EFI` або `/EFI/systemd/systemd-bootx64.efi`.
- **PCR 5 (Дані завантажувача):** Фіксує структуру таблиці розділів GPT диска. Якщо перерозмітити диск або додати новий розділ, PCR 5 зміниться, навіть якщо самі завантажувальні файли лишилися недоторканими.
- **PCR 7 (Політика Secure Boot):** Найбільш критичний регістр для запечатування дискових ключів. Він вимірює вміст змінних `PK` (Platform Key), `KEK`, `db` (дозволені сертифікати), `dbx` (список заборон) та прапорець увімкнення Secure Boot. Якщо Secure Boot вимкнути в меню BIOS, PCR 7 змінить своє значення, що запобігає розшифруванню диска при спробі обходу перевірки підписів.

### Група операційної системи та systemd (PCR 8–15)

Ці регістри використовуються компонентами завантажувача Linux та операційною системою:

- **PCR 8 та 9 (Класичний завантажувач GRUB):** GRUB2 виконує вимірювання текстового рядка параметрів ядра у PCR 8 та архіву початкової файлової системи initramfs у PCR 9. Оскільки оновлення ядра змінює initramfs, ці регістри є вкрай ламкими при авто-оновленнях.
- **PCR 10 (IMA):** Використовується підсистемою ядра Linux Integrity Measurement Architecture. Кожен виконуваний файл у просторі користувача перед запуском вимірюється і розширює PCR 10.
- **PCR 11 (Unified Kernel Image, UKI):** Впроваджений завантажувачем `systemd-stub`. Замість вимірювання окремих частин у PCR 8 і 9, `systemd-stub` вимірює єдиний контейнер UKI (що об'єднує ядро, initramfs, cmdline та os-release) у PCR 11. Це дозволяє створювати стабільні підписані політики запечатування.

## Динамічні регістри PCR (16–23)

Регістри з 16 по 23 використовуються для технологій динамічного кореня довіри (Dynamic Root of Trust for Measurement, DRTM), таких як Intel TXT (Trusted Execution Technology) або AMD SKINIT, а також для розмежування рівнів доступу (Locality).

| Номер PCR | Назва / Призначення | Опис механізму |
|---|---|---|
| **PCR 16** | Debug / Local Testing | Власні вимірювання операційної системи та налагоджувальних утиліт. Може скидатися без перезавантаження (скидання Locality). |
| **PCR 17** | DRTM Details (Intel TXT / AMD SKINIT) | Фіксує вимірювання модуля пізньої ініціалізації (SINIT ACM / SKINIT code), що запускає захищене середовище ізоляції. |
| **PCR 18** | DRTM Environment & Policy | Вимірювання конфігурації безпечного середовища гипервізора або захищеного ядра (SMM, Trusted OS). |
| **PCR 19** | DRTM Control Authority | Ідентифікатор органу авторизації, що підписав модуль DRTM. |
| **PCR 20** | DRTM Kernel / Hypervisor | Вимірювання завантаженого через DRTM гіпервізора (Xen, KVM) або безпечного ядра (Secure Kernel). |
| **PCR 21** | DRTM OS State | Стан конфігурації захищеного операційного середовища. |
| **PCR 22** | DRTM Reserved | Резервний регістр специфікацій TCG DRTM. |
| **PCR 23** | Application Specific / Locality 4 | Використовується виключно спеціалізованими апаратними агентами безпеки з високим рівнем привілеїв Locality. |

## Банки криптографічних алгоритмів (PCR Banks)

У специфікації TPM 2.0 один і той самий номер PCR існує паралельно у кількох незалежних **банках хешування** (PCR Banks). Кожен банк відповідає за власний криптографічний алгоритм:

- **SHA-1 Bank**: Застарілий 160-бітний банк (підтримується для зворотної сумісності з TPM 1.2, не рекомендований для безпечних політик).
- **SHA-256 Bank**: Стандартний 256-бітний банк сучасних систем Linux та Windows. Основний вибір для запечатування ключів LUKS2.
- **SHA-384 Bank**: 384-бітний банк підвищеної стійкості (використовується у корпоративних прошивках та криптографії CNSA/Suite B).
- **SM3-256 Bank**: 256-бітний банк на основі китайського национального криптографічного стандарту SM3.

При виконанні команди `TPM2_Extend` компонент може передавати хеш одночасно у кілька банків. Якщо прошивка обчислює SHA-256 та SHA-384, вона оновлює відповідні осередки обох банків паралельно за один виклик чипа.

Сучасні дистрибутиви Linux орієнтуються на використання банку SHA-256, оскільки він забезпечує оптимальний баланс обчислювальної швидкості та криптографічної стійкості до сучасних атак.

## Апаратна та логічна структура PCR у TPM 2.0

З погляду внутрішньої архітектури чипа TPM 2.0, регістри PCR є спеціалізованою осередковою пам'яттю, розміщеною у поєднанні енергозалежної оперативної пам'яті (Volatile RAM) та незмінного криптографічного процесорного ядра. Кожен PCR є не просто масивом байтів, а специфічною структурою даних, зв'язаною з атрибутами безпеки та привілеями доступу.

### Локальності доступу (Locality Levels 0–4)

Взаємодія з регістрами PCR контролюється апаратним механізмом **Locality** (рівні локальності). Рівень локальності визначається фізичними сигналами шини (LPC/SPI) або апаратними реєстрами шини MMIO, через які процесор зв'язується з чипом TPM:

- **Locality 0**: Стандартний рівень доступу для операційної системи, завантажувача та програм простору користувача. Усі звичайні команди `TPM2_PCR_Extend` виконуються на цьому рівні.
- **Locality 1**: Призначено для високопривілейованих компонентів прошивки або операційної системи.
- **Locality 2**: Призначено для ізольованих середовищ виконання, завантаження безпечного ядра або програмних гіпервізорів.
- **Locality 3**: Використовується модулями апаратного запуска DRTM (Intel TXT ACM, AMD SKINIT). Команда `GETSEC[SENTER]` або `SKINIT` перемикає апаратуру на Locality 3.
- **Locality 4**: Найвищий привілейований апаратний рівень. Доступний виключно мікрокоду процесора (CPU Microcode) та прошивці System Management Mode (SMM). Тільки з Locality 4 можливе виконання скидання певних DRTM регістрів (наприклад, PCR 17–22).

### Структури специфікації TCG для масивів PCR

У специфікації TCG TPM 2.0 для вибірки та маніпуляції декількома PCR застосовуються базові типи даних:

- `TPMS_PCR_SELECTION`: Визначає алгоритм банку (`hashAlg`, наприклад `TPM2_ALG_SHA256`) та бітову маску обираних регістрів (`pcrSelect`).
- `TPML_PCR_SELECTION`: Масив структур `TPMS_PCR_SELECTION`, який дозволяє вибрати регістри з кількох банків одночасно в рамках однієї командної транзакції (наприклад, PCR 0, 4, 7 в банку SHA-256 і PCR 0, 7 в банку SHA-384).

При старті системи (Power-On Reset) чип TPM ініціалізує регістри Static Root of Trust (PCR 0–15) нульовими значеннями (`0x0000...00`), тоді як окремі регістри DRTM (наприклад, PCR 17–22) можуть ініціалізуватися байтами `0xFFFF...FF`.

## Протокол вимірювання TCG та атомарність операції TPM2_PCR_Extend

Процес накопичення вимірювань у PCR регулюється криптографічним інваріантом однонаправленої акумуляції. Головна команда оновлення — `TPM2_PCR_Extend`.

### Атомарне оновлення банків

Коли центральний процесор відправляє команду `TPM2_PCR_Extend`, він передає номер регістра `pcrHandle` та структуру `TPML_DIGEST_VALUES`, що містить хеші для кожного активного банку.

Обробка всередині TPM відбуваються атомарно:

1. Чип блокує внутрішній стан обраного регістра `pcrHandle`.
2. Для кожного банку, вказаного у команді, чип зчитує поточний вміст `PCR_current`.
3. Чип конкатенує `PCR_current` та новий вхідний хеш `H_input`.
4. Чип обчислює `PCR_next = HASH_alg(PCR_current || H_input)`.
5. Значення `PCR_next` перезаписує осередок пам'яті регістра.
6. Блокування знімається.

Якщо під час виконання операції станеться збій живлення або помилка шини, внутрішній стан регістра або повністю оновиться для всіх банків, або залишиться незмінним. Часткове оновлення одного банку без іншого у TPM 2.0 виключено апаратно.

### Механізм фіксації та інвалідація ("Caps")

Після завершення критичних етапів завантаження операційна система або завантажувач має можливість "запечатати" відкриті регістри від подальших маніпуляцій шкодочинним кодом. Оскільки скинути PCR 0–15 без повного перезавантаження ПК неможливо, ядро Linux може виконати операцію інвалідації ("Cap"):

```text
PCR_capped = TPM2_PCR_Extend(PCR_target, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
```

Після виконання такої операції підсумковий хеш регістра змінюється на непередбачуване випадкове значення, що унеможливлює розпечатування будь-яких ключів, прив'язаних до цього PCR до наступного перезавантаження системи.

## Інтерфейси ядра Linux: sysfs, securityfs та пристрої /dev/tpm0 /dev/tpmrm0

Операційна система Linux надає декілька рівнів абстракції для взаємодії з апаратним TPM 2.0 та читання стану PCR.

### Символьні пристрої `/dev/tpm0` та `/dev/tpmrm0`

- `/dev/tpm0`: Прямий символьний пристрій доступу до чипа TPM. Вимоги до доступу: привілеї `root` або членство у групі `tss`. Одночасний доступ декількох процесів до `/dev/tpm0` без синхронізації може призвести до збоїв транзакцій.
- `/dev/tpmrm0`: Трафік-менеджер ресурсів ядра (In-kernel TPM Resource Manager). Автоматично віртуалізує сесії, контексти ключів та транзакції команд між багатьма процесами у просторі користувача.

### Інтерфейс sysfs (`/sys/class/tpm/tpm0/`)

Ядро Linux експортує поточні значення регістрів PCR у зручному текстовому форматі через файлову систему `sysfs`:

```
/sys/class/tpm/tpm0/
├── device
├── pcr-sha1/
│   ├── 0
│   ├── 1
│   └── ...
├── pcr-sha256/
│   ├── 0
│   ├── 1
│   └── ...
└── pcr-sha384/
```

Зчитати поточне значення PCR 0 у банку SHA-256 можна безпосередньо з файлу `/sys/class/tpm/tpm0/pcr-sha256/0`.

### Інтерфейс securityfs (`/sys/kernel/security/`)

Для доступу до повного журналу вимірювань завантаження ядро Linux монтує файлову систему `securityfs`:

- `/sys/kernel/security/tpm0/binary_bios_measurements`: Повний бінарний TCG Event Log, записаний UEFI прошивкою та завантажувачем під час старту системи.
- `/sys/kernel/security/tpm-ima/binary_runtime_measurements`: Бінарний журнал вимірювань файлів підсистеми IMA (Integrity Measurement Architecture), яка веде вимірювання у PCR 10.

## Крайові випадки та інваріанти роботи з PCR

Під час розробки програмного забезпечення для роботи з TPM 2.0 необхідно враховувати специфічні крайові випадки:

1. **Режими сну S3 (Suspend-to-RAM) та S4 (Hibernate):**
   При переході в режим S3 живлення чипа TPM може вимикатися або переводитися в режим низького споживання, що призводить до втрати вмісту Volatile RAM (включаючи PCR). Під час відновлення системи прошивка UEFI виконує спеціальний скорочений ланцюг завантаження (Firmware Waking Vector) та повторно відтворює вимірювання PCR 0–7. Якщо за час сну відбулася підміна пам'яті або прошивки, підсумкові PCR 0–7 будуть відрізнятися, що запобіжить несанкціонованому розпечатуванню ключів після прокидання.

2. **Відсутність або відключення криптографічних банків:**
   Не всі чипи TPM 2.0 мають активованими всі банки хешування. Спроба зчитати значення з відсутнього банку (наприклад, SHA-384 на дешевому вбудованому контролері) поверне помилку ядра або порожній рядок у sysfs.

3. **Коди помилок TPM2_PCR_Extend:**
   При передачі неправильного індексу регістра або невідповідного розміру хешу чип TPM повертає специфічні коди помилок:
   - `TPM_RC_PCR`: Недійсний індекс PCR (наприклад, спроба звернутися до PCR 25).
   - `TPM_RC_HASH`: Переданий алгоритм хешування не підтримується TPM або деактивований у поточній конфігурації.
   - `TPM_RC_VALUE`: Розмір переданого масиву байтів не відповідає специфікації вибраного алгоритму хешування.

4. **Емульовані та віртуальні середовища (vTPM / swtpm):**
   У віртуальних машинах (QEMU/KVM, Hyper-V) реалізація PCR повністю програмна. Оскільки програмний TPM запускається на рівні гіпервізора, вимірювання PCR 0–7 у vTPM відображають стан віртуального BIOS (OVMF/SeaBIOS), а не фізичного обладнання хост-сервера.

## Практичні приклади зчитання та інспекції PCR мовами C та C++

Нижче наведено робочі приклади програм, які виконують вичитання та перевірку формату значень PCR 0–7 з банку SHA-256 через системний інтерфейс ядра Linux `sysfs`.

:::tabs
```c
/* pcr_reader.c — Програма зчитування банків PCR мовою C (POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define SYSFS_PCR_SHA256_FMT "/sys/class/tpm/tpm0/pcr-sha256/%u"
#define PCR_HEX_STRING_LEN 64

int read_pcr_sha256(unsigned int pcr_index, char *out_hex, size_t max_len) {
    if (pcr_index > 23 || max_len < PCR_HEX_STRING_LEN + 1) {
        errno = EINVAL;
        return -1;
    }

    char path[256];
    snprintf(path, sizeof(path), SYSFS_PCR_SHA256_FMT, pcr_index);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    ssize_t bytes_read = read(fd, out_hex, max_len - 1);
    close(fd);

    if (bytes_read <= 0) {
        return -1;
    }

    /* Видалення символу нового рядка, якщо він присутній */
    out_hex[bytes_read] = '\0';
    char *newline = strchr(out_hex, '\n');
    if (newline) {
        *newline = '\0';
    }

    return 0;
}

int main(void) {
    printf("--- Зчитання банків PCR-SHA256 через sysfs (C) ---\n");

    for (unsigned int i = 0; i <= 7; ++i) {
        char pcr_hex[128] = {0};
        if (read_pcr_sha256(i, pcr_hex, sizeof(pcr_hex)) == 0) {
            printf("PCR-%02u: %s\n", i, pcr_hex);
        } else {
            fprintf(stderr, "Помилка читання PCR-%02u: %s\n", i, strerror(errno));
        }
    }

    return EXIT_SUCCESS;
}
```
```cpp
// pcr_reader.cpp — Ідіоматична програма зчитування PCR мовою C++20
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

enum class PcrReadError {
    InvalidIndex,
    FileNotFound,
    ReadFailure,
    InvalidFormat
};

struct PcrErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "PcrReadError"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<PcrReadError>(ev)) {
            case PcrReadError::InvalidIndex: return "Недійсний індекс PCR (допустимо 0-23)";
            case PcrReadError::FileNotFound: return "Файл PCR не знайдено у sysfs";
            case PcrReadError::ReadFailure: return "Помилка читання даних з sysfs";
            case PcrReadError::InvalidFormat: return "Недійсний шістнадцятковий формат PCR";
            default: return "Невідома помилка";
        }
    }
};

inline const PcrErrorCategory g_pcr_error_category;

inline std::error_code make_error_code(PcrReadError e) {
    return {static_cast<int>(e), g_pcr_error_category};
}

class PcrSysfsReader {
public:
    explicit PcrSysfsReader(fs::path base_path = "/sys/class/tpm/tpm0/pcr-sha256")
        : base_path_(std::move(base_path)) {}

    [[nodiscard]] std::expected<std::string, std::error_code> read_pcr(uint32_t index) const {
        if (index > 23) {
            return std::unexpected(make_error_code(PcrReadError::InvalidIndex));
        }

        const fs::path pcr_path = base_path_ / std::to_string(index);
        if (!fs::exists(pcr_path)) {
            return std::unexpected(make_error_code(PcrReadError::FileNotFound));
        }

        std::ifstream file(pcr_path);
        if (!file.is_open()) {
            return std::unexpected(make_error_code(PcrReadError::ReadFailure));
        }

        std::string hex_val;
        if (!(file >> hex_val)) {
            return std::unexpected(make_error_code(PcrReadError::ReadFailure));
        }

        if (hex_val.length() != 64) {
            return std::unexpected(make_error_code(PcrReadError::InvalidFormat));
        }

        return hex_val;
    }

private:
    fs::path base_path_;
};

int main() {
    std::cout << "--- Зчитання банків PCR-SHA256 через sysfs (C++20) ---\n";
    PcrSysfsReader reader;

    for (uint32_t i = 0; i <= 7; ++i) {
        auto result = reader.read_pcr(i);
        if (result) {
            std::cout << "PCR-" << (i < 10 ? "0" : "") << i << ": " << *result << "\n";
        } else {
            std::cerr << "Помилка читання PCR-" << i << ": " << result.error().message() << "\n";
        }
    }

    return 0;
}
```
:::

## Підсумок

Регістри PCR в архітектурі TCG PC Client забезпечують криптографічний фундамент вимірюваного завантаження. Розуміння точного розподілу обов'язків між прошивкою UEFI, завантажувачем, підсистемами ядра Linux (`systemd-stub`, IMA) та простором користувача дозволяє будувати надійні безпекові політики запечатування ключів LUKS2 та проводити коректну віддалену атестацію вузлів інфраструктури.
