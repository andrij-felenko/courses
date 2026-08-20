# ⚙️ Мінімальний рантайм акторів: черга повідомлень і диспетчер потоків

Для глибокого розуміння моделі акторів недостатньо розглядати її як абстрактну концепцію. Найкращий спосіб збагнути механіку поштових скриньок, квантування обчислень та ізоляції стану — побудувати власний компактний, але повністю функціональний рантайм акторів системного рівня.

Нижче реалізовано повноцінний мінімальний рушій акторів на мовах C та C++. Архітектура базується на трьох фундаментальних блоках:
1. **Структура повідомлення та поштової скриньки:** Впорядкована потокобезпечна черга повідомлень (FIFO), що належить конкретному актору.
2. **Контекст актора:** Ізольований локальний стан, черга повідомлень та покажчик на поточну функцію поведінки (`behavior`).
3. **Пул потоків-планувальників:** Набір системних робочих потоків (воркерів), які витягують активних акторів із глобальної черги готовності (`ready queue`), обробляють обмежену порцію повідомлень (квант редукцій) та повертають актора назад у чергу за наявності залишкових повідомлень.

### Реалізація рантайму: C та сучасний C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_ACTORS 64
#define MSG_BATCH_QUOTA 4

typedef struct Actor Actor;

typedef enum {
    MSG_PING,
    MSG_PONG,
    MSG_DATA,
    MSG_STOP
} MessageType;

typedef struct Message {
    MessageType type;
    int payload;
    uint32_t sender_id;
    struct Message* next;
} Message;

typedef void (*Behavior)(Actor* self, Message* msg);

typedef struct {
    Message* head;
    Message* tail;
    pthread_mutex_t lock;
} Mailbox;

struct Actor {
    uint32_t id;
    int state_value;
    Behavior behavior;
    Mailbox mailbox;
    bool is_active;
    bool is_scheduled;
    struct Actor* next_ready;
};

typedef struct {
    Actor* head;
    Actor* tail;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    bool stop_flag;
} ReadyQueue;

typedef struct {
    Actor* actors[MAX_ACTORS];
    uint32_t actor_count;
    ReadyQueue ready_queue;
    pthread_t workers[4];
    size_t num_workers;
} ActorSystem;

static ActorSystem g_system;

void mailbox_init(Mailbox* mb) {
    mb->head = NULL;
    mb->tail = NULL;
    pthread_mutex_init(&mb->lock, NULL);
}

void mailbox_push(Mailbox* mb, Message* msg) {
    msg->next = NULL;
    pthread_mutex_lock(&mb->lock);
    if (mb->tail) {
        mb->tail->next = msg;
        mb->tail = msg;
    } else {
        mb->head = mb->tail = msg;
    }
    pthread_mutex_unlock(&mb->lock);
}

Message* mailbox_pop(Mailbox* mb) {
    pthread_mutex_lock(&mb->lock);
    Message* msg = mb->head;
    if (msg) {
        mb->head = msg->next;
        if (!mb->head) mb->tail = NULL;
    }
    pthread_mutex_unlock(&mb->lock);
    return msg;
}

void ready_queue_init(ReadyQueue* rq) {
    rq->head = NULL;
    rq->tail = NULL;
    rq->stop_flag = false;
    pthread_mutex_init(&rq->lock, NULL);
    pthread_cond_init(&rq->cond, NULL);
}

void ready_queue_push(ReadyQueue* rq, Actor* actor) {
    pthread_mutex_lock(&rq->lock);
    actor->next_ready = NULL;
    if (rq->tail) {
        rq->tail->next_ready = actor;
        rq->tail = actor;
    } else {
        rq->head = rq->tail = actor;
    }
    pthread_cond_signal(&rq->cond);
    pthread_mutex_unlock(&rq->lock);
}

