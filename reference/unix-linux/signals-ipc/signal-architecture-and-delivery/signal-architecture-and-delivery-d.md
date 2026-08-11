# Архітектура та доставка сигналів

<preknowlist>
- [Концепції ядра Linux](book:unix-linux/kernel-and-userspace) — базовий устрій системних викликів та простору користувача.
</preknowlist>


У цьому розділі ми детально розглянемо архітектуру сигналів в Unix/Linux, їх доставку, а також ключові системні виклики, які використовуються для роботи з сигналами.

<div class="preknowlist">

- **book:reference/unix-linux/processes/process-model**: Модель процесів, контекст процесу, стани процесів.
- **book:reference/unix-linux/signals-ipc/signal-model**: Базова модель сигналів та їх призначення.

</div>

## Життєвий цикл сигналу

Сигнали в Unix-подібних системах проходять через три основні етапи:
1. **Генерація (Generation)**: Сигнал створюється ядром або іншим процесом (наприклад, за допомогою `kill()`).
2. **Очікування (Pending)**: Сигнал додається до черги очікування цільового процесу.
3. **Доставка (Delivery)**: Ядро перериває нормальне виконання процесу для обробки сигналу (через обробник, ігнорування або дію за замовчуванням).

## Системний виклик `sigaction`

Найважливішим інструментом для налаштування реакції на сигнали є `sigaction`. На відміну від застарілого `signal()`, він забезпечує передбачувану поведінку.

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

void handler(int signum) {
    const char *msg = "Отримано сигнал!\n";
    write(STDOUT_FILENO, msg, strlen(msg));
}

int main() {
    struct sigaction sa;
    sa.sa_handler = handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0; // Або SA_RESTART

    if (sigaction(SIGINT, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    while(1) {
        sleep(1);
    }
    return 0;
}
```

## Маска сигналів та `sigpending`

Кожен процес має **маску сигналів** (signal mask), яка визначає, які сигнали тимчасово заблоковані. Заблоковані сигнали залишаються у стані *pending*, поки їх не розблокують.

Для роботи з маскою використовується `sigprocmask` (або `pthread_sigmask` у багатопотокових програмах), а для перевірки очікуючих сигналів — `sigpending`.

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

int main() {
    sigset_t mask, pending;

    // Блокуємо SIGINT
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigprocmask(SIG_BLOCK, &mask, NULL);
    
    printf("SIGINT заблоковано. Натисніть Ctrl+C...\n");
    sleep(5); // У цей час SIGINT стає pending
    
    // Перевіряємо pending сигнали
    sigpending(&pending);
    if (sigismember(&pending, SIGINT)) {
        printf("\nSIGINT знаходиться в черзі очікування!\n");
    }
    
    // Розблоковуємо
    sigprocmask(SIG_UNBLOCK, &mask, NULL);
    printf("Розблоковано.\n"); // Якщо SIGINT був у черзі, процес завершиться тут (дія за замовчуванням)

    return 0;
}
```

## Signal Frame та `altstack`

Коли ядро доставляє сигнал, воно створює так званий **signal frame** у стеку процесу. Це контекст, у якому викликається обробник сигналу. Після завершення обробника ядро використовує системний виклик `sigreturn` (який зазвичай додається автоматично стандартною бібліотекою C), щоб відновити попередній стан процесу.

Якщо стек процесу переповнено (наприклад, нескінченна рекурсія, помилка `SIGSEGV`), ядро не зможе створити signal frame у звичайному стеку. У таких випадках обробник навіть не запуститься, і процес буде завершено.
Щоб запобігти цьому, можна налаштувати **альтернативний стек сигналів** за допомогою `sigaltstack()`.

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void segv_handler(int signum) {
    const char *msg = "Перехоплено SIGSEGV на альтернативному стеку!\n";
    write(STDOUT_FILENO, msg, 49);
    _exit(1);
}

int main() {
    stack_t ss;
    ss.ss_sp = malloc(SIGSTKSZ);
    ss.ss_size = SIGSTKSZ;
    ss.ss_flags = 0;
    
    if (sigaltstack(&ss, NULL) == -1) {
        perror("sigaltstack");
        return 1;
    }

    struct sigaction sa;
    sa.sa_handler = segv_handler;
    sigemptyset(&sa.sa_mask);
    // SA_ONSTACK вказує використовувати альтернативний стек
    sa.sa_flags = SA_ONSTACK; 

    sigaction(SIGSEGV, &sa, NULL);

    // Провокуємо SIGSEGV нескінченною рекурсією (переповнення стеку)
    main();

    return 0;
}
```

## Відправка сигналів: `kill`

Для генерації сигналів іншим процесам найчастіше використовується системний виклик `kill()`.

```c
#include <signal.h>

// Відправити SIGTERM процесу з ідентифікатором pid
kill(pid, SIGTERM);
```
Дія `kill` підпорядковується правилам дозволів: процес може відправляти сигнали лише тим процесам, які належать тому ж користувачу, або якщо він має права `root`.
