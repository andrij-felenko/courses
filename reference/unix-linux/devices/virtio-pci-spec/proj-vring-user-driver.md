# ⚙️ Практична реалізація vring-драйвера в користувацькому просторі

Користувацькі драйвери вводу/виводу, такі як фреймворки DPDK (Data Plane Development Kit), SPDK (Storage Performance Development Kit) або реалізації `vhost-user` (наприклад, у `QEMU`, `vhost-user-net`, `OVS-DPDK` або `Cilium`), маніпулюють чергами Virtio безпосередньо з простору користувача. Це дозволяє здійснювати пересилання мережевих пакетів та дискових блоків без жодного перемикання контексту в ядро Linux і без використання повільних системних викликів `syscall`.

У цьому проектному матеріалі розглянуто повну архітектуру та реалізацію користувацького драйвера класичного Split Virtqueue. Ми розберемо розрахунок геометрії пам'яті, побудову безблочного обхідника дескрипторів, протокол обміну пам'яттю `vhost-user`, роботу з великими сторінками (Hugepages), бар'єрами пам'яті та реалізуємо робочий приклад двома мовами — C та C++.

---

## 1. Розрахунок геометрії та вирівнювання пам'яті (Memory Alignment)

Специфікація Virtio вимагає, щоб три структури Split Virtqueue (Descriptor Table, Available Ring та Used Ring) розташовувалися в неперервному блоці фізичної пам'яті із суворим дотриманням меж вирівнювання (за замовчуванням `4096` байтів для сумісності з розміром сторінки RAM).

Обчислення розмірів і зсувів у пам'яті для черги розміром `N`:

1. **Таблиця дескрипторів (Descriptor Table):**
   Масив містить `N` елементів `struct virtq_desc`. Оскільки розмір одного дескриптора становить 16 байтів, загальний обсяг обчислюється як:
   ```
   desc_bytes = sizeof(struct virtq_desc) · N = 16 · N
   ```
2. **Доступне кільце (Available Ring):**
   Містить заголовок з двох 16-бітних полів (`flags` та `idx`), масив `ring` з `N` 16-бітних елементів та 16-бітне поле `used_event`:
   ```
   avail_bytes = sizeof(uint16_t) · (3 + N) = 6 + 2 · N
   ```
3. **Вирівнювання для Used Ring:**
   Використане кільце має починатися з нової 4096-байтної сторінки пам'яті для оптимізації доступу контролера DMA та запобігання промахам кешу (False Sharing між CPU гостя та хоста).
   ```
   used_offset = (desc_bytes + avail_bytes + 4095) & ~4095
   ```
4. **Використане кільце (Used Ring):**
   Містить заголовок (`flags`, `idx`), масив з `N` елементів `struct virtq_used_elem` (по 8 байтів кожен) та поле `avail_event`:
   ```
   used_bytes = sizeof(uint16_t) · 3 + sizeof(struct virtq_used_elem) · N = 6 + 8 · N
   ```

Загальний обсяг пам'яті для створення однієї черги розміром `N = 256` становить приблизно `12 КБ`.

---

## 2. Протокол vhost-user та робота з Hugepages

При роботі користувацького драйвера у високопродуктивних мережевих стеках (DPDK / vhost-user) пам'ять для віртуальних черг та буферів даних виділяється з механізму великих сторінок пам'яті (Hugepages) розміром 2 МБ або 1 ГБ через системний виклик `mmap()` із прапорцем `MAP_HUGETLB`.

Використання Hugepages забезпечує дві вирішальні переваги:
- **Зменшення промахів TLB (Translation Lookaside Buffer):** Буфер розміром 1 ГБ вимагає лише 1 запис у кеші TLB замість 262 144 записів для стандартних 4 КБ сторінок.
- **Фізична неперервність пам'яті (Physical Contiguity):** Великі сторінки гарантовано залишаються неперервними у фізичному адресному просторі, що спрощує роботу DMA-контролерів та мережевих карт.

Для передачі доступу до цієї пам'яті між процесом користувача (наприклад, QEMU) та зовнішнім демоном (наприклад, DPDK / Open vSwitch) використовується протокол **vhost-user**:
1. Демон створює UNIX Domain Socket.
2. Процес QEMU підключається до сокета і передає файлові дескриптори виділених Hugepages через механізм допоміжних даних `SCM_RIGHTS` виклику `sendmsg()`.
3. Демон виконує `mmap()` цих файлових дескрипторів і отримує прямий доступ до пам'яті віртуальної машини гостя.
4. Процес QEMU передає файлові дескриптори `eventfd` для дверних дзвоників (`VHOST_USER_SET_VRING_KICK`) та переривань (`VHOST_USER_SET_VRING_CALL`).

