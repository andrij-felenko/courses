# ⚙️ Перевірка підтримки вкладеної віртуалізації KVM через ioctl

Цей проєкт демонструє практичну реалізацію низькорівневої програми на мовах C та C++, яка розмовляє безпосередньо з інтерфейсом ядра KVM через системний виклик `ioctl`. Програма призначена для діагностики апаратної віртуалізації host-системи, перевірки підтримки вкладеної віртуалізації (Nested Virtualization) у підсистемі KVM та зчитування поточних параметрів модуля ядра у системній файловій системі sysfs.

Взаємодія з KVM відбувається без використання високорівневих бібліотек управління (таких як libvirt чи QEMU), що дозволяє наочно простежить механіку роботи системних викликів ядра Linux, правильне виділення пам'яті під динамічні структури `ioctl` та обробку апаратних прапорців CPUID.

## 1. Архітектурні вимоги та порядок викликів KVM API

Взаємодія користувальницького застосунку з драйвером KVM підпорядковується чіткому протоколу послідовних системних викликів:

1. **Відкриття символьного пристрою `/dev/kvm`:** Драйвер KVM експортує глобальний файловий пристрій `/dev/kvm`. Процес відкриває цей файл із прапорцями `O_RDWR | O_CLOEXEC`. Отриманий файловий дескриптор являє собою системний контекст KVM (KVM System FD).
2. **Перевірка версії API (`KVM_GET_API_VERSION`):** Перед виконанням будь-яких дій програма повинна переконатися, що ядро Linux підтримує поточну версію інтерфейсу KVM. Константа `KVM_API_VERSION` у сучасних ядрах Linux дорівнює `12`. Якщо виклик `ioctl(kvm_fd, KVM_GET_API_VERSION, 0)` повертає число, відмінне від `12`, продовження роботи є небезпечним через можливу несумісність бінарного ABI.
3. **Виділення пам'яті під структуру `struct kvm_cpuid2`:** Отримання списку підтримуваних функцій процесора здійснюється за допомогою `ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid_struct)`. Особливістю структури `struct kvm_cpuid2` є те, що вона має змінну довжину. Заголовок містить кількість елементів `nent`, за якими у пам'яті розміщується масив структур `struct kvm_cpuid_entry2`. Програма повинна виділити динамічну пам'ять необхідного розміру (зазвичай розраховану на 64 або 128 записів), інакше ядро поверне помилку `EFAULT` або обріже список.
4. **Парсинг прапорців VMX та SVM:**
   - **Intel VT-x (VMX):** Перевіряється у листку CPUID `0x00000001`. Регістр `ECX`, біт 5 (`1 << 5`) означає наявність VMX.
   - **AMD-V (SVM):** Перевіряється у розширеному листку CPUID `0x80000001`. Регістр `ECX`, біт 2 (`1 << 2`) означає наявність SVM.
5. **Зчитування параметрів модуля у sysfs:** Наявність підтримки VMX/SVM у CPUID свідчить про те, що процесор та ядро *здатні* виконувати віртуалізацію. Проте чи дозволено саме вкладену віртуалізацію, визначається параметром модуля ядра `/sys/module/kvm_intel/parameters/nested` або `/sys/module/kvm_amd/parameters/nested`. Програма зчитує вміст цих файлів і перевіряє значення (`1`/`Y`).

## 2. Реалізація C та C++

У реалізації мовою C використано прямі POSIX виклики `open`, `read`, `close` та `malloc`. У реалізації мовою C++ застосовано ідіому RAII для автоматичного управління файловим дескриптором, безпечні контейнери `std::vector`, сучасний механізм обробки помилок `std::expected` (C++23) та типізовані константи `constexpr`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

#define VMX_BIT (1 << 5)  /* CPUID.01H:ECX bit 5 */
#define SVM_BIT (1 << 2)  /* CPUID.80000001H:ECX bit 2 */

static int check_sysfs_nested(const char *module_name) {
    char path[128];
    snprintf(path, sizeof(path), "/sys/module/%s/parameters/nested", module_name);
    
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    
    char buf[8] = {0};
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    if (n > 0) {
        if (buf[0] == 'Y' || buf[0] == 'y' || buf[0] == '1') {
            return 1;
        }
        return 0;
    }
    return -1;
}

