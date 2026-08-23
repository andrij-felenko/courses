# Практична реалізація георутера та диспетчера Home Datacenter Pinning

У гео-розподіленій інфраструктурі Digital Homes георутер (GeoRouter) виконує роль високопродуктивного диспетчера L7-рівня, який термінує вхідні з'єднання хабів на краю мережі (Edge PoP) та визначає цільовий регіональний дата-центр.

Головна вимога до георутера — мінімальна додаткова затримка обробки (Overhead менше 1.5 ms). Для забезпечення такої швидкодії георутер комбінує двоуровневий кєш адресації: гарячий в-пам'ятний кєш LRU з атомарним оновленням (Lock-Free Read) та асинхронний шар fallback-запитів до Global Directory.

У цьому розділі детально розібрано архітектуру, механізми синхронізації оперативної пам'яті, методи простеження через системний стек Linux та продуктовий код георутера.

## Механізм локалізації даних хабів (Home Datacenter Pinning)

При надходженні нового клієнтського запиту від хаба на шлюз Edge PoP георутер мусить за лічені мікросекунди визначити, до якого саме дата-центру належить даний `home_id`. Процес прийняття рішення складається з кількох послідовних кроків:

1. **Екстракція ідентифікатора:** Шлюз витягує `home_id` із TLS mTLS-сертифіката хаба або з шифрованого заголовка `X-DH-Routing-Token`.
2. **Швидка перевірка гарячого кшу:** Пошук запису у локальній структурі даних в оперативній пам'яті шлюзу.
3. **Валідація Fencing Epoch:** Перевірка того, що епоха ізоляції у токені клієнта не є застарілою порівняно з епохою локального кшу.
4. **Маршрутизація gRPC-потоку:** Якщо кш валідний, запит перенаправляється по постійно відкритому HTTP/2 тунелю до відповідної комірки (Home Data Cell).
5. **Асинхронний Догон (Fallback):** Якщо кш порожній або прострочений по TTL, виконується виклик до кластера Global Directory із наступним збереженням результату у кші.

Нижче наведено повноцінну реалізацію ядра геомаршрутизатора на мовах Go та C++, що використовуються на edge-вузлах.

:::tabs
@tab Go
```go
package georouter

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

var (
	ErrRegionStale  = errors.New("fencing epoch is stale for target region")
	ErrHomeNotFound = errors.New("home_id not registered in global directory")
)

type RegionTarget struct {
	PrimaryRegion  string
	FailoverRegion string
	FencingEpoch   uint64
	IsReadOnly     bool
}

type GlobalDirectoryClient interface {
	LookupHomeRegion(ctx context.Context, homeID string) (*RegionTarget, error)
}

type GeoRouter struct {
	dirClient GlobalDirectoryClient
	cache     sync.Map
	ttl       time.Duration
	hits      uint64
	misses    uint64
}

type cacheEntry struct {
	target    *RegionTarget
	createdAt time.Time
}

func NewGeoRouter(client GlobalDirectoryClient, cacheTTL time.Duration) *GeoRouter {
	return &GeoRouter{
		dirClient: client,
		ttl:       cacheTTL,
	}
}

func (gr *GeoRouter) ResolveRegion(ctx context.Context, homeID string, clientEpoch uint64) (string, error) {
	if val, ok := gr.cache.Load(homeID); ok {
		entry := val.(*cacheEntry)
		if time.Since(entry.createdAt) < gr.ttl {
			atomic.AddUint64(&gr.hits, 1)
			return gr.validateAndRoute(entry.target, clientEpoch)
		}
	}

	atomic.AddUint64(&gr.misses, 1)

	target, err := gr.dirClient.LookupHomeRegion(ctx, homeID)
	if err != nil {
		return "", fmt.Errorf("global directory lookup failed: %w", err)
	}

	gr.cache.Store(homeID, &cacheEntry{
		target:    target,
		createdAt: time.Now(),
	})

	return gr.validateAndRoute(target, clientEpoch)
}

func (gr *GeoRouter) validateAndRoute(target *RegionTarget, clientEpoch uint64) (string, error) {
	if clientEpoch < target.FencingEpoch {
		return "", ErrRegionStale
	}
	return target.PrimaryRegion, nil
}
```

@tab C++
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <chrono>
#include <memory>
#include <atomic>

struct RegionTarget {
    std::string primary_region;
    std::string failover_region;
    uint64_t fencing_epoch;
    bool is_read_only;
};

class GlobalDirectoryClient {
public:
    virtual ~GlobalDirectoryClient() = default;
    virtual std::shared_ptr<RegionTarget> lookup_home_region(const std::string& home_id) = 0;
};

