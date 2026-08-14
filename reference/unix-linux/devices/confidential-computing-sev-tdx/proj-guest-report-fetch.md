# ⚙️ Практика: Отримання атестаційного звіту SEV-SNP та Intel TDX у Linux

Завдання: у гостьовій операційній системі під керуванням Linux розробити та реалізувати демон атестації (Attestation Agent), який безпечно звертається до апаратних захищених символьних пристроїв (`/dev/sev-guest` для машин AMD SEV-SNP або `/dev/tdx-guest` для машин Intel TDX), запитує криптографічно підписаний звіт про стан початкового завантаження ВМ із прив'язкою до 64-байтного векторного значення (nonce), витягує SHA-384 хеш виміру пам'яті (Measurement Digest / MRTD), виконує перевірку ехо-відповіді та готує атестаційне свідоцтво для передачі зовнішньому сервісу управління ключами (KMS).

---

## 1. Архітектурний аналіз та механіка виконання у ядрі

Перед викликом програмою системного виклику `ioctl()` операційна система Linux виконує серію перевірок безпеки та підготовки контексту. Демон атестації виконується в просторі користувача (Userspace), але сама операція взаємодії з апаратним криптографічним співпроцесором AMD Secure Processor (ASP) або модулем Intel TDX Module вимагає найвищих привілеїв ядра.

### Шлях виконання запиту SEV-SNP усередині ядра Linux

Коли програма викликає `ioctl(fd, SNP_GET_REPORT, &ioctl_req)`, ядро виконує таку послідовність кроків:

1. **Перевірка прав доступу та контектсу**: Драйвер `drivers/virt/coco/sev-guest/sev-guest.c` перевіряє, чи має викликаючий процес права на виконання запиту до пристрою `/dev/sev-guest`.
2. **Маршалінг та копіювання пам'яті**: Драйвер зчитує з простору користувача 64 байти `user_data` та значення `vmpl` через виклик `copy_from_user()`.
3. **Захист від атак повтору через лічильники послідовностей**: Драйвер зчитує з внутрішніх структур ядра поточний значення лічильника послідовності `vmpck_seq` для обраного ключа VMPCK. Це значення інкрементується при кожному виклику. Приймаючи запит, співпроцесор ASP перевіряє, що лічильник строго більший за попередній, блокуючи спроби гіпервізора підмінити або повторно відправити старий зашифрований пакет (replay attack).
4. **Шифрування GHCB-повідомлення**: Драйвер зашифровує структуру запиту алгоритмом AES-256-GCM за допомогою симетричного ключа VMPCK, узгодженого між прошивкою ASP та ядром під час старту ВМ.
5. **Виклик Hypercall**: Драйвер заповнює захищену сторінку GHCB (Guest-Hypervisor Communication Block) і виконує інструкцію `VMGEXIT`, передаючи керування апаратурі.
6. **Дешифрування та підпис апаратурою**: Співпроцесор ASP розшифровує повідомлення, обчислює підпис ключем VCEK і повертає відповідь.

---

## 2. Повна реалізація мовами C та C++

Нижче наведено два повноцінні варіанти реалізації демона атестації. Варіант мовою C спирається на прямі системні виклики POSIX, явний контроль пам'яті через `memset()` та `memcpy()`, а також класичну обробку помилок. Варіант мовою C++23 демонструє ідіоматичний об'єктно-орієнтований підхід із використанням RAII-обгортки для файлових дескрипторів, концепції неволодіючих зрізів пам'яті `std::span` та монодичної обробки помилок за допомогою `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/random.h>
#include <sys/types.h>
#include <linux/types.h>

/* Локальне оголошення системних структур для AMD SEV-SNP */
#ifndef SNP_GET_REPORT

struct snp_report_req {
    __u8 user_data[64];
    __u32 vmpl;
    __u8 rsvd[28];
};

struct snp_report_resp {
    __u8 data[4000];
};

struct snp_guest_request_ioctl {
    __u8 msg_version;
    __u64 req_data;
    __u64 resp_data;
    __u64 fw_error;
};

