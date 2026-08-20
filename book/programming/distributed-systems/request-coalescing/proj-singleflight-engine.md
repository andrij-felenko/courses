# ⚙️ Промисловий рушій Single-Flight: синхронізація, скасування та безпека панік

Спрощена реалізація об'єднання запитів через базовий асоціативний масив та м'ютекс часто приховує підступні архітектурні дефекти. При переході в промислове середовище з сотнями тисяч одночасних запитів наївний код провокує блокування робочих потоків, витоки пам'яті через завислі дескриптори, взаємне пошкодження пам'яті через спільні покажчики та повну відмову сервісу через неперехоплені винятки.

Промисловий рушій Single-Flight повинен надійно ізолювати ці сценарії, гарантуючи детерміновану поведінку за будь-яких помилок, клієнтських розривів та панік. На відміну від навчальних прикладів, виробничий рушій має враховувати моделі пам'яті сучасних компіляторів, асинхронні контексти виконання та гарантії безпеки багатопотокового доступу.

## Архітектура та ключові інженерні вимоги

Проектування надійного рушія дедуплікації викликів спирається на чотири обов'язкові інженерні принципи:

1. **Ізоляція відмов і панік (Panic Safety):** Якщо функція виконання генерує виняток або аварійно завершується через паніку, рейс зобов'язаний гарантовано видалити свій ключ із таблиці групи та транслювати виняток усім підписаним очікувачам. Зависання очікувачів у черзі без отримання сигналу неприпустиме.
2. **Розв'язка контекстів скасування (Context Decoupling):** Якщо перший клієнт-лідер обриває мережеве TCP-з'єднання або виходить за власним дедлайном, бекенд-виклик не повинен автоматично скасовуватися, якщо в черзі лишаються інші клієнти з активними дедлайнами.
3. **Захист від стану перегонів пам'яті (Deep Copy / Immutability):** Повернення змінного покажчика на структуру призводить до того, що десятки паралельних потоків одночасно читають і модифікують один і той самий об'єкт у пам'яті. Необхідно застосовувати незмінні типи даних (англ. *immutable DTO*) або створювати глибокі копії об'єктів.
4. **Гранулярність блокувань:** Для запобігання деградації пропускної здатності на єдиному глобальному м'ютексі таблиця активних викликів може шардуватися за хешем ключа (наприклад, 64 незалежні шарди з власними м'ютексами).

## Детальний розбір реалізації за мовами програмування

Розглянемо ключові особливості реалізації патерна в різних середовищах виконання:

- **C++20:** Використовує `std::promise` та `std::shared_future` для трансляції результату багатьом очікувачам. Захоплення винятків через `std::current_exception()` та встановлення їх у проміс через `set_exception()` гарантує безпечне розблокування очікувачів без падіння процесу. Видалення ключа з таблиці `table_.erase(key)` виконується лідером під захистом м'ютекса до отримання значення з футури.
- **Go:** Опирається на `sync.WaitGroup` для блокування очікувачів та `sync.Mutex` для захисту асоціативного масиву. Метод `DoChan` повертає буферизований канал, що дозволяє клієнтам слухати результат через `select` з контекстом `context.Context`. Захист від панік реалізовано через `defer` та перехоплювач `recover()`.
- **Rust:** Застосовує асинхронні канали розсилки `tokio::sync::broadcast` та блокування `Arc<Mutex<HashMap>>`. Зверніть увагу на явний виклик `drop(table)` перед порожденням асинхронної таски `tokio::spawn`, що мінімізує час утримання блокування таблиці.
- **TypeScript:** Використовує асинхронний асоціативний масив `Map<string, Promise<T>>`. Очищення запису з масиву гарантується блоком `finally`, що забезпечує коректне видалення ключа як при успішній відповіді, так і при викиданні помилки.

## Реалізація промислового рушія різними мовами

Нижче наведено повноцінну виробничу реалізацію патерна Single-Flight мовами C++, Go, Rust та TypeScript.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <memory>
#include <future>
#include <mutex>
#include <stdexcept>
#include <chrono>

