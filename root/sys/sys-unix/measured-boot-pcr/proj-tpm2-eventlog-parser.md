# ⚙️ Практикум: аналізатор TCG Event Log та відтворення PCR мовами C і C++

У цьому практикумі розробляється аналізатор системного журналу вимірюваного завантаження TCG Event Log. Програма зчитує бінарні дані з інтерфейсу ядра `/sys/kernel/security/tpm0/binary_bios_measurements`, розбирає формати подій Crypto Agile (`TCG_PCR_EVENT2`), послідовно обчислює операцію `Extend` для кожного запису та звіряє підрахований стан з апаратними регістрами PCR чипа TPM 2.0.

Журнал вимірювань завантаження SecurityFS є головним містком між негнучким 256-бітним криптографічним акумулятором усередині TPM та реальними виконуваними файлами на диску. Без можливості розібрати цей бінарний потік розробник засобів безпеки не зможе з'ясувати причину відмови розпечатування диска чи побудувати сервіс віддаленої атестації.

## Архітектура та двофазний бінарний формат TCG Event Log

Згідно зі специфікацією TCG EFI Protocol Specification, журнал подій у пам'яті складається з двох суттєво різних за структурою секцій:

1. **Перший запис (Specification ID Header Event):** Для забезпечення зворотної сумісності зі старими системами перший запис у логу завжди відформатовано за застарілою специфікацією TCG 1.2 (`TCG_PCR_EVENT`). Цей запис містить заголовкові метадані, версію специфікації TCG 2.0 та перелік активних банків криптографічних алгоритмів (SHA-1, SHA-256, SHA-384).
2. **Основний потік подій (Agile Event Log):** Усі наступні записи відформатовано згідно зі специфікацією TCG 2.0 Crypto Agile (`TCG_PCR_EVENT2`). Замість одного фіксованого хешу кожен запис містить масив дайджестів для всіх увімкнених банків хешування.

### Перетворення бінарних полів запису TCG_PCR_EVENT2

Кожен запис подій у потоці Agile має таку байтову структуру:

- `PCRIndex` (4 байти, Little-Endian): Номер регістра PCR (від 0 до 23), для якого призначене вимірювання.
- `EventType` (4 байти, Little-Endian): Категорія події (наприклад, `EV_POST_CODE`, `EV_S_CRTM_VERSION`, `EV_EFI_BOOT_SERVICES_APPLICATION`).
- `DigestCount` (4 байти, Little-Endian): Кількість дайджестів у даному записі.
- `Digests` (Масив забійних структур `TPMT_HA`): Для кожного дайджесту вказується `AlgorithmID` (2 байти, наприклад `0x000B` для SHA-256, `0x0004` для SHA-1, `0x000C` для SHA-384) та сирий хеш відповідної довжини (32 байти для SHA-256, 20 байтів для SHA-1, 48 байтів для SHA-384).
- `EventSize` (4 байти, Little-Endian): Довжина полів опису події.
- `Event` (Масив байтів довжиною `EventSize`): Допоміжні дані події (наприклад, шлях до завантаженого файлу EFI, рядок аргументів ядра або назва змінної Secure Boot).

## Специфікація заголовка TCG Spec ID Header Event

Перший запис у журналі (`TCG_PCR_EVENT`) має індекс PCR рівний 0, тип події `EV_NO_ACTION` (`0x03`) і 20-байтний порожній дайджест SHA-1. Поле `Event` цього запису містить критичну структуру `TCG_EfiSpecIDEventStruct`:

| Зміщення (байти) | Розмір | Назва поля | Опис та стандартні значення |
|---|---|---|---|
| `0x00` | 16 байтів | `signature` | Символьна сигнатура `"Spec ID Event03\0"` |
| `0x10` | 4 байти | `platformClass` | Клас платформи (для PC Client — `0x00000000`) |
| `0x14` | 1 байт | `specVersionMinor` | Другорядний номер версії специфікації (наприклад, `0` або `2`) |
| `0x15` | 1 байт | `specVersionMajor` | Основний номер версії специфікації (для TPM 2.0 — `2`) |
| `0x16` | 1 байт | `specErrata` | Номер виправлення специфікації (Errata) |
| `0x17` | 1 байт | `uintnSize` | Розмір покажчика архітектури (1 = 32 біти, 2 = 64 біти) |
| `0x18` | 4 байти | `numberOfAlgorithms` | Кількість зареєстрованих криптографічних банків `N_alg` |
| `0x1C` | `N_alg × 4` B | `digestSizes` | Масив структур: `algorithmId` (2B) + `digestSize` (2B) |
| Змінне | 1 байт | `vendorInfoSize` | Довжина додаткових даних постачальника прошивки |
| Змінне | `V` байтів | `vendorInfo` | Допоміжні дані прошивки (наприклад, назва BIOS) |

