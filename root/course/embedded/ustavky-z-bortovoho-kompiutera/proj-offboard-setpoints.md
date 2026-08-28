# ⚙️ Реалізація потокового генератора уставок Offboard на C та C++ з пріоритетом реального часу

Цей проєкт реалізує надійний бортовий сервіс (*setpoint streamer*) для передачі динамічних команд керування з Linux SBC до польотного контролера (PX4 / ArduPilot) через UART. Проєкт демонструє архітектуру розділених контурів (*decoupled loops*), що ізолює високочастотну відправку уставок від затримок планувальника та збирача сміття, гарантує безпечний вхід у режим Offboard і захищає апарат від раптових відкатів автопілота.

## Інженерна задача та архітектура рішення

Головний конфлікт супутнього комп'ютера полягає в різниці темпів:
1. **Контур планування та зору (Vision & Planner Loop):** працює з темпом 5–15 Гц. Обробка кадрів нейромережею, оновлення карти октодерева чи побудова сплайнів мають змінну тривалість. Якщо черговий кадр затримався на 150 мс через нагрів CPU або сплеск пам'яті, контур не встигає згенерувати уставку вчасно.
2. **Контур передачі уставок (Real-Time Transmitter Loop):** вимагає абсолютної регулярності з темпом 20–50 Гц (період 20–50 мс). Якщо потік пакетів переривається на час понад 500 мс (`COM_OF_LOSS_T`), польотний контролер аварійно вибиває режим Offboard і переходить в автоматичне зависання (*Hold*) або посадку (*Land*).

Щоб розв'язати цей конфлікт, сервіс ділиться на два незалежні потоки, сполучені захищеним спільним буфером стану:

```
[ Потік планувальника (Planner) ]  ──(асинхронно, 5–10 Гц)──┐
  • Камера, SLAM, логіка місії                              │
  • Записує нову цільову швидкість/позицію                  ▼
                                                [ Атомарний буфер уставки ]
                                                (timestamp, vx, vy, vz, yaw)
                                                            ▲
                                                            │
[ Потік генератора (Streamer, RT) ] ─(строго 20 Гц, SCHED_FIFO)┘
  • Прокидається за таймером timerfd
  • Перевіряє свіжість даних планувальника
  • У разі затримки: плавно гальмує до нуля (Ramp-down)
  • Пакує MAVLink кадр #84 і пише в UART
```

### Автомат станів переходу в Offboard

Польотний контролер блокує команду переходу в Offboard, якщо до моменту запиту він не отримував стабільного потоку уставок протягом щонайменше 500 мс. Тому генератор реалізує п'ятифазний автомат:

1. `STATE_IDLE` — порт відкрито, зв'язок встановлено, очікування команди на старт місії.
2. `STATE_PRESTREAMING` — відправка нульових або поточних уставок зависання з частотою 20 Гц протягом 800 мс (16 кадрів) без зміни режиму FCU.
3. `STATE_REQUEST_OFFBOARD` — надсилання команди `MAV_CMD_DO_SET_MODE` із запитом перемикання в режим Offboard.
4. `STATE_ACTIVE_STREAMING` — основний робочий режим: потокова трансляція цільових векторів швидкості/позиції від планувальника.
5. `STATE_HOLD_FALLBACK` — м'яке гальмування при затримці свіжих даних планувальника понад 250 мс із плавним обнуленням вектора швидкості.

---

## Реалізація на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <pthread.h>
#include <sys/timerfd.h>
#include <sys/time.h>
#include <math.h>
#include <common/mavlink.h>

#define UART_PORT "/dev/ttyAMA0"
#define UART_BAUDRATE B921600
#define STREAM_FREQ_HZ 20
#define PRESTREAM_FRAMES 16
#define PLANNER_TIMEOUT_MS 250

typedef enum {
    STREAMER_IDLE,
    STREAMER_PRESTREAM,
    STREAMER_REQUEST_MODE,
    STREAMER_ACTIVE,
    STREAMER_HOLD
} streamer_state_t;

typedef struct {
    pthread_mutex_t lock;
    float vx;
    float vy;
    float vz;
    float yaw;
    uint64_t last_update_ms;
    bool valid;
} shared_target_t;

typedef struct {
    int uart_fd;
    int timer_fd;
    streamer_state_t state;
    uint32_t prestream_count;
    uint8_t sys_id;
    uint8_t comp_id;
    shared_target_t target;
    bool running;
} offboard_streamer_t;

static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