Після цього обмін даними відбувається на швидкості пам'яті без участі ядра Linux.

---

## 3. Алгоритм додавання буфера у чергу (vq_add_buffer)

Процедура подачі нового I/O-запиту драйвером складається з кількох кроків:

1. **Перевірка наявності вільних дескрипторів:** Драйвер підтримує лічильник `num_free`. Якщо `num_free < 1`, черга переповнена і додавання неможливе.
2. **Формування дескриптора:** Драйвер бере перший вільний індекс із голови списку вільних дескрипторів (`free_head`), записує туди фізичну адресу буфера `addr`, довжину `len` та прапорці напрямку (`VIRTQ_DESC_F_WRITE` для запису пристроєм або `0` для читання).
3. **Публікація у Avail Ring:** Драйвер обчислює позицію у доступному кільці за маскою `avail_slot = avail->idx & (N - 1)` і записує туди індекс головного дескриптора.
4. **Встановлення бар'єра пам'яті:** Перед оновленням `avail->idx` драйвер виконує інструкцію бар'єра пам'яті (`smp_wmb`), яка скидає кеш-буфери запису CPU.
5. **Оновлення лічильника:** Драйвер збільшує `avail->idx` на `1`.

---

## 4. Двомовна реалізація драйвера (C та C++)

Нижче наведено робочі реалізації користувацького драйвера vring. Приклад мовою C демонструє пряму роботу із вказівниками та системними викликами виділення вирівняної пам'яті (`posix_memalign`). Приклад мовою C++ демонструє ідіоматичний підхід із використанням концепції RAII, інкапсуляції в клас, безпечної передачі буферів через `std::span` та управління пам'яттю через `std::unique_ptr`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define VIRTQ_DESC_F_NEXT  1
#define VIRTQ_DESC_F_WRITE 2

#define VRING_ALIGN 4096
#define QUEUE_SIZE  16

struct virtq_desc {
    uint64_t addr;
    uint32_t len;
    uint16_t flags;
    uint16_t next;
};

struct virtq_avail {
    uint16_t flags;
    uint16_t idx;
    uint16_t ring[QUEUE_SIZE];
    uint16_t used_event;
};

struct virtq_used_elem {
    uint32_t id;
    uint32_t len;
};

struct virtq_used {
    uint16_t flags;
    uint16_t idx;
    struct virtq_used_elem ring[QUEUE_SIZE];
    uint16_t avail_event;
};

struct virtqueue {
    uint16_t num;
    struct virtq_desc *desc;
    struct virtq_avail *avail;
    struct virtq_used *used;
    uint16_t last_used_idx;
    uint16_t free_head;
    uint16_t num_free;
};

static void memory_write_barrier(void) {
    __asm__ __volatile__("sfence" ::: "memory");
}

static void memory_read_barrier(void) {
    __asm__ __volatile__("lfence" ::: "memory");
}

struct virtqueue *vq_create(uint16_t queue_size) {
    struct virtqueue *vq = (struct virtqueue *)calloc(1, sizeof(struct virtqueue));
    if (!vq) return NULL;

    vq->num = queue_size;
    vq->num_free = queue_size;
    vq->free_head = 0;
    vq->last_used_idx = 0;

    size_t desc_bytes = sizeof(struct virtq_desc) * queue_size;
    size_t avail_bytes = sizeof(uint16_t) * (3 + queue_size);
    size_t used_bytes = sizeof(uint16_t) * 3 + sizeof(struct virtq_used_elem) * queue_size;

    void *mem = NULL;
    size_t total_size = desc_bytes + avail_bytes + used_bytes + VRING_ALIGN;
    if (posix_memalign(&mem, VRING_ALIGN, total_size) != 0) {
        free(vq);
        return NULL;
    }
    memset(mem, 0, total_size);

    vq->desc = (struct virtq_desc *)mem;
    vq->avail = (struct virtq_avail *)((uintptr_t)mem + desc_bytes);

    uintptr_t used_addr = (uintptr_t)vq->avail + avail_bytes;
    used_addr = (used_addr + VRING_ALIGN - 1) & ~(VRING_ALIGN - 1);
    vq->used = (struct virtq_used *)used_addr;