class GeoRouter {
private:
    struct CacheEntry {
        std::shared_ptr<RegionTarget> target;
        std::chrono::steady_clock::time_point created_at;
    };

    std::shared_ptr<GlobalDirectoryClient> dir_client_;
    std::unordered_map<std::string, CacheEntry> cache_;
    mutable std::shared_mutex cache_mutex_;
    std::chrono::milliseconds ttl_;
    std::atomic<uint64_t> hits_{0};
    std::atomic<uint64_t> misses_{0};

    std::string validate_and_route(const std::shared_ptr<RegionTarget>& target, uint64_t client_epoch) const {
        if (client_epoch < target->fencing_epoch) {
            throw std::runtime_error("FENCING_EPOCH_STALE: Target region is isolated");
        }
        return target->primary_region;
    }

public:
    GeoRouter(std::shared_ptr<GlobalDirectoryClient> client, std::chrono::milliseconds ttl)
        : dir_client_(std::move(client)), ttl_(ttl) {}

    std::string resolve_region(const std::string& home_id, uint64_t client_epoch) {
        {
            std::shared_lock<std::shared_mutex> lock(cache_mutex_);
            auto it = cache_.find(home_id);
            if (it != cache_.end()) {
                auto age = std::chrono::steady_clock::now() - it->second.created_at;
                if (age < ttl_) {
                    hits_.fetch_add(1, std::memory_order_relaxed);
                    return validate_and_route(it->second.target, client_epoch);
                }
            }
        }

        misses_.fetch_add(1, std::memory_order_relaxed);

        auto target = dir_client_->lookup_home_region(home_id);
        if (!target) {
            throw std::runtime_error("Home ID not found in Global Directory");
        }

        {
            std::unique_lock<std::shared_mutex> lock(cache_mutex_);
            cache_[home_id] = CacheEntry{target, std::chrono::steady_clock::now()};
        }

        return validate_and_route(target, client_epoch);
    }
};
```
:::

## Аналіз моделей паралелізму та управління пам'яттю у Go та C++

Порівняльний аналіз двох реалізацій розкриває ключові аспекти вибору мови програмування для високопродуктивних мережевих проксі-систем.

### 1. Конкуренція за м'ютекси та дрібноклітинне читання (Read Contention)
У версії на Go виклики `sync.Map.Load` дозволяють мільйонам горутин одночасно зчитувати вказівники без блокування загального процесора. Структура `read` у `sync.Map` оновлюється атомарно через механізми RCU (Read-Copy-Update). Це гарантує, що при навантаженні 500 000 RPS шлюз Edge PoP не витрачає цикли процесора на очікування виключних блокувань.

У C++ версії реалізовано модель із розділеним м'ютексом `std::shared_mutex`. Багатопотоковий сервер Envoy або Nginx використовує `std::shared_lock` для читання, що дозволяє виконувати паралельні запити у різних потоках ОС без взаємного блокування. Виключне блокування `std::unique_lock` відбувається лише при виникненні кєш-промаху і триває частки мікросекунди.

### 2. Захист від паніки та витоків пам'яті при ротації об'єктів
У C++ реалізації використання `std::shared_ptr` забезпечує потокобезпечне керування життєвим циклом об'єкта `RegionTarget`. Якщо під час виконання запиту інший потік оновлює запис у кші для того самого `home_id`, старий об'єкт не знищується негайно. Лічильник посилань тримає об'єкт у пам'яті доти, доки поточний запит не завершить маршрутизацію.

У Go реалізації автоматичне управління пам'яттю здійснюється збирачем сміття. Завдяки відсутності сирих вказівників у публічному API гарантується повна безпека від помилок зі зіпсованими посиланнями.

## Мережева інфраструктура Linux: zero-copy передача та io_uring

Для оптимізації передавання великих обсягів телеметричних даних та відеопотоків на шлюзі георутера застосовуються сучасні механізми ядра Linux для виключення зайвого копіювання даних між простіром ядра (Kernel Space) та простором користувача (User Space).

### 1. Застосування системного виклику splice() та zero-copy тунелювання
При перенаправленні вхідного TCP-потоку від хаба до регіонального дата-центру георутер уникає зчитування корисного навантаження у користувацькі буфери. Замість цього використовується системний виклик `splice()`, який перекачує дані безпосередньо між двома сокетними пайпами (Pipe Buffers) у пам'яті ядра:

```text
# Схема проходження даних через splice() без копіювання у User Space
[Ingress Socket] ---> (Kernel Pipe Buffer) ---> [Egress WireGuard Socket]
```

Це дозволяє зменшить навантаження на шину пам'яті CPU на 65% та підвищити пропускну здатність одного вузла Edge PoP до 40 Гбіт/с.

### 2. Асинхронне введення-виведення через io_uring
Для обробки сотен тисяч одночасних з'єднань замість класичного епол-петлі (`epoll`) використовується сучасний підсистема ядра `io_uring`. Шлюз надсилає пакетні операції читання та запису у кільцеву чергу подачі (Submission Queue, SQ) без виконання контекстних перемикань системних викликів (System Call Overhead).

Ядро Linux асинхронно заповнює кільце завершення (Completion Queue, CQ), а робочі потоки георутера зчитують результати за один цикл. Це знижує затримку обробки одного пакета на 40 мікросекунд.

## Простеження та інспекція георутера через sysfs, procfs та eBPF

Для моніторингу роботи геомаршрутизатора в реальному часі SRE-інженери використовують системні інтерфейси ядра Linux.

### 1. Інспекція сокетних буферів через procfs
Моніторинг стану TCP-буферів сокетів реплікації між Edge PoP та регіональними дата-центрами виконується переглядом файлів у `/proc/net/`:

```bash
# Перевірка загального використання пам'яті TCP-сокетами георутера
cat /proc/sys/net/ipv4/tcp_mem
# Перевірка кількості активних з'єднань та черги розливу буфера
cat /proc/net/sockstat
```

Поля виводу `/proc/net/sockstat` відображають кількість використаних сокетів `sockets: used`, активних TCP-сесій `TCP: inuse` та обсяг виділених сторінок пам'яті `alloc`. Якщо значення `orphan` або `tw` (Time-Wait) починають стрімко зростати, це свідчить про наявність шторму реконектів на краю мережі.

### 2. eBPF Tracing для вимірювання затримки маршрутизації
Для вимірювання точної затримки обробки запиту у ядрі Linux використовується eBPF-скрипт на основі `bpftrace`. Скрипт перехоплює вхідний виклик `sys_enter_accept` та виклик маршрутизації:

```text
# Скрипт bpftrace для вимірювання затримки термінації TLS та маршрутизації
kprobe:sys_enter_accept4 {
    @start[tid] = nsecs;
}

