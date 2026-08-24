# ⚙️ Розслідування краху __cxa_pure_virtual у реальному проекті

У програмах мовами C та C++ аварійне завершення з діагностичним повідомленням `pure virtual method called` або `pure virtual function call` є однією з найпідступніших помилок часу виконання. Компілятор гарантує, що створити екземпляр абстрактного типу неможливо. Проте під час роботи програми процес раптово гине, не залишаючи звичайного стеку винятків C++, оскільки системний обробник перериває роботу через `std::terminate()` або `abort()`.

Нижче наведено детальний аналіз виникнення цього краху в реальній багатопотоковій черзі мережевих повідомлень, покрокове дослідження стану регістрів і пам'яті у зневаджувачі GDB, аналіз впливу оптимізацій компілятора, розбір крайових випадків у множинному спадкуванні, порівняння поведінки C++ із середовищами Java і C#, а також побудова надійної архітектури безпечної ініціалізації на основі [RAII](topic:programming/raii) та патерна фабрики.

## Практичний сценарій: мережевий приймач пакетів

Розглянемо систему обробки мережевого трафіку. Базовий абстрактний клас `PacketReceiver` інкапсулює дескриптор сокета, кільцевий буфер і загальну логіку з'єднання. Оскільки структура самого протоколу залежить від прикладного рівня, розбір корисного навантаження делеговано чистому віртуальному методу `process_payload()`.

Типова інженерна помилка полягає у спробі виконати початкове налаштування підсистеми або зареєструвати об'єкт у диспетчері подій безпосередньо всередині конструктора базового класу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обробник помилки чистого виклику */
void pure_virtual_trap(void) {
    fprintf(stderr, "FATAL: pure virtual method called!\n");
    abort();
}

typedef struct PacketReceiver PacketReceiver;

typedef struct ReceiverVTable {
    void (*process_payload)(PacketReceiver* self, const uint8_t* data, size_t len);
    void (*cleanup)(PacketReceiver* self);
} ReceiverVTable;

struct PacketReceiver {
    const ReceiverVTable* vptr;
    int socket_fd;
};

/* Спільна допоміжна функція налаштування предка */
void receiver_setup_subsystem(PacketReceiver* self) {
    const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
    /* Непрямий виклик через vptr до завершення конструювання нащадка! */
    self->vptr->process_payload(self, handshake, sizeof(handshake));
}