Actor* ready_queue_pop(ReadyQueue* rq) {
    pthread_mutex_lock(&rq->lock);
    while (!rq->head && !rq->stop_flag) {
        pthread_cond_wait(&rq->cond, &rq->lock);
    }
    if (rq->stop_flag && !rq->head) {
        pthread_mutex_unlock(&rq->lock);
        return NULL;
    }
    Actor* actor = rq->head;
    rq->head = actor->next_ready;
    if (!rq->head) rq->tail = NULL;
    pthread_mutex_unlock(&rq->lock);
    return actor;
}

void actor_send(uint32_t target_id, MessageType type, int payload, uint32_t sender_id) {
    if (target_id >= g_system.actor_count) return;
    Actor* target = g_system.actors[target_id];
    if (!target || !target->is_active) return;

    Message* msg = (Message*)malloc(sizeof(Message));
    msg->type = type;
    msg->payload = payload;
    msg->sender_id = sender_id;

    mailbox_push(&target->mailbox, msg);

    pthread_mutex_lock(&target->mailbox.lock);
    bool should_schedule = !target->is_scheduled;
    target->is_scheduled = true;
    pthread_mutex_unlock(&target->mailbox.lock);

    if (should_schedule) {
        ready_queue_push(&g_system.ready_queue, target);
    }
}

void ping_behavior(Actor* self, Message* msg);
void pong_behavior(Actor* self, Message* msg);

void ping_behavior(Actor* self, Message* msg) {
    if (msg->type == MSG_PONG) {
        printf("[Ping Actor %u] Отримано PONG (раунд %d)\n", self->id, msg->payload);
        if (msg->payload >= 5) {
            printf("[Ping Actor %u] Ліміт раундів досягнуто. Зупинка.\n", self->id);
            actor_send(msg->sender_id, MSG_STOP, 0, self->id);
            self->is_active = false;
        } else {
            usleep(100000);
            actor_send(msg->sender_id, MSG_PING, msg->payload + 1, self->id);
        }
    }
}

void pong_behavior(Actor* self, Message* msg) {
    if (msg->type == MSG_PING) {
        printf("[Pong Actor %u] Отримано PING (%d), надсилаю PONG\n", self->id, msg->payload);
        usleep(100000);
        actor_send(msg->sender_id, MSG_PONG, msg->payload, self->id);
    } else if (msg->type == MSG_STOP) {
        printf("[Pong Actor %u] Отримано команду STOP. Завершення.\n", self->id);
        self->is_active = false;
    }
}

void* worker_thread_func(void* arg) {
    (void)arg;
    while (true) {
        Actor* actor = ready_queue_pop(&g_system.ready_queue);
        if (!actor) break;

        size_t processed = 0;
        while (processed < MSG_BATCH_QUOTA) {
            Message* msg = mailbox_pop(&actor->mailbox);
            if (!msg) break;

            if (actor->is_active && actor->behavior) {
                actor->behavior(actor, msg);
            }
            free(msg);
            processed++;
        }

        pthread_mutex_lock(&actor->mailbox.lock);
        if (actor->mailbox.head && actor->is_active) {
            ready_queue_push(&g_system.ready_queue, actor);
        } else {
            actor->is_scheduled = false;
        }
        pthread_mutex_unlock(&actor->mailbox.lock);
    }
    return NULL;
}

uint32_t actor_spawn(Behavior init_behavior, int initial_state) {
    uint32_t id = g_system.actor_count++;
    Actor* actor = (Actor*)malloc(sizeof(Actor));
    actor->id = id;
    actor->state_value = initial_state;
    actor->behavior = init_behavior;
    actor->is_active = true;
    actor->is_scheduled = false;
    actor->next_ready = NULL;
    mailbox_init(&actor->mailbox);

    g_system.actors[id] = actor;
    return id;
}

void system_init(size_t workers) {
    g_system.actor_count = 0;
    g_system.num_workers = workers;
    ready_queue_init(&g_system.ready_queue);
    for (size_t i = 0; i < workers; ++i) {
        pthread_create(&g_system.workers[i], NULL, worker_thread_func, NULL);
    }
}

