# ⚙️ Пісочниця на сто рядків: запустити чужу команду з урізаним доступом

Напишемо `sandbox` — програму, якій дають три списки каталогів (на читання, на запис, звідки можна запускати) і команду, а вона будує набір правил, замикає пісочницю й підміняє себе цією командою. Це та сама річ, що лежить у ядрі як зразок `samples/landlock/sandboxer.c`, — і корисна вона не лише як приклад: після збирання нею користуються щодня, обгортаючи `make`, конвертери й чужі скрипти.

## Форма інструмента

Списки шляхів приходять аргументами, через двокрапку, як `PATH`:

```
./sandbox -r /etc -w /tmp/box -x /usr/bin:/usr/lib -- cat /etc/hostname
```

Кожному списку відповідає своя маска прав. Читання — це `READ_FILE` і `READ_DIR`. Запис — усе, що змінює вміст і структуру: `WRITE_FILE`, `TRUNCATE`, `REMOVE_FILE`, `REMOVE_DIR`, сімейство `MAKE_*` і `REFER`; туди ж додано `IOCTL_DEV`, бо керувати пристроєм — теж дія над ним, а не читання. Виконання варто тримати окремим списком, а не домішувати до читання: `EXECUTE` потрібне небагатьом системним каталогам, і саме воно робить каталог небезпечним — маючи його, процес запустить звідти будь-що, зокрема й те, що сам туди поклав.

Одна дрібниця в наборі прав неочевидна й дешева. Оголошувати в `handled_access_fs` варто **більше**, ніж роздаєте правилами: право, оголошене й нікому не дане, заборонене скрізь без винятку. Тому `MAKE_CHAR` і `MAKE_BLOCK` потрапляють в оголошення, але в жодну маску — створити файл пристрою в пісочниці стає неможливо взагалі, а коштувало це два рядки.

Обгортка не лишається наглядачем: останнім її ділом є `execvp`, який заміняє її саму на потрібну команду. Це не економія на процесі, а властивість механізму: обмеження живе на самому процесі й переживає заміну образу, тож стежити за ним ззовні нема потреби. У системі не з'являється ні супровідного демона, ні батька, що тримає дитину під `ptrace`, — є один процес, який спершу відрізав собі зайве, а тоді став чимось іншим. Убити наглядача, щоб вийти з пісочниці, тут просто нема кого.

Далі — те, через що така програма ніколи не буває на десять рядків. Перелік прав, які знає ядро, з часом росте, і зібрана вами програма мусить працювати й там, де ядро старіше за неї. Тож першим ділом питаємо номер версії ABI і прибираємо все, чого це ядро не знає. Прибирати треба **у двох місцях**: з оголошення й з кожної маски правил. Забудете друге — і `landlock_add_rule` поверне `EINVAL`, бо правило не може дозволяти більше, ніж набір узяв на себе.

## Код

