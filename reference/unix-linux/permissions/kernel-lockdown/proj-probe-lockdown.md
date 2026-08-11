# ⚙️ Проба меж: програма, що стукає в двері ядра й розбирає відповідь

Сто двадцять рядків мовою C, які кажуть про конкретну машину те, чого не скаже жоден файл із налаштуваннями: які саме двері всередину ядра на ній зараз відчинені — і **чому** зачинені решта, бо так вирішило блокування, бо бракує мандата, чи бо цих дверей у ядрі просто не зібрали.

<preknowlist>
- [Можливості (capabilities)](book:unix-linux/capabilities) — всевладдя root розібране на окремі мандати; доступ до сирого заліза дає `CAP_SYS_RAWIO`.
- [Журнал ядра: printk і dmesg](book:unix-linux/kernel-log-printk) — ядро пише свої повідомлення в кільцевий буфер, звідки їх читають `dmesg` і `/dev/kmsg`.
- [Псевдо-ФС: procfs, sysfs, tmpfs](book:unix-linux/pseudo-filesystems) — файли, за якими немає диска; securityfs із них.
- [Обов'язковий контроль доступу: SELinux і AppArmor](book:unix-linux/mac-selinux-apparmor) — окремий сторож, що судить операцію за політикою, незалежно від прав власника.
- [Підсистема perf: лічильники й вибірковий профіль](book:unix-linux/perf-events) — `perf_event_open()` віддає дескриптор, з якого читають вибірки подій.
</preknowlist>

## Чому одного файла в securityfs замало

Здається, питання вичерпується одним рядком:

```
$ cat /sys/kernel/security/lockdown
[none] integrity confidentiality
```

Три причини не вірити цьому рядку як опису стану машини.

**Файла може не бути** — і його відсутність нічого не означає. Або securityfs не змонтовано, або ядро зібрано без `CONFIG_SECURITY_LOCKDOWN_LSM`. У першому випадку блокування може бути й увімкнене, просто вікна в нього немає.

**Рівень називає політику, а не стан кожних дверей.** Частину з них тримає зачиненими зовсім не блокування: `CONFIG_STRICT_DEVMEM` у збірці, політика SELinux, параметр `msr.allow_writes=off`, `kernel.perf_event_paranoid`. Частина, навпаки, лишається відчиненою всупереч рівню — про це нижче.

**Ядра дистрибутивів мають власні латки.** Fedora, RHEL і Ubuntu вмикають блокування самі, коли прошивка повідомляє про перевірене завантаження, — і поводяться інакше, ніж основне ядро при тому самому вмісті файла.

Отже, рівень читаємо — але далі стукаємо в кожні двері окремо.

## Ідея: три свідчення на кожні двері

Стук сам по собі майже нічого не доводить. `−EPERM` повертає і блокування, і брак `CAP_SYS_RAWIO`, і SELinux, і фільтр запису MSR — а `errno` в усіх один. Тому проба збирає на кожні двері **три** свідчення й лише з них складає вирок.

Перше — код повернення того виклику, **у якому справді стоїть перевірка**. Друге — свій власний набір можливостей із `/proc/self/status`: без `CAP_SYS_RAWIO` уся проба міряє ваші права, а не політику машини. Третє — те, що ядро дописало в журнал **саме за час цього стуку**: відмовляючи через блокування, воно друкує рядок виду

```
Lockdown: lockdown-probe: /dev/mem,kmem,port is restricted; see man kernel_lockdown.7
```

де посередині — ім'я програми, а далі людська назва причини з таблиці `lockdown_reasons[]` у ядрі. Щоб зловити тільки свіжі рядки, проба відкриває `/dev/kmsg` і одразу переставляє позицію в кінець буфера (`lseek(…, 0, SEEK_END)`), а після кожного стуку вичерпує все, що встигло дописатися.

![Із коду повернення, журналу ядра й власних можливостей складається вирок про кожні двері](/reference/unix-linux/permissions/kernel-lockdown/img/verdict-tree.svg)

*Сам код повернення нічого не доводить: вирок складають із трьох свідчень.*

## Програма

```c
/* lockdown-probe.c — які двері в ядро відчинені на цій машині й чому зачинені решта.
 * gcc -O2 -o lockdown-probe lockdown-probe.c      запускати від root, x86-64
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#if defined(__i386__) || defined(__x86_64__)
#include <sys/io.h>                       /* ioperm() є лише на x86 */
#endif

#define CAP_SYS_RAWIO 17

static int  kmsg = -1;                    /* /dev/kmsg, поставлений на кінець журналу */
static char note[300];                    /* сюди лягає знайдений рядок Lockdown: */

/* Забираємо все, що ядро дописало від попереднього стуку, і шукаємо слід блокування. */
static int lockdown_said_no(void)
{
    char rec[8192];
    int found = 0;

    note[0] = '\0';
    if (kmsg < 0)
        return 0;
    for (;;) {
        ssize_t n = read(kmsg, rec, sizeof rec - 1);
        if (n < 0) {
            if (errno == EPIPE) continue;         /* старі записи витиснули — читаємо далі */
            break;                                /* EAGAIN: нового більше немає */
        }
        rec[n] = '\0';
        char *p = strstr(rec, "Lockdown: ");
        if (p && !found) {
            char *nl = strchr(p, '\n');
            if (nl) *nl = '\0';
            snprintf(note, sizeof note, "%s", p);
            found = 1;
        }
    }
    return found;
}

static unsigned long long cap_eff(void)
{
    unsigned long long v = 0;
    char line[256];
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "CapEff:", 7)) { v = strtoull(line + 7, NULL, 16); break; }
    fclose(f);
    return v;
}

static int knock_devmem(void)   /* перевірка стоїть в open_port() — тобто на відкритті */
{
    int fd = open("/dev/mem", O_RDONLY);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}

static int knock_kcore(void)
{
    int fd = open("/proc/kcore", O_RDONLY);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}

static int knock_ioport(void)
{
#if defined(__i386__) || defined(__x86_64__)
    if (ioperm(0x80, 1, 1) < 0) return -errno;    /* лише просимо дозвіл, у порт не пишемо */
    ioperm(0x80, 1, 0);
    return 0;
#else
    return -ENOSYS;
#endif
}

/* MSR: перевірка стоїть НЕ на відкритті, а на записі. Пишемо 4 байти — ядро спитає
 * блокування, потім спіткнеться об «довжина не кратна 8» і поверне EINVAL,
 * так і не діставшись жодного регістра. */
static int knock_msr(void)
{
    unsigned int half = 0;
    int fd = open("/dev/cpu/0/msr", O_RDWR);
    if (fd < 0) return -errno;
    ssize_t r = pwrite(fd, &half, sizeof half, 0x1b0 /* IA32_ENERGY_PERF_BIAS */);
    int e = (r < 0) ? -errno : 0;
    close(fd);
    return (e == -EINVAL) ? 0 : e;                /* EINVAL = блокування пропустило */
}

static int perf_knock(int kernel_regs)
{
    struct perf_event_attr a;
    memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_SOFTWARE;
    a.size = sizeof a;
    a.config = PERF_COUNT_SW_CPU_CLOCK;
    a.sample_period = 1000000;
    a.sample_type = PERF_SAMPLE_IP;
    a.disabled = 1;
    if (kernel_regs) {
        a.sample_type |= PERF_SAMPLE_REGS_INTR;   /* саме це просить регістри ядра */
        a.sample_regs_intr = 1;                   /* один дійсний біт маски — і досить */
    }
    int fd = syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}
static int knock_perf_plain(void) { return perf_knock(0); }
static int knock_perf_regs(void)  { return perf_knock(1); }

static const struct door {
    const char *call;                             /* лише ASCII: за ним іде вирівняне поле */
    int (*knock)(void);
} doors[] = {
    { "open(\"/dev/mem\")",            knock_devmem     },
    { "ioperm(0x80, 1, 1)",            knock_ioport     },
    { "pwrite(\"/dev/cpu/0/msr\")",    knock_msr        },
    { "open(\"/proc/kcore\")",         knock_kcore      },
    { "perf_event_open()",             knock_perf_plain },
    { "perf_event_open(+REGS_INTR)",   knock_perf_regs  },
};

static const char *verdict(int rc, int said, unsigned long long eff)
{
    if (rc == 0)       return "двері відчинені";
    if (said)          return "зачинило блокування";
    if (rc == -EPERM && !((eff >> CAP_SYS_RAWIO) & 1))
                       return "−EPERM, журнал мовчить: найпевніше бракує CAP_SYS_RAWIO";
    if (rc == -EPERM)  return "−EPERM без сліду блокування: інший сторож";
    if (rc == -EACCES) return "відмовив обов'язковий контроль доступу";
    if (rc == -ENOENT || rc == -ENXIO || rc == -ENODEV)
                       return "дверей немає: ядро зібрано без цього інтерфейсу";
    if (rc == -ENOSYS) return "немає на цій архітектурі";
    return "інша причина";
}

int main(void)
{
    char buf[128];
    int fd = open("/sys/kernel/security/lockdown", O_RDONLY);
    if (fd < 0) {
        printf("оголошений рівень: файла немає (%s)\n", strerror(errno));
    } else {
        ssize_t n = read(fd, buf, sizeof buf - 1);
        buf[n > 0 ? n : 0] = '\0';
        printf("оголошений рівень: %s", buf);
        close(fd);
    }

    unsigned long long eff = cap_eff();
    printf("CAP_SYS_RAWIO:     %s\n\n",
           (eff >> CAP_SYS_RAWIO) & 1 ? "є" : "НЕМАЄ — далі буде видно ваші права, а не політику");

    kmsg = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);
    if (kmsg >= 0) lseek(kmsg, 0, SEEK_END);

    for (size_t i = 0; i < sizeof doors / sizeof *doors; i++) {
        int rc   = doors[i].knock();
        int said = lockdown_said_no();
        /* вирок друкуємо ОСТАННІМ: ширина поля рахує байти, а кирилиця в UTF-8
           займає по два — вирівняти можна лише те, що ліворуч від неї */
        printf("%-30s %-24s %s\n", doors[i].call,
               rc == 0 ? "пройшло" : strerror(-rc), verdict(rc, said, eff));
        if (note[0]) printf("%-30s %s\n", "", note);
    }
    return 0;
}
```

## Що воно друкує

Спершу на машині, де блокування не вмикали:

```
# ./lockdown-probe
оголошений рівень: [none] integrity confidentiality
CAP_SYS_RAWIO:     є

open("/dev/mem")               пройшло                  двері відчинені
ioperm(0x80, 1, 1)             пройшло                  двері відчинені
pwrite("/dev/cpu/0/msr")       пройшло                  двері відчинені
open("/proc/kcore")            пройшло                  двері відчинені
perf_event_open()              пройшло                  двері відчинені
perf_event_open(+REGS_INTR)    пройшло                  двері відчинені
```

Тепер піднімемо рівень і повторимо. Пам'ятайте, що це рух в один бік: понизити його не зможе ніхто, повертає систему тільки перезавантаження.

```
# echo integrity > /sys/kernel/security/lockdown
# ./lockdown-probe
оголошений рівень: none [integrity] confidentiality
CAP_SYS_RAWIO:     є

open("/dev/mem")               Operation not permitted  зачинило блокування
                               Lockdown: lockdown-probe: /dev/mem,kmem,port is restricted; see man kernel_lockdown.7
ioperm(0x80, 1, 1)             Operation not permitted  зачинило блокування
                               Lockdown: lockdown-probe: raw io port access is restricted; see man kernel_lockdown.7
pwrite("/dev/cpu/0/msr")       Operation not permitted  зачинило блокування
                               Lockdown: lockdown-probe: raw MSR access is restricted; see man kernel_lockdown.7
open("/proc/kcore")            пройшло                  двері відчинені
perf_event_open()              пройшло                  двері відчинені
perf_event_open(+REGS_INTR)    пройшло                  двері відчинені
```

Три верхні двері зачинилися, три нижні лишилися відчиненими — і це рівно та межа, що відділяє причини запису від причин читання. На `confidentiality` додасться `/proc/kcore access is restricted`, а з двох викликів `perf_event_open` упаде **лише другий**: блокування судить не сам виклик, а прохання про стан регістрів на момент переривання — саме таку вибірку, за документацією, повертають із регістрами ядра, якщо лічильник перебрав, поки працював код ядра. Звідси й назва причини в ядрі — «unsafe use of perf», небезпечне вживання, а не вживання взагалі.

## Пастки

**Перевірку ставлять на відкритті — але не завжди.** У `/dev/mem` питання про блокування стоїть в `open_port()`, тобто на `open()`; звідси головний наслідок для проби: **уже відкритий дескриптор нічого не покаже**. Служба, що відкрила `/dev/mem` до підняття рівня, пише в нього й далі, і жодна проба цього не виявить: вона питає ядро про **нове** відкриття, а старий дескриптор уже пройшов перевірку колись. Шукати такі дескриптори треба не в `/dev`, а в таблицях відкритих файлів усіх процесів:

```
# ls -l /proc/*/fd/* 2>/dev/null | grep -E '/dev/(mem|port)|/proc/kcore'
lrwx------ 1 root root 64 /proc/812/fd/7 -> /dev/mem
```

Один такий рядок скасовує весь звіт проби: скільки б дверей вона не показала зачиненими, у процесі 812 лежить ключ від однієї з них. Саме тому рівень, піднятий записом у securityfs десь посеред завантаження, слабший за той самий рівень, заданий параметром командного рядка. А от у драйвері MSR перевірка стоїть на **записі**, не на відкритті: `open("/dev/cpu/0/msr")` вдасться на будь-якому рівні. Проба, яка обмежилася б відкриттям, впевнено збрехала б, що двері відчинені.

**Один `errno` на кілька сторожів.** Для портів вводу-виводу ядро питає обидві перевірки в одній умові — `!capable(CAP_SYS_RAWIO) || security_locked_down(LOCKDOWN_IOPORT)` — і повертає `−EPERM` незалежно від того, котра спрацювала. Розрізнити їх можна тільки збоку: за рядком у журналі та за власним набором можливостей.

**Рядок у журналі не завжди означає, що відмовив саме він.** В `open_kcore()` результат `security_locked_down(LOCKDOWN_KCORE)` беруть **першим**, а перевірку `CAP_SYS_RAWIO` роблять після нього. Отже, непривілейований процес на замкненій машині отримає `−EPERM` через брак мандата, а рядок `Lockdown:` у журналі все одно з'явиться. Він свідчить, що блокування **питали**, а не що воно й винне.

**Журнал рвано-обмежений.** Повідомлення друкує `pr_notice_ratelimited()`, тому щільна серія стуків або кілька запусків підряд з'їдять частину рядків, і проба покаже «журнал мовчить» там, де блокування насправді відмовило. Стукайте поволі й по одних дверях за раз. Додайте до цього `kernel.dmesg_restrict=1`, за якого `/dev/kmsg` непривілейованому процесові взагалі не відкриється, і ім'я програми в рядку, зрізане до п'ятнадцяти символів, — за довшим іменем шукати марно.

**Двері відчинилися — кімната може бути порожня.** З `CONFIG_STRICT_DEVMEM` (типова збірка дистрибутива) `open("/dev/mem")` вдається, а спроба прочитати сторінку звичайної оперативної пам'яті повертає `−EPERM` з іншої перевірки. Проба чесно скаже «відчинено», і це правда — просто читати за цими дверима нема чого.

**Не все, що відмовляє, є блокуванням.** Ту саму відмову дають політика [SELinux чи AppArmor](book:unix-linux/mac-selinux-apparmor) — тоді слід лишається не в `Lockdown:`, а в записах аудиту з міткою `avc: denied`; параметр `msr.allow_writes=off`, за якого фільтр запису MSR повертає `−EPERM` ще до всякого блокування; `kernel.perf_event_paranoid` для perf. Проба таких випадків не плутає рівно тому, що дивиться на журнал, а не на `errno`.

**`ENOENT` — це не «зачинено».** Якщо ядро зібрали без `CONFIG_DEVMEM` або `CONFIG_PROC_KCORE`, дверей просто немає. Так само й `/dev/kmem`: із сучасних ядер його прибрали зовсім, і жодного стосунку до блокування це не має.

**Проба нічого не псує — і це не випадковість.** Кожен стук навмисно спинено на півдорозі: у порт ми не пишемо, лише просимо й одразу віддаємо дозвіл; чотирибайтовий запис у MSR ядро відкидає перевіркою довжини **раніше**, ніж дійде до `wrmsr` і до позначення ядра як «поза специфікацією»; лічильник perf створюємо вимкненим. Єдиний слід у журналі — одне попередження драйвера MSR про запис у нерозпізнаний регістр, теж рвано-обмежене.

## Джерела

- [security/security.c, torvalds/linux](https://github.com/torvalds/linux/blob/master/security/security.c) — масив `lockdown_reasons[]`: саме звідси рядки «/dev/mem,kmem,port», «raw io port access», «raw MSR access», «/proc/kcore access», «unsafe use of perf».
- [security/lockdown/lockdown.c, torvalds/linux](https://github.com/torvalds/linux/blob/master/security/lockdown/lockdown.c) — `lockdown_is_locked_down()` друкує повідомлення через `pr_notice_ratelimited()`; `lockdown_read()` бере поточний рівень у квадратні дужки.
- [drivers/char/mem.c, torvalds/linux](https://github.com/torvalds/linux/blob/master/drivers/char/mem.c) — `open_port()`: спершу `capable(CAP_SYS_RAWIO)`, потім `security_locked_down(LOCKDOWN_DEV_MEM)`; `page_is_allowed()` під `CONFIG_STRICT_DEVMEM`; `/dev/kmem` у переліку пристроїв уже немає.
- [arch/x86/kernel/msr.c, torvalds/linux](https://github.com/torvalds/linux/blob/master/arch/x86/kernel/msr.c) — `msr_write()`: `security_locked_down(LOCKDOWN_MSR)` → `filter_write()` → `if (count % 8) return -EINVAL;`, і лише після цього `wrmsr`.
- [arch/x86/kernel/ioport.c, torvalds/linux](https://github.com/torvalds/linux/blob/master/arch/x86/kernel/ioport.c) — обидві перевірки в одній умові `!capable(CAP_SYS_RAWIO) || security_locked_down(LOCKDOWN_IOPORT)`.
- [perf_event_open(2), Linux manual page](https://man7.org/linux/man-pages/man2/perf_event_open.2.html) — про `PERF_SAMPLE_REGS_INTR`: значення регістрів будуть станом регістрів ядра, якщо перебирання сталося під час виконання коду ядра.
- [kernel_lockdown(7), Linux manual page](https://man7.org/linux/man-pages/man7/kernel_lockdown.7.html) — перелік того, що замикають режими; `perf` у ньому не згадано, деталь довелося брати з коду. *Статус: сторінка описує механізм у загальних рисах і відстає від коду ядра.*
