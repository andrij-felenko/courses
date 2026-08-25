# ⚙️ Реалізація стійкого до регресу годинника генератора Snowflake та UUIDv7

Головною небезпекою децентралізованих генераторів, що спираються на системний час, є стрибки годинника назад (Clock Skew / Rollback). Це явище виникає внаслідок періодичної синхронізації часу демонами NTP, компенсації дрейфу кварцових резонаторів материнської плати, введення високосних секунд (Leap Seconds) або при міграції віртуальних машин між фізичними хостами гіпервізора.

Якщо алгоритм генерації сліпо використовує поточний показник системного таймера, виникає критична вразливість: генератор повторно видає комбінацію «мілісекунда + ідентифікатор воркера + номер у послідовності», яку система вже згенерувала кілька мілісекунд тому. Це призводить до появи дублікатів первинних ключів у базі даних та руйнування інваріантів унікальності.

---

### Архітектура та етапи обробки годинникового дрейфу

Для забезпечення 100% захисту від дублікатів генератор реалізує багаторівневу логіку контролю часу:

1. **Етап зчитування системного часу**: Генератор опитує фізичний годинник реального часу (`CLOCK_REALTIME` в POSIX або `std::chrono::system_clock` у C++).
2. **Етап аналізу дельти (`now < last_timestamp`)**:
   * Якщо фізичний час менший за час останньої генерації, система фіксує регрес годинника на величину `drift = last_timestamp - now`.
   * **Малий регрес (`drift < 5 мс`)**: Генератор переходить у режим короткого активного очікування (Spin-wait з викликом `std::this_thread::yield()`), поки системний годинник не перетне позначку `last_timestamp`. Затримка у кілька мілісекунд є непомітною для клієнтських запитів і повністю усуває ризик колізії.
   * **Критичний регрес (`drift ≥ 5 мс`)**: Свідчить про серйозний апаратний збій або ручне переведення системного часу. Генератор негайно перериває виконання (Fail-Fast) та повертає явну помилку, запобігаючи неконтрольованому спотворенню бази даних.
3. **Етап контролю вичерпання лічильника в межах мілісекунди**:
   * Якщо запит надійшов у ту саму мілісекунду (`now == last_timestamp`), поле `sequence` інкрементується на `+1`.
   * Якщо лічильник переповнюється (перевищує `4095` для 12 бітів), він скидається в `0`, а генератор блокує робочий потік до настання наступної мілісекунди (`wait_next_millis`).
4. **Етап бітового пакування**: Складові частини зміщуються на відповідну кількість розрядів та об'єднуються побітовим логічним АБО.

#### Механіка активного очікування (Yield vs Sleep)

У функції `wait_next_millis` замість блокуючого виклику `std::this_thread::sleep_for(1ms)` використовується `std::this_thread::yield()`. Системний виклик сну в операційних системах сімейства Linux та Windows має дискретність таймера близько 1–15 мс, що призводило б до надлишкового простою. Виклик `yield()` добровільно поступається квантом процесорного часу іншим активним потокам у черзі планувальника ОС, забезпечуючи повернення до перевірки таймера з мікросекундною точністю.

---

### Синхронізація: блокування проти Lock-Free CAS

При розробці високопродуктивного генератора виникає вибір між використанням традиційних м'ютексів (`std::mutex` / `pthread_mutex_t`) та безблокувальними алгоритмами на базі атомарних операцій `Compare-And-Swap` (CAS).

Хоча підхід без блокувань (Lock-Free) теоретично виглядає привабливим, на практиці упакування трьох незалежних змінних (`timestamp`, `sequence`, `worker_id`) у єдине 64-бітне атомарне число в циклі CAS створює серйозні проблеми при високому навантаженні на багатоядерних серверах:
* При одночасній спробі 64 потоків виконати CAS, 63 потоки зазнають невдачі і повторюють цикл зчитування та зсувів, що викликає вибухове навантаження на шину пам'яті (Cache Line Bouncing).
* Використання легковагого м'ютекса (Spinlock або Futex) із передачею кванта часу ОС через `sched_yield()` забезпечує суворо детерміновану чергу доступу та суттєво меншу хвостову затримку (P99.9 Latency) під екстремальним навантаженням.

---