```c
/* sandbox.c — запустити команду з урізаним доступом до файлової системи.
   Збірка:  cc -Wall -O2 -o sandbox sandbox.c                            */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

/* обгорток у бібліотеці C немає — кличемо номерами */
#ifndef __NR_landlock_create_ruleset
#define __NR_landlock_create_ruleset 444
#define __NR_landlock_add_rule       445
#define __NR_landlock_restrict_self  446
#endif

/* права, що з'явилися пізніше за заголовки, які може мати ця машина */
#ifndef LANDLOCK_ACCESS_FS_REFER
#define LANDLOCK_ACCESS_FS_REFER     (1ULL << 13)
#endif
#ifndef LANDLOCK_ACCESS_FS_TRUNCATE
#define LANDLOCK_ACCESS_FS_TRUNCATE  (1ULL << 14)
#endif
#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#define ACCESS_RO (LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR)

#define ACCESS_X  (ACCESS_RO | LANDLOCK_ACCESS_FS_EXECUTE)

#define ACCESS_RW (ACCESS_RO                       | \
    LANDLOCK_ACCESS_FS_WRITE_FILE  | LANDLOCK_ACCESS_FS_TRUNCATE   | \
    LANDLOCK_ACCESS_FS_REMOVE_FILE | LANDLOCK_ACCESS_FS_REMOVE_DIR | \
    LANDLOCK_ACCESS_FS_MAKE_REG    | LANDLOCK_ACCESS_FS_MAKE_DIR   | \
    LANDLOCK_ACCESS_FS_MAKE_SYM    | LANDLOCK_ACCESS_FS_MAKE_SOCK  | \
    LANDLOCK_ACCESS_FS_MAKE_FIFO   | LANDLOCK_ACCESS_FS_REFER      | \
    LANDLOCK_ACCESS_FS_IOCTL_DEV)

/* оголошуємо більше, ніж роздаємо: MAKE_CHAR і MAKE_BLOCK не дістануться нікому */
#define HANDLED (ACCESS_RW | ACCESS_X | \
    LANDLOCK_ACCESS_FS_MAKE_CHAR | LANDLOCK_ACCESS_FS_MAKE_BLOCK)

static int add_path(int ruleset_fd, const char *path, __u64 access)
{
    struct landlock_path_beneath_attr rule = { .allowed_access = access };
    int err;

    rule.parent_fd = open(path, O_PATH | O_CLOEXEC);
    if (rule.parent_fd < 0) {
        fprintf(stderr, "sandbox: %s: %s\n", path, strerror(errno));
        return -1;
    }
    err = syscall(__NR_landlock_add_rule, ruleset_fd,
                  LANDLOCK_RULE_PATH_BENEATH, &rule, 0);
    if (err)
        fprintf(stderr, "sandbox: правило на %s: %s\n", path, strerror(errno));
    close(rule.parent_fd);
    return err;
}

/* "a:b:c" → по правилу на елемент; рядок псується на місці, і це argv */
static int add_list(int ruleset_fd, char *list, __u64 access)
{
    if (list == NULL || access == 0)
        return 0;
    for (char *p = strtok(list, ":"); p != NULL; p = strtok(NULL, ":"))
        if (add_path(ruleset_fd, p, access) != 0)
            return -1;
    return 0;
}

int main(int argc, char *argv[])
{
    char *ro = NULL, *rw = NULL, *ex = NULL;
    __u64 handled = HANDLED;
    int i, abi, ruleset_fd;

    for (i = 1; i + 1 < argc; i += 2) {
        if      (strcmp(argv[i], "-r") == 0) ro = argv[i + 1];
        else if (strcmp(argv[i], "-w") == 0) rw = argv[i + 1];
        else if (strcmp(argv[i], "-x") == 0) ex = argv[i + 1];
        else break;
    }
    if (i < argc && strcmp(argv[i], "--") == 0)
        i++;
    if (i >= argc) {
        fprintf(stderr, "вжиток: %s [-r шляхи] [-w шляхи] [-x шляхи]"
                        " -- команда…\n", argv[0]);
        return 2;
    }

    /* 1. питаємо, що вміє це ядро, і прибираємо решту з оголошення */
    abi = syscall(__NR_landlock_create_ruleset, NULL, 0,
                  LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 0) {
        fprintf(stderr, "sandbox: Landlock недоступний: %s\n", strerror(errno));
        return 1;
    }
    if (abi < 2) handled &= ~LANDLOCK_ACCESS_FS_REFER;
    if (abi < 3) handled &= ~LANDLOCK_ACCESS_FS_TRUNCATE;
    if (abi < 5) handled &= ~LANDLOCK_ACCESS_FS_IOCTL_DEV;

    /* 2. набір: оголошуємо, за що беремо відповідальність.
          хвіст структури мусить бути нульовий — на ньому тримається
          сумісність із ядром, що знає менше полів                      */
    struct landlock_ruleset_attr attr = { .handled_access_fs = handled };

    ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof attr, 0);
    if (ruleset_fd < 0) {
        perror("sandbox: landlock_create_ruleset");
        return 1;
    }

    /* 3. правила — з тією самою вкороченою маскою */
    if (add_list(ruleset_fd, ex, ACCESS_X  & handled) != 0 ||
        add_list(ruleset_fd, ro, ACCESS_RO & handled) != 0 ||
        add_list(ruleset_fd, rw, ACCESS_RW & handled) != 0)
        return 1;

    /* 4. замок; порядок обов'язковий — без no_new_privs буде EPERM */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("sandbox: PR_SET_NO_NEW_PRIVS");
        return 1;
    }
    if (syscall(__NR_landlock_restrict_self, ruleset_fd, 0) != 0) {
        perror("sandbox: landlock_restrict_self");
        return 1;
    }
    close(ruleset_fd);

    /* 5. з цієї миті назад дороги нема */
    execvp(argv[i], &argv[i]);
    fprintf(stderr, "sandbox: %s: %s\n", argv[i], strerror(errno));
    return 127;
}
```

Три місця тут варто прочитати повільно.

Номери `444`–`446` вписані руками, бо бібліотека C обгорток для цих викликів не дає й, найпевніше, не дасть: `syscall()` — єдиний спосіб. Значення однакові на всіх звичних архітектурах, тож `#ifndef` тут страхує не від чужого процесора, а від заголовків, старіших за Landlock.

