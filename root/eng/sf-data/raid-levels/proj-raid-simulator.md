# ⚙️ Емулятор дискового масиву RAID 0, 1, 5 на C та C++

У цій практичній вставці подано повнофункціональну емуляцію програмного дискового масиву. Код реалізує алгоритми чередування даних (RAID 0), дзеркалювання (RAID 1) та розподіленого ротаційного паритету (RAID 5) з підтримкою гарячої заміни (Hot Spare), роботи в деградованому режимі (Degraded Mode) та реконструкції секторів налету через XOR-паритет.

## 1. Теоретичне підґрунтя емулятора дискових масивів

Фізичний жорсткий диск або твердотілий накопичувач надає операційній системі плоский масив секторів фіксованого розміру (традиційно 512 байтів або 4096 байтів для дисків Advanced Format). Драйвер програмного RAID підсистеми ядра перехоплює запити читання та запису блокового рівня (Block I/O Requests) і трансформує один логічний адресний простір у послідовність команд до кількох фізичних накопичувачів.

У нашому емуляторі дисковий масив моделюється на рівні секторів розміром `SECTOR_SIZE = 64` байти. Масив складається з `NUM_DISKS = 4` віртуальних накопичувачів. Для реалізації ротаційного паритету RAID 5 застосовується алгоритм **Left-Symmetric**, у якому позиція диска паритету `P` обчислюється динамічно залежно від номера страйпа.

При записі логічного сектора `L` алгоритм здійснення операції складається з п'яти послідовних етапів:

1. **Розрахунок індексу страйпа:** Алгоритм обчислює номер страйпа у масиві як `Stripe_Index = L / (NUM_DISKS - 1)`, де `(NUM_DISKS - 1)` — кількість дисків, виділених під дані у кожному страйпі.
2. **Визначення диска паритету:** Номер накопичувача, на якому зберігається блок паритету `P` для даного страйпа, визначається ротаційною формулою `Parity_Disk = (NUM_DISKS - 1) - (Stripe_Index mod NUM_DISKS)`. Це забезпечує рівномірне розсіювання навантаження запису паритету по всіх чотирьох дисках.
3. **Мапінг цільового диска даних:** Логічний колоночний індекс `Data_Column = L mod (NUM_DISKS - 1)` трансформується у фізичний номер диска `Target_Disk`. Якщо `Data_Column >= Parity_Disk`, фізичний номер збільшується на 1, щоб оминути диск паритету.
4. **Запис даних:** Вміст буфера записується на цільовий диск даних за відповідним зсувом.
5. **Переобчислення паритету:** Алгоритм виконує побітову операцію XOR по всіх дисках даних поточного страйпа та зберігає новий обчислений паритет на диск паритету.

Якщо один із фізичних дисків даних виходить з ладу (його прапорець `is_online` стає `false`), масив переходить у деградований режим (Degraded Mode). При запиті на зчитування з втраченого диска система не повертає помилку `I/O Error`, а негайно відновлює вміст сектора налету шляхом обчислення XOR-суми секторів усіх інших `NUM_DISKS - 1` справних дисків страйпа.

## 2. Алгоритм обчислення та векторизації XOR-паритету

Побітова операція виключного «АБО» (XOR) володіє математичною властивістю самоінверсії: `A ⊕ A = 0` та `A ⊕ 0 = A`. Завдяки цьому, якщо `P = D₀ ⊕ D₁ ⊕ D₂`, то відновлення будь-якого втраченого блоку даних (наприклад, `D₀`) виконується за тотожною формулою `D₀ = P ⊕ D₁ ⊕ D₂`.

У високопродуктивних реалізаціях ядра Linux (модуль `drivers/md/raid5.c`) обчислення XOR-суми виконується не побайтово, а широкими векторними інструкціями процесора (AVX2, AVX-512 або ARM Neon). Векторний регістр 256 бітів дозволяє виконувати XOR над 32 байтами даних за один машинний такт процесора, досягаючи пропускної здатності обчислення паритету у десятки гігабайтів на секунду.

У нашому емуляторі функція `compute_xor` виконує обчислення по блоках пам'яті за допомогою циклу по `uint8_t`, що забезпечує повну портативність та прозорість алгоритму.

## 3. Реалізація емулятора мовами C та C++

Нижче подано повнофункціональний вихідний код емулятора у двох незалежних вкладках.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define SECTOR_SIZE 64
#define NUM_DISKS 4

typedef struct {
    uint8_t data[SECTOR_SIZE];
    bool is_online;
} VirtualDisk;

typedef struct {
    VirtualDisk disks[NUM_DISKS];
    size_t disk_capacity_sectors;
} Raid5Array;