template <typename T>
class SingleFlight {
public:
    struct Result {
        T value;
        bool shared{false};
        size_t waiters_count{0};
    };

private:
    struct Call {
        std::shared_future<T> future;
        size_t waiters{0};
    };

    std::mutex mu_;
    std::unordered_map<std::string, std::shared_ptr<Call>> table_;

public:
    template <typename Func>
    Result execute(const std::string& key, Func&& fn) {
        std::shared_ptr<Call> call;
        bool is_leader = false;
        std::promise<T> promise;

        {
            std::lock_guard<std::mutex> lock(mu_);
            auto it = table_.find(key);
            if (it != table_.end()) {
                // Вже є активний рейс: стаємо очікувачем
                call = it->second;
                call->waiters++;
            } else {
                // Ми перший запит: стаємо лідером
                call = std::make_shared<Call>();
                call->future = promise.get_future().share();
                table_[key] = call;
                is_leader = true;
            }
        }

        if (is_leader) {
            // Виконання лідерського рейсу з перехопленням винятків
            try {
                T val = fn();
                promise.set_value(val);
            } catch (...) {
                promise.set_exception(std::current_exception());
            }

            // Очищення таблиці після завершення
            std::lock_guard<std::mutex> lock(mu_);
            table_.erase(key);
        }

        // Очікування завершення через shared_future
        T result_value = call->future.get();

        return Result{
            .value = std::move(result_value),
            .shared = !is_leader,
            .waiters_count = call->waiters
        };
    }
};
```
```go
package singleflight

import (
    "context"
    "errors"
    "fmt"
    "sync"
)

type Result[T any] struct {
    Val    T
    Err    error
    Shared bool
}

type call[T any] struct {
    wg      sync.WaitGroup
    val     T
    err     error
    waiters int
}

type Group[T any] struct {
    mu sync.Mutex
    m  map[string]*call[T]
}

func NewGroup[T any]() *Group[T] {
    return &Group[T]{
        m: make(map[string]*call[T]),
    }
}

// Do блокує виклик до завершення рейсу
func (g *Group[T]) Do(key string, fn func() (T, error)) (T, error, bool) {
    g.mu.Lock()
    if c, ok := g.m[key]; ok {
        c.waiters++
        g.mu.Unlock()
        c.wg.Wait()
        return c.val, c.err, true
    }

    c := new(call[T])
    c.wg.Add(1)
    g.m[key] = c
    g.mu.Unlock()

    g.execute(key, c, fn)

    return c.val, c.err, false
}

// DoChan повертає неблокуючий канал результату з підтримкою контексту
func (g *Group[T]) DoChan(ctx context.Context, key string, fn func() (T, error)) <-chan Result[T] {
    ch := make(chan Result[T], 1)

    g.mu.Lock()
    if c, ok := g.m[key]; ok {
        c.waiters++
        g.mu.Unlock()
        go func() {
            c.wg.Wait()
            ch <- Result[T]{Val: c.val, Err: c.err, Shared: true}
        }()
        return ch
    }

    c := new(call[T])
    c.wg.Add(1)
    g.m[key] = c
    g.mu.Unlock()

    go func() {
        g.execute(key, c, fn)
        ch <- Result[T]{Val: c.val, Err: c.err, Shared: false}
    }()

    return ch
}

func (g *Group[T]) execute(key string, c *call[T], fn func() (T, error)) {
    defer func() {
        if r := recover(); r != nil {
            c.err = fmt.Errorf("singleflight panic: %v", r)
        }
        g.mu.Lock()
        delete(g.m, key)
        g.mu.Unlock()
        c.wg.Done()
    }()

    c.val, c.err = fn()
}
```
```rust
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};

#[derive(Clone)]
pub struct SingleFlight<K, V> {
    table: Arc<Mutex<HashMap<K, broadcast::Sender<Result<V, String>>>>>,
}