void system_shutdown(void) {
    pthread_mutex_lock(&g_system.ready_queue.lock);
    g_system.ready_queue.stop_flag = true;
    pthread_cond_broadcast(&g_system.ready_queue.cond);
    pthread_mutex_unlock(&g_system.ready_queue.lock);

    for (size_t i = 0; i < g_system.num_workers; ++i) {
        pthread_join(g_system.workers[i], NULL);
    }
}

int main(void) {
    printf("Запуск системи акторів...\n");
    system_init(2);

    uint32_t ping_pid = actor_spawn(ping_behavior, 0);
    uint32_t pong_pid = actor_spawn(pong_behavior, 0);

    // Ініціюємо перший PING
    actor_send(pong_pid, MSG_PING, 1, ping_pid);

    sleep(2);
    system_shutdown();
    printf("Систему акторів зупинено коректно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <memory>
#include <variant>
#include <functional>
#include <chrono>

enum class MessageType { Ping, Pong, Stop };

struct Message {
    MessageType type;
    int payload;
    uint32_t sender_id;
};

class ActorSystem;

class Actor {
public:
    using Behavior = std::function<void(Actor& self, const Message& msg)>;

    Actor(uint32_t id, Behavior init_behavior, ActorSystem& system)
        : id_(id), behavior_(std::move(init_behavior)), system_(system) {}

    uint32_t id() const noexcept { return id_; }
    bool is_active() const noexcept { return is_active_.load(std::memory_order_relaxed); }
    void stop() noexcept { is_active_.store(false, std::memory_order_relaxed); }

    void become(Behavior new_behavior) {
        behavior_ = std::move(new_behavior);
    }

    void enqueue(Message msg);
    void process_batch(size_t max_messages);
    ActorSystem& system() noexcept { return system_; }

private:
    uint32_t id_;
    Behavior behavior_;
    ActorSystem& system_;
    std::queue<Message> mailbox_;
    std::mutex mailbox_mutex_;
    std::atomic<bool> is_active_{true};
    std::atomic<bool> is_scheduled_{false};
};

class ActorSystem {
public:
    explicit ActorSystem(size_t thread_count = std::thread::hardware_concurrency())
        : stop_requested_(false) {
        workers_.reserve(thread_count);
        for (size_t i = 0; i < thread_count; ++i) {
            workers_.emplace_back([this] { worker_loop(); });
        }
    }

    ~ActorSystem() {
        shutdown();
    }

    uint32_t spawn(Actor::Behavior behavior) {
        std::lock_guard<std::mutex> lock(actors_mutex_);
        auto id = static_cast<uint32_t>(actors_.size());
        actors_.push_back(std::make_unique<Actor>(id, std::move(behavior), *this));
        return id;
    }

    void send(uint32_t target_id, Message msg) {
        std::lock_guard<std::mutex> lock(actors_mutex_);
        if (target_id < actors_.size()) {
            actors_[target_id]->enqueue(std::move(msg));
        }
    }

    void schedule(Actor* actor) {
        {
            std::lock_guard<std::mutex> lock(ready_mutex_);
            ready_queue_.push(actor);
        }
        ready_cv_.notify_one();
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(ready_mutex_);
            stop_requested_ = true;
        }
        ready_cv_.notify_all();
        for (auto& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

private:
    void worker_loop() {
        constexpr size_t quota = 4;
        while (true) {
            Actor* actor = nullptr;
            {
                std::unique_lock<std::mutex> lock(ready_mutex_);
                ready_cv_.wait(lock, [this] {
                    return stop_requested_ || !ready_queue_.empty();
                });

                if (stop_requested_ && ready_queue_.empty()) {
                    return;
                }

                actor = ready_queue_.front();
                ready_queue_.pop();
            }

            if (actor) {
                actor->process_batch(quota);
            }
        }
    }

    std::vector<std::unique_ptr<Actor>> actors_;
    std::mutex actors_mutex_;
    std::queue<Actor*> ready_queue_;
    std::mutex ready_mutex_;
    std::condition_variable ready_cv_;
    std::vector<std::thread> workers_;
    bool stop_requested_;
};

void Actor::enqueue(Message msg) {
    if (!is_active()) return;

    bool was_empty = false;
    {
        std::lock_guard<std::mutex> lock(mailbox_mutex_);
        was_empty = mailbox_.empty();
        mailbox_.push(std::move(msg));
    }

    bool expected = false;
    if (is_scheduled_.compare_exchange_strong(expected, true)) {
        system_.schedule(this);
    }
}

void Actor::process_batch(size_t max_messages) {
    size_t processed = 0;
    while (processed < max_messages) {
        Message msg;
        {
            std::lock_guard<std::mutex> lock(mailbox_mutex_);
            if (mailbox_.empty()) break;
            msg = std::move(mailbox_.front());
            mailbox_.pop();
        }

        if (is_active_ && behavior_) {
            behavior_(*this, msg);
        }
        ++processed;
    }

    std::lock_guard<std::mutex> lock(mailbox_mutex_);
    if (!mailbox_.empty() && is_active_) {
        system_.schedule(this);
    } else {
        is_scheduled_.store(false, std::memory_order_release);
    }
}

int main() {
    std::cout << "Ініціалізація C++ рантайму акторів...\n";
    ActorSystem system(2);

    uint32_t ping_pid = 0;
    uint32_t pong_pid = 0;

    ping_pid = system.spawn([&system](Actor& self, const Message& msg) {
        if (msg.type == MessageType::Pong) {
            std::cout << "[C++ Ping " << self.id() << "] Отримано PONG (раунд " << msg.payload << ")\n";
            if (msg.payload >= 5) {
                std::cout << "[C++ Ping] Завершення обміну.\n";
                system.send(msg.sender_id, Message{MessageType::Stop, 0, self.id()});
                self.stop();
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                system.send(msg.sender_id, Message{MessageType::Ping, msg.payload + 1, self.id()});
            }
        }
    });

    pong_pid = system.spawn([&system](Actor& self, const Message& msg) {
        if (msg.type == MessageType::Ping) {
            std::cout << "[C++ Pong " << self.id() << "] Отримано PING (" << msg.payload << "), відповідаю PONG\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            system.send(msg.sender_id, Message{MessageType::Pong, msg.payload, self.id()});
        } else if (msg.type == MessageType::Stop) {
            std::cout << "[C++ Pong] Отримано STOP. Зупинка.\n";
            self.stop();
        }
    });

    // Запуск обміну
    system.send(pong_pid, Message{MessageType::Ping, 1, ping_pid});

    std::this_thread::sleep_for(std::chrono::seconds(2));
    system.shutdown();
    std::cout << "C++ систему акторів зупинено успішно.\n";
    return 0;
}
```
:::

### Ключові інженерні акценти реалізації

1. **Ізоляція пам'яті та усунення стану гонки:** Потоки воркерів не мають прямого доступу до локальних змінних актора поза контекстом обробки повідомлення. Локальний стан актора змінюється виключно в момент, коли потік виконує функцію `behavior` для вилученого зі скриньки елемента. Оскільки кожен актор опрацьовує повідомлення строго послідовно, розробник пише код у звичному однопотоковому стилі, не викликаючи м'ютекси для внутрішніх полів.
2. **Квота редукцій (`MSG_BATCH_QUOTA`):** Обробка обмеженої кількості повідомлень за один сеанс виконання унеможливлює ситуацію, коли один «гарячий» актор монополізує робочий потік операційної системи й спричиняє голодування (*starvation*) решти сотень тисяч акторів. Після вичерпання ліміту актор кооперативно поступається ресурсом CPU наступним акторам у черзі готовності.
3. **Атомарний протокол диспетчеризації (`is_scheduled`):** Актор додається до черги `ready_queue` лише тоді, коли він ще не запланований і в його скриньці з'явилися нові повідомлення. Використання атомарного обміну (`compare_exchange_strong`) гарантує, що жоден актор не потрапить до двох робочих потоків воркерів одночасно, забезпечуючи непорушний однопотоковий інваріант обробки локального стану без глобального блокування всього рантайму.

### Покрокове простеження життєвого циклу повідомлення

Розгляньмо динаміку взаємодії при виклику `actor_send(target_id, MSG_PING, payload, sender_id)`:

1. **Створення конверта:** У пам'яті виділяється вузол повідомлення, що містить тип події, корисне навантаження та числовий ідентифікатор відправника. У високонавантажених системах замість динамічного виділення через системний `malloc` використовують пули фіксованих блоків пам'яті (*arena allocators*), щоб уникнути фрагментації купи.
2. **Захоплення черги скриньки:** Відправник блокує локальний м'ютекс скриньки отримувача (`mailbox.lock`) на мінімальний час, необхідний для оновлення одного покажчика `tail->next = msg`.
3. **Перевірка статусу виконання:** Відправник перевіряє прапорець `is_scheduled`. Якщо актор перебував у стані спокою (`is_scheduled == false`), відправник переводить його в активний стан `is_scheduled = true` та поміщає адресу актора в чергу готових до виконання сутностей `ready_queue`. Якщо ж актор уже обробляється іншим робочим потоком або вже стоїть у черзі, відправник просто додає повідомлення у скриньку й негайно завершує виклик, не турбуючи планувальник.
4. **Захоплення воркером:** Вільний робочий потік пулу, що очікував на умовній змінній `ready_cv`, прокидається, забирає актора з черги `ready_queue` і починає послідовно вилучати повідомлення з його скриньки.
5. **Виконання поведінки:** Для кожного вилученого повідомлення викликається поточна функція поведінки `behavior(self, msg)`. Всередині обробника актор може змінити свій локальний стан, породити нових акторів або надіслати нові повідомлення іншим сутностям.
6. **Повернення або засинання:** Коли оброблено `MSG_BATCH_QUOTA` повідомлень, потік перевіряє стан скриньки. Якщо у скриньці лишилися необроблені елементи, актор повторно додається в кінець `ready_queue`. Якщо ж скринька спорожніла, потік скидає прапорець `is_scheduled = false` і переходить до очікування наступного готового актора.

### Аналіз крайових випадків та інженерних пасток

1. **Вибух обсягу поштової скриньки (Mailbox Overflow):** Якщо швидкість надходження повідомлень перевищує пропускну здатність одного ядра, необмежена зв'язним списком скринька нескінченно зростає в пам'яті, що врешті-решт призводить до аварійного завершення процесу через OOM (*Out Of Memory*). Промислові рантайми вирішують це за допомогою кільцевих буферів фіксованого розміру (*bounded ring buffers*) або механізмів зворотного тиску (*backpressure*), які блокують відправника або відкидають застарілі повідомлення.
2. **Конкуренція за глобальну чергу готовності:** У наведеному прикладі всі воркери читають єдину чергу `ready_queue`, захищену спільним м'ютексом. При масштабуванні на 32 чи 64 процесорні ядра спільний замок стає «вузьким місцем» через конкуренцію за кеш-лінії шини пам'яті. У промислових рушіях (таких як BEAM в Erlang чи рантайм Akka) кожен воркер має власну локальну чергу готових задач, а розподіл навантаження відбувається через алгоритм розкрадання роботи (*work-stealing*) без централізованих блокувань.
3. **Коректна зупинка системи (Graceful Drain):** При завершенні роботи застосунку не можна просто припинити виконання потоків, оскільки у скриньках можуть залишатися критичні транзакційні повідомлення. Рантайм повинен виставити прапорець зупинки, сповістити всі потоки через `ready_cv.notify_all()`, дати акторам змогу спорожнити черги повідомлень або виконати фінальні деструктори, і лише після цього звільнити системні ресурси.