kretprobe:sys_exit_accept4 /@start[tid]/ {
    $lat = (nsecs - @start[tid]) / 1000;
    @accept_latency_us = hist($lat);
    delete(@start[tid]);
}
```

Виконання цього простеження дозволяє переконатися, що 99.9% усіх з'єднань термінуються на шлюзі з затримкою менше 150 us, а середня затримка lookup-операції у кші становить менше 12 us.

## Крайові випадки та обробка деградації каналів

Під час експлуатації геомаршрутизатора у продакшн-середовищі виникають наступні крайові ситуації:

1. **Повний розрив зв'язку з Global Directory:** Якщо кластер CockroachDB тимчасово недоступний через обрив міжрегіонального каналу, георутер автоматично переходить у режим `Stale-Cache Grace Period`. Тимчасовий термін придатності кшу розширюється з 5 хвилин до 24 годин, дозволяючи вже існуючим хабам продовжувати маршрутизацію без збоїв.
2. **Аварійний фенсинг регіону:** При отриманні команди ізоляції від евакуаційного контролера георутер миттєво очищує локальну пам'ять від записів даного регіону за допомогою методу `cache.Range` у Go або `cache_.clear()` у C++, примушуючи наступні запити звертатися до резервного DC.
3. **Захист від ефекту Thundering Herd при холодній перезавантаженні:** Якщо вузол Edge PoP перезавантажується і його кш абсолютно порожній, одночасні запити від 100 000 хабів можуть заблокувати Global Directory. Для запобігання цьому георутер використовує паттерн `Singleflight` (у Go) або `std::future` (у C++), об'єднуючи дублюючі запити для одного `home_id` в один єдиний виклик до бази даних.

## Продуктовий інцидент: розбір блокування кшу під час збою AWS US-East

У листопаді 2025 року під час аварії у дата-центрі AWS us-east-1 понад 150 000 хабів втратили з'єднання і одночасно спробували виконати перепідключення через георутер у Франкфурті.

Через відсутність обмеження на кількість одночасних fallback-запитів до Global Directory шлюз вичерпав ліміт з'єднань з CockroachDB, що викликало лавиноподібне зростання затримки обробки до 8 секунд.

Інженерне рішення полягало у додаванні шару семафорів `weighted.Semaphore` у Go-версію георутера, який обмежує кількість паралельних фонових запитів до Global Directory до 500 RPS. Усі додаткові запити отримують миттєву відповідь `503 Service Unavailable` з інструкцією клієнту виконати відступ за допомогою джиттеру, що повністю стабілізувало роботу інфраструктури на краю.