Наявність динамічної таблиці `digestSizes` є критично важливою для парсингу: вона вказує аналізатору, скільки байтів слід вичитати з бінарного потоку для будь-якого `algorithmId` без необхідності жорстко зашивати розміри у код програми.

## Глибокий аналіз еволюції бінарного протоколу TCG Event Log

Перехід від стандарту TPM 1.2 до TPM 2.0 вимагав кардинального перегляду способів кодування бінарного журналу вимірюваного завантаження. Головною причиною реформування стала криптографічна вразливість алгоритму SHA-1. Застарілий формат `TCG_PCR_EVENT` жорстко передбачав наявність єдиного 20-байтного масиву хешу в кожному записі. Коли індустрія почала перехід на SHA-256 та SHA-384, стало зрозуміло, що розширення структури шляхом додавання полів фіксованого розміру призведе до повної втрати сумісності із наявними парсерами прошивок.

Рішенням консорціуму TCG стало впровадження принципів **Crypto Agility** (криптографічної гнучкості). Згідно з цією концепцією, формат запису журналу не повинен залежати від математичних параметрів конкретного алгоритму хешування. Замість цього кожен запис повинен самодокументуватися, містити ясні ідентифікатори алгоритмів та інструкції щодо розмірів даних.

Для збереження повної зворотної сумісності з legacy-завантажувачами було прийнято гібридний підхід: перший елемент журналу залишається у форматі TCG 1.2, але його змістовне поле `Event` використовується як мета-контейнер `TCG_EfiSpecIDEventStruct`. Цей заголовок виконує роль своерідного паспорта журналу. Він оголошує операційній системі, які саме криптографічні банки були активовані прошивкою під час поточного запуску комп'ютера.

Бінарне вирівнювання полів (Data Alignment) у потоці даних розроблено з урахуванням 64-бітних архітектур x86-64 та ARM64. Усі 32-бітні цілі числа (`PCRIndex`, `EventType`, `DigestCount`, `EventSize`) зберігаються у форматі Little-Endian. Однак розробникам парсерів слід пам'ятати, що масив дайджестів у структурі `TCG_PCR_EVENT2` не має падингу (padding bytes) між хешами різних банків. Хеш SHA-1 (20 байтів) безпосередньо межує з наступним хешем SHA-256 (32 байти), що вимагає потокового побайтового читання замість безпосереднього приведення типів вказівників у пам'яті (Pointer Casting).

## Деталізований каталог типів подій TCG Event Types

Специфікація TCG визначає розширений набір стандартизованих констант типів подій, кожна з яких виконує строго визначену функцію у ланцюгу забезпечення цілісності:

- `EV_POST_CODE` (`0x00000001`): Записує вимірювання самотестування BIOS та коди системної діагностики POST. Фіксує початкові етапи ініціалізації контролера пам'яті та системної шини.
- `EV_NO_ACTION` (`0x00000003`): Спеціальні інформаційні записи метаданих, які **не розширюють** регістри PCR у чипі TPM. Вони слугують для передачі конфігураційних таблиць (включаючи `Spec ID Event`, структури SCSI завантаження та маніфести SMM).
- `EV_SEPARATOR` (`0x00000004`): Записується прошивкою наприкінці фази ініціалізації перед передачею контролю завантажувачу. Прошивка виконує `Extend` значення `0x00000000` або `0xFFFFFFFF` у регістри PCR 0–7. Ця подія створює чітку криптографічну межу, унеможливлюючи атаки імітації подій прошивки зі сторони програм простору користувача.
- `EV_ACTION` (`0x00000005`): Текстові рядки опису дій прошивки (наприклад, `"Calling EFI Application from Boot Option"`).
- `EV_S_CRTM_VERSION` (`0x00000008`): Вимірювання текстового рядка або бінарного коду версії CRTM (Core Root of Trust for Measurement), що виконує найпершу інструкцію процесора.
- `EV_CPU_MICROCODE` (`0x00000009`): Вимірювання бінарних оновлень мікрокоду центрального процесора, які завантажуються прошивкою до старту основних ядер.
- `EV_PLATFORM_CONFIG_FLAGS` (`0x0000000A`): Вимірювання апаратних прапорців конфігурації материнської плати, стану джамперів безпеки та перемикачів режимів.
- `EV_EFI_VARIABLE_DRIVER_CONFIG` (`0x00008001`): Вимірювання незмінних та змінних налаштувань UEFI (наприклад, `BootOrder`, `SetupMode`, `SecureBoot`).
- `EV_EFI_BOOT_SERVICES_APPLICATION` (`0x00008002`): Вимірювання виконуваних модулів EFI, включно із завантажувачами `bootx64.efi`, `grubx64.efi`, `systemd-boot`.
- `EV_EFI_BOOT_SERVICES_DYNAMIC` (`0x00008003`): Динамічно завантажувані драйвери обладнання DXE (наприклад, EFI-драйвери мережевих карт або NVMe-контролерів).
- `EV_EFI_VARIABLE_AUTHORITY` (`0x0000800E`): Сертифікати та ключі безпеки (`db`, `dbx`, `PK`), які використано для підтвердження підпису завантажуваного завантажувача.

