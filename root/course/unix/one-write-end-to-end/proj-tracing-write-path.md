# ⚙️ Практикум: наскрізне трасування шляху write() через eBPF

Щоб перевірити теоретичну модель проходження запису крізь підсистеми ядра Linux, необхідно інструментувати ключові вузли операційної системи. Інструмент `bpftrace` на базі технології eBPF дозволяє прикріпитися до статичних точок трасування (*tracepoints*) та динамічних зондів ядра (*kprobes*) без перекомпіляції ядра і без відчутного уповільнення системи.

```
+-------------------------------------------------------------------------------+
|  sys_enter_write -> vfs_write -> folio_mark_dirty                             |
|       |                                                                       |
|       v (асинхронно / fsync)                                                  |
|  ext4_writepages -> block_bio_queue -> block_rq_issue -> nvme_setup_cmd       |
+-------------------------------------------------------------------------------+
```

## Архітектура точок спостереження в ядрі

Для побудови повної часової діаграми необхідно перехопити події на чотирьох структурних кордонах ядра:

1. **Межа користувач — ядро:** Статична точка `tracepoint:syscalls:sys_enter_write` спрацьовує безпосередньо після виконання машинної інструкції `syscall` на процесорі. Вона фіксує момент передачі керування в ядро, аргументи виклику (файловий дескриптор, адресу буфера у віртуальній пам'яті процесу та замовлений обсяг байтів) і фіксує початкову часову мітку процесу.
2. **Шар VFS та модифікація кешу:** Динамічний зонд `kprobe:vfs_write` перехоплює вхід у диспетчер віртуальної файлової системи, а зонд `kprobe:folio_mark_dirty` (або `kprobe:set_page_dirty`) фіксує точну наносекунду, коли байти з простору користувача скопійовано у фізичний фрейм RAM і сторінку позначено апаратним прапорцем модифікації `PG_dirty`.
3. **Блоковий рівень:** Точка `tracepoint:block:block_bio_queue` фіксує перетворення сторінок пам'яті на структури `struct bio` та їхню передачу в черги планувальника `blk-mq`. Наступна точка `tracepoint:block:block_rq_issue` спрацьовує, коли планувальник об'єднав суміжні сектори у фінальний запит `struct request` і передав його драйверу пристрою.
4. **Апаратний контролер накопичувача:** Точки `tracepoint:nvme:nvme_setup_cmd` та `tracepoint:nvme:nvme_complete_rq` фіксують відправку 64-байтової команди у чергу Submission Queue контролера та прихід апаратного переривання MSI-X про завершення DMA-передачі.

## Тестова програма: генератор контрольованих записів

Для відстеження сформуємо процес, який виконує передбачувану послідовність дій: відкриває файл у буферизованому режимі, записує 4096 байтів, робить паузу у дві секунди та примусово викликає `fdatasync()` для синхронізації з носієм.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    const char *path = "/tmp/trace_test.dat";
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    char buffer[4096];
    memset(buffer, 'A', sizeof(buffer));

    printf("PID: %d | Виконуємо write()...\n", getpid());
    ssize_t written = write(fd, buffer, sizeof(buffer));
    if (written < 0) {
        perror("write");
        close(fd);
        return 1;
    }

    printf("Записано %zd байтів у Page Cache. Очікування 2 секунди...\n", written);
    sleep(2);

    printf("Виконуємо fdatasync()...\n");
    if (fdatasync(fd) < 0) {
        perror("fdatasync");
        close(fd);
        return 1;
    }

    printf("Синхронізацію завершено. Закриваємо файл.\n");
    close(fd);
    unlink(path);
    return 0;
}
```
@tab C++
```cpp
#include <array>
#include <chrono>
#include <cstddef>
#include <fcntl.h>
#include <iostream>
#include <print>
#include <string_view>
#include <system_error>
#include <thread>
#include <unistd.h>

class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_{fd} {}
    ~FileDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