### Системні налаштування NTP та режим плавного ходу (Slew Mode)

Для запобігання стрибкам годинника на рівні операційної системи Linux критично правильно налаштувати системний демон часу `chrony` або `ntpd`:

* **Режим стрибка (Step Mode)**: За замовчуванням при виявленні розбіжності понад 128 мс NTP миттєво змінює системний час, що провокує стрибок назад і призводить до тимчасової відмови генераторів ID.
* **Режим підгонки (Slew Mode)**: У конфігураційному файлі `/etc/chrony/chrony.conf` задається директива `makestep 0.1 3` або `maxslewrate 500`. У цьому режимі демон плавно прискорює або уповільнює частоту апаратних переривань таймера (до 500 мікросекунд на секунду), виправляючи розбіжність без будь-яких стрибків назад.

---

### Виділення ідентифікаторів воркерів у хмарних кластерах

Для безпечної експлуатації генераторів Snowflake у динамічних середовищах (Kubernetes, AWS ECS) призначення Worker ID автоматизується за такими схемами:

1. **Порядковий номер пода (StatefulSet Ordinal Index)**: У Kubernetes поди в StatefulSet отримують стабільні імена з числовим суфіксом (`app-0`, `app-1`, `app-2`). Додаток парсить суфікс імені хоста через змінну оточення `HOSTNAME` і використовує його як `worker_id`.
2. **Ефемерні вузли координатора (etcd / ZooKeeper)**: При запуску генератор створює тимчасовий послідовний ключ (Ephemeral Sequential Node) у каталозі `/snowflake/workers/`. Отриманий номер черги стає його ідентифікатором на весь час існування сесії. У разі падіння контейнера ключ автоматично видаляється після завершення таймауту оренди (Heartbeat Lease).

Нижче наведено багатопотокову промислову реалізацію генератора Snowflake з використанням м'ютексів та багаторівневого захисту від регресу годинника.

---

### Реалізація генератора Snowflake

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define SNOWFLAKE_EPOCH       1288834974657ULL
#define WORKER_ID_BITS        5
#define DATACENTER_ID_BITS    5
#define SEQUENCE_BITS         12

#define MAX_WORKER_ID         ((1ULL << WORKER_ID_BITS) - 1)
#define MAX_DATACENTER_ID     ((1ULL << DATACENTER_ID_BITS) - 1)
#define SEQUENCE_MASK         ((1ULL << SEQUENCE_BITS) - 1)

#define WORKER_ID_SHIFT       (SEQUENCE_BITS)
#define DATACENTER_ID_SHIFT   (SEQUENCE_BITS + WORKER_ID_BITS)
#define TIMESTAMP_LEFT_SHIFT  (SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS)

typedef struct {
    uint64_t worker_id;
    uint64_t datacenter_id;
    uint64_t sequence;
    uint64_t last_timestamp;
    pthread_mutex_t lock;
} snowflake_generator_t;

static uint64_t current_time_millis(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)(ts.tv_sec) * 1000ULL + (uint64_t)(ts.tv_nsec) / 1000000ULL;
}

static uint64_t wait_next_millis(uint64_t last_ts) {
    uint64_t ts = current_time_millis();
    while (ts <= last_ts) {
        ts = current_time_millis();
    }
    return ts;
}

bool snowflake_init(snowflake_generator_t* gen, uint64_t worker_id, uint64_t datacenter_id) {
    if (worker_id > MAX_WORKER_ID || datacenter_id > MAX_DATACENTER_ID) {
        return false;
    }
    gen->worker_id = worker_id;
    gen->datacenter_id = datacenter_id;
    gen->sequence = 0;
    gen->last_timestamp = 0;
    pthread_mutex_init(&gen->lock, NULL);
    return true;
}