## Декодування та аналіз внутрішніх структур даних подій UEFI

Для точного відтворення аналізу недостатньо лише зчитати дайджести — парсер повинен уміти декодувати вміст поля `Event` залежно від `EventType`.

### 1. Події змінних UEFI (`EV_EFI_VARIABLE_DRIVER_CONFIG` та `EV_EFI_VARIABLE_AUTHORITY`)

Коли прошивка вимірює змінну UEFI (наприклад, конфігурацію Secure Boot у PCR 7 або завантажувальні змінні у PCR 5), поле `Event` містить бінарну структуру `UEFI_VARIABLE_DATA`:

```c
typedef struct {
    uint8_t  variable_guid[16];   /* GUID категорії змінної */
    uint64_t unicode_name_length; /* Кількість Unicode UTF-16LE символів */
    uint64_t variable_data_length;/* Довжина сирих байтів вмісту змінної */
    uint16_t unicode_name[1];    /* Масив UTF-16LE символів назви */
    /* uint8_t variable_data[1]; */ /* Безпосередній вміст змінної */
} uefi_variable_data_t;
```

Стандартні GUID категорій включають:
- `EFI_GLOBAL_VARIABLE_GUID`: `{8BE4DF61-93CA-11D2-AA0D-00E098032B8C}` (використовується для `BootOrder`, `Boot0000`, `SecureBoot`).
- `EFI_IMAGE_SECURITY_DATABASE_GUID`: `{D719B2CB-3D3A-4596-A3BC-DAD00E67656F}` (використовується для баз ключів `PK`, `KEK`, `db`, `dbx`).

При вимірюванні змінних прошивка обчислює хеш від конкатенації `variable_guid` + `unicode_name` + `variable_data`. Якщо користувач змінює порядок завантажувальних пристроїв у меню BIOS, зміна `BootOrder` призведе до оновлення хешу цієї змінної, що в свою чергу змінить підсумкове значення регістра PCR 5.

### 2. Події завантаження EFI-додатків (`EV_EFI_BOOT_SERVICES_APPLICATION`)

Для записів завантажувачів операційної системи (PCR 4) поле `Event` описується структурою `UEFI_IMAGE_LOAD_EVENT`:

```c
typedef struct {
    uint64_t image_location_in_memory; /* Фізична адреса завантаження у RAM */
    uint64_t image_length_in_memory;   /* Розмір образу у пам'яті (байтів) */
    uint64_t link_time_address;        /* Базова адреса компонування */
    uint64_t device_path_length;       /* Довжина UEFI Device Path структури */
    uint8_t  device_path[1];           /* Бінарне дерево шляху до пристрою */
} uefi_image_load_event_t;
```

Принцип верифікації завантажувача: прошивка зчитує виконуваний файл PE/COFF (`grubx64.efi` або `systemd-bootx64.efi`) з системного EFI-розділу (ESP), обчислює Authenticode SHA-256 хеш від бінарного вмісту диска та записує цей хеш у відповідну подібну структуру `TCG_PCR_EVENT2`.

## Конвеєр відтворення PCR та математичний механізм верифікації

Процес перевірки логу полягає у покроковому повторенні (Replay) всіх операцій `Extend`, які виконувалися прошивкою та завантажувачем з моменту включення ПК.

### Алгоритм відтворення

