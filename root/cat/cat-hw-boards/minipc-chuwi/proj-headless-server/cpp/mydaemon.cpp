// mydaemon.cpp — живучий демон під systemd
// збірка:  g++ -O2 -o mydaemon mydaemon.cpp -lsystemd
#include <systemd/sd-daemon.h>   // sd_notify: READY=1, WATCHDOG=1
#include <csignal>
#include <cstdio>
#include <ctime>
#include <unistd.h>
#include <atomic>

// Прапорець «час завершуватися». volatile sig_atomic_t — єдиний тип,
// який стандарт дозволяє безпечно чіпати всередині обробника сигналу.
static volatile sig_atomic_t g_stop = 0;

// Обробник SIGTERM: НІЧОГО важкого тут не робимо — лише піднімаємо прапорець.
// Друкувати, малочити, звертатися до бази в обробнику НЕ можна: він може
// перервати програму будь-де, і складні виклики там небезпечні.
static void on_sigterm(int)
{
    g_stop = 1;
}

int main()
{
    // 1. Перехопити SIGTERM (систему просить зупинитися) і SIGINT (Ctrl-C).
    struct sigaction sa = {};
    sa.sa_handler = on_sigterm;
    sigaction(SIGTERM, &sa, nullptr);
    sigaction(SIGINT,  &sa, nullptr);

    // 2. --- ІНІЦІАЛІЗАЦІЯ ---
    // Тут реально: відкрити файли, під'єднатися до бази, підняти сокет.
    // Помилку старту повертаємо ненульовим кодом — systemd це побачить.
    fprintf(stdout, "старт: ініціалізація завершена\n");
    fflush(stdout);                     // під journald буфер варто скидати одразу

    // 3. Сказати systemd «я готовий» — цього чекає Type=notify.
    sd_notify(0, "READY=1\nSTATUS=збираю показники");

    // 4. --- ГОЛОВНИЙ ЦИКЛ ---
    unsigned long tick = 0;
    while (!g_stop)                     // виходимо ЛИШЕ коли попросили
    {
        // ... тут корисна робота: зчитати показник, записати, віддати ...
        fprintf(stdout, "такт %lu: діло зроблено\n", tick++);
        fflush(stdout);

        // Годуємо сторожа: «я живий». WatchdogSec=30 → кличемо частіше.
        sd_notify(0, "WATCHDOG=1");

        sleep(1);                       // темп роботи
    }

    // 5. --- ЧИСТИЙ ВИХІД (потрапляємо сюди за SIGTERM) ---
    // Тут реально: дописати файл, закрити базу, віддати сокет.
    sd_notify(0, "STOPPING=1");
    fprintf(stdout, "зупинка: дописав, закрив — виходжу чисто\n");
    fflush(stdout);

    return 0;                           // код 0 = чистий вихід, Restart не спрацює
}