    for (uint16_t i = 0; i < queue_size - 1; i++) {
        vq->desc[i].next = i + 1;
    }
    vq->desc[queue_size - 1].next = 0xFFFF;

    return vq;
}

int vq_add_buffer(struct virtqueue *vq, uint64_t phys_addr, uint32_t len, bool is_write) {
    if (vq->num_free < 1) return -1;

    uint16_t head = vq->free_head;
    vq->desc[head].addr = phys_addr;
    vq->desc[head].len = len;
    vq->desc[head].flags = is_write ? VIRTQ_DESC_F_WRITE : 0;
    vq->free_head = vq->desc[head].next;
    vq->num_free--;

    memory_write_barrier();

    uint16_t avail_slot = vq->avail->idx & (vq->num - 1);
    vq->avail->ring[avail_slot] = head;

    memory_write_barrier();
    vq->avail->idx++;

    return head;
}

void vq_kick_notify(struct virtqueue *vq, volatile uint32_t *doorbell_reg) {
    memory_write_barrier();
    if (doorbell_reg) {
        *doorbell_reg = 0; // Запис у дверний дзвоник (Kick)
    }
}

int vq_poll_used(struct virtqueue *vq, uint32_t *len_written) {
    memory_read_barrier();

    if (vq->last_used_idx == vq->used->idx) {
        return -1; // Немає завершених запитів
    }

    uint16_t used_slot = vq->last_used_idx & (vq->num - 1);
    struct virtq_used_elem *elem = &vq->used->ring[used_slot];

    uint32_t head = elem->id;
    if (len_written) *len_written = elem->len;

    vq->desc[head].next = vq->free_head;
    vq->free_head = head;
    vq->num_free++;

    vq->last_used_idx++;
    return (int)head;
}

void vq_free(struct virtqueue *vq) {
    if (vq) {
        free(vq->desc);
        free(vq);
    }
}