1. Ініціалізувати локальний масив симульованого регістра: `PCR_simulated[i] = 0x0000...00` для всіх `i` від 0 до 23.
2. Прочитати перший запис `Header Event`. Отримати масив відповідностей `algorithmId` → `digestSize`.
3. Поки потік файлу не досягне кінця:
   - Зчитати `PCRIndex`, `EventType`, `DigestCount`.
   - Проітерувати за `DigestCount`. Якщо знайдено `algorithmId == TPM2_ALG_SHA256`:
     - Зчитати 32 байти `eventDigest`.
     - Якщо `EventType != EV_NO_ACTION`:
       - Виконати акумуляцію: `PCR_simulated[PCRIndex] = SHA256(PCR_simulated[PCRIndex] || eventDigest)`
   - Прочитати `EventSize` та пропустити `EventSize` байтів даних опису події.
4. Прочитати поточне апаратне значення `PCR_hardware[N]` з системного файлу `/sys/class/tpm/tpm0/pcr-sha256/N`.
5. Звірити `PCR_simulated[N]` з `PCR_hardware[N]`. Якщо значення збігаються до останнього біта, журнал є повністю автентичним і не піддавався маніпуляціям.

### Вимірювання у просторі користувача: Підсистема IMA (PCR 10)

Після завершення передачі контролю від завантажувача до ядра Linux, ініціатива вимірювання переходить до підсистеми IMA (Integrity Measurement Architecture). IMA веде власне вимірювання у PCR 10 і створює окремий лог `/sys/kernel/security/tpm-ima/binary_runtime_measurements`.

Кожен виконуваний бінарний файл, системний скрипт чи динамічна бібліотека `.so`, яка відкривається ядрами системних викликів `execve()` або `mmap()`, вимірюється підсистемою IMA перед запуском. Якщо хеш файлу не відповідає записаному в розширених атрибутах `security.ima`, ядро блокує виконання файлу.

## Покрокова інструкція термінального аналізу бінарного журналу

Перед розробкою власного парсера корисно провести ручний аналіз сирих байтів журналу у терміналі Linux для розуміння низькорівневої структури даних.

### 1. Перегляд перших байтів Spec ID Header Event

Для інспекції перших 64 байтів бінарного журналу використайте утиліту `hexdump` або `xxd`:

```bash
sudo hexdump -C /sys/kernel/security/tpm0/binary_bios_measurements | head -n 10
```

Типовий вивід перших трьох рядків дампа має такий вигляд:

```text
00000000  00 00 00 00 03 00 00 00  00 00 00 00 00 00 00 00  |................|
00000010  00 00 00 00 25 00 00 00  53 70 65 63 20 49 44 20  |....%...Spec ID |
00000020  45 76 65 6e 74 30 33 00  00 00 00 00 00 02 00 00  |Event03.........|
```

Аналіз зміщень:
- `0x00..0x03`: `PCRIndex = 0x00000000` (4 байти).
- `0x04..0x07`: `EventType = 0x00000003` (`EV_NO_ACTION`).
- `0x08..0x1B`: 20 нульових байтів дайджесту SHA-1.
- `0x1C..0x1F`: `EventSize = 0x00000025` (37 байтів).
- `0x20..0x2F`: Сигнатура `"Spec ID Event03\0"`.

### 2. Порівняльний аналіз із утилітою tpm2_eventlog

Офіційний пакет `tpm2-tools` надає утиліту `tpm2_eventlog`, яка парсить бінарний лог та виводить його у форматі YAML:

```bash
sudo tpm2_eventlog /sys/kernel/security/tpm0/binary_bios_measurements
```

Порівнюючи вивід власної програми з результатом `tpm2_eventlog`, ви можете легко перевірити коректність обчислення відтвореного стану PCR для кожного з увімкнених банків хешування.

## Особливості апаратної атестації та верифікації підписів TPM2_Quote

Сам по собі файл TCG Event Log у файловій системі `/sys/kernel/security/tpm0/binary_bios_measurements` знаходиться у звичайній оперативній пам'яті, сформований ядром Linux на основі даних ACPI/UEFI. Це означає, що зкомпрометоване ядро чи зловмисний модуль ядра теоретично можуть модифікувати бінарні дані логу у пам'яті.

Щоб запобігти такій компрометації, у криптографічній архітектурі TCG журналювання завжди працює у зв'язці з апаратною цитатою **TPM2_Quote**:

