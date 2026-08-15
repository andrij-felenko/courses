# ⚙️ Міні-гіпервізор на KVM: реалізація тестового контейнера виконання

Практична реалізація власного міні-гіпервізора є найкращим способом зрозуміти взаємодію між користувацьким простором та підсистемою KVM ядра Linux. Наведений нижче приклад створює віртуальну машину, виділяє для неї 2 МіБ фізичної пам'яті, завантажує бінарний машинний код у режимі 16-бітного Real Mode, налаштовує сегментні регістри та регістри загального призначення vCPU і здійснює цикл обробки виходів `KVM_RUN` із перехопленням операцій запису у порт I/O `0x10`.

Тестова гостьова програма складається з таких інструкцій x86:

```assembly
mov $0x48, %al  ; Завантажити символ 'H' у регістр AL
out %al, $0x10  ; Вивести символ 'H' у порт I/O 0x10 (викличе KVM_EXIT_IO)
mov $0x49, %al  ; Завантажити символ 'I' у регістр AL
out %al, $0x10  ; Вивести символ 'I' у порт I/O 0x10
hlt             ; Зупинити процесор (викличе KVM_EXIT_HLT)
```

Машинний байт-код цієї програми у 16-бітному режимі Real Mode: `\xb0\x48\xe6\x10\xb0\x49\xe6\x10\xf4`.

## Архітектурні етапи створення гіпервізора

Реалізація контейнера виконання KVM складається з семи послідовних кроків, кожен з яких ініціалізує відповідний шар апаратної віртуалізації:

1. **Ініціалізація підсистеми KVM:** Програма відкриває системний пристрій `/dev/kvm` за допомогою системного виклику `open("/dev/kvm", O_RDWR | O_CLOEXEC)` і перевіряє сумісність версії API викликом `ioctl(KVM_GET_API_VERSION)`. Повернуте значення мусить дорівнювати `12`.
2. **Створення екземпляра VM:** Викликом `ioctl(KVM_CREATE_VM)` створюється новий дескриптор віртуальної машини `vm_fd`, який виділяє унікальний простір адрес (GPA) та готує контекст для слотів пам'яті.
3. **Виділення та реєстрація пам'яті:** За допомогою системного виклику `mmap()` виділяється анонімна пам'ять у хості (HVA), після чого вона прив'язується до фізичної адреси гостя GPA 0x00000000 через структуру `struct kvm_userspace_memory_region` і виклик `KVM_SET_USER_MEMORY_REGION`.
4. **Створення vCPU та спільної пам'яті:** Створюється дескриптор віртуального процесора `vcpu_fd` викликом `KVM_CREATE_VCPU`. Далі через `mmap()` на файловому дескрипторі `vcpu_fd` отримується вказівник на структуру `struct kvm_run`, яка слугує спільним буфером зв'язку між ядром та користувацьким простором.
5. **Завантаження машинного коду:** Масив байтів гостьової програми копіюється безпосередньо в область пам'яті, виділену на кроці 3 за адресою зсуву `0x0000`.
6. **Конфігурація регістрів vCPU:** За допомогою `KVM_GET_SREGS` та `KVM_SET_SREGS` сегментний регістр `CS` налаштовується на базову адресу `0x0000` та селектор `0x0000`. За допомогою `KVM_SET_REGS` регістр `RIP` встановлюється в `0x0000`, а прапори `RFLAGS` отримують значення `0x0002` (обов'язковий біт 1 за специфікацією x86).
7. **Головний цикл виконання (Execution Loop):** У нескінченному циклі викликається `ioctl(vcpu_fd, KVM_RUN, 0)`. При поверненні перевіряється поле `run->exit_reason`. Якщо це `KVM_EXIT_IO` на порт `0x10`, дані зчитуються зі зсуву `run->io.data_offset` і виводяться у консоль. При виході `KVM_EXIT_HLT` цикл завершується.

## Двомовна реалізація: C та C++

Нижче наведено дві повноцінні реалізації міні-гіпервізора: класичний C-код на базі низькорівневих системних викликів POSIX та ідіоматичний C++20 код із використанням RAII-обгорток для ресурсів, винятків замість кодів помилок і `std::span` замість пари «вказівник + довжина».

:::tabs
== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

#define RAM_SIZE (2 * 1024 * 1024)

int main(void) {
    // 1. Відкриття /dev/kvm
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    // Перевірка версії API KVM
    int api_ver = ioctl(kvm_fd, KVM_GET_API_VERSION, 0);
    if (api_ver != 12) {
        fprintf(stderr, "Непідтримувана версія KVM API: %d\n", api_ver);
        close(kvm_fd);
        return 1;
    }

    // 2. Створення віртуальної машини
    int vm_fd = ioctl(kvm_fd, KVM_CREATE_VM, 0);
    if (vm_fd < 0) {
        perror("Помилка KVM_CREATE_VM");
        close(kvm_fd);
        return 1;
    }

    // 3. Виділення RAM для гостя
    void *mem = mmap(NULL, RAM_SIZE, PROT_READ | PROT_WRITE,
                     MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (mem == MAP_FAILED) {
        perror("Помилка mmap RAM");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // Реєстрація слота пам'яті в KVM (GPA 0x00000000 -> HVA mem)
    struct kvm_userspace_memory_region region = {
        .slot = 0,
        .flags = 0,
        .guest_phys_addr = 0x0,
        .memory_size = RAM_SIZE,
        .userspace_addr = (unsigned long)mem,
    };
    if (ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION, &region) < 0) {
        perror("Помилка KVM_SET_USER_MEMORY_REGION");
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 4. Створення віртуального процесора (vCPU 0)
    int vcpu_fd = ioctl(vm_fd, KVM_CREATE_VCPU, 0);
    if (vcpu_fd < 0) {
        perror("Помилка KVM_CREATE_VCPU");
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // Відображення структури kvm_run у простір користувача
    int mmap_size = ioctl(kvm_fd, KVM_GET_VCPU_MMAP_SIZE, 0);
    if (mmap_size < 0) {
        perror("Помилка KVM_GET_VCPU_MMAP_SIZE");
        close(vcpu_fd);
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    struct kvm_run *run = mmap(NULL, mmap_size, PROT_READ | PROT_WRITE,
                               MAP_SHARED, vcpu_fd, 0);
    if (run == MAP_FAILED) {
        perror("Помилка mmap struct kvm_run");
        close(vcpu_fd);
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 5. Завантаження гостьового коду за адресою 0x0000
    const unsigned char code[] = {
        0xb0, 0x48,             // mov $0x48, %al  ('H')
        0xe6, 0x10,             // out %al, $0x10
        0xb0, 0x49,             // mov $0x49, %al  ('I')
        0xe6, 0x10,             // out %al, $0x10
        0xf4                    // hlt
    };
    memcpy(mem, code, sizeof(code));

    // 6. Налаштування початкових регістрів vCPU
    struct kvm_sregs sregs;
    if (ioctl(vcpu_fd, KVM_GET_SREGS, &sregs) < 0) {
        perror("Помилка KVM_GET_SREGS");
        goto cleanup;
    }
    sregs.cs.base = 0;
    sregs.cs.selector = 0;
    if (ioctl(vcpu_fd, KVM_SET_SREGS, &sregs) < 0) {
        perror("Помилка KVM_SET_SREGS");
        goto cleanup;
    }

    struct kvm_regs regs = {
        .rip = 0x0,
        .rflags = 0x2, // Обов'язковий біт 1 у прапорах x86
    };
    if (ioctl(vcpu_fd, KVM_SET_REGS, &regs) < 0) {
        perror("Помилка KVM_SET_REGS");
        goto cleanup;
    }

    // 7. Головний цикл виконання vCPU (Execution Loop)
    printf("Запуск міні-гіпервізора KVM...\nГостьовий вивід: ");
    fflush(stdout);

    int running = 1;
    while (running) {
        if (ioctl(vcpu_fd, KVM_RUN, 0) < 0) {
            perror("Помилка KVM_RUN");
            break;
        }

        switch (run->exit_reason) {
            case KVM_EXIT_IO:
                if (run->io.direction == KVM_EXIT_IO_OUT && run->io.port == 0x10) {
                    char *data = (char *)run + run->io.data_offset;
                    putchar(*data);
                    fflush(stdout);
                }
                break;

            case KVM_EXIT_HLT:
                printf("\n[KVM] Гість виконав інструкцію HLT. Завершення.\n");
                running = 0;
                break;

            case KVM_EXIT_FAIL_ENTRY:
                fprintf(stderr, "\n[KVM] Апаратна помилка входу: 0x%llx\n",
                        (unsigned long long)run->fail_entry.hardware_entry_failure_reason);
                running = 0;
                break;

            default:
                fprintf(stderr, "\n[KVM] Необроблена причина виходу: %d\n", run->exit_reason);
                running = 0;
                break;
        }
    }

cleanup:
    munmap(run, mmap_size);
    close(vcpu_fd);
    munmap(mem, RAM_SIZE);
    close(vm_fd);
    close(kvm_fd);
    return 0;
}
```

== C++
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

// RAII обгортка для файлового дескриптора POSIX
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для відображеної пам'яті mmap
class MappedMemory {
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
public:
    MappedMemory(void* addr, std::size_t size) : addr_(addr), size_(size) {}
    ~MappedMemory() {
        if (addr_ != MAP_FAILED && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    MappedMemory(const MappedMemory&) = delete;
    MappedMemory& operator=(const MappedMemory&) = delete;

    MappedMemory(MappedMemory&& other) noexcept 
        : addr_(other.addr_), size_(other.size_) {
        other.addr_ = MAP_FAILED;
        other.size_ = 0;
    }

    [[nodiscard]] void* get() const noexcept { return addr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
};

class MiniHypervisor {
    static constexpr std::size_t kRamSize = 2 * 1024 * 1024;
    
    UniqueFd kvm_fd_{-1};
    UniqueFd vm_fd_{-1};
    UniqueFd vcpu_fd_{-1};
    MappedMemory ram_{MAP_FAILED, 0};
    MappedMemory run_mmap_{MAP_FAILED, 0};
    struct kvm_run* run_{nullptr};

public:
    MiniHypervisor() {
        // 1. Відкриття /dev/kvm
        kvm_fd_ = UniqueFd{::open("/dev/kvm", O_RDWR | O_CLOEXEC)};
        if (!kvm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /dev/kvm");
        }

        int api_ver = ::ioctl(kvm_fd_.get(), KVM_GET_API_VERSION, 0);
        if (api_ver != 12) {
            throw std::runtime_error("Непідтримувана версія KVM API: " + std::to_string(api_ver));
        }

        // 2. Створення VM
        vm_fd_ = UniqueFd{::ioctl(kvm_fd_.get(), KVM_CREATE_VM, 0)};
        if (!vm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_CREATE_VM");
        }

        // 3. Виділення RAM
        void* ram_ptr = ::mmap(nullptr, kRamSize, PROT_READ | PROT_WRITE,
                               MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (ram_ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap RAM");
        }
        ram_ = MappedMemory{ram_ptr, kRamSize};

        struct kvm_userspace_memory_region region{
            .slot = 0,
            .flags = 0,
            .guest_phys_addr = 0x0,
            .memory_size = kRamSize,
            .userspace_addr = reinterpret_cast<std::uint64_t>(ram_.get()),
        };
        if (::ioctl(vm_fd_.get(), KVM_SET_USER_MEMORY_REGION, &region) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_USER_MEMORY_REGION");
        }

        // 4. Створення vCPU
        vcpu_fd_ = UniqueFd{::ioctl(vm_fd_.get(), KVM_CREATE_VCPU, 0)};
        if (!vcpu_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_CREATE_VCPU");
        }

        int mmap_size = ::ioctl(kvm_fd_.get(), KVM_GET_VCPU_MMAP_SIZE, 0);
        if (mmap_size < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_GET_VCPU_MMAP_SIZE");
        }

        void* run_ptr = ::mmap(nullptr, static_cast<std::size_t>(mmap_size), 
                               PROT_READ | PROT_WRITE, MAP_SHARED, vcpu_fd_.get(), 0);
        if (run_ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap struct kvm_run");
        }
        run_mmap_ = MappedMemory{run_ptr, static_cast<std::size_t>(mmap_size)};
        run_ = static_cast<struct kvm_run*>(run_mmap_.get());
    }

    void load_payload(std::span<const std::uint8_t> payload) {
        if (payload.size() > ram_.size()) {
            throw std::invalid_argument("Розмір коду перевищує RAM");
        }
        std::memcpy(ram_.get(), payload.data(), payload.size());
    }

    void setup_registers() {
        struct kvm_sregs sregs{};
        if (::ioctl(vcpu_fd_.get(), KVM_GET_SREGS, &sregs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_GET_SREGS");
        }
        sregs.cs.base = 0;
        sregs.cs.selector = 0;
        if (::ioctl(vcpu_fd_.get(), KVM_SET_SREGS, &sregs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_SREGS");
        }

        struct kvm_regs regs{
            .rip = 0x0,
            .rflags = 0x2,
        };
        if (::ioctl(vcpu_fd_.get(), KVM_SET_REGS, &regs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_REGS");
        }
    }

    void run() {
        std::cout << "Запуск міні-гіпервізора KVM (C++ RAII)...\nГостьовий вивід: " << std::flush;

        bool running = true;
        while (running) {
            if (::ioctl(vcpu_fd_.get(), KVM_RUN, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка KVM_RUN");
            }

            switch (run_->exit_reason) {
                case KVM_EXIT_IO:
                    if (run_->io.direction == KVM_EXIT_IO_OUT && run_->io.port == 0x10) {
                        const char* data = reinterpret_cast<const char*>(run_) + run_->io.data_offset;
                        std::cout << *data << std::flush;
                    }
                    break;

                case KVM_EXIT_HLT:
                    std::cout << "\n[KVM] Гість виконав HLT. Завершення.\n";
                    running = false;
                    break;

                case KVM_EXIT_FAIL_ENTRY:
                    std::cerr << "\n[KVM] Апаратна помилка входу: " 
                              << run_->fail_entry.hardware_entry_failure_reason << '\n';
                    running = false;
                    break;

                default:
                    std::cerr << "\n[KVM] Необроблена причина виходу: " << run_->exit_reason << '\n';
                    running = false;
                    break;
            }
        }
    }
};

int main() {
    try {
        MiniHypervisor hypervisor;

        const std::vector<std::uint8_t> code = {
            0xb0, 0x48, // mov $0x48, %al ('H')
            0xe6, 0x10, // out %al, $0x10
            0xb0, 0x49, // mov $0x49, %al ('I')
            0xe6, 0x10, // out %al, $0x10
            0xf4        // hlt
        };

        hypervisor.load_payload(code);
        hypervisor.setup_registers();
        hypervisor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Аналіз відмінностей та переваг C++ реалізації

Низькорівневий інтерфейс `ioctl` KVM вимагає строгої послідовності створення та вилучення файлових дескрипторів і відображень пам'яті. У реалізації мовою C ресурси звільняє не мова, а автор: у наведеному коді до мітки `cleanup` доходять лише пізні помилки, а кожен ранній вихід — після `KVM_CREATE_VM`, після `mmap`, після `KVM_CREATE_VCPU` — тягне власний хвіст із `close()` та `munmap()`, який доводиться виписувати вручну. Таких хвостів у наведеному лістингу сім, кожен наступний довший за попередній, і саме в них найлегше забути один рядок: рівно так і витікають дескриптори.

У C++ версії застосовано два ідіоматичні типи RAII (Resource Acquisition Is Initialization):

- **`UniqueFd`:** Клас-обгортка для файлового дескриптора POSIX. Він володіє цілим числом `fd`, забороняє копіювання (Move-only тип), але дозволяє безпечне переміщення семантикою `std::move`. Деструктор класу гарантовано викликає `close()`, коли об'єкт виходить із області видимості (зокрема й при викиданні винятків `std::system_error`).
- **`MappedMemory`:** Клас-обгортка для відображеної пам'яті `mmap()`. Зберігає вказівник та розмір регіону. Деструктор автоматично викликає `munmap()`.

Оскільки поля в класі `MiniHypervisor` оголошені у порядку `kvm_fd_`, `vm_fd_`, `vcpu_fd_`, `ram_`, `run_mmap_`, деструктори C++ викликаються у строго зворотному порядку при знищенні об'єкта `MiniHypervisor`:
1. Знімається відображення `run_mmap_` зі структурою `struct kvm_run`.
2. Знімається відображення пам'яті гостя `ram_`.
3. Закривається файловий дескриптор `vcpu_fd_`.
4. Закривається дескриптор віртуальної машини `vm_fd_`.
5. Закривається системний дескриптор `/dev/kvm` (`kvm_fd_`).

Це повністю виключає можливість витоків файлових дескрипторів або залишків відображень пам'яті в ядрі навіть при виникненні несподіваних помилок на етапі запуску.

## Дослідження коду гостя та декодування інструкцій

Гостьовий код, завантажений у RAM, виконується процесором у режимі 16-бітного Real Mode. Розберемо кожну машинну інструкцію побайтово:

- `0xb0 0x48` (`mov $0x48, %al`): Опкод `0xb0` завантажує однобайтне константне значення `0x48` (ASCII-код символу `'H'`) у 8-бітний регістр `AL`.
- `0xe6 0x10` (`out %al, $0x10`): Опкод `0xe6` записує один байт із регістра `AL` у порт введення-виведення, номер якого заданий другим байтом (`0x10`). Сусідній опкод `0xe7` виводив би у той самий порт цілий `AX` (два байти), тож для одного символу потрібен саме `0xe6`. Виконання цієї інструкції в гостьовому режимі зупиняє vCPU і викликає `VMExit` з кодом `KVM_EXIT_IO`.
- `0xb0 0x49` (`mov $0x49, %al`): Завантажує символ `'I'` (ASCII `0x49`) у регістр `AL`.
- `0xe6 0x10` (`out %al, $0x10`): Повторно виконує вивід у порт `0x10`.
- `0xf4` (`hlt`): Зупиняє виконання процесора до приходу переривання. У віртуалізованому середовищі викликає `VMExit` з кодом `KVM_EXIT_HLT`.

Коли KVM перехоплює інструкцію `OUT`, ядро записує в структуру `struct kvm_run` такі значення:
- `exit_reason` = `KVM_EXIT_IO` (2)
- `io.direction` = `KVM_EXIT_IO_OUT` (1)
- `io.size` = `1`
- `io.port` = `0x10`
- `io.count` = `1`
- `io.data_offset` = зсув у байтах від початку структури `run` до буфера з байтом `'H'`.

Потік користувацького простору читає символ за цією адресою, друкує його у стандартний вивід та викликає `KVM_RUN` знову.

## Компіляція та запуск

Для компіляції та запуску прикладів у системі Linux необхідний доступ до файлу пристрою `/dev/kvm`.

Компіляція програми C:

```bash
gcc -O2 -Wall -std=c11 main.c -o mini_hypervisor_c
```

Компіляція програми C++:

```bash
g++ -O2 -Wall -std=c++20 main.cpp -o mini_hypervisor_cpp
```

Перевірка прав доступу та запуск:

```bash
# Перевірка, чи поточний користувач входить до групи kvm
groups | grep kvm

# Якщо прав немає, запуск здійснюється через sudo або після додавання користувача до групи:
# sudo usermod -aG kvm $USER
./mini_hypervisor_cpp
```

Очікуваний вивід у терміналі:

```text
Запуск міні-гіпервізора KVM (C++ RAII)...
Гостьовий вивід: HI
[KVM] Гість виконав HLT. Завершення.
```

## Пастки та крайні випадки реалізації

1. **Прапор `RFLAGS` 0x2:** В архітектурі x86 біт 1 у регістрі `RFLAGS` за специфікацією завжди повинен бути встановлений у `1`, і апаратна перевірка стану гостя при вході цього не пробачає. Спроба викликати `KVM_RUN` із `rflags = 0` завершується збоєм входу: залежно від ядра та режиму це `KVM_EXIT_FAIL_ENTRY` або `KVM_EXIT_INTERNAL_ERROR`, але гість не виконає жодної інструкції.
2. **Адресний зсув `data_offset`:** Дані порту I/O знаходяться не в самій структурі `run->io`, а в буфері за адресою `((char *)run + run->io.data_offset)`. Пряме читання `run->io` є поширеною помилкою, оскільки структура лише описує розмір та порт, а самі байти розміщуються у вирівняній області даних за зсувом.
3. **Обмеження Real Mode:** За замовчуванням процесор стартує у 16-бітному режимі. Якщо ваша програма гостя перевищує 64 КіБ або використовує 32/64-бітні адреси, необхідно самостійно створити в пам'яті гостя таблиці GDT/PML4 та перевести процесор у Protected Mode або Long Mode через маніпуляції з прапорами `CR0.PE` та `EFER.LME` у структурі `struct kvm_sregs`.
4. **Обробка сигналів POSIX:** Під час перебування потоку всередині `ioctl(vcpu_fd, KVM_RUN, 0)` сигнал хоста (наприклад, `SIGINT` або `SIGALRM`) перериває виклик із помилкою `EINTR` або повертає `exit_reason = KVM_EXIT_INTR`. Програма повинна бути готовою поновити цикл `KVM_RUN` після обробки сигналу.