#define SNP_GUEST_REQ_IOC_TYPE 'S'
#define SNP_GET_REPORT _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, struct snp_guest_request_ioctl)

#endif

/* Функція генерації кріптографічно стійкого nonce */
static int generate_secure_nonce(unsigned char nonce[64]) {
    ssize_t ret = getrandom(nonce, 64, 0);
    if (ret != 64) {
        perror("Помилка генерації випадкових даних через getrandom()");
        return -1;
    }
    return 0;
}

/* Функція звернення до пристрою AMD SEV-SNP */
static int fetch_sev_snp_report(const unsigned char nonce[64], unsigned char out_measurement[48]) {
    int fd = open("/dev/sev-guest", O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити символьний пристрій /dev/sev-guest");
        return -1;
    }

    struct snp_report_req req;
    struct snp_report_resp resp;
    struct snp_guest_request_ioctl ioctl_req;

    /* Явне занулення пам'яті для запобігання витоку даних зі стака */
    memset(&req, 0, sizeof(req));
    memset(&resp, 0, sizeof(resp));
    memset(&ioctl_req, 0, sizeof(ioctl_req));

    memcpy(req.user_data, nonce, 64);
    req.vmpl = 0; /* Виклик від імені найвищого рівня привілеїв ВМ VMPL0 */

    ioctl_req.msg_version = 1;
    ioctl_req.req_data = (unsigned long)&req;
    ioctl_req.resp_data = (unsigned long)&resp;

    printf("[C-Driver] Надсилання ioctl(SNP_GET_REPORT) до апаратного процесора ASP...\n");
    if (ioctl(fd, SNP_GET_REPORT, &ioctl_req) < 0) {
        perror("[C-Driver] Помилка системного виклику ioctl");
        if (ioctl_req.fw_error != 0) {
            fprintf(stderr, "[C-Driver] Апаратна відмова прошивки ASP. Код: 0x%llx\n", 
                    (unsigned long long)ioctl_req.fw_error);
        }
        close(fd);
        return -1;
    }

    /* 
     * Хеш виміру SHA-384 (Launch Measurement Digest) розташовано за зсувом 0x98 
     * у структурі snp_attestation_report (довжина 48 байтів)
     */
    memcpy(out_measurement, &resp.data[0x98], 48);

    /* Перевірка ехо-відповіді user_data у звіті (зсув 0x58) */
    if (memcmp(&resp.data[0x58], nonce, 64) != 0) {
        fprintf(stderr, "[C-Driver] КРИТИЧНА ПОМИЛКА: Nonce у звіті не збігається з переданим!\n");
        close(fd);
        return -1;
    }

    close(fd);
    return 0;
}