1. **Генерація цитати:** Сервер атестації надсилає вузлу випадковий челендж (Nonce). Чип TPM виконує внутрішню криптографічну операцію `TPM2_Quote`, беручи поточні апаратні значення регістрів PCR, підписуючи їх закритим ключем атестації Attestation Key (AK) та додаючи Nonce.
2. **Передача даних:** Вузол відправляє на сервер атестації зашифровану цитату `TPM2_Quote` та бінарний журнал TCG Event Log.
3. **Апаратна валідація:** Сервер перевіряє криптографічний підпис цитати за допомогою відкритого ключа `AK`, переконуючись, що значення PCR дійсно згенеровані незмінним чипом TPM.
4. **Реконструкція та аудит:** Сервер проганяє локальний парсер Event Log, перераховує очікувані значення PCR і порівнює їх із запечатаними в апаратній цитаті `TPM2_Quote`. Якщо значення збігаються, сервер перевіряє кожен виконуваний компонент у логу за базою дозволених хешів (Golden Measurement Database).

## Повнофункціональна реалізація мовами C та C++

Нижче наведено робочі реалізації аналізатора журналу TCG Event Log. Обидві програми зчитують бінарний потік з інтерфейсу SecurityFS ядра Linux, розбирають заголовки `TCG_PCR_EVENT2`, декодують описові типи подій, виконують послідовне акумулювання хешів для PCR 0–7 за допомогою бібліотеки OpenSSL libcrypto та друкують відтворений апаратний підсумок.

У версії мовою C++ застосовано сучасний стандарт C++20: використання `std::filesystem::path`, безпечна робота з файлами через `std::ifstream`, обгортка неволодіючих зрізів пам'яті через `std::span`, тип `std::expected` для безпечної обробки помилок введення-виведення без використання винятків, а також повна відсутність сирих вказівників і ручного управління пам'яттю (`malloc`/`free`).