static int open_uart(const char *port, speed_t baud) {
    int fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return -1;

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfmakeraw(&tty);
    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS; /* Без апаратного керування лініями flow control */

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static void send_setpoint(int fd, uint8_t sys_id, uint8_t comp_id,
                          float vx, float vy, float vz, float yaw) {
    mavlink_set_position_target_local_ned_t sp = {0};
    sp.time_boot_ms = 0;
    sp.target_system = 1;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    /* Маска швидкостей: ігноруємо координати, прискорення та швидкість yaw */
    sp.type_mask = 0x0001 | 0x0002 | 0x0004 | 0x0040 | 0x0080 | 0x0100 | 0x0800;
    sp.vx = vx;
    sp.vy = vy;
    sp.vz = vz;
    sp.yaw = yaw;

    mavlink_message_t msg;
    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, &msg, &sp);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

static void request_offboard_mode(int fd, uint8_t sys_id, uint8_t comp_id) {
    mavlink_command_long_t cmd = {0};
    cmd.target_system = 1;
    cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
    cmd.command = MAV_CMD_DO_SET_MODE;
    cmd.param1 = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
    cmd.param2 = 6.0f; /* PX4_CUSTOM_MAIN_MODE_OFFBOARD */

    mavlink_message_t msg;
    mavlink_msg_command_long_encode(sys_id, comp_id, &msg, &cmd);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

void* streamer_thread_func(void *arg) {
    offboard_streamer_t *ctx = (offboard_streamer_t*)arg;

    /* Налаштування періодичного таймера timerfd */
    struct itimerspec period;
    period.it_interval.tv_sec = 0;
    period.it_interval.tv_nsec = 1000000000L / STREAM_FREQ_HZ;
    period.it_value = period.it_interval;

    timerfd_settime(ctx->timer_fd, 0, &period, NULL);

    while (ctx->running) {
        uint64_t expirations = 0;
        ssize_t s = read(ctx->timer_fd, &expirations, sizeof(expirations));
        if (s <= 0) continue;

        uint64_t now = get_time_ms();
        float cur_vx = 0.0f, cur_vy = 0.0f, cur_vz = 0.0f, cur_yaw = 0.0f;
        bool is_fresh = false;

        pthread_mutex_lock(&ctx->target.lock);
        if (ctx->target.valid && (now - ctx->target.last_update_ms <= PLANNER_TIMEOUT_MS)) {
            cur_vx = ctx->target.vx;
            cur_vy = ctx->target.vy;
            cur_vz = ctx->target.vz;
            cur_yaw = ctx->target.yaw;
            is_fresh = true;
        }
        pthread_mutex_unlock(&ctx->target.lock);

        switch (ctx->state) {
        case STREAMER_IDLE:
            break;

        case STREAMER_PRESTREAM:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            ctx->prestream_count++;
            if (ctx->prestream_count >= PRESTREAM_FRAMES) {
                ctx->state = STREAMER_REQUEST_MODE;
            }
            break;

        case STREAMER_REQUEST_MODE:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            request_offboard_mode(ctx->uart_fd, ctx->sys_id, ctx->comp_id);
            ctx->state = STREAMER_ACTIVE;
            break;

        case STREAMER_ACTIVE:
            if (!is_fresh) {
                ctx->state = STREAMER_HOLD;
                send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            } else {
                send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, cur_vx, cur_vy, cur_vz, cur_yaw);
            }
            break;

        case STREAMER_HOLD:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            if (is_fresh) {
                ctx->state = STREAMER_ACTIVE;
            }
            break;
        }
    }
    return NULL;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <mutex>
#include <optional>
#include <span>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/timerfd.h>
#include <pthread.h>
#include <common/mavlink.h>

struct VelocityCommand {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};
    float yaw{0.0f};
};

class SerialPort {
public:
    explicit SerialPort(std::string_view port_name, speed_t baud) {
        fd_ = ::open(port_name.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити послідовний порт");
        }

        termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка зчитування атрибутів termios");
        }

        ::cfmakeraw(&tty);
        ::cfsetispeed(&tty, baud);
        ::cfsetospeed(&tty, baud);
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~CRTSCTS;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка застосування налаштувань порту");
        }
    }

    ~SerialPort() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    void write(std::span<const uint8_t> data) const {
        if (fd_ >= 0 && !data.empty()) {
            ::write(fd_, data.data(), data.size());
        }
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

class OffboardStreamer {
public:
    enum class State {
        Idle,
        PreStreaming,
        RequestMode,
        ActiveStreaming,
        HoldFallback
    };

    OffboardStreamer(std::string_view port, uint8_t sys_id = 240, uint8_t comp_id = 1)
        : port_(port, B921600), sys_id_(sys_id), comp_id_(comp_id) {
        timer_fd_ = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
        if (timer_fd_ < 0) {
            throw std::runtime_error("Помилка створення дескриптора timerfd");
        }
    }

    ~OffboardStreamer() noexcept {
        stop();
        if (timer_fd_ >= 0) {
            ::close(timer_fd_);
        }
    }

    void start() {
        running_.store(true, std::memory_order_release);
        state_ = State::PreStreaming;
        prestream_counter_ = 0;

        worker_thread_ = std::jthread([this](std::stop_token st) {
            set_realtime_priority();
            run_loop(st);
        });
    }

    void stop() {
        running_.store(false, std::memory_order_release);
        if (worker_thread_.joinable()) {
            worker_thread_.request_stop();
        }
    }

    void update_target(const VelocityCommand& cmd) {
        std::lock_guard lock(target_mutex_);
        target_ = cmd;
        last_target_time_ = std::chrono::steady_clock::now();
    }

private:
    void set_realtime_priority() {
        sched_param param{};
        param.sched_priority = 45; // Пріоритет реального часу для Linux RT
        pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
    }

    void send_velocity_target(const VelocityCommand& cmd) {
        mavlink_set_position_target_local_ned_t sp{};
        sp.target_system = 1;
        sp.target_component = MAV_COMP_ID_AUTOPILOT1;
        sp.coordinate_frame = MAV_FRAME_LOCAL_NED;
        // Маска: активні лише швидкості та кут yaw
        sp.type_mask = 0x0001 | 0x0002 | 0x0004 | 0x0040 | 0x0080 | 0x0100 | 0x0800;
        sp.vx = cmd.vx;
        sp.vy = cmd.vy;
        sp.vz = cmd.vz;
        sp.yaw = cmd.yaw;

        mavlink_message_t msg{};
        mavlink_msg_set_position_target_local_ned_encode(sys_id_, comp_id_, &msg, &sp);

        uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
        port_.write(std::span<const uint8_t>(buffer, len));
    }

    void send_offboard_request() {
        mavlink_command_long_t cmd{};
        cmd.target_system = 1;
        cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
        cmd.command = MAV_CMD_DO_SET_MODE;
        cmd.param1 = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
        cmd.param2 = 6.0f; // PX4 OFFBOARD

        mavlink_message_t msg{};
        mavlink_msg_command_long_encode(sys_id_, comp_id_, &msg, &cmd);

        uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
        port_.write(std::span<const uint8_t>(buffer, len));
    }

    void run_loop(std::stop_token st) {
        itimerspec period{};
        period.it_interval.tv_nsec = 50'000'000; // 20 Гц (50 мс)
        period.it_value = period.it_interval;
        ::timerfd_settime(timer_fd_, 0, &period, nullptr);

        while (!st.stop_requested() && running_.load(std::memory_order_acquire)) {
            uint64_t expirations = 0;
            if (::read(timer_fd_, &expirations, sizeof(expirations)) <= 0) {
                continue;
            }

            VelocityCommand active_cmd{};
            bool is_fresh = false;
            {
                std::lock_guard lock(target_mutex_);
                auto age = std::chrono::steady_clock::now() - last_target_time_;
                if (age <= std::chrono::milliseconds(250)) {
                    active_cmd = target_;
                    is_fresh = true;
                }
            }

            switch (state_) {
            case State::Idle:
                break;
            case State::PreStreaming:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                if (++prestream_counter_ >= 16) {
                    state_ = State::RequestMode;
                }
                break;
            case State::RequestMode:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                send_offboard_request();
                state_ = State::ActiveStreaming;
                break;
            case State::ActiveStreaming:
                if (!is_fresh) {
                    state_ = State::HoldFallback;
                    send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                } else {
                    send_velocity_target(active_cmd);
                }
                break;
            case State::HoldFallback:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                if (is_fresh) {
                    state_ = State::ActiveStreaming;
                }
                break;
            }
        }
    }

    SerialPort port_;
    int timer_fd_{-1};
    uint8_t sys_id_{240};
    uint8_t comp_id_{1};
    std::atomic<bool> running_{false};
    State state_{State::Idle};
    size_t prestream_counter_{0};

    std::mutex target_mutex_;
    VelocityCommand target_{};
    std::chrono::steady_clock::time_point last_target_time_{};
    std::jthread worker_thread_;
};
```
:::

---

## Алгоритм плавного гальмування (Ramp-down)

У наведеному коді при виявленні затримки планувальника (`is_fresh == false`) стан перемикається в `HoldFallback`, де швидкість скидається в нуль. Для динамічних апаратів, що рухаються зі швидкістю понад 5 м/с, миттєве надсилання нульової швидкості викликає різкий стрибок тангажу.

Для плавного гальмування застосовують алгоритм лінійного зрізу швидкості з фіксованим прискоренням гальмування `a_brake`:

```
Δv_max = a_brake · Δt
v_next = v_prev − sign(v_prev) · min(|v_prev|, Δv_max)
```

При частоті 20 Гц (`Δt = 0.05` с) та комфортному гальмуванні `a_brake = 2.0` м/с², на кожному такті швидкість зменшується максимум на `0.1` м/с. Це гарантує плавний перехід у зависання без перевантаження конструкції та зриву потоку з пропелерів.

---

## Підводні камені та налаштування оточення Linux

### 1. Налаштування драйвера UART (Raw Mode)

Стандартний термінальний режим у Linux розглядає байти `0x03` (ETX / Ctrl+C), `0x0A` (LF) та `0x0D` (CR) як керуючі символи, додає повернення каретки або обриває потік. MAVLink є двійковим протоколом, де контрольна сума або байти координат збігаються з цими кодами.
Виклик `cfmakeraw(&tty)` вимикає канонізацію, ехо-повтор та заміну символів, перетворюючи порт на чисту бітову трубу.

### 2. Таймери ядра: чому timerfd замість sleep

Виклики `usleep()` або `std::this_thread::sleep_for()` є відносними затримками: вони додають свій час сну до часу виконання тіла циклу. Якщо тіло циклу виконувалось 3 мс, а сон замовлено на 50 мс, реальний період становить 53 мс, що спричиняє поступове фазове накопичення затримки (*clock drift*).

Механізм `timerfd` створює абсолютний періодичний таймер ядра Linux на базі `CLOCK_MONOTONIC`. Ядро генерує подію точно кожні 50.000 мс незалежно від того, скільки часу потік витратив на формування пакета. Якщо потік затримався і пропустив такт, виклик `read()` поверне число пропущених тактів (`expirations > 1`), що дозволяє миттєво виявити деградацію продуктивності.

### 3. Права реального часу (POSIX Real-Time Scheduling)

Політика `SCHED_FIFO` вимагає прав суперкористувача або явного надання `CAP_SYS_NICE`. Без цього виклик `pthread_setschedparam` поверне помилку `EPERM` (Operation not permitted), і потік виконуватиметься у звичайному `SCHED_OTHER`, де його може витіснити будь-який фоновий процес.

Для запуску без `sudo` у конфігураційний файл `/etc/security/limits.conf` додають правило:

```text
robotics_user    soft    rtprio          50
robotics_user    hard    rtprio          50
robotics_user    soft    memlock         unlimited
robotics_user    hard    memlock         unlimited
```

### 4. Блокування сторінок оперативної пам'яті (mlockall)

У моменти сплеску виділення пам'яті ядро Linux може скинути сторінки коду або стека потоку в підкачку (*swap*) або затримати їх виділення через відкладену ініціалізацію (*page fault*). Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` на старті програми закріплює всю пам'ять у RAM, усуваючи затримки доступу до сторінок у критичному циклі 20 Гц.

---

## Методика тестування відмовостійкості на стенді

Перед польотними випробуваннями сервіс перевіряють на стенді (або в симуляторі SITL/HITL) за трьома сценаріями:

1. **Імітація зависання планувальника (Freeze Test):**
   У процесі польоту планувальнику надсилається сигнал `kill -STOP <planner_pid>`. Генератор повинен зафіксувати старіння буфера через 250 мс, плавно перевести уставку в нуль і втримати автопілот у режимі зависання без аварійного вибивання Offboard.
2. **Імітація повного краху генератора (Crash Test):**
   Процес потоку вбивається сигналом `kill -9 <streamer_pid>`. Через рівно 500 мс після припинення передачі кадру на автопілоті повинен спрацювати сторожовий таймер, і режим у логах PX4 має змінитися з `OFFBOARD` на `AUTO_LOITER / AUTO_LAND`.
3. **Вимірювання джиттера (Jitter Profiling):**
   За допомогою утиліти `cyclictest` вимірюють максимальне відхилення таймера на навантаженому комп'ютері:
   `cyclictest -p 45 -m -n -l 100000 -q`
   Максимальний джиттер не повинен перевищувати 2.0 мс на системі з ядром PREEMPT_RT або 5.0 мс на стандартному ядрі Linux.