int main(void) {
    unsigned char nonce[64];
    unsigned char measurement[48];

    printf("=== Демон атестації AMD SEV-SNP (Мова C) ===\n");

    if (generate_secure_nonce(nonce) != 0) {
        return EXIT_FAILURE;
    }

    if (fetch_sev_snp_report(nonce, measurement) == 0) {
        printf("Успішно отримано та валідовано SHA-384 Launch Digest ВМ:\n");
        for (int i = 0; i < 48; i++) {
            printf("%02x", measurement[i]);
        }
        printf("\n");
        return EXIT_SUCCESS;
    } else {
        fprintf(stderr, "Процедура атестації завершилася помилкою.\n");
        return EXIT_FAILURE;
    }
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <array>
#include <span>
#include <vector>
#include <system_error>
#include <expected>
#include <memory>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/random.h>
#include <linux/types.h>

namespace confidential_compute {

#ifndef SNP_GET_REPORT
struct snp_report_req {
    __u8 user_data[64];
    __u32 vmpl;
    __u8 rsvd[28];
};

struct snp_report_resp {
    __u8 data[4000];
};

struct snp_guest_request_ioctl {
    __u8 msg_version;
    __u64 req_data;
    __u64 resp_data;
    __u64 fw_error;
};

#define SNP_GUEST_REQ_IOC_TYPE 'S'
#define SNP_GET_REPORT _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, struct snp_guest_request_ioctl)
#endif

// RAII класу-обгортки для файлового дескриптора POSIX
class SafeFileDescriptor {
    int fd_{-1};
public:
    explicit SafeFileDescriptor(const char* path, int flags) noexcept
        : fd_{::open(path, flags)} {}
    
    ~SafeFileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SafeFileDescriptor(const SafeFileDescriptor&) = delete;
    SafeFileDescriptor& operator=(const SafeFileDescriptor&) = delete;
    
    SafeFileDescriptor(SafeFileDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

struct SevAttestationData {
    std::array<uint8_t, 48> launch_measurement{};
    uint64_t firmware_error_code{0};
};

enum class AttestationError {
    DeviceOpenFailed,
    RandomGenerationFailed,
    IoctlFailed,
    NonceMismatch,
    FirmwareError
};

class AttestationService {
public:
    [[nodiscard]] static auto generate_nonce() 
        -> std::expected<std::array<uint8_t, 64>, AttestationError> 
    {
        std::array<uint8_t, 64> nonce{};
        if (::getrandom(nonce.data(), nonce.size(), 0) != static_cast<ssize_t>(nonce.size())) {
            return std::unexpected(AttestationError::RandomGenerationFailed);
        }
        return nonce;
    }

    [[nodiscard]] static auto request_snp_report(std::span<const uint8_t, 64> nonce) 
        -> std::expected<SevAttestationData, AttestationError> 
    {
        SafeFileDescriptor dev("/dev/sev-guest", O_RDWR);
        if (!dev.is_valid()) {
            std::cerr << "[C++ Driver] Не вдалося відкрити /dev/sev-guest (errno: " << errno << ")\n";
            return std::unexpected(AttestationError::DeviceOpenFailed);
        }

        snp_report_req req{};
        snp_report_resp resp{};
        snp_guest_request_ioctl ioctl_req{};

        std::memcpy(req.user_data, nonce.data(), nonce.size());
        req.vmpl = 0; // VMPL0

        ioctl_req.msg_version = 1;
        ioctl_req.req_data = reinterpret_cast<uint64_t>(&req);
        ioctl_req.resp_data = reinterpret_cast<uint64_t>(&resp);

        if (::ioctl(dev.get(), SNP_GET_REPORT, &ioctl_req) < 0) {
            if (ioctl_req.fw_error != 0) {
                std::cerr << "[C++ Driver] Помилка прошивки ASP: 0x" 
                          << std::hex << ioctl_req.fw_error << std::dec << "\n";
            }
            return std::unexpected(AttestationError::IoctlFailed);
        }

        // Перевірка ехо Nonce у вихідній структурі (зсув 0x58)
        if (std::memcmp(&resp.data[0x58], nonce.data(), 64) != 0) {
            return std::unexpected(AttestationError::NonceMismatch);
        }

        SevAttestationData result{};
        result.firmware_error_code = ioctl_req.fw_error;
        std::memcpy(result.launch_measurement.data(), &resp.data[0x98], result.launch_measurement.size());

        return result;
    }
};

} // namespace confidential_compute

int main() {
    using namespace confidential_compute;
    std::cout << "=== Демон атестації AMD SEV-SNP (Мова C++23/RAII) ===\n";

    auto nonce_res = AttestationService::generate_nonce();
    if (!nonce_res) {
        std::cerr << "Не вдалося згенерувати бепечний nonce.\n";
        return EXIT_FAILURE;
    }

    auto report_res = AttestationService::request_snp_report(*nonce_res);
    if (report_res) {
        std::cout << "Успішно завантажено та перевірено Measurement Digest (SHA-384):\n";
        std::cout << std::hex << std::setfill('0');
        for (uint8_t byte : report_res->launch_measurement) {
            std::cout << std::setw(2) << static_cast<int>(byte);
        }
        std::cout << std::dec << "\n";
        return EXIT_SUCCESS;
    } else {
        std::cerr << "Помилка отримання атестаційного звіту.\n";
        return EXIT_FAILURE;
    }
}
```
:::

---

## 3. Детальний покроковий розбір коду

Аналіз ключових викликів та структурних елементів у поданих прикладах:

### Виклик `getrandom()` для створення стійкого Nonce
Створення 64 байтів криптографічного вектору виконується за допомогою системного виклику `getrandom(nonce, 64, 0)`. На відміну від застарілих функцій `rand()` або `random()`, системний виклик `getrandom()` звертається безпосередньо до внутрішнього криптографічного генератора ядра Linux (CSPRNG), який ініціалізується за допомогою ентропії апаратних подій CPU (інструкції `RDRAND` / `RDSEED`). Використання 64 випадкових байтів гарантує, що кожен згенерований атестаційний звіт є унікальним у часі.

### Використання модифікаторів макросів `_IOWR`
Макрос `_IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, struct snp_guest_request_ioctl)` кодує в 32-бітному цілому числі номер команди, напрямок передачі даних (вхід та вихід `_IOWR`), тип сімейства (`'S'`) та точний розмір керуючої структури. Це дозволяє ядру Linux на етапі обробки системного виклику перевірити, що переданий із простору користувача вказівник є дійсним і за адресою знаходиться достатній обсяг виділеної пам'яті.

### Гарантія ресурсного очищення у C++23 (RAII)
У версії мовою C++ застосовано клас `SafeFileDescriptor`, який реалізує паттерн RAII (Resource Acquisition Is Initialization). Конструктор відкриває файл пристрою, а деструктор гарантовано викликає `close()`, навіть якщо під час виконання виклику `ioctl()` або обробки пам'яті буде згенеровано виняток (exception). Конструктор копіювання та оператор присвоєння явно видалені (`= delete`), що унеможливлює випадкове подвійне закриття файлового дескриптора (double free / double close).

---

## 4. Практичні підводні камені та крайні випадки (Edge Cases)

При розгортанні демонів атестації у виробничому середовищі хмари інженери зіштовхуються з кількома специфічними проблемами:

1. **Переповнення лічильника послідовностей `vmpck_seq`**: Оскільки кожне зчитування звіту через `/dev/sev-guest` збільшує лічильник послідовності `vmpck_seq` у процесорі ASP, при досягненні максимального значення `2^32 - 1` співпроцесор ASP відмовиться видавати нові звіти і почне повертати код помилки `0x3B` (`VMPCK_INVALID`). У цьому разі гостьова ОС вимагає перезавантаження або процедури повторного узгодження ключів перевірки (re-keying). Тому демони атестації **не повинні викликати ioctl у нескінченному циклі polling**, а мають запитувати звіт лише при старті ВМ чи оновленні ключів TLS.
2. **Обмеження прав доступу в непривілейованих контейнерах**: Якщо демон атестації запускається всередині Docker/Kubernetes контейнера на конфіденційній ВМ, файл `/dev/sev-guest` за замовчуванням недоступний. Необхідно явно прокидати пристрій у конфігурації pod:
   ```yaml
   securityContext:
     devices:
       - hostPath: /dev/sev-guest
         containerPath: /dev/sev-guest
   ```
3. **Поведінка при живій міграції (Live Migration)**: Під час живої міграції ВМ на інший хост значення ідентифікаторів `report_id` та `platform_version` змінюються, оскільки новий хостовий сервер може мати іншу версію мікрокоду CPU (TCB). Демон атестації повинен уміти обробляти зміну підпису та запитувати новий звіт після завершення процедури міграції.
4. **Обробка викликів у підключених модулях прошивок (Busy Retry Loop)**: Співпроцесор AMD ASP є однопотоковим мікроконтролером (ARM Cortex-A5). Якщо одночасно кілька процесів гостя запитують атестацію, прошивка повертає код помилки `0x1A` (`BUSY`). Продуктивний демон атестації повинен реалізовувати повторні спроби виклику з експоненціальною затримкою (exponential backoff).