:::tabs
```c
/* tpm2_log_parser.c — Повнофункціональний парсер TCG Event Log мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <openssl/sha.h>

#define TPM2_ALG_SHA1   0x0004
#define TPM2_ALG_SHA256 0x000B
#define TPM2_ALG_SHA384 0x000C

#define SHA1_DIGEST_SIZE   20
#define SHA256_DIGEST_SIZE 32
#define SHA384_DIGEST_SIZE 48

#define EV_NO_ACTION 0x0003
#define EV_SEPARATOR 0x0004

typedef struct {
    uint32_t pcr_index;
    uint32_t event_type;
    uint8_t  digest[SHA1_DIGEST_SIZE];
    uint32_t event_size;
} __attribute__((packed)) tcg_pcr_event_hdr_t;

typedef struct {
    uint16_t alg_id;
    uint16_t digest_size;
} alg_size_entry_t;

static uint16_t get_digest_size(uint16_t alg_id, const alg_size_entry_t *alg_table, uint32_t table_count) {
    for (uint32_t i = 0; i < table_count; ++i) {
        if (alg_table[i].alg_id == alg_id) {
            return alg_table[i].digest_size;
        }
    }
    switch (alg_id) {
        case TPM2_ALG_SHA1:   return SHA1_DIGEST_SIZE;
        case TPM2_ALG_SHA256: return SHA256_DIGEST_SIZE;
        case TPM2_ALG_SHA384: return SHA384_DIGEST_SIZE;
        default: return 0;
    }
}

static const char* get_event_type_name(uint32_t type) {
    switch (type) {
        case 0x00000001: return "EV_POST_CODE";
        case 0x00000003: return "EV_NO_ACTION";
        case 0x00000004: return "EV_SEPARATOR";
        case 0x00000005: return "EV_ACTION";
        case 0x00000008: return "EV_S_CRTM_VERSION";
        case 0x00000009: return "EV_CPU_MICROCODE";
        case 0x0000000A: return "EV_PLATFORM_CONFIG_FLAGS";
        case 0x00008001: return "EV_EFI_VARIABLE_DRIVER_CONFIG";
        case 0x00008002: return "EV_EFI_BOOT_SERVICES_APPLICATION";
        case 0x00008003: return "EV_EFI_BOOT_SERVICES_DYNAMIC";
        case 0x0000800E: return "EV_EFI_VARIABLE_AUTHORITY";
        default: return "EV_UNKNOWN";
    }
}

void pcr_extend_sha256(uint8_t pcr[SHA256_DIGEST_SIZE], const uint8_t event_digest[SHA256_DIGEST_SIZE]) {
    uint8_t buffer[SHA256_DIGEST_SIZE * 2];
    memcpy(buffer, pcr, SHA256_DIGEST_SIZE);
    memcpy(buffer + SHA256_DIGEST_SIZE, event_digest, SHA256_DIGEST_SIZE);
    
    SHA256(buffer, sizeof(buffer), pcr);
}

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; ++i) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    const char *path = "/sys/kernel/security/tpm0/binary_bios_measurements";
    if (argc > 1) {
        path = argv[1];
    }

    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "Помилка відкриття логу (%s): %s\n", path, strerror(errno));
        return EXIT_FAILURE;
    }

    /* Читання першого заголовка TCG 1.2 Header */
    tcg_pcr_event_hdr_t header;
    if (fread(&header, sizeof(header), 1, f) != 1) {
        fprintf(stderr, "Помилка зчитування заголовка логу\n");
        fclose(f);
        return EXIT_FAILURE;
    }

    uint8_t *event_data = (uint8_t*)malloc(header.event_size);
    if (!event_data) {
        fclose(f);
        return EXIT_FAILURE;
    }

    if (fread(event_data, header.event_size, 1, f) != 1) {
        fprintf(stderr, "Помилка зчитування SpecIDEvent\n");
        free(event_data);
        fclose(f);
        return EXIT_FAILURE;
    }

    alg_size_entry_t alg_table[16];
    uint32_t num_algs = 0;

    if (header.event_size >= 0x1C) {
        uint32_t count = *(uint32_t*)(event_data + 0x18);
        if (count > 16) count = 16;
        num_algs = count;

        size_t offset = 0x1C;
        for (uint32_t i = 0; i < count; ++i) {
            if (offset + 4 > header.event_size) break;
            alg_table[i].alg_id = *(uint16_t*)(event_data + offset);
            alg_table[i].digest_size = *(uint16_t*)(event_data + offset + 2);
            offset += 4;
        }
    }
    free(event_data);

    uint8_t simulated_pcrs[8][SHA256_DIGEST_SIZE];
    memset(simulated_pcrs, 0, sizeof(simulated_pcrs));

    printf("Парсинг TCG 2.0 Agile Event Log (%s)...\n", path);

    size_t event_count_total = 0;
    while (!feof(f)) {
        uint32_t pcr_index, event_type, count;
        if (fread(&pcr_index, sizeof(pcr_index), 1, f) != 1) break;
        if (fread(&event_type, sizeof(event_type), 1, f) != 1) break;
        if (fread(&count, sizeof(count), 1, f) != 1) break;

        event_count_total++;

        for (uint32_t i = 0; i < count; ++i) {
            uint16_t alg_id;
            if (fread(&alg_id, sizeof(alg_id), 1, f) != 1) break;

            uint16_t digest_sz = get_digest_size(alg_id, alg_table, num_algs);
            if (digest_sz == 0) {
                fprintf(stderr, "Невідомий алгоритм: 0x%04x\n", alg_id);
                fclose(f);
                return EXIT_FAILURE;
            }

            uint8_t digest_buf[64];
            if (fread(digest_buf, digest_sz, 1, f) != 1) break;

            if (alg_id == TPM2_ALG_SHA256 && pcr_index < 8) {
                if (event_type != EV_NO_ACTION) {
                    pcr_extend_sha256(simulated_pcrs[pcr_index], digest_buf);
                }
            }
        }

        uint32_t event_size;
        if (fread(&event_size, sizeof(event_size), 1, f) != 1) break;
        fseek(f, event_size, SEEK_CUR);
    }

    fclose(f);

    printf("Успішно оброблено подій: %zu\n", event_count_total);
    for (int i = 0; i < 8; ++i) {
        char label[64];
        snprintf(label, sizeof(label), "Відтворений PCR %d (SHA-256)", i);
        print_hex(label, simulated_pcrs[i], SHA256_DIGEST_SIZE);
    }

    return EXIT_SUCCESS;
}
```
```cpp
// tpm2_log_parser.cpp — Ідіоматичний аналізатор TCG Event Log мовою C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <filesystem>
#include <iomanip>
#include <cstdint>
#include <expected>
#include <system_error>
#include <openssl/sha.h>

namespace fs = std::filesystem;

constexpr uint16_t ALG_SHA1   = 0x0004;
constexpr uint16_t ALG_SHA256 = 0x000B;
constexpr uint16_t ALG_SHA384 = 0x000C;

constexpr size_t SHA256_SIZE = 32;
constexpr uint32_t EV_NO_ACTION = 0x0003;

using Digest256 = std::array<uint8_t, SHA256_SIZE>;
using PcrBankArray = std::array<Digest256, 8>;

enum class LogParseError {
    FileNotFound,
    HeaderReadError,
    InvalidSpecId,
    CorruptedStream
};

struct LogErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "TcgLogParser"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<LogParseError>(ev)) {
            case LogParseError::FileNotFound: return "Неможливо відкрити файл логу";
            case LogParseError::HeaderReadError: return "Помилка читання заголовка SpecID";
            case LogParseError::InvalidSpecId: return "Невідома сигнатура SpecID Event";
            case LogParseError::CorruptedStream: return "Пошкодження бінарного потоку подій";
            default: return "Невідома помилка";
        }
    }
};

inline const LogErrorCategory g_log_error_category;

inline std::error_code make_error_code(LogParseError e) {
    return {static_cast<int>(e), g_log_error_category};
}

class TpmPcrAccumulator {
public:
    TpmPcrAccumulator() {
        for (auto& pcr : pcrs_) {
            pcr.fill(0x00);
        }
    }

    void extend_sha256(uint32_t pcr_index, uint32_t event_type, std::span<const uint8_t, SHA256_SIZE> event_digest) {
        if (pcr_index >= pcrs_.size() || event_type == EV_NO_ACTION) {
            return;
        }

        std::array<uint8_t, SHA256_SIZE * 2> buffer{};
        std::copy(pcrs_[pcr_index].begin(), pcrs_[pcr_index].end(), buffer.begin());
        std::copy(event_digest.begin(), event_digest.end(), buffer.begin() + SHA256_SIZE);

        SHA256(buffer.data(), buffer.size(), pcrs_[pcr_index].data());
    }

    [[nodiscard]] const Digest256& get_pcr(size_t index) const {
        return pcrs_.at(index);
    }

    [[nodiscard]] const PcrBankArray& get_all_pcrs() const noexcept {
        return pcrs_;
    }

private:
    PcrBankArray pcrs_{};
};

class EventLogParser {
public:
    explicit EventLogParser(fs::path log_path) : log_path_(std::move(log_path)) {}

    [[nodiscard]] std::expected<PcrBankArray, std::error_code> parse_and_replay() {
        std::ifstream file(log_path_, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(make_error_code(LogParseError::FileNotFound));
        }

        // Читання TCG 1.2 Header
        uint32_t pcr_index{}, event_type{}, event_size{};
        std::array<uint8_t, 20> header_digest{};

        if (!file.read(reinterpret_cast<char*>(&pcr_index), sizeof(pcr_index)) ||
            !file.read(reinterpret_cast<char*>(&event_type), sizeof(event_type)) ||
            !file.read(reinterpret_cast<char*>(header_digest.data()), header_digest.size()) ||
            !file.read(reinterpret_cast<char*>(&event_size), sizeof(event_size))) {
            return std::unexpected(make_error_code(LogParseError::HeaderReadError));
        }

        std::vector<uint8_t> spec_id_data(event_size);
        if (!file.read(reinterpret_cast<char*>(spec_id_data.data()), spec_id_data.size())) {
            return std::unexpected(make_error_code(LogParseError::HeaderReadError));
        }

        TpmPcrAccumulator accumulator;

        // Парсинг TCG 2.0 Agile потік
        while (file.peek() != EOF) {
            uint32_t idx{}, evt_type{}, count{};
            if (!file.read(reinterpret_cast<char*>(&idx), sizeof(idx))) break;
            if (!file.read(reinterpret_cast<char*>(&evt_type), sizeof(evt_type))) break;
            if (!file.read(reinterpret_cast<char*>(&count), sizeof(count))) break;

            for (uint32_t i = 0; i < count; ++i) {
                uint16_t alg_id{};
                if (!file.read(reinterpret_cast<char*>(&alg_id), sizeof(alg_id))) break;

                if (alg_id == ALG_SHA256) {
                    Digest256 digest{};
                    if (!file.read(reinterpret_cast<char*>(digest.data()), digest.size())) break;
                    accumulator.extend_sha256(idx, evt_type, digest);
                } else if (alg_id == ALG_SHA1) {
                    file.ignore(20);
                } else if (alg_id == ALG_SHA384) {
                    file.ignore(48);
                } else {
                    return std::unexpected(make_error_code(LogParseError::CorruptedStream));
                }
            }

            uint32_t evt_sz{};
            if (!file.read(reinterpret_cast<char*>(&evt_sz), sizeof(evt_sz))) break;
            file.ignore(evt_sz);
        }

        return accumulator.get_all_pcrs();
    }

private:
    fs::path log_path_;
};

int main(int argc, char* argv[]) {
    const fs::path path = (argc > 1) ? argv[1] : "/sys/kernel/security/tpm0/binary_bios_measurements";

    std::cout << "Аналіз TCG Event Log (C++20): " << path << std::endl;

    EventLogParser parser(path);
    auto result = parser.parse_and_replay();

    if (!result) {
        std::cerr << "Помилка розбору логу: " << result.error().message() << std::endl;
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < result->size(); ++i) {
        std::cout << "Відтворений PCR " << i << " (SHA-256): ";
        for (uint8_t byte : (*result)[i]) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        std::cout << std::dec << std::endl;
    }

    return EXIT_SUCCESS;
}
```
:::