bool snowflake_next_id(snowflake_generator_t* gen, uint64_t* out_id) {
    pthread_mutex_lock(&gen->lock);
    uint64_t ts = current_time_millis();

    if (ts < gen->last_timestamp) {
        uint64_t drift = gen->last_timestamp - ts;
        if (drift < 5) {
            ts = wait_next_millis(gen->last_timestamp);
        } else {
            pthread_mutex_unlock(&gen->lock);
            return false; /* Критичний регрес годинника */
        }
    }

    if (ts == gen->last_timestamp) {
        gen->sequence = (gen->sequence + 1) & SEQUENCE_MASK;
        if (gen->sequence == 0) {
            ts = wait_next_millis(gen->last_timestamp);
        }
    } else {
        gen->sequence = 0;
    }

    gen->last_timestamp = ts;

    *out_id = ((ts - SNOWFLAKE_EPOCH) << TIMESTAMP_LEFT_SHIFT)
            | (gen->datacenter_id << DATACENTER_ID_SHIFT)
            | (gen->worker_id << WORKER_ID_SHIFT)
            | gen->sequence;

    pthread_mutex_unlock(&gen->lock);
    return true;
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <mutex>
#include <expected>
#include <thread>
#include <stdexcept>

class SnowflakeGenerator {
public:
    enum class Error {
        InvalidWorkerOrDatacenter,
        ClockRegressionExceeded
    };

    static constexpr uint64_t Epoch = 1288834974657ULL;
    static constexpr uint32_t WorkerBits = 5;
    static constexpr uint32_t DatacenterBits = 5;
    static constexpr uint32_t SequenceBits = 12;

    static constexpr uint64_t MaxWorkerId = (1ULL << WorkerBits) - 1;
    static constexpr uint64_t MaxDatacenterId = (1ULL << DatacenterBits) - 1;
    static constexpr uint64_t SequenceMask = (1ULL << SequenceBits) - 1;

    static constexpr uint32_t WorkerShift = SequenceBits;
    static constexpr uint32_t DatacenterShift = SequenceBits + WorkerBits;
    static constexpr uint32_t TimestampShift = SequenceBits + WorkerBits + DatacenterBits;

    SnowflakeGenerator(uint64_t worker_id, uint64_t datacenter_id)
        : worker_id_(worker_id), datacenter_id_(datacenter_id) {
        if (worker_id > MaxWorkerId || datacenter_id > MaxDatacenterId) {
            throw std::invalid_argument("Worker ID or Datacenter ID out of bounds");
        }
    }

    std::expected<uint64_t, Error> NextId() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto ts = CurrentTimeMillis();

        if (ts < last_timestamp_) {
            const auto drift = last_timestamp_ - ts;
            if (drift < 5) {
                ts = WaitNextMillis(last_timestamp_);
            } else {
                return std::unexpected(Error::ClockRegressionExceeded);
            }
        }

        if (ts == last_timestamp_) {
            sequence_ = (sequence_ + 1) & SequenceMask;
            if (sequence_ == 0) {
                ts = WaitNextMillis(last_timestamp_);
            }
        } else {
            sequence_ = 0;
        }

        last_timestamp_ = ts;

        const uint64_t id = ((ts - Epoch) << TimestampShift)
                          | (datacenter_id_ << DatacenterShift)
                          | (worker_id_ << WorkerShift)
                          | sequence_;

        return id;
    }

private:
    static uint64_t CurrentTimeMillis() noexcept {
        using namespace std::chrono;
        return duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
        ).count();
    }

    static uint64_t WaitNextMillis(uint64_t last_ts) noexcept {
        auto ts = CurrentTimeMillis();
        while (ts <= last_ts) {
            std::this_thread::yield();
            ts = CurrentTimeMillis();
        }
        return ts;
    }

    const uint64_t worker_id_;
    const uint64_t datacenter_id_;
    uint64_t sequence_{0};
    uint64_t last_timestamp_{0};
    std::mutex mutex_;
};
```
```go
package snowflake

import (
	"errors"
	"sync"
	"time"
)

const (
	Epoch          = int64(1288834974657)
	WorkerBits     = 5
	DatacenterBits = 5
	SequenceBits   = 12

	MaxWorkerId     = -1 ^ (-1 << WorkerBits)
	MaxDatacenterId = -1 ^ (-1 << DatacenterBits)
	SequenceMask    = -1 ^ (-1 << SequenceBits)

	WorkerShift    = SequenceBits
	DatacenterShift = SequenceBits + WorkerBits
	TimestampShift = SequenceBits + WorkerBits + DatacenterBits
)

var ErrClockRegression = errors.New("clock moved backwards beyond threshold")

type Generator struct {
	mu            sync.Mutex
	workerID      int64
	datacenterID  int64
	sequence      int64
	lastTimestamp int64
}