Структуру `attr` обов'язково ініціалізувати з нулями — і саме тому вона оголошена присвоєнням, а не порожньою. Ядро дивиться на переданий розмір: більший за свій воно приймає, лише поки зайвий хвіст нульовий. Локальна змінна без ініціалізації несе сміття зі стека — і виклик відмовить на ядрі, яке просто не знає новіших полів.

Неіснуючий шлях у списку — помилка, а не мовчазний пропуск. Спокуса пропустити його велика (список системних каталогів у різних дистрибутивах різний), але друкарська помилка в такому списку тихо звужує пісочницю до неробочої, і шукати причину доведеться в чужій програмі, а не у своїй.

## Зібрати й перевірити

```
$ cc -Wall -O2 -o sandbox sandbox.c
$ mkdir -p /tmp/box/sub

$ ./sandbox -x /usr/bin:/usr/lib:/usr/lib64:/lib64 \
            -r /etc/hostname -w /tmp/box -- cat /etc/hostname
thinkpad

$ ./sandbox -x /usr/bin:/usr/lib:/usr/lib64:/lib64 \
            -r /etc/hostname -w /tmp/box -- cat ~/.ssh/id_ed25519
cat: /home/andrij/.ssh/id_ed25519: Permission denied

$ cat ~/.ssh/id_ed25519 | head -1
-----BEGIN OPENSSH PRIVATE KEY-----
```

Останні два рядки й є вся суть: файл ваш, класичні права його відкривають, і поза пісочницею він читається — а всередині ні. Правило на `/etc/hostname` показує заразом, що правило кладуть не лише на каталог: об'єктом може бути й окремий файл.

Запис перевіряється так само з двох боків:

```
$ ./sandbox … -w /tmp/box -- cp /etc/hostname /tmp/box/name
$ ./sandbox … -w /tmp/box -- cp /etc/hostname /tmp/name
cp: cannot create regular file '/tmp/name': Permission denied
```

Створити файл поруч, у тому самому `/tmp`, не вийшло: `MAKE_REG` дали лише на `/tmp/box`, а на `/tmp` — нічого.

Межу цієї пісочниці варто назвати одразу, щоб не покластися на неї більше, ніж вона тримає. Обмежені тут самі файли: команда всередині так само відкриє мережеве з'єднання, надішле сигнал сусідньому процесові й перегляне `/proc`. Метадані теж поза грою — `stat` покаже розмір, права й час зміни будь-чого, куди дістають класичні права, навіть якщо вміст уже не читається. Замикати порти й сигнали той самий виклик теж уміє, але то інші поля тієї самої структури, і в наш інструмент вони не потрапили.

## Що насправді відкриває `execvp`

![Ліворуч ланцюжок із шести кроків згори вниз, кожен із зазначенням потрібного права. Оболонка знайшла cat по PATH і покликала execvp — прав не треба. Ядро відкриває /usr/bin/cat — потрібні EXECUTE і READ_FILE. У ELF записаний інтерпретатор, тож ядро відкриває і /lib64/ld-linux — знову EXECUTE і READ_FILE. Динамічний завантажувач відкриває /etc/ld.so.cache — READ_FILE, і тут є запасний шлях. Динамічний завантажувач відкриває libc.so.6 у /usr/lib — READ_FILE. Аж тепер починається main. Праворуч чотири пояснення. Перше: нема правила на /lib64 — execve падає ще до першого рядка програми з повідомленням cannot execute Permission denied, бо інтерпретатора не вдалося відкрити. Друге: нема правила на /usr/lib — програма таки стартує й гине пізніше з повідомленням про libc.so.6 cannot open shared object file Permission denied і кодом виходу 127. Третє: бібліотеки відкривають звичайним читанням, тож їм досить READ_FILE, а EXECUTE потрібне лише там, звідки запускає саме ядро — програма та її інтерпретатор. Четверте: діагностика через strace з фільтром на openat показує рівно те відкриття, що впало](img/exec-chain.svg)

*Один `execvp` — це щонайменше чотири відкриття, і три з них робить не ваша програма.*

Забутий каталог із бібліотеками — найчастіша причина, чому «пісочниця не працює, хоча всі потрібні теки перелічені». Перелічені теки з **даними**; про [динамічний завантажувач](book:unix-linux/dynamic-loader) при цьому не згадав ніхто, бо поза пісочницею його не видно ніколи.