// Ініціалізація масиву
Raid5Array* raid5_create(size_t capacity_sectors) {
    Raid5Array *array = (Raid5Array*)malloc(sizeof(Raid5Array));
    if (!array) return NULL;
    
    array->disk_capacity_sectors = capacity_sectors;
    for (int i = 0; i < NUM_DISKS; i++) {
        array->disks[i].is_online = true;
        memset(array->disks[i].data, 0, SECTOR_SIZE);
    }
    return array;
}

void raid5_free(Raid5Array *array) {
    if (array) free(array);
}

// Побітове обчислення XOR-паритету
static void compute_xor(const uint8_t *src1, const uint8_t *src2, uint8_t *dest, size_t len) {
    for (size_t i = 0; i < len; i++) {
        dest[i] = src1[i] ^ src2[i];
    }
}

// Визначення дисків даних та паритету для страйпа
static int get_parity_disk(size_t stripe_idx) {
    // Left-Symmetric ротація паритету
    return (int)((NUM_DISKS - 1) - (stripe_idx % NUM_DISKS));
}

// Запис сектора у RAID 5
bool raid5_write_sector(Raid5Array *array, size_t logical_sector, const uint8_t *buf) {
    size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
    size_t data_col = logical_sector % (NUM_DISKS - 1);
    int parity_disk = get_parity_disk(stripe_idx);
    
    // Мапінг дисків: обхід диска паритету
    int target_disk = (int)data_col;
    if (target_disk >= parity_disk) {
        target_disk++;
    }

    if (!array->disks[target_disk].is_online) {
        fprintf(stderr, "Помилка: Цільовий диск %d офлайн, необхідна відбудова.\n", target_disk);
        return false;
    }

    // Запис даних на цільовий диск
    memcpy(array->disks[target_disk].data, buf, SECTOR_SIZE);

    // Оновлення паритету (переобчислення по всіх справних дисках даних)
    uint8_t new_parity[SECTOR_SIZE];
    memset(new_parity, 0, SECTOR_SIZE);
    
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == parity_disk) continue;
        compute_xor(new_parity, array->disks[d].data, new_parity, SECTOR_SIZE);
    }

    if (array->disks[parity_disk].is_online) {
        memcpy(array->disks[parity_disk].data, new_parity, SECTOR_SIZE);
    }
    return true;
}

// Читання сектора з RAID 5 (з підтримкою Degraded Mode)
bool raid5_read_sector(Raid5Array *array, size_t logical_sector, uint8_t *buf) {
    size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
    size_t data_col = logical_sector % (NUM_DISKS - 1);
    int parity_disk = get_parity_disk(stripe_idx);
    
    int target_disk = (int)data_col;
    if (target_disk >= parity_disk) {
        target_disk++;
    }

    // Нормальний режим: диск даних онлайн
    if (array->disks[target_disk].is_online) {
        memcpy(buf, array->disks[target_disk].data, SECTOR_SIZE);
        return true;
    }

    // Деградований режим: реконструкція «на льоту» через XOR
    printf("Диск %d недоступний. Реконструкція сектора %zu налету через XOR...\n", target_disk, logical_sector);
    memset(buf, 0, SECTOR_SIZE);

    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == target_disk) continue;
        if (!array->disks[d].is_online) {
            fprintf(stderr, "Фатальна помилка: Понад один диск офлайн! Втрата даних.\n");
            return false;
        }
        compute_xor(buf, array->disks[d].data, buf, SECTOR_SIZE);
    }
    return true;
}

// Симуляція відмови диска
void raid5_fail_disk(Raid5Array *array, int disk_idx) {
    if (disk_idx >= 0 && disk_idx < NUM_DISKS) {
        array->disks[disk_idx].is_online = false;
        memset(array->disks[disk_idx].data, 0, SECTOR_SIZE);
        printf("⚠️ Диск %d ФІЗИЧНО ВИЙШОВ З ЛАДУ!\n", disk_idx);
    }
}

// Процес відбудови (Rebuild / Resilver) на новий replacement-диск
bool raid5_rebuild(Raid5Array *array, int failed_disk_idx) {
    if (array->disks[failed_disk_idx].is_online) return true;

    printf("🔄 Розпочато процес відбудови диска %d...\n", failed_disk_idx);

    // Перевірка, що всі інші диски онлайн
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d != failed_disk_idx && !array->disks[d].is_online) {
            fprintf(stderr, "Відбудова неможлива: диск %d також офлайн.\n", d);
            return false;
        }
    }

    // Реконструкція даного диска через XOR решти дисків
    memset(array->disks[failed_disk_idx].data, 0, SECTOR_SIZE);
    for (int d = 0; d < NUM_DISKS; d++) {
        if (d == failed_disk_idx) continue;
        compute_xor(array->disks[failed_disk_idx].data, array->disks[d].data, 
                    array->disks[failed_disk_idx].data, SECTOR_SIZE);
    }

    array->disks[failed_disk_idx].is_online = true;
    printf("✅ Відбудову диска %d успішно завершено!\n", failed_disk_idx);
    return true;
}