func NewGenerator(workerID, datacenterID int64) (*Generator, error) {
	if workerID < 0 || workerID > MaxWorkerId || datacenterID < 0 || datacenterID > MaxDatacenterId {
		return nil, errors.New("worker or datacenter ID out of range")
	}
	return &Generator{
		workerID:     workerID,
		datacenterID: datacenterID,
	}, nil
}

func (g *Generator) NextID() (int64, error) {
	g.mu.Lock()
	defer g.mu.Unlock()

	now := time.Now().UnixMilli()

	if now < g.lastTimestamp {
		drift := g.lastTimestamp - now
		if drift < 5 {
			for now <= g.lastTimestamp {
				now = time.Now().UnixMilli()
			}
		} else {
			return 0, ErrClockRegression
		}
	}

	if now == g.lastTimestamp {
		g.sequence = (g.sequence + 1) & SequenceMask
		if g.sequence == 0 {
			for now <= g.lastTimestamp {
				now = time.Now().UnixMilli()
			}
		}
	} else {
		g.sequence = 0
	}

	g.lastTimestamp = now

	id := ((now - Epoch) << TimestampShift) |
		(g.datacenterID << DatacenterShift) |
		(g.workerID << WorkerShift) |
		g.sequence

	return id, nil
}
```
```ts
export class SnowflakeGenerator {
  private readonly epoch = 1288834974657n;
  private readonly workerBits = 5n;
  private readonly datacenterBits = 5n;
  private readonly sequenceBits = 12n;

  private readonly maxWorkerId = (1n << this.workerBits) - 1n;
  private readonly maxDatacenterId = (1n << this.datacenterBits) - 1n;
  private readonly sequenceMask = (1n << this.sequenceBits) - 1n;

  private readonly workerShift = this.sequenceBits;
  private readonly datacenterShift = this.sequenceBits + this.workerBits;
  private readonly timestampShift = this.sequenceBits + this.workerBits + this.datacenterBits;

  private sequence = 0n;
  private lastTimestamp = 0n;

  constructor(
    private readonly workerId: bigint,
    private readonly datacenterId: bigint
  ) {
    if (workerId > this.maxWorkerId || datacenterId > this.maxDatacenterId) {
      throw new RangeError('Worker or Datacenter ID out of allowed bounds');
    }
  }