int main(void) {
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return EXIT_FAILURE;
    }

    int api_ver = ioctl(kvm_fd, KVM_GET_API_VERSION, 0);
    if (api_ver != KVM_API_VERSION) {
        fprintf(stderr, "Невідповідність KVM API: очікується %d, отримано %d\n", KVM_API_VERSION, api_ver);
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    /* Виділяємо пам'ять під 64 записи CPUID */
    int nent = 64;
    size_t sz = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
    struct kvm_cpuid2 *cpuid = (struct kvm_cpuid2 *)malloc(sz);
    if (!cpuid) {
        perror("Помилка виділення пам'яті");
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    memset(cpuid, 0, sz);
    cpuid->nent = nent;

    if (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
        perror("Помилка KVM_GET_SUPPORTED_CPUID");
        free(cpuid);
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    int has_vmx = 0;
    int has_svm = 0;

    for (__u32 i = 0; i < cpuid->nent; i++) {
        if (cpuid->entries[i].function == 0x01) {
            if (cpuid->entries[i].ecx & VMX_BIT) {
                has_vmx = 1;
            }
        } else if (cpuid->entries[i].function == 0x80000001) {
            if (cpuid->entries[i].ecx & SVM_BIT) {
                has_svm = 1;
            }
        }
    }

    printf("=== Перевірка апаратних розширень у KVM ===\n");
    printf("Intel VT-x (VMX) у CPUID: %s\n", has_vmx ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ");
    printf("AMD-V (SVM) у CPUID:     %s\n", has_svm ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ");

    int sysfs_intel = check_sysfs_nested("kvm_intel");
    int sysfs_amd = check_sysfs_nested("kvm_amd");

    printf("\n=== Стан sysfs nested у хостовому ядрі ===\n");
    if (sysfs_intel >= 0) {
        printf("kvm_intel.nested: %s\n", sysfs_intel ? "УВІМКНЕНО (1/Y)" : "ВИМКНЕНО (0/N)");
    }
    if (sysfs_amd >= 0) {
        printf("kvm_amd.nested:   %s\n", sysfs_amd ? "УВІМКНЕНО (1/Y)" : "ВИМКНЕНО (0/N)");
    }

    free(cpuid);
    close(kvm_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <memory>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

class KvmDevice {
public:
    static std::expected<KvmDevice, std::error_code> open_default() {
        int fd = ::open("/dev/kvm", O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return KvmDevice(fd);
    }

    ~KvmDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    KvmDevice(const KvmDevice&) = delete;
    KvmDevice& operator=(const KvmDevice&) = delete;

    KvmDevice(KvmDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    KvmDevice& operator=(KvmDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    std::expected<int, std::error_code> get_api_version() const {
        int ver = ::ioctl(fd_, KVM_GET_API_VERSION, 0);
        if (ver < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return ver;
    }

    struct CpuFlags {
        bool vmx{false};
        bool svm{false};
    };

    std::expected<CpuFlags, std::error_code> get_supported_cpu_flags() const {
        constexpr uint32_t nent = 64;
        const size_t alloc_size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
        
        std::vector<uint8_t> buffer(alloc_size, 0);
        auto* cpuid = reinterpret_cast<struct kvm_cpuid2*>(buffer.data());
        cpuid->nent = nent;

        if (::ioctl(fd_, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        CpuFlags flags{};
        constexpr uint32_t vmx_bit = 1 << 5;
        constexpr uint32_t svm_bit = 1 << 2;

        for (uint32_t i = 0; i < cpuid->nent; ++i) {
            const auto& entry = cpuid->entries[i];
            if (entry.function == 0x01) {
                if (entry.ecx & vmx_bit) flags.vmx = true;
            } else if (entry.function == 0x80000001) {
                if (entry.ecx & svm_bit) flags.svm = true;
            }
        }
        return flags;
    }

private:
    explicit KvmDevice(int fd) : fd_(fd) {}
    int fd_{-1};
};

static std::expected<bool, std::error_code> check_sysfs_parameter(const std::string& module_name) {
    std::string path = "/sys/module/" + module_name + "/parameters/nested";
    std::ifstream file(path);
    if (!file.is_open()) {
        return std::unexpected(std::error_code(ENOENT, std::generic_category()));
    }
    char val = 0;
    file >> val;
    return (val == 'Y' || val == 'y' || val == '1');
}

int main() {
    auto kvm_res = KvmDevice::open_default();
    if (!kvm_res) {
        std::cerr << "Не вдалося відкрити /dev/kvm: " << kvm_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    const auto& kvm = *kvm_res;
    auto api_ver = kvm.get_api_version();
    if (!api_ver || *api_ver != KVM_API_VERSION) {
        std::cerr << "Невідповідність KVM API\n";
        return EXIT_FAILURE;
    }

    auto flags_res = kvm.get_supported_cpu_flags();
    if (!flags_res) {
        std::cerr << "Помилка читання CPUID прапорців: " << flags_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    const auto& flags = *flags_res;
    std::cout << "=== Перевірка апаратних розширень (C++ RAII) ===\n";
    std::cout << "Intel VT-x (VMX): " << (flags.vmx ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ") << '\n';
    std::cout << "AMD-V (SVM):     " << (flags.svm ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ") << '\n';

    std::cout << "\n=== Стан sysfs parameters ===\n";
    if (auto intel_nested = check_sysfs_parameter("kvm_intel")) {
        std::cout << "kvm_intel.nested: " << (*intel_nested ? "УВІМКНЕНО" : "ВИМКНЕНО") << '\n';
    }
    if (auto amd_nested = check_sysfs_parameter("kvm_amd")) {
        std::cout << "kvm_amd.nested:   " << (*amd_nested ? "УВІМКНЕНО" : "ВИМКНЕНО") << '\n';
    }

    return EXIT_SUCCESS;
}
```
:::

## 3. Глибокий розбір пасток та крайових випадків

Під час реалізації низькорівневого коду для роботи з KVM розробники часто стикаються з серією тонких помилок:

- **Пастка з виділенням пам'яті під `kvm_cpuid2`:** Структура `struct kvm_cpuid2` у заголовочному файлі `<linux/kvm.h>` визначена як заголовок із масивом нулевої довжини наприкінці (`struct kvm_cpuid_entry2 entries[0]`). Якщо оголосити змінну цієї структури на стеку `struct kvm_cpuid2 cpuid;`, її розмір складе лише 8 байтів. При передачі цієї структури у `ioctl` ядро Linux спробує записати десятки елементів у пам'ять за межами структури, що призведе до руйнування стека (Stack Smashing) та негайного збою сигналу `SIGSEGV`. Потрібно обов'язково виділяти буфер динамічно з урахуванням `nent * sizeof(struct kvm_cpuid_entry2)`.
- **Прапорець `O_CLOEXEC` при відкритті `/dev/kvm`:** Завжди відкривайте дескриптор `/dev/kvm` із прапорцем `O_CLOEXEC`. Якщо застосунок пізніше виконає системний виклик `execve()` для запуску дочірнього процесу (наприклад, виконуючи скрипт розгортання ВМ), відкритий дескриптор KVM витече у дочірній процес, блокуючи можливість вивантаження або перезавантаження модулів ядра `kvm_intel`/`kvm_amd`.
- **Різниця між `KVM_GET_SUPPORTED_CPUID` та `KVM_GET_EMULATED_CPUID`:** Запит `KVM_GET_SUPPORTED_CPUID` повертає лише ті функції CPUID, які апаратно підтримуються поточним фізичним CPU і можуть виконуватися з апаратною швидкістю. Запит `KVM_GET_EMULATED_CPUID` повертає функції, які фізичний процесор не підтримує, але ядро KVM здатне емулювати програмно. Прапорець VMX для вкладеності має сенс перевіряти саме у `KVM_GET_SUPPORTED_CPUID`, оскільки програмна емуляція VMX без апаратної підтримки є вкрай повільною.
- **Встановлення конфігурації ВМ через `KVM_SET_CPUID2`:** Проста перевірка `KVM_GET_SUPPORTED_CPUID` не вмикає VMX у ВМ автоматично. Демони керування ВМ (такі як QEMU або kvmtool) під час створення віртуального процесора VCPU повинні викликати `ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid_struct)`, явно встановивши біт VMX у списку переданих функцій. Якщо цього не зробити, KVM не виділить структури `nested_vmx` для VCPU, і спроба гостя виконати `VMON` завершиться винятком `#UD`.
- **Обробка помилок `E2BIG` при запиті CPUID:** Якщо ядро KVM підтримує більше елементів CPUID, ніж програма вказала у полі `cpuid->nent`, виклик `ioctl` повертає помилку `-E2BIG`, а значення `cpuid->nent` оновлюється реальним необхідним числом. Рекомендований підхід — виконувати повторний виклик `ioctl` після збільшення розміру бувера до значення `nent`, яке повернуло ядро.
- **Права доступу до `/dev/kvm`:** Стандартно символьний пристрій `/dev/kvm` належить користувачеві `root` та групі `kvm` із правами `0660`. Якщо програма запускається від імені звичайного користувача без включення до групи `kvm`, виклик `open("/dev/kvm")` завершиться помилкою `EACCES` (Permission denied).