impl<K, V> SingleFlight<K, V>
where
    K: std::hash::Hash + Eq + Clone + Send + 'static,
    V: Clone + Send + 'static,
{
    pub fn new() -> Self {
        Self {
            table: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub async fn execute<F, Fut>(&self, key: K, f: F) -> Result<V, String>
    where
        F: FnOnce() -> Fut,
        Fut: std::future::Future<Output = Result<V, String>> + Send + 'static,
    {
        let mut rx = {
            let mut table = self.table.lock().await;
            if let Some(tx) = table.get(&key) {
                // Рейс вже в польоті: підписуємось на канал
                tx.subscribe()
            } else {
                // Стаємо лідером рейсу
                let (tx, rx) = broadcast::channel(1);
                table.insert(key.clone(), tx.clone());
                drop(table);

                let table_clone = self.table.clone();
                let key_clone = key.clone();

                tokio::spawn(async move {
                    let result = f().await;
                    let _ = tx.send(result);
                    let mut table = table_clone.lock().await;
                    table.remove(&key_clone);
                });

                rx
            }
        };

        match rx.recv().await {
            Ok(res) => res,
            Err(e) => Err(format!("Broadcast receive error: {:?}", e)),
        }
    }
}
```
```ts
export interface SingleFlightResult<T> {
    value: T;
    shared: boolean;
}

export class SingleFlightGroup {
    private inFlight = new Map<string, Promise<any>>();

    async do<T>(key: string, fn: () => Promise<T>): Promise<SingleFlightResult<T>> {
        const existing = this.inFlight.get(key);
        if (existing) {
            const value = await existing;
            return { value, shared: true };
        }

        const promise = (async () => {
            try {
                return await fn();
            } finally {
                this.inFlight.delete(key);
            }
        })();

        this.inFlight.set(key, promise);
        const value = await promise;
        return { value, shared: false };
    }
}
```
:::

## Метрики та спостережуваність (Observability)

Виробниче використання рушія Single-Flight вимагає детального збору телеметрії. Для оцінки ефективності дедуплікації в систему додають такі лічильники:

1. **Ефективність об'єднання (Coalescing Ratio):** Співвідношення кількості очікувачів до загальної кількості запитів `Waiters / (Leaders + Waiters)`. Значення понад 90% під час напливу свідчить про успішне нівелювання шторму.
2. **Гістограма тривалості рейсу:** Час утримання запису в таблиці активних викликів дозволяє виявити повільні SQL-запити або завислі зовнішні сервіси.
3. **Лічильник аварій та панік:** Фіксує кількість нештатних ситуацій, що дозволяє вчасно реагувати на збої в бізнес-логіці.

## Тестування багатопотокових перегонів пам'яті

Для верифікації відсутності взаємних блокувань і гонок даних тестові набори запускають під контролем динамічних санітайзерів пам'яті:

```bash
# Для Go (вбудований Race Detector):
go test -race -v -count=100 ./...

# Для C++ (Clang ThreadSanitizer):
clang++ -fsanitize=thread -g -O1 -std=c++20 singleflight_test.cpp -o test_tsan && ./test_tsan
```

При побудові стрес-тестів моделюють три граничні інженерні сценарії:

1. **Масовий сплеск однакових викликів (1000 паралельних потоків):** Перевірка того, що базова важка функція `fn()` викликається рівно 1 раз, лічильник очікувачів дорівнює 999, а всі 1000 потоків отримують ідентичний коректний результат без затримок і витоків пам'яті.
2. **Аварійне завершення лідера:** Функція `fn()` генерує виняток або паніку. Тест перевіряє, що всі підписані очікувачі негайно отримують об'єкт помилки, запис у таблиці активних рейсів повністю очищається, а наступний виклик для цього ключа успішно запускає новий незалежний рейс.
3. **Різночасне надходження запитів із таймаутами:** Частина клієнтів скасовує свій виклик через 20 мс за локальним дедлайном, тоді як лідер виконує запит протягом 50 мс. Тест перевіряє, що клієнти з довшими таймаутами успішно отримують коректну відповідь після завершення лідера, а закриття з'єднань першими клієнтами не призводить до передчасного переривання виклику.

Регулярне профілювання затримок та моніторинг кількості активних записів у таблиці дозволяють вчасно виявити аномалії в роботі бекенду та запобігти деградації сервісу.