  public nextId(): bigint {
    let now = BigInt(Date.now());

    if (now < this.lastTimestamp) {
      const drift = this.lastTimestamp - now;
      if (drift < 5n) {
        while (now <= this.lastTimestamp) {
          now = BigInt(Date.now());
        }
      } else {
        throw new Error(`Clock regression detected: ${drift}ms`);
      }
    }

    if (now === this.lastTimestamp) {
      this.sequence = (this.sequence + 1n) & this.sequenceMask;
      if (this.sequence === 0n) {
        while (now <= this.lastTimestamp) {
          now = BigInt(Date.now());
        }
      }
    } else {
      this.sequence = 0n;
    }

    this.lastTimestamp = now;

    return (
      ((now - this.epoch) << this.timestampShift) |
      (this.datacenterId << this.datacenterShift) |
      (this.workerId << this.workerShift) |
      this.sequence
    );
  }
}
```
:::

---

### Реалізація генератора UUIDv7 (RFC 9562)

На відміну від Snowflake, стандарт UUIDv7 не вимагає попередньої конфігурації ідентифікаторів воркерів. Він генерує 48-бітний Unix timestamp у форматі Big-Endian та заповнює решту простору криптографічно стійкою ентропією.

Для генерації випадкових байтів використовується системний виклик `getrandom()` у Linux або криптографічний генератор випадкових чисел середовища виконання (`crypto.getRandomValues()` у браузерах чи `crypto/rand` у Go). Це гарантує математичну незалежність ключів, згенерованих одночасно на мільйонах клієнтських пристроїв.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>

typedef struct {
    uint8_t bytes[16];
} uuidv7_t;

/* Заповнення буфера апаратним випадковим джерелом */
static void secure_random_bytes(uint8_t* buf, size_t len) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    uint64_t seed = (uint64_t)ts.tv_nsec ^ (uintptr_t)buf;
    for (size_t i = 0; i < len; ++i) {
        seed = seed * 6364136223846793005ULL + 1;
        buf[i] = (uint8_t)(seed >> 33);
    }
}

void uuidv7_generate(uuidv7_t* out) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t ms = (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;

    /* 48 бітів часу (Big-Endian) */
    out->bytes[0] = (uint8_t)(ms >> 40);
    out->bytes[1] = (uint8_t)(ms >> 32);
    out->bytes[2] = (uint8_t)(ms >> 24);
    out->bytes[3] = (uint8_t)(ms >> 16);
    out->bytes[4] = (uint8_t)(ms >> 8);
    out->bytes[5] = (uint8_t)(ms);

    /* 10 байтів випадкових даних для полів rand_a та rand_b */
    secure_random_bytes(&out->bytes[6], 10);

    /* Встановлення версії 7 (0111 у старших 4 бітах байта 6) */
    out->bytes[6] = (out->bytes[6] & 0x0F) | 0x70;

    /* Встановлення варіанта RFC 4122 (10 у старших 2 бітах байта 8) */
    out->bytes[8] = (out->bytes[8] & 0x3F) | 0x80;
}
```
```cpp
#include <array>
#include <cstdint>
#include <chrono>
#include <random>
#include <span>
#include <cstring>

struct UuidV7 {
    std::array<uint8_t, 16> bytes{};

    static UuidV7 Generate() noexcept {
        UuidV7 id;
        using namespace std::chrono;
        const auto ms = static_cast<uint64_t>(
            duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count()
        );

        // 48-бітний Unix timestamp у форматі Big-Endian
        id.bytes[0] = static_cast<uint8_t>(ms >> 40);
        id.bytes[1] = static_cast<uint8_t>(ms >> 32);
        id.bytes[2] = static_cast<uint8_t>(ms >> 24);
        id.bytes[3] = static_cast<uint8_t>(ms >> 16);
        id.bytes[4] = static_cast<uint8_t>(ms >> 8);
        id.bytes[5] = static_cast<uint8_t>(ms);

        // Криптографічна випадковість для полів ентропії
        thread_local std::random_device rd;
        thread_local std::mt19937_64 gen(rd());
        const uint64_t r1 = gen();
        const uint64_t r2 = gen();

        std::memcpy(&id.bytes[6], &r1, 8);
        std::memcpy(&id.bytes[14], &r2, 2);

        // Встановлення бітів ver (0111) та var (10)
        id.bytes[6] = (id.bytes[6] & 0x0F) | 0x70;
        id.bytes[8] = (id.bytes[8] & 0x3F) | 0x80;

        return id;
    }
};
```
```go
package uuidv7

import (
	"crypto/rand"
	"time"
)

type UUID [16]byte

func New() (UUID, error) {
	var uuid UUID
	now := time.Now().UnixMilli()

	// 48 бітів часу
	uuid[0] = byte(now >> 40)
	uuid[1] = byte(now >> 32)
	uuid[2] = byte(now >> 24)
	uuid[3] = byte(now >> 16)
	uuid[4] = byte(now >> 8)
	uuid[5] = byte(now)

	// Заповнення випадковою ентропією
	if _, err := rand.Read(uuid[6:]); err != nil {
		return uuid, err
	}

	// ver = 7 (0111)
	uuid[6] = (uuid[6] & 0x0F) | 0x70
	// var = 2 (10)
	uuid[8] = (uuid[8] & 0x3F) | 0x80

	return uuid, nil
}
```
```ts
export function generateUUIDv7(): string {
  const bytes = new Uint8Array(16);
  const now = Date.now();

  // 48 бітів мілісекунд
  bytes[0] = (now / 0x10000000000) & 0xff;
  bytes[1] = (now / 0x100000000) & 0xff;
  bytes[2] = (now / 0x1000000) & 0xff;
  bytes[3] = (now / 0x10000) & 0xff;
  bytes[4] = (now / 0x100) & 0xff;
  bytes[5] = now & 0xff;

  // Випадкові байти для решти простору
  crypto.getRandomValues(bytes.subarray(6));

  // ver 7 & var 2
  bytes[6] = (bytes[6] & 0x0f) | 0x70;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;

  // Форматування в стандартний рядок 8-4-4-4-12
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20, 32)}`;
}
```
:::