## Крайові випадки, аномалії бінарного формату та безпека парсингу

Під час практичної експлуатації аналізатора у реальних промислових середовищах необхідно обробляти низку крайових випадків та аномалій:

1. **Нелінійний розмір полів даних (`EventSize`):**
   Поле `EventSize` може містити значення від 0 до десятків кілобайтів (наприклад, при записі в лог повних таблиць SMBIOS, сертифікатів або атрибутів змінних UEFI). Використання фіксованих буферів замість динамічного пропуску зсуву (`fseek` у C чи `file.ignore` у C++) призведе до зсуву бінарних меж і фатальної поломки розбору наступних подій.

2. **Захист від атак на парсер (Malicious Event Log & Integer Overflow):**
   Якщо лог вичитано з невідомого або зовнішнього джерела (наприклад, під час віддаленої атестації), зловмисник може сформувати бінарний файл із підробленим значенням `EventSize` (наприклад `0xFFFFFFFF`). Спроба виконати `malloc(EventSize)` у парсері без перевірки верхньої межі спричинить переповнення цілого числа або відмову у обслуговуванні (OOM Crash). Парсер повинен жорстко перевіряти, що `EventSize` не перевищує залишок розміру файлу.

3. **Паралельна наявність кількох банків хешування:**
   Один і той самий запис події містить хеші для SHA-1, SHA-256 та SHA-384. Програмування аналізатора вимагає точної ітерації за лічильником `count` та коректного визначення розміру дайджестів для кожного алгоритму з таблиці `digestSizes` заголовка Spec ID.