int main() {
    constexpr std::string_view path = "/tmp/trace_test.dat";
    FileDescriptor file{::open(path.data(), O_WRONLY | O_CREAT | O_TRUNC, 0644)};
    if (!file.valid()) {
        std::println(stderr, "Помилка відкриття: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::array<char, 4096> buffer{};
    buffer.fill('A');

    std::println("PID: {} | Виконуємо write()...", ::getpid());
    const ssize_t written = ::write(file.get(), buffer.data(), buffer.size());
    if (written < 0) {
        std::println(stderr, "Помилка write: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::println("Записано {} байтів у Page Cache. Очікування 2 секунди...", written);
    std::this_thread::sleep_for(std::chrono::seconds(2));

    std::println("Виконуємо fdatasync()...");
    if (::fdatasync(file.get()) < 0) {
        std::println(stderr, "Помилка fdatasync: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::println("Синхронізацію завершено. Закриваємо файл.");
    ::unlink(path.data());
    return 0;
}
```
:::

## Скрипт трасування на bpftrace

Скрипт перехоплює подію входження в системний виклик, проходження крізь VFS, модифікацію кешу, стадію блокового запису та передачу команди в NVMe-контролер.

```bt
#!/usr/bin/env bpftrace

BEGIN
{
    printf("Трасування наскрізного шляху запису розпочато... Натисніть Ctrl+C для зупинки.\n");
    printf("%-10s %-16s %-8s %-24s %s\n", "ЧАС (мкс)", "ПРОЦЕС", "PID", "ФУНКЦІЯ / ПОДІЯ", "ДЕТАЛІ");
}

/* 1. Точка входу в системний виклик */
tracepoint:syscalls:sys_enter_write
/comm == "trace_test"/
{
    @t_start[tid] = nsecs;
    printf("%-10d %-16s %-8d %-24s fd=%d, bytes=%lu\n",
           elapsed / 1000, comm, pid, "sys_enter_write", args.fd, args.count);
}

/* 2. Шар VFS */
kprobe:vfs_write
/comm == "trace_test"/
{
    printf("%-10d %-16s %-8d %-24s count=%lu\n",
           elapsed / 1000, comm, pid, "vfs_write", arg2);
}

/* 3. Запис у Page Cache та маркування брудної сторінки */
kprobe:folio_mark_dirty
/comm == "trace_test"/
{
    printf("%-10d %-16s %-8d %-24s folio marked PG_dirty\n",
           elapsed / 1000, comm, pid, "folio_mark_dirty");
}

/* 4. Повернення з системного виклику write */
tracepoint:syscalls:sys_exit_write
/comm == "trace_test"/
{
    $lat = (nsecs - @t_start[tid]) / 1000;
    delete(@t_start[tid]);
    printf("%-10d %-16s %-8d %-24s ret=%ld, латентність=%lu мкс\n",
           elapsed / 1000, comm, pid, "sys_exit_write", args.ret, $lat);
}

/* 5. Початок скидання сторінок ФС (під час fdatasync або writeback) */
kprobe:ext4_writepages
{
    printf("%-10d %-16s %-8d %-24s виштовхування брудних сторінок\n",
           elapsed / 1000, comm, pid, "ext4_writepages");
}

/* 6. Постановка struct bio в чергу блокового рівня */
tracepoint:block:block_bio_queue
{
    printf("%-10d %-16s %-8d %-24s dev=%d,%d sector=%llu bytes=%u\n",
           elapsed / 1000, comm, pid, "block_bio_queue",
           args.dev >> 20, args.dev & 0xfffff, args.sector, args.nr_sector * 512);
}

/* 7. Передача сформованого request у драйвер пристрою */
tracepoint:block:block_rq_issue
{
    printf("%-10d %-16s %-8d %-24s dev=%d,%d sector=%llu bytes=%u\n",
           elapsed / 1000, comm, pid, "block_rq_issue",
           args.dev >> 20, args.dev & 0xfffff, args.sector, args.bytes);
}

/* 8. Формування команди в драйвері NVMe */
tracepoint:nvme:nvme_setup_cmd
{
    printf("%-10d %-16s %-8d %-24s qid=%u, cmdid=%u, nsid=%u\n",
           elapsed / 1000, comm, pid, "nvme_setup_cmd",
           args.qid, args.cmdid, args.nsid);
}

/* 9. Апаратне підтвердження завершення операції накопичувачем */
tracepoint:nvme:nvme_complete_rq
{
    printf("%-10d %-16s %-8d %-24s qid=%u, cmdid=%u, status=0x%x\n",
           elapsed / 1000, comm, pid, "nvme_complete_rq",
           args.qid, args.cmdid, args.status);
}

END
{
    clear(@t_start);
}
```

## Покроковий розбір журналу трасування

Запустивши скрипт `bpftrace` у першому терміналі з правами адміністратора `sudo bpftrace write_trace.bt` та виконавши бінарний файл `trace_test` у другому, отримуємо такий детальний часовий зріз:

```text
ЧАС (мкс)  ПРОЦЕС           PID      ФУНКЦІЯ / ПОДІЯ          ДЕТАЛІ
102400     trace_test       4120     sys_enter_write          fd=3, bytes=4096
102402     trace_test       4120     vfs_write                count=4096
102404     trace_test       4120     folio_mark_dirty         folio marked PG_dirty
102405     trace_test       4120     sys_exit_write           ret=4096, латентність=5 мкс
...
2102510    trace_test       4120     ext4_writepages          виштовхування брудних сторінок
2102515    trace_test       4120     block_bio_queue          dev=259,1 sector=20971520 bytes=4096
2102520    trace_test       4120     block_rq_issue           dev=259,1 sector=20971520 bytes=4096
2102522    trace_test       4120     nvme_setup_cmd           qid=2, cmdid=48, nsid=1
2102568    swapper/2        0        nvme_complete_rq         qid=2, cmdid=48, status=0x0
```

Отриманий журнал наочно виявляє ключові закономірності поведінки підсистем ядра:

1. **Розрив у часі між RAM та носієм:**
   Зверніть увагу на часові позначки: виклик `write()` завершився на позначці `102405` мкс, витративши всього 5 мікросекунд на копіювання байтів у сторінку пам'яті ядра та встановлення прапорця `PG_dirty`. Проте реальний запис на накопичувач розпочався лише на позначці `2102510` мкс — рівно через дві секунди, коли процес явно викликав системний виклик `fdatasync()`.
2. **Проходження блокового рівня за 10 мікросекунд:**
   Файлова система `ext4` викликала `ext4_writepages`, перетворила логічне зміщення файлу на номер сектора `sector=20971520` і передала `struct bio` у шар `blk-mq`. За 5 мікросекунд планувальник обробив чергу і сформував запит `struct request`, викликавши диспетчер `block_rq_issue`.
3. **Апаратна затримка контролера NVMe:**
   Драйвер NVMe надіслав команду з ідентифікатором `cmdid=48` у чергу `qid=2` о `2102522` мкс. Фізичне підтвердження `nvme_complete_rq` надійшло через апаратне переривання ядра на нульовому процесі ядра `swapper/2` о `2102568` мкс. Чиста тривалість операції контролера та DMA-передачі склала 46 мікросекунд.

## Відстеження злиття секторів: як працює блоковий планувальник

Під час інтенсивного послідовного виведення великого файлу (наприклад, копіювання масиву розміром 64 Мегабайти) окремі 4 КіБ сторінки Page Cache не повинні ставати ізольованими командами контролера накопичувача. Для перевірки роботи механізму злиття секторів (*I/O merging*) можна розширити скрипт спостереження точками `block:block_bio_backmerge` та `block:block_bio_frontmerge`.

Коли планувальник отримує новий `struct bio`, він перевіряє, чи не збігається його стартовий сектор із кінцевим сектором уже розміщеного в черзі `struct request`. Якщо так — фіксується подія `backmerge`:

```bt
tracepoint:block:block_bio_backmerge
{
    printf("ЗЛИТТЯ: bio з сектором %llu приєднано до існуючого запиту (розмір: %u байтів)\n",
           args.sector, args.nr_sector * 512);
}
```

У журналі спостереження можна побачити, як тридцять два послідовні виклики `write()` по 4 КіБ породжують рівно один апаратний виклик `block_rq_issue` на 128 КіБ: тридцять одна операція завершилася миттєвим приєднанням до черги без генерації додаткових транзакцій на шині PCIe.

## Порівняння гістограм: буферизований запис проти прямого вводу O_DIRECT

Для глибокого аналізу впливу Page Cache на латентність прикладних програм можна зібрати розподіл затримок системного виклику за допомогою логарифмічних гістограм eBPF.

Запустимо такий однорядковий скрипт:

```bash
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_write { @start[tid] = nsecs; }
tracepoint:syscalls:sys_exit_write /@start[tid]/ {
    @latency_us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'
```

Під час виконання навантаження з буферизованим записом 4 КіБ блоків розподіл затримок концентрується в діапазоні 1–4 мікросекунди:

```text
@latency_us:
[1]                 1824 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[2, 4)               452 |@@@@@@@@@@@@@                                       |
[4, 8)                38 |@                                                   |
[8, 16)                6 |                                                    |
```

Якщо ж відкрити файл із прапорцем прямого вводу-виводу `O_DIRECT | O_SYNC`, минаючи сторінковий кеш, розподіл зміщується вправо на два порядки, демонструючи реальну фізичну затримку накопичувача (50–150 мікросекунд):

```text
@latency_us:
[32, 64)              94 |@@@@@@                                              |
[64, 128)           1420 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[128, 256)           310 |@@@@@@@@@@@                                         |
```

## Інженерні підводні камені під час профілювання вводу-виводу

Під час проведення діагностики у виробничих середовищах необхідно враховувати три критичні обмеження інструментарію:

1. **Накладні витрати динамічних зондів (kprobes):**
   На відміну від статичних точок трасування, що компілюються в код ядра як інструкції `NOP` і активуються підміною кількох байтів інструкції, зонди `kprobe` викликають програмне переривання ядра (*breakpoint trap*) або інструкцію переходу `int3`. Якщо система виконує понад 500 000 IOPS, встановлення зонда на гарячу функцію `vfs_write` може забрати до 15–25 % процесорного часу одного ядра. Для високоінтенсивного профілювання слід надавати перевагу статичним точкам `tracepoint:*` або fexit/fentry зондам на базі BTF.
2. **Втрата подій у кільцевому буфері (Dropped Events):**
   Під час масованого скидання гігабайтів брудних сторінок ядро генерує сотні тисяч подій блокового шару на секунду. Якщо пропускна здатність кільцевого буфера `perf_event_output` eBPF вичерпується, у терміналі з'являється повідомлення `Lost X events`. Для усунення втрат слід збільшувати розмір виділеного буфера через параметр `bpftrace -b 64M` або звужувати фільтри вибірки за ідентифікатором процесу чи дескриптором цільового пристрою.
3. **Асинхронний контекст переривань (IRQ vs Process Context):**
   Завершення блокового запиту `nvme_complete_rq` та очищення сторінок `end_page_writeback` виконуються не в контексті процесу, який викликав `write()`, а в контексті обробника переривань `swapper` або системного потоку `kworker`. Спроби фільтрувати події завершення за `comm == "my_app"` або `pid == target_pid` призведуть до повної відсутності результатів у виводі трасування: зв'язування запиту з початковим процесом необхідно здійснювати за адресою дескриптора `struct request` або числовим ідентифікатором команди `cmdid`.