int main(void) {
    struct virtqueue *vq = vq_create(QUEUE_SIZE);
    if (!vq) {
        fprintf(stderr, "Помилка створення virtqueue\n");
        return 1;
    }

    char buffer[512] = "Приклад даних Virtio I/O";
    int head = vq_add_buffer(vq, (uint64_t)(uintptr_t)buffer, sizeof(buffer), false);
    printf("Додано буфер у vring: head index = %d, avail idx = %u\n", head, vq->avail->idx);

    vq_kick_notify(vq, NULL);

    // Симуляція обробки гіпервізором:
    vq->used->ring[0].id = head;
    vq->used->ring[0].len = sizeof(buffer);
    vq->used->idx = 1;

    uint32_t bytes_done = 0;
    int completed_head = vq_poll_used(vq, &bytes_done);
    if (completed_head >= 0) {
        printf("Завершено обробку буфера %d, оброблено байт: %u\n", completed_head, bytes_done);
    }

    vq_free(vq);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <cstdint>
#include <cstring>
#include <atomic>
#include <span>
#include <optional>
#include <stdexcept>

enum class DescriptorFlags : uint16_t {
    None = 0,
    Next = 1,
    Write = 2
};

inline DescriptorFlags operator|(DescriptorFlags a, DescriptorFlags b) {
    return static_cast<DescriptorFlags>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

struct alignas(16) VirtqDesc {
    uint64_t addr{0};
    uint32_t len{0};
    uint16_t flags{0};
    uint16_t next{0};
};

struct VirtqAvail {
    uint16_t flags{0};
    uint16_t idx{0};
    uint16_t ring[16]{0};
    uint16_t used_event{0};
};

struct VirtqUsedElem {
    uint32_t id{0};
    uint32_t len{0};
};

struct VirtqUsed {
    uint16_t flags{0};
    uint16_t idx{0};
    VirtqUsedElem ring[16]{0};
    uint16_t avail_event{0};
};

class VirtqueueDriver {
public:
    explicit VirtqueueDriver(uint16_t queue_size = 16)
        : num_{queue_size}, num_free_{queue_size}, free_head_{0}, last_used_idx_{0} {
        
        if ((queue_size & (queue_size - 1)) != 0) {
            throw std::invalid_argument("Розмір черги має бути степенем двійки!");
        }

        desc_storage_.resize(queue_size);
        avail_storage_ = std::make_unique<VirtqAvail>();
        used_storage_ = std::make_unique<VirtqUsed>();

        for (uint16_t i = 0; i < queue_size - 1; ++i) {
            desc_storage_[i].next = i + 1;
        }
        desc_storage_[queue_size - 1].next = 0xFFFF;
    }

    std::optional<uint16_t> add_buffer(std::span<const std::byte> buffer, bool is_write) {
        if (num_free_ == 0) {
            return std::nullopt;
        }

        uint16_t head = free_head_;
        VirtqDesc& desc = desc_storage_[head];
        desc.addr = reinterpret_cast<uint64_t>(buffer.data());
        desc.len = static_cast<uint32_t>(buffer.size());
        desc.flags = static_cast<uint16_t>(is_write ? DescriptorFlags::Write : DescriptorFlags::None);

        free_head_ = desc.next;
        --num_free_;

        std::atomic_thread_fence(std::memory_order_release);

        uint16_t avail_slot = avail_storage_->idx & (num_ - 1);
        avail_storage_->ring[avail_slot] = head;

        std::atomic_thread_fence(std::memory_order_release);
        avail_storage_->idx++;

        return head;
    }

    void kick(volatile uint32_t* doorbell = nullptr) const noexcept {
        std::atomic_thread_fence(std::memory_order_seq_cst);
        if (doorbell) {
            *doorbell = 0;
        }
    }

    struct CompletedBuffer {
        uint16_t head;
        uint32_t len_written;
    };

    std::optional<CompletedBuffer> poll_used() noexcept {
        std::atomic_thread_fence(std::memory_order_acquire);

        if (last_used_idx_ == used_storage_->idx) {
            return std::nullopt;
        }

        uint16_t used_slot = last_used_idx_ & (num_ - 1);
        const VirtqUsedElem& elem = used_storage_->ring[used_slot];

        uint16_t head = static_cast<uint16_t>(elem.id);
        uint32_t len = elem.len;

        desc_storage_[head].next = free_head_;
        free_head_ = head;
        ++num_free_;

        ++last_used_idx_;
        return CompletedBuffer{head, len};
    }

    VirtqUsed* raw_used() noexcept { return used_storage_.get(); }
    uint16_t avail_idx() const noexcept { return avail_storage_->idx; }

private:
    uint16_t num_;
    uint16_t num_free_;
    uint16_t free_head_;
    uint16_t last_used_idx_;

    std::vector<VirtqDesc> desc_storage_;
    std::unique_ptr<VirtqAvail> avail_storage_;
    std::unique_ptr<VirtqUsed> used_storage_;
};

int main() {
    try {
        VirtqueueDriver vq(16);

        std::string payload = "Дані для передачі через Virtqueue C++ RAII";
        std::span<const std::byte> bytes_span{
            reinterpret_cast<const std::byte*>(payload.data()), payload.size()
        };

        auto head_opt = vq.add_buffer(bytes_span, false);
        if (head_opt) {
            std::cout << "Буфер додано у vring C++: head = " << *head_opt 
                      << ", avail_idx = " << vq.avail_idx() << std::endl;
        }

        vq.kick();

        auto* used = vq.raw_used();
        used->ring[0].id = *head_opt;
        used->ring[0].len = static_cast<uint32_t>(payload.size());
        used->idx = 1;

        auto result = vq.poll_used();
        if (result) {
            std::cout << "Завершено обробку у C++: head = " << result->head 
                      << ", оброблено байтів = " << result->len_written << std::endl;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
```
:::

---

## 5. Аналіз потокобезпеки та крайових випадків

- **Потокобезпека без блокувань (Lock-Free SPSC):** Структура даних розрахована на виконання в режимі Single-Producer Single-Consumer. Якщо декілька потоків гостя намагаються одночасно викликати `vq_add_buffer()`, драйвер зобов'язаний застосувати зовнішню синхронізацію (наприклад, spinlock). Однак потік додавання буферів та потік збору результатів (`vq_poll_used()`) є повністю незалежними і працюють без блокувань.
- **Особливості архітектур ARM64 / POWER (Weak Memory Ordering):** На відміну від x86, процесори з нестрогою моделлю пам'яті можуть змінювати порядок запису в `desc` та `avail->idx`. Використання `std::atomic_thread_fence(std::memory_order_release)` у C++ створює інструкцію `dmb st` на ARM64, гарантуючи впорядкування записів у RAM.
- **Обробка переповнення черги:** Якщо `vq_add_buffer()` повертає помилку (`num_free == 0`), драйвер в режимі Poll Mode спиняє прийом нових пакетів від вищих шарів і в циклі опитує `vq_poll_used()`, поки не звільниться бодай один дескриптор.