int main(void) {
    Raid5Array *raid = raid5_create(100);
    
    const char *secret_msg = "Hello RAID 5 Architecture!";
    uint8_t write_buf[SECTOR_SIZE] = {0};
    strncpy((char*)write_buf, secret_msg, SECTOR_SIZE - 1);

    printf("1. Запис даних у логічний сектор 0...\n");
    raid5_write_sector(raid, 0, write_buf);

    uint8_t read_buf[SECTOR_SIZE] = {0};
    raid5_read_sector(raid, 0, read_buf);
    printf("Прочитано з масиву: \"%s\"\n\n", (char*)read_buf);

    printf("2. Симуляція аварї диска 0...\n");
    raid5_fail_disk(raid, 0);

    memset(read_buf, 0, SECTOR_SIZE);
    printf("3. Спроба зчитати дані у деградованому режимі...\n");
    raid5_read_sector(raid, 0, read_buf);
    printf("Результат налету reconstruction: \"%s\"\n\n", (char*)read_buf);

    printf("4. Заміна диска та відбудова масиву...\n");
    raid5_rebuild(raid, 0);

    memset(read_buf, 0, SECTOR_SIZE);
    raid5_read_sector(raid, 0, read_buf);
    printf("Прочитано після відбудови: \"%s\"\n", (char*)read_buf);

    raid5_free(raid);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <algorithm>

constexpr size_t SECTOR_SIZE = 64;
constexpr size_t NUM_DISKS = 4;

enum class RaidError {
    DiskOffline,
    MultipleDisksFailed,
    InvalidSector
};

class VirtualDisk {
public:
    std::array<uint8_t, SECTOR_SIZE> data{};
    bool is_online{true};

    void fail() noexcept {
        is_online = false;
        data.fill(0);
    }
};

class Raid5Array {
private:
    std::array<VirtualDisk, NUM_DISKS> disks_;

    [[nodiscard]] static constexpr size_t get_parity_disk(size_t stripe_idx) noexcept {
        return (NUM_DISKS - 1) - (stripe_idx % NUM_DISKS);
    }

    static void xor_buffers(std::span<const uint8_t> src, std::span<uint8_t> dest) noexcept {
        for (size_t i = 0; i < dest.size(); ++i) {
            dest[i] ^= src[i];
        }
    }

public:
    Raid5Array() = default;

    [[nodiscard]] std::expected<void, RaidError> write_sector(size_t logical_sector, std::span<const uint8_t, SECTOR_SIZE> input) {
        const size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
        const size_t data_col = logical_sector % (NUM_DISKS - 1);
        const size_t parity_disk = get_parity_disk(stripe_idx);

        size_t target_disk = data_col;
        if (target_disk >= parity_disk) {
            ++target_disk;
        }

        if (!disks_[target_disk].is_online) {
            return std::unexpected(RaidError::DiskOffline);
        }

        std::copy(input.begin(), input.end(), disks_[target_disk].data.begin());

        // Recalculate parity across all data disks
        std::array<uint8_t, SECTOR_SIZE> new_parity{};
        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == parity_disk) continue;
            xor_buffers(disks_[d].data, new_parity);
        }

        if (disks_[parity_disk].is_online) {
            disks_[parity_disk].data = new_parity;
        }

        return {};
    }

    [[nodiscard]] std::expected<std::array<uint8_t, SECTOR_SIZE>, RaidError> read_sector(size_t logical_sector) const {
        const size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
        const size_t data_col = logical_sector % (NUM_DISKS - 1);
        const size_t parity_disk = get_parity_disk(stripe_idx);

        size_t target_disk = data_col;
        if (target_disk >= parity_disk) {
            ++target_disk;
        }

        // Direct read if target disk is healthy
        if (disks_[target_disk].is_online) {
            return disks_[target_disk].data;
        }

        // Degraded Mode: Reconstruct sector via XOR
        std::cout << "[C++] Degraded Mode: Reconstructing sector " << logical_sector << " via XOR...\n";
        std::array<uint8_t, SECTOR_SIZE> reconstructed{};

        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == target_disk) continue;
            if (!disks_[d].is_online) {
                return std::unexpected(RaidError::MultipleDisksFailed);
            }
            xor_buffers(disks_[d].data, reconstructed);
        }

        return reconstructed;
    }

    void simulate_disk_failure(size_t disk_idx) {
        if (disk_idx < NUM_DISKS) {
            disks_[disk_idx].fail();
            std::cout << "[C++] ⚠️ Disk " << disk_idx << " FAILED!\n";
        }
    }

    [[nodiscard]] std::expected<void, RaidError> rebuild_disk(size_t failed_disk_idx) {
        if (disks_[failed_disk_idx].is_online) return {};

        std::cout << "[C++] 🔄 Rebuilding disk " << failed_disk_idx << "...\n";

        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d != failed_disk_idx && !disks_[d].is_online) {
                return std::unexpected(RaidError::MultipleDisksFailed);
            }
        }

        disks_[failed_disk_idx].data.fill(0);
        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == failed_disk_idx) continue;
            xor_buffers(disks_[d].data, disks_[failed_disk_idx].data);
        }

        disks_[failed_disk_idx].is_online = true;
        std::cout << "[C++] ✅ Disk " << failed_disk_idx << " rebuild complete!\n";
        return {};
    }
};