Ламається це у двох різних місцях, і виглядає теж по-різному. Файл самої програми та її інтерпретатор відкриває ядро, і відкриває **на виконання**: тут потрібні `EXECUTE` і `READ_FILE` разом, бо одне відкриття рахується як обидва. Не давши їх, ви не дістанете навіть першого рядка програми — `execve` поверне `EACCES`. А спільні бібліотеки завантажувач відкриває вже звичайним читанням, як дані, і їм досить самого `READ_FILE`; забувши цей каталог, ви побачите старт, а тоді смерть із `libc.so.6: cannot open shared object file`.

Потрібний перелік не треба вгадувати: `ldd /usr/bin/cat` показує й самого інтерпретатора, й кожну бібліотеку з повним шляхом.

## Пастки

**Правило, дане надто високо.** Найпоширеніший спосіб «полагодити» пісочницю — дописати `-r /`, поки не запрацює. Після цього вона й далі боронить від запису, але від витоку не боронить нічим: на читання віддано геть усе, до чого дотягуються ваші класичні права, — ключі, історія оболонки, чужі проєкти. Виправити це звуженням не вийде, бо правила в Landlock бувають лише дозвільні: сказати «`/home`, крім `.ssh`» немає чим. Перелічуйте робочі каталоги, а не їхніх батьків.

**Дескриптори, відкриті до замка.** Ось та сама пісочниця без жодного правила на домівку:

```
$ ./sandbox -x /usr/bin:/usr/lib:/usr/lib64:/lib64 -- cat < ~/.ssh/id_ed25519
-----BEGIN OPENSSH PRIVATE KEY-----
…
```

Ключ витік. Файл відкрила оболонка — до того, як `sandbox` узагалі почав працювати, — і [дескриптор пережив заміну образу](book:unix-linux/exec-semantics), як переживає її завжди. Судити тут уже нічого: перевірка стоїть на **відкритті**, а воно сталося ще до пісочниці. Тому пісочниця настільки тісна, наскільки скупий набір [дескрипторів, які ви в неї передали](book:unix-linux/open-file-description): перед замком варто глянути на `ls -l /proc/self/fd` і позакривати зайве. Та сама властивість, до речі, — головний робочий прийом: усе потрібне відкривають наперед, а замикаються після.

**`EXDEV` замість `EACCES`.** Перенесення файлу між каталогами й [жорстке посилання](book:unix-linux/hard-and-symbolic-links) — операції над двома ієрархіями одразу, і без права `REFER` вони заборонені. Наша програма це право роздає разом із рештою запису, але живе воно лише з ABI 2 — на давнішому ядрі рядок `if (abi < 2)` прибирає його зовсім, і тоді відмовляє навіть перенесення всередині самої пісочниці:

```
$ ./sandbox … -w /tmp/box -- ln /tmp/box/name /tmp/box/sub/link
ln: failed to create hard link '/tmp/box/sub/link'
    => '/tmp/box/name': Invalid cross-device link
```

`EXDEV` — це «різні файлові системи», код, який програми давно вміють обробляти: `mv`, побачивши його, мовчки копіює й вилучає. Через це наслідок такої відмови буває не помилкою, а дивною повільністю на великих файлах або зламаним інструментом, що будує дерево з жорстких посилань. І навіть із `REFER` `EXDEV` лишається можливим: ядро відмовить, якщо в новому місці файл дістав би більше прав, ніж мав у старому.

**Замок вішається на потік, а не на процес.** `landlock_restrict_self` обмежує той потік, який його покликав. Нашій обгортці це байдуже — до `execvp` вона однопотокова. А от коли той самий код вставляють усередину готової програми, яка вже підняла пул робітників, обмеженим виявиться один потік, решта працюватиме як раніше, і пісочниці фактично не буде. Прапорець `LANDLOCK_RESTRICT_SELF_TSYNC`, що накладає домен на всі потоки одразу, з'явився аж у восьмій версії ABI, тож правило лишається простим: замикатися до першого `pthread_create`.

**Список правил старіє разом із програмою.** Найдешевший спосіб зібрати чесний перелік — подивитися, що програма відкриває насправді, [простеживши її системні виклики](book:unix-linux/syscall-tracing):

```
$ strace -f -e trace=openat -o /tmp/tr ./real-command
$ grep -o '"[^"]*"' /tmp/tr | sort -u
```

Отриманий перелік — це відкриття **цього** запуску: рідкісна гілка коду, аварійний журнал чи запасний шлях у ньому не з'являться. Тому список звужують поступово й перевіряють на тих самих випадках, на яких перевіряють саму програму, — інакше пісочниця, зібрана за одним успішним прогоном, розсиплеться першої ж нештатної хвилини.