void receiver_base_init(PacketReceiver* self, int fd) {
    static const ReceiverVTable base_vtable = {
        .process_payload = pure_virtual_trap,
        .cleanup = NULL
    };
    /* Встановлюємо таблицю базового типу */
    self->vptr = &base_vtable;
    self->socket_fd = fd;

    /* Викликаємо логіку налаштування */
    receiver_setup_subsystem(self);
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <cstdint>

class PacketReceiver {
public:
    explicit PacketReceiver(int socket_fd) : m_socket_fd(socket_fd) {
        // Конструктор базового класу кличе допоміжний метод конфігурації
        setup_subsystem();
    }

    virtual ~PacketReceiver() = default;

    // Контракт обробки корисного навантаження
    virtual void process_payload(const uint8_t* data, std::size_t len) = 0;

private:
    void setup_subsystem() {
        const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
        // НЕБЕЗПЕКА: непрямий віртуальний виклик під час виконання конструктора предка!
        process_payload(handshake, sizeof(handshake));
    }

    int m_socket_fd;
};

class TelemetryReceiver : public PacketReceiver {
public:
    explicit TelemetryReceiver(int socket_fd) : PacketReceiver(socket_fd) {}

    void process_payload(const uint8_t* data, std::size_t len) override {
        std::cout << "Успішна обробка телеметрії, розмір: " << len << " байтів\n";
    }
};
```
:::

Під час запуску цього коду програма завершується аварійно:

```
$ g++ -O0 -g receiver.cpp -o receiver && ./receiver
pure virtual method called
terminate called without an active exception
Aborted (core dumped)
```

## Дослідження аварії під зневаджувачем GDB

Відкриємо згенерований дамп пам'яті (core dump) у зневаджувачі GDB, щоб дослідити точний стан об'єкта, стеку викликів і пам'яті в момент аварії.

```
$ gdb ./receiver core
(gdb) bt
#0  __pthread_kill_implementation () at ./nptl/pthread_kill.c:44
#1  0x00007ffff7c427f5 in raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#2  0x00007ffff7c28859 in abort () at ./stdlib/abort.c:79
#3  0x00007ffff7e87b9d in __cxa_pure_virtual () at ../../../../libstdc++-v3/libsupc++/pure.cc:50
#4  0x0000555555555234 in PacketReceiver::setup_subsystem (this=0x7fffffffe340) at receiver.cpp:18
#5  0x00005555555551dc in PacketReceiver::PacketReceiver (this=0x7fffffffe340, socket_fd=3) at receiver.cpp:8
#6  0x000055555555517b in TelemetryReceiver::TelemetryReceiver (this=0x7fffffffe340, socket_fd=3) at receiver.cpp:27
#7  0x0000555555555124 in main () at receiver.cpp:35
```

Перейдемо до кадру виклику `#4` та перевіримо значення внутрішнього покажчика на таблицю віртуальних методів `vptr`:

```
(gdb) frame 4
(gdb) print this
$1 = (PacketReceiver * const) 0x7fffffffe340

(gdb) print *(void**)this
$2 = (void *) 0x555555557d90 <vtable for PacketReceiver+16>

(gdb) x/4a 0x555555557d90
0x555555557d90 <vtable for PacketReceiver+16>: 0x7ffff7e87b90 <__cxa_pure_virtual>
0x555555557d98 <vtable for PacketReceiver+24>: 0x555555555310 <PacketReceiver::~PacketReceiver()>
```

Розглянемо асемблерний код виклику методу всередині `setup_subsystem`:

```
(gdb) disassemble PacketReceiver::setup_subsystem
   0x000055555555521c <+0>:  push   %rbp
   0x000055555555521d <+1>:  mov    %rsp,%rbp
   0x0000555555555220 <+4>:  sub    $0x20,%rsp
   0x0000555555555224 <+8>:  mov    %rdi,-0x18(%rbp)     ; Збереження this
   0x0000555555555228 <+12>: mov    -0x18(%rbp),%rax     ; rax = this
   0x000055555555522c <+16>: mov    (%rax),%rax          ; rax = *this (завантаження vptr)
   0x000055555555522f <+19>: mov    (%rax),%rax          ; rax = vtable[0] (адреса слота)
   0x0000555555555232 <+22>: call   *%rax                ; Непрямий перехід у __cxa_pure_virtual!
```

Цей лістинг наочно демонструє механіку аварії:
1. Під час виконання конструктора базового класу `PacketReceiver` компілятор ініціалізує перші 8 байтів об'єкта адресою `vtable for PacketReceiver`.
2. У першому слоті цієї таблиці міститься адреса функції `__cxa_pure_virtual`.
3. Інструкція `call *%rax` виконує непрямий перехід за цією адресою, миттєво перериваючи роботу процесу.

## Вплив оптимізацій компілятора: девіртуалізація та інструкція ud2

Цікавий ефект спостерігається при збиранні коду з високими рівнями оптимізації (`-O2` або `-O3`). Якщо компілятор під час міжпроцедурного аналізу (Interprocedural Analysis, IPA) бачить, що невіртуальний метод `setup_subsystem()` викликається виключно з конструктора `PacketReceiver`, він виконує інлайнінг обох функцій.

Знаючи, що на цьому етапі динамічний тип об'єкта точно є `PacketReceiver`, оптимізатор замінює непрямий виклик через `vtable` на прямий перехід до цільової функції слота. Оскільки цільовою функцією є чистий віртуальний метод, компілятор Clang або GCC генерує прямий виклик `call __cxa_pure_virtual` або взагалі підставляє асемблерну інструкцію недопустимої операції `ud2` (Undefined Instruction Trap), що призводить до негайного апаратного переривання (Illegal Instruction).

Для автоматичного виявлення таких помилок на етапі тестування рекомендується збирати код із санітайзером типів:
```
g++ -O1 -g -fsanitize=undefined,vptr receiver.cpp -o receiver
```
Санітайзер `UBSan` перехоплює невалідний стан покажчика `vptr` ще до здійснення непрямого стрибка й виводить вичерпний звіт із зазначенням файлу та номера рядка виклику.

## Крах у багатопотоковому середовищі через передчасну публікацію покажчика

Ще складніший випадок виникає тоді, коли конструктор базового класу не кличе віртуальний метод сам, але запускає фоновий потік виконання або реєструє покажчик `this` у глобальному диспетчері подій:

```cpp
class Worker {
public:
    Worker() {
        // Фоновий потік стартує ДО завершення конструктора похідного класу!
        m_thread = std::thread([this]() {
            this->do_work(); // ГОНКА: vptr може ще вказувати на vtable for Worker!
        });
    }

    virtual ~Worker() {
        if (m_thread.joinable()) m_thread.join();
    }

    virtual void do_work() = 0;

private:
    std::thread m_thread;
};
```

Тут виникає стан гонки (race condition): якщо планувальник операційної системи передасть квант часу новоствореному потоку до того, як головний потік перейде до виконання конструктора нащадка `DerivedWorker`, фоновий потік зчитає `vptr`, налаштований на `vtable for Worker`, і впаде у `__cxa_pure_virtual`. Ця помилка виникає нерегулярно й залежить від навантаження на процесор і таймінгів планувальника.

## Крайовий випадок: множинне та віртуальне спадкування

У складних ієрархіях із множинним спадкуванням об'єкт містить кілька таблиць віртуальних методів і кілька покажчиків `vptr` (по одному для кожної базової гілки).

Розглянемо клас `MultiChannelReceiver`, який успадковує два незалежні абстрактні класи `IFrameSource` та `ILogSink`:
1. Спочатку конструюється перша базова частина `IFrameSource`. Її `vptr` налаштовується на `vtable for IFrameSource`.
2. Потім конструюється друга базова частина `ILogSink`. Її `vptr` налаштовується на `vtable for ILogSink`.
3. Якщо всередині конструктора `ILogSink` викликати метод першого предка через збережене посилання, ми потрапляємо в ситуацію, коли перший предок уже сконструйований, але кінцевий клас ще ні. Будь-який чистий віртуальний виклик через інтерфейс `ILogSink` так само аварійно викличе `__cxa_pure_virtual`.

Більше того, у множинному спадкуванні компілятор використовує спеціальні перехідники адреси (thunks) для коригування покажчика `this`. Якщо виклик відбувається над незавершеним об'єктом, коригування зміщення в пам'яті вказує на неініціалізовані байти, що посилює руйнування пам'яті.

## Порівняння з мовами Java та C#

Поведінка C++ під час конструювання істотно відрізняється від інших об'єктних мов:

* **У мовах Java та C#** таблиця віртуальних методів (`vtable` / `vmt`) прив'язується до об'єкта **одразу на початку конструювання** для кінцевого типу нащадка. Якщо викликати віртуальний метод у конструкторі базового класу Java або C#, середовище виконання викличе метод похідного класу! Проте в цей момент поля нащадка ще не проініціалізовані й містять `null` або `0`, що призводить до винятків `NullPointerException` або некоректної роботи з неініціалізованим станом.
* **У мові C++** віртуальна таблиця змінюється поступово разом із просуванням по ланцюгу конструкторів. Це гарантує, що код ніколи не звернеться до неініціалізованих полів нащадка, але робить виклик чистих віртуальних методів фатальним крахом.

## Безпечне розв'язання: двоетапна фабрична ініціалізація та NVI

Єдиний надійний спосіб запобігти краху `__cxa_pure_virtual` — суворо розділити відповідальність:
1. **Конструктори** повинні займатися виключно ініціалізацією власних полів і встановленням локальних інваріантів пам'яті. Вони ніколи не повинні виконувати віртуальні виклики та не повинні публікувати незрілий покажчик `this` іншим потокам.
2. **Поліморфний запуск** переноситься у відкритий метод життєвого циклу, який викликається через статичну фабричну функцію після повного завершення всіх конструкторів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct PacketReceiver PacketReceiver;

typedef struct ReceiverVTable {
    void (*process_payload)(PacketReceiver* self, const uint8_t* data, size_t len);
    void (*destroy)(PacketReceiver* self);
} ReceiverVTable;

struct PacketReceiver {
    const ReceiverVTable* vptr;
    int socket_fd;
};

typedef struct TelemetryReceiver {
    PacketReceiver base;
    uint64_t processed_packets;
} TelemetryReceiver;

static void telemetry_process(PacketReceiver* self_base, const uint8_t* data, size_t len) {
    TelemetryReceiver* self = (TelemetryReceiver*)self_base;
    self->processed_packets++;
    printf("Пакет телеметрії #%lu успішно розібрано, байтів: %zu\n", self->processed_packets, len);
}

static void telemetry_destroy(PacketReceiver* self_base) {
    free(self_base);
}

static const ReceiverVTable g_telemetry_vtable = {
    .process_payload = telemetry_process,
    .destroy = telemetry_destroy
};

/* Безпечна фабрика створення */
PacketReceiver* telemetry_receiver_create(int socket_fd) {
    TelemetryReceiver* obj = (TelemetryReceiver*)malloc(sizeof(TelemetryReceiver));
    if (!obj) return NULL;

    obj->base.vptr = &g_telemetry_vtable;
    obj->base.socket_fd = socket_fd;
    obj->processed_packets = 0;

    /* Безпечний виклик: таблиця конкретного нащадка гарантовано встановлена */
    const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
    obj->base.vptr->process_payload((PacketReceiver*)obj, handshake, sizeof(handshake));

    return (PacketReceiver*)obj;
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <cstdint>

class PacketReceiver {
public:
    virtual ~PacketReceiver() = default;

    // Контракт чистої віртуальної поведінки
    virtual void process_payload(const uint8_t* data, std::size_t len) = 0;

    // Каркасний метод запуску (NVI)
    void start_receiver() {
        const uint8_t handshake[4] = {0xAA, 0x55, 0x01, 0x00};
        // Безпечно: цей метод викликається лише після повного конструювання об'єкта
        process_payload(handshake, sizeof(handshake));
    }

protected:
    // Конструктор доступний лише похідним класам
    explicit PacketReceiver(int socket_fd) : m_socket_fd(socket_fd) {}

private:
    int m_socket_fd;
};

class TelemetryReceiver final : public PacketReceiver {
public:
    // Статична фабрика повертає повністю ініціалізований розумний покажчик
    static std::unique_ptr<TelemetryReceiver> create(int socket_fd) {
        // Створюємо об'єкт: виконуються конструктори PacketReceiver і TelemetryReceiver
        auto instance = std::unique_ptr<TelemetryReceiver>(new TelemetryReceiver(socket_fd));

        // Тепер vptr гарантовано вказує на vtable for TelemetryReceiver
        instance->start_receiver();
        return instance;
    }

    void process_payload(const uint8_t* data, std::size_t len) override {
        std::cout << "Телеметрію розібрано, розмір: " << len << " байтів\n";
    }

private:
    // Конструктор приватний: створення лише через create()
    explicit TelemetryReceiver(int socket_fd) : PacketReceiver(socket_fd) {}
};
```
:::

Завдяки патерну фабрики:
* Створення екземпляра в обхід фабрики заборонено на рівні компілятора приватним або захищеним конструктором.
* Початкова поліморфна робота виконується лише тоді, коли об'єкт досяг зрілого стану й покажчик `vptr` остаточно закріплений за таблицею конкретного похідного класу `TelemetryReceiver`.
* Помилка `__cxa_pure_virtual` стає архітектурно неможливою.