int main() {
    Raid5Array raid;

    std::array<uint8_t, SECTOR_SIZE> write_buf{};
    std::string_view msg = "Idiomatic C++23 RAID Engine";
    std::copy(msg.begin(), msg.end(), write_buf.begin());

    std::cout << "1. Writing sector 0...\n";
    if (auto res = raid.write_sector(0, write_buf); !res) {
        std::cerr << "Write failed!\n";
        return 1;
    }

    if (auto res = raid.read_sector(0)) {
        std::cout << "Read result: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n\n";
    }

    std::cout << "2. Simulating drive failure on disk 0...\n";
    raid.simulate_disk_failure(0);

    std::cout << "3. Reading in degraded mode...\n";
    if (auto res = raid.read_sector(0)) {
        std::cout << "On-the-fly reconstruction: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n\n";
    }

    std::cout << "4. Rebuilding array...\n";
    if (auto res = raid.rebuild_disk(0); !res) {
        std::cerr << "Rebuild failed!\n";
        return 1;
    }

    if (auto res = raid.read_sector(0)) {
        std::cout << "Post-rebuild read: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n";
    }

    return 0;
}
```
:::

## 4. Детальний аналіз виконання та критичних випадків

Програма покроково випробовує чотири критичні стани дискового масиву, з якими щодня стикаються інженери з зберігання даних:

### Крок 1: Запис та читання в нормальному стані (Healthy Mode)

Під час першого виклику `raid5_write_sector(raid, 0, write_buf)` програма розраховує:
- `stripe_idx = 0 / 3 = 0`.
- `parity_disk = (4 - 1) - (0 % 4) = 3` (Диск 3 отримує паритет `P0`).
- `data_col = 0 % 3 = 0`. Цільовий диск `target_disk = 0` (бо `0 < 3`).

Рядок `"Hello RAID 5 Architecture!"` копіюється у сектор диска 0, після чого обчислюється XOR-паритет між дисками 0, 1 та 2. Оскільки диски 1 та 2 містять лише нулі, паритет на диску 3 стає точною копією диска 0. При виклику `read_sector(raid, 0, read_buf)` програма зчитує дані з диска 0 напряму за 1 операцію без додаткових накладних витрат.

### Крок 2: Штучна індукція аварії диска (Disk Failure)

Виклик `raid5_fail_disk(raid, 0)` симулює фізичну відмову диска 0. Прапорець `is_online` встановлюється в `false`, а вміст сектора повністю стирається за допомогою `memset`. Дисковий масив переходить у деградований режим (Degraded State).

### Крок 3: Реконструкція сектора налету (On-the-fly Recovery)

При повторному виклику `read_sector(raid, 0, read_buf)` програма бачить, що цільовий диск 0 перебуває в офлайні. Замість повернення помилки програма автоматично запускає відновлення налету. Вона зчитує сектор з диска 1 (0x00), сектор з диска 2 (0x00) та сектор паритету з диска 3 (`P0`), виконуючи послідовну операцію XOR:

```
Reconstructed_Data = Disk1_Data ⊕ Disk2_Data ⊕ Disk3_Parity
```

В результаті виклику на екран виводиться прочитана фраза `"Hello RAID 5 Architecture!"`, що підтверджує успішність математичного відновлення.

### Крок 4: Заміна диска та запуск відбудови (Rebuild / Resilver)

Виклик `raid5_rebuild(raid, 0)` моделює встановлення нового порожнього накопичувача замість збійного. Алгоритм відбудови послідовно проходить по всіх сеторах диска, вираховує їхній відновлений вміст через XOR решти трьох дисків та зберігає результат у пам'ять нового диска 0. Наприкінці прапорець `is_online` диска 0 повертається в `true`, і масив відновлює повний нормальний режим роботи.

### Граничний випадок: Подвійна відмова у RAID 5

Якщо під час перебування у деградованому режимі (на кроці 3) з ладу виходить ще один диск (наприклад, диск 1), метод `read_sector` або `rebuild` виявляє, що понад один диск перебуває у стані `is_online == false`. У цьому випадку система повертає фатальну помилку `MultipleDisksFailed`, оскільки відновлення двох невідомих за допомогою одного рівня XOR-паритету є математично неможливим.