4. **Віртуальні та емульовані TPM (vTPM / swtpm):**
   У середовищах віртуалізації (QEMU/KVM з прошивкою OVMF та бінарним симулятором `swtpm`) перший запис `Header Event` може містити специфічні розширення Vendor-ID або мати інший перелік активованих банків, що вимагає динамічного аналізу таблиці алгоритмів замість зашивання констант у код.

## Інтеграція в симулятори віддаленої атестації та CI/CD

Розроблений парсер є фундаментальним модулем для побудови автоматизованих засобів перевірки хостів (Host Attestation Agents). У великих хмарних інфраструктурах подібний код інтегрується у вигляді демона, який під час кожного перезавантаження вузла зчитує бінарні вимірювання, відтворює стан регістрів PCR і надсилає підписане твердження `TPM2_Quote` до центрального сервера безпеки.

Якщо відтворений стан відрізняється від еталонного золотого образу (Golden Image), вузол автоматично ізолюється від мережі до проходження ручного інспектування адміністратором.

## Інструкція зі збірки та тестування на реальній системі

Щоб перевірити роботу збірки та зіставити результат відтворення з дійсним значенням апаратного регістра PCR 0 вашого комп'ютера, виконайте у терміналі такі команди:

```bash
# 1. Інсталяція необхідних системних бібліотек розробки OpenSSL
sudo apt-get install build-essential libssl-dev

# 2. Збірка варіанту C++20
g++ -std=c++20 tpm2_log_parser.cpp -lssl -lcrypto -o tpm2_log_parser

# 3. Збірка варіанту C11
gcc -std=c11 tpm2_log_parser.c -lssl -lcrypto -o tpm2_log_parser_c

# 4. Запуск аналізу
./tpm2_log_parser

# 5. Порівняння з дійсним значенням із sysfs ядра Linux
cat /sys/class/tpm/tpm0/pcr-sha256/0
```

Якщо підрахований шістнадцятковий рядок повністю збігається з виводом `/sys/class/tpm/tpm0/pcr-sha256/0`, ваш парсер успішно проаналізував весь ланцюг завантаження від першого кроку CRTM до роботи операційної системи.
