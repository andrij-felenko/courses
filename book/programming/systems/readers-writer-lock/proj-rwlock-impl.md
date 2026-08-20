# ⚙️ Реалізація замка читачів-письменника з пріоритетом запису

Створення власного замка читачів-письменника з нуля — найкращий спосіб глибоко зрозуміти інваріанти синхронізації та уникнути прихованих пасток багатопотоковості. Найбільш затребуваним на практиці є варіант із **пріоритетом запису** (англ. *write-preferring rwlock*). Він надійно запобігає голодуванню письменників у системах, де читання становить 95–99% усіх звернень.

### Стан та інваріанти структури

Для коректного відстеження стану замка потрібні три змінні лічильників та прапорців, захищені внутрішнім м'ютексом, а також дві умовні змінні (англ. *condition variables*):

1. `readers` (ціле число): кількість читачів, які зараз перебувають усередині критичної секції.
2. `writers_waiting` (ціле число): кількість письменників, які чекають у черзі на отримання монопольного доступу.
3. `writer_active` (булевий прапорець): дорівнює `true`, якщо один із письменників зараз утримує монопольне блокування.
4. `cond_readers`: умовна змінна, на якій засинають заблоковані читачі.
5. `cond_writers`: умовна змінна, на якій засинають заблоковані письменники.

Інваріанти, які алгоритм зобов'язаний непорушно підтримувати в кожен момент часу:
- Якщо `writer_active == true`, то `readers == 0` (письменник завжди працює в повній монопольній ізоляції від усіх інших потоків).
- Якщо `readers > 0`, то `writer_active == false` (читачі працюють лише за відсутності активного запису).
- Новий читач може увійти лише за умови `writer_active == false` ТА `writers_waiting == 0`. Якщо хоча б один письменник став у чергу (`writers_waiting > 0`), усі нові читачі негайно блокуються на `cond_readers`. Це формує бар'єр, який відсікає нових читачів і дозволяє активним читачам швидко вичерпатися.

### Покроковий алгоритм операцій

#### Захоплення для читання (`read_lock`)
1. Захопити внутрішній м'ютекс.
2. У циклі `while (writer_active || writers_waiting > 0)` заснути на умовній змінній `cond_readers`. Перевірка в циклі `while` обов'язкова для захисту від хибних пробуджень (англ. *spurious wakeups*), коли операційна система виводить потік зі сну без явної команди.
3. Збільшити лічильник активних читачів: `readers++`.
4. Відпустити внутрішній м'ютекс. Тепер потік може безпечно й паралельно з іншими читачами зчитувати спільні дані.

#### Звільнення після читання (`read_unlock`)
1. Захопити внутрішній м'ютекс.
2. Зменшити лічильник читачів: `readers--`.
3. Якщо лічильник впав до нуля (`readers == 0`) і в черзі є очікуючі письменники (`writers_waiting > 0`), надіслати точковий сигнал `signal` на `cond_writers`. Будити треба саме одного очікуючого письменника, оскільки писати може лише один потік.
4. Відпустити внутрішній м'ютекс.

#### Захоплення для запису (`write_lock`)
1. Захопити внутрішній м'ютекс.
2. Збільшити лічильник очікуючих письменників: `writers_waiting++` (це виставляє негайний бар'єр для всіх наступних читачів).
3. У циклі `while (writer_active || readers > 0)` заснути на умовній змінній `cond_writers`.
4. Зменшити лічильник очікуючих: `writers_waiting--`.
5. Встановити прапорець активного запису: `writer_active = true`.
6. Відпустити внутрішній м'ютекс. Потік отримує монопольне право змінювати дані.

#### Звільнення після запису (`write_unlock`)
1. Захопити внутрішній м'ютекс.
2. Скинути прапорець монопольного запису: `writer_active = false`.
3. Якщо в черзі ще є інші очікуючі письменники (`writers_waiting > 0`), надіслати сигнал `signal` на `cond_writers` (передати естафету наступному запису).
4. Інакше, якщо черга письменників порожня, надіслати групове сповіщення `broadcast` на `cond_readers`, щоб розбудити весь накопичений пул заблокованих читачів одночасно.
5. Відпустити внутрішній м'ютекс.

### Повна реалізація мовами C та C++ з тестовим стендом

Нижче наведено повністю робочий код реалізації write-preferring rwlock разом із тестовим стендом для перевірки паралельного доступу мовами C (POSIX threads) та C++ (сучасний стандарт C++17).

:::tabs
```c
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t  cond_readers;
    pthread_cond_t  cond_writers;
    int             readers;
    int             writers_waiting;
    bool            writer_active;
} custom_rwlock_t;

int custom_rwlock_init(custom_rwlock_t *rw) {
    if (!rw) return -1;
    rw->readers = 0;
    rw->writers_waiting = 0;
    rw->writer_active = false;
    if (pthread_mutex_init(&rw->mutex, NULL) != 0) return -1;
    if (pthread_cond_init(&rw->cond_readers, NULL) != 0) {
        pthread_mutex_destroy(&rw->mutex);
        return -1;
    }
    if (pthread_cond_init(&rw->cond_writers, NULL) != 0) {
        pthread_cond_destroy(&rw->cond_readers);
        pthread_mutex_destroy(&rw->mutex);
        return -1;
    }
    return 0;
}

void custom_rwlock_destroy(custom_rwlock_t *rw) {
    if (!rw) return;
    pthread_mutex_destroy(&rw->mutex);
    pthread_cond_destroy(&rw->cond_readers);
    pthread_cond_destroy(&rw->cond_writers);
}

void custom_rwlock_rdlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    while (rw->writer_active || rw->writers_waiting > 0) {
        pthread_cond_wait(&rw->cond_readers, &rw->mutex);
    }
    rw->readers++;
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_rdunlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->readers--;
    if (rw->readers == 0 && rw->writers_waiting > 0) {
        pthread_cond_signal(&rw->cond_writers);
    }
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_wrlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->writers_waiting++;
    while (rw->writer_active || rw->readers > 0) {
        pthread_cond_wait(&rw->cond_writers, &rw->mutex);
    }
    rw->writers_waiting--;
    rw->writer_active = true;
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_wrunlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->writer_active = false;
    if (rw->writers_waiting > 0) {
        pthread_cond_signal(&rw->cond_writers);
    } else {
        pthread_cond_broadcast(&rw->cond_readers);
    }
    pthread_mutex_unlock(&rw->mutex);
}

// Тестовий спільний стан
static custom_rwlock_t g_lock;
static long            g_shared_value = 0;

void* reader_thread(void *arg) {
    long id = (long)arg;
    for (int i = 0; i < 5; ++i) {
        custom_rwlock_rdlock(&g_lock);
        // Безпечне читання спільного ресурсу
        long val = g_shared_value;
        usleep(1000); // Імітація роботи
        custom_rwlock_rdunlock(&g_lock);
    }
    return NULL;
}

void* writer_thread(void *arg) {
    long id = (long)arg;
    for (int i = 0; i < 3; ++i) {
        custom_rwlock_wrlock(&g_lock);
        // Монопольний запис у спільний ресурс
        g_shared_value += 10;
        usleep(2000); // Імітація запису
        custom_rwlock_wrunlock(&g_lock);
    }
    return NULL;
}
```
```cpp
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

class WritePreferringRwLock {
public:
    WritePreferringRwLock() = default;
    ~WritePreferringRwLock() = default;

    WritePreferringRwLock(const WritePreferringRwLock&) = delete;
    WritePreferringRwLock& operator=(const WritePreferringRwLock&) = delete;

    void lock_shared() {
        std::unique_lock<std::mutex> lock(mutex_);
        cond_readers_.wait(lock, [this]() {
            return !writer_active_ && writers_waiting_ == 0;
        });
        ++readers_;
    }

    void unlock_shared() {
        std::unique_lock<std::mutex> lock(mutex_);
        --readers_;
        if (readers_ == 0 && writers_waiting_ > 0) {
            cond_writers_.notify_one();
        }
    }

    void lock() {
        std::unique_lock<std::mutex> lock(mutex_);
        ++writers_waiting_;
        cond_writers_.wait(lock, [this]() {
            return !writer_active_ && readers_ == 0;
        });
        --writers_waiting_;
        writer_active_ = true;
    }

    void unlock() {
        std::unique_lock<std::mutex> lock(mutex_);
        writer_active_ = false;
        if (writers_waiting_ > 0) {
            cond_writers_.notify_one();
        } else {
            cond_readers_.notify_all();
        }
    }

private:
    std::mutex              mutex_;
    std::condition_variable cond_readers_;
    std::condition_variable cond_writers_;
    int                     readers_ = 0;
    int                     writers_waiting_ = 0;
    bool                    writer_active_ = false;
};

// RAII-обгортки для автоматичного звільнення блокувань при розгортанні стека
class SharedLockGuard {
public:
    explicit SharedLockGuard(WritePreferringRwLock& lock) : lock_(lock) {
        lock_.lock_shared();
    }
    ~SharedLockGuard() {
        lock_.unlock_shared();
    }
    SharedLockGuard(const SharedLockGuard&) = delete;
    SharedLockGuard& operator=(const SharedLockGuard&) = delete;

private:
    WritePreferringRwLock& lock_;
};

class ExclusiveLockGuard {
public:
    explicit ExclusiveLockGuard(WritePreferringRwLock& lock) : lock_(lock) {
        lock_.lock();
    }
    ~ExclusiveLockGuard() {
        lock_.unlock();
    }
    ExclusiveLockGuard(const ExclusiveLockGuard&) = delete;
    ExclusiveLockGuard& operator=(const ExclusiveLockGuard&) = delete;

private:
    WritePreferringRwLock& lock_;
};
```
:::

### Порівняння: умовні змінні проти атомарного futex

Наведена вище реалізація на базі `std::mutex` та `std::condition_variable` є навчальним еталоном ясності та надійності: вона переносима між будь-якими POSIX та C++11 системами. Проте вона має помітні накладні витрати: кожна операція взяття або відпускання блокування змушена захоплювати внутрішній м'ютекс.

У високопродуктивних системних бібліотеках (як-от `pthread_rwlock_t` у glibc або `std::shared_mutex` у сучасних компіляторах) використовують комбіновану двошарову архітектуру:
1. **Швидкий шлях у просторі користувача (User-space Fast Path):** перевірка стану та інкремент лічильника читачів здійснюється через єдину атомарну інструкцію CAS (`std::atomic::compare_exchange_weak`). Якщо конфлікту немає, замок захоплюється за 5–15 тактів процесора без системних викликів.
2. **Повільний шлях у ядрі (Kernel Slow Path):** лише тоді, коли CAS зазнає невдачі через активного або очікуючого письменника, потік звертається до системного виклику `futex` (Fast Userspace Mutex у Linux), передаючи ядру команду заснути в черзі очікування.

### Аналіз тонких крайових випадків та тестування

Під час розробки та аудиту коду замків читачів-письменника слід звертати увагу на чотири фундаментальні аспекти коректності:

1. **Розділення черг очікування читачів і письменників:**
   Якщо для обох груп використовувати одну умовну змінну, виклик `signal` або `notify_one()` під час виходу останнього читача може помилково розбудити іншого заблокованого читача замість очікуючого письменника. Розбуджений читач побачить, що `writers_waiting > 0`, і знову засне, а письменник так і залишиться спати в черзі, бо сповіщення було витрачене на читача. Використання двох окремих умовних змінних `cond_readers` та `cond_writers` повністю усуває цю гонку.
2. **Атомарність зміни стану лічильника очікування:**
   Письменник зобов'язаний збільшити `writers_waiting++` ДО того, як засне в очікуванні `cond_writers`. Це виставляє негайний бар'єр для всіх нових читачів. Зменшення `writers_waiting--` відбувається лише тоді, коли потік уже прокинувся і перевірив предикат `readers == 0`.
3. **Групове сповіщення проти одиничного сигналу:**
   Коли письменник відпускає замок за відсутності інших письменників, критично важливо викликати `broadcast` / `notify_all`. Виклик `signal` / `notify_one` розбудить лише одного читача, позбавляючи систему головної переваги RWLock — миттєвого паралельного запуску всієї групи зчитування.
4. **Стрес-тестування на дедлоки та перегони даних:**
   Для валідації власного замка створюють тестовий стенд із 16 потоками читання та 4 потоками запису, які безперервно інкрементують та перевіряють спільні контрольні суми. Запуск тесту під керуванням динамічного аналізатора перегонів даних ThreadSanitizer (TSan) із прапорцем `-fsanitize=thread` дозволяє гарантувати відсутність несинхронізованих доступів до пам'яті.
