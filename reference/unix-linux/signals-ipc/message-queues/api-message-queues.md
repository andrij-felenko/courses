# 📋 Інтерфейс черг повідомлень

Це повний контракт обох родин черг повідомлень — сигнатури, поля структур, прапорці, коди помилок і межі, за які ядро не пустить, — потрібний тому, що спільного між родинами немає жодного виклику, жодної структури й жодного простору імен: знання про одну про другу не каже нічого. Значення звірені з man7.org для Linux; де поведінка є розширенням Linux, а не вимогою POSIX, це позначено окремо.

Спершу орієнтир. Рядок таблиці означає однаковий **намір**, а не однакову семантику: `msgctl(IPC_SET)` і `mq_setattr` стоять поряд лише тому, що обидва звуться «змінити параметри» — насправді перший міняє стелю черги, а другий не міняє нічого, крім режиму блокування.

| Намір | System V | POSIX |
|---|---|---|
| створити або відкрити | `msgget` | `mq_open` |
| відправити | `msgsnd` | `mq_send`, `mq_timedsend` |
| прийняти | `msgrcv` | `mq_receive`, `mq_timedreceive` |
| прочитати стан | `msgctl(IPC_STAT)` | `mq_getattr` |
| змінити параметри | `msgctl(IPC_SET)` | `mq_setattr` (лише `O_NONBLOCK`) |
| відпустити хендл | — (ідентифікатор не закривають) | `mq_close` |
| знищити об'єкт | `msgctl(IPC_RMID)` | `mq_unlink` |
| сповістити про появу | — | `mq_notify` |
| з оболонки | `ipcs -q`, `ipcrm -q` | `ls`, `cat`, `rm` у `/dev/mqueue` |
| збирання | нічого окремо | `-lrt` (від glibc 2.34 librt влито в libc, порожній стаб лишили заради сумісності) |

## System V

```c
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>

int     msgget(key_t key, int msgflg);
int     msgsnd(int msqid, const void *msgp, size_t msgsz, int msgflg);
ssize_t msgrcv(int msqid, void *msgp, size_t msgsz, long msgtyp, int msgflg);
int     msgctl(int msqid, int op, struct msqid_ds *buf);

key_t   ftok(const char *path, int proj_id);
```

### Ключ і створення

`msgget` повертає не дескриптор, а **ідентифікатор** — ціле число, чинне в межах простору імен IPC. Різниця не термінологічна: ідентифікатор не закривають (парного виклику до `msgget` просто нема), він не займає місця в таблиці відкритих файлів, не видно його в `/proc/<pid>/fd`, він переживає `execve` і не має жодного стосунку до `select` чи `epoll`. Знайти чужу чергу можна лише за ключем, і ключ береться одним із трьох способів:

- **`IPC_PRIVATE`** (значення 0) — щоразу створює новий об'єкт без ключа. Знайти його ззовні неможливо: ідентифікатор передають самі — успадкуванням через `fork`, аргументом, файлом.
- **Стала в коді** — обидві сторони просто домовилися про число.
- **`ftok(path, proj_id)`** — зліплює ключ із молодших 8 бітів `proj_id`, молодших 16 бітів номера inode і молодших 8 бітів номера пристрою. Файл мусить існувати й бути доступним, `proj_id` — ненульовим. Унікальності стандарт не обіцяє: два файли на різних пристроях легко дають однаковий ключ, а перевстановлення пакета міняє inode — і ключ мовчки стає іншим.

Молодші 9 бітів `msgflg` — права доступу в тому самому форматі, що й аргумент `mode` в `open`; біти виконання не вживаються ([біти прав](book:unix-linux/permission-bits) — трійки rwx для власника, групи й решти та порядок, у якому ядро їх перевіряє). Решта прапорців:

| Прапорець | Дія |
|---|---|
| `IPC_CREAT` | створити, якщо за ключем нічого нема; інакше — просто відкрити наявне |
| `IPC_CREAT \| IPC_EXCL` | створити або впасти з `EEXIST`, якщо об'єкт уже є |
| без `IPC_CREAT` | лише відкрити наявне; нема — `ENOENT` |

Помилки `msgget`: `EACCES` (нема прав і нема `CAP_IPC_OWNER`), `EEXIST`, `ENOENT`, `ENOMEM`, `ENOSPC` (уперлися в `MSGMNI`).

Нова черга стартує так: `msg_perm.cuid`/`uid` — з ефективного UID, `msg_perm.cgid`/`gid` — з ефективного GID, `mode` — молодші 9 бітів `msgflg`, `msg_qnum`, `msg_lspid`, `msg_lrpid`, `msg_stime`, `msg_rtime` — нулі, `msg_ctime` — поточний час, `msg_qbytes` — системне `MSGMNB`.

### Передача

```c
struct msgbuf {
    long mtype;     /* тип, СУВОРО додатний */
    char mtext[1];  /* тіло; на практиці описують власну структуру */
};
```

`msgsz` — довжина **тіла**, без поля `mtype` (а воно завширшки з `long`, тобто різне на 32- і 64-бітних машинах). `msgsnd` повертає 0, `msgrcv` — скільки байтів справді скопійовано в `mtext`.

| `msgtyp` у `msgrcv` | Що буде взято |
|---|---|
| `0` | перше повідомлення в черзі, хай який у нього тип |
| `> 0` | перше повідомлення саме цього типу |
| `< 0` | перше повідомлення з **найменшим** типом, що не перевищує модуля `msgtyp` |

| `msgflg` | Дія |
|---|---|
| `IPC_NOWAIT` | не блокуватися: `msgsnd` падає з `EAGAIN`, `msgrcv` — з `ENOMSG` |
| `MSG_NOERROR` | `msgrcv`: обрізати тіло до `msgsz` замість `E2BIG`; відрізане пропадає безслідно |
| `MSG_EXCEPT` | `msgrcv` при `msgtyp > 0`: узяти перше повідомлення з **іншим** типом (Linux) |
| `MSG_COPY` | `msgrcv`: неруйнівно скопіювати повідомлення, що стоїть у черзі на позиції `msgtyp` (нумерація з нуля), не знімаючи його. Лише разом з `IPC_NOWAIT`, несумісне з `MSG_EXCEPT`; від Linux 3.8 і лише при `CONFIG_CHECKPOINT_RESTORE` |

Успішний `msgsnd` записує в `msg_lspid` свій PID, збільшує `msg_qnum` і оновлює `msg_stime`; успішний `msgrcv` — `msg_lrpid`, зменшує `msg_qnum` і оновлює `msg_rtime`.

| Помилка | Коли |
|---|---|
| `E2BIG` | `msgrcv`: тіло довше за `msgsz`, `MSG_NOERROR` не задано — повідомлення лишається в черзі |
| `EAGAIN` | `msgsnd`: черга заповнена (за `msg_qbytes`) і задано `IPC_NOWAIT` |
| `ENOMSG` | `msgrcv`: нічого не підходить під `msgtyp`, задано `IPC_NOWAIT` |
| `EIDRM` | чергу знищили через `IPC_RMID`, поки виклик спав |
| `EINTR` | сон перервав обробник сигналу |
| `EINVAL` | недійсний `msqid`, `mtype < 1` або `msgsz` за межами `MSGMAX` |
| `EACCES` | нема права запису (`msgsnd`) чи читання (`msgrcv`) |
| `ENOMEM` | ядру бракує пам'яті під копію повідомлення |
| `EFAULT` | `msgp` вказує поза доступною пам'яттю |

`EINTR` тут має неочевидну властивість: **`msgsnd` і `msgrcv` не перезапускаються ніколи**, хай як виставлено `SA_RESTART` ([EINTR і перезапуск викликів](book:unix-linux/eintr-and-restart) — які виклики ядро повторює саме після обробника сигналу, а які повертають помилку завжди). Цикл повтору доводиться писати руками.

### Керування

```c
struct msqid_ds {
    struct ipc_perm msg_perm;   /* власник і права */
    time_t          msg_stime;  /* час останнього msgsnd */
    time_t          msg_rtime;  /* час останнього msgrcv */
    time_t          msg_ctime;  /* створення або останньої зміни */
    unsigned long   msg_cbytes; /* байтів у черзі зараз */
    msgqnum_t       msg_qnum;   /* повідомлень у черзі зараз */
    msglen_t        msg_qbytes; /* стеля черги в байтах */
    pid_t           msg_lspid;  /* PID останнього msgsnd */
    pid_t           msg_lrpid;  /* PID останнього msgrcv */
};

struct ipc_perm {
    key_t          __key;  /* ключ, переданий у msgget */
    uid_t          uid;    /* власник (змінюваний) */
    gid_t          gid;    /* група власника (змінювана) */
    uid_t          cuid;   /* творець */
    gid_t          cgid;   /* група творця */
    unsigned short mode;   /* права (змінювані) */
    unsigned short __seq;  /* лічильник поколінь ідентифікатора */
};
```

| `op` | Дія |
|---|---|
| `IPC_STAT` | скопіювати `msqid_ds` у `buf`; треба право читання |
| `IPC_SET` | записати з `buf` **лише** `msg_qbytes`, `msg_perm.uid`, `msg_perm.gid` і молодші 9 бітів `msg_perm.mode`; оновлює `msg_ctime` |
| `IPC_RMID` | негайно знищити чергу разом із вмістом; усі, хто спав у `msgsnd`/`msgrcv`, прокидаються з `EIDRM`. `buf` ігнорується |
| `IPC_INFO`, `MSG_INFO` | (Linux) системні межі та поточне споживання у `struct msginfo` |
| `MSG_STAT`, `MSG_STAT_ANY` | (Linux) як `IPC_STAT`, але `msqid` — індекс у внутрішньому масиві ядра; саме так `ipcs` обходить усе підряд. `MSG_STAT_ANY` (від Linux 4.17) не перевіряє прав |

`IPC_SET` і `IPC_RMID` дозволені власникові (`msg_perm.uid`), творцеві (`msg_perm.cuid`) або привілейованому процесові. Підняти `msg_qbytes` вище системного `MSGMNB` можна лише з `CAP_SYS_RESOURCE` ([можливості процесу](book:unix-linux/capabilities) — розщеплення всесилля root на окремі дозволи, кожен з яких видається незалежно).

Помилки `msgctl`: `EACCES`, `EFAULT`, `EIDRM`, `EINVAL`, `EPERM`.

### З оболонки

```
ipcs -q                # перелік черг: ключ, msqid, власник, права, зайняті байти, повідомлення
ipcs -q -i 32768       # усе про одну чергу, включно з msg_lspid і msg_lrpid
ipcs -q -l             # чинні межі: MSGMNI, MSGMAX, MSGMNB
ipcs -q -t             # часи msg_stime, msg_rtime, msg_ctime
ipcrm -q 32768         # знищити за ідентифікатором (те саме, що msgctl IPC_RMID)
ipcrm -Q 0x0102abcd    # знищити за ключем
```

## POSIX

```c
#include <fcntl.h>      /* сталі O_* */
#include <sys/stat.h>   /* сталі режиму */
#include <mqueue.h>

mqd_t   mq_open(const char *name, int oflag);
mqd_t   mq_open(const char *name, int oflag, mode_t mode, struct mq_attr *attr);
int     mq_send(mqd_t mqdes, const char *msg_ptr, size_t msg_len, unsigned msg_prio);
ssize_t mq_receive(mqd_t mqdes, char *msg_ptr, size_t msg_len, unsigned *msg_prio);
int     mq_timedsend(mqd_t mqdes, const char *msg_ptr, size_t msg_len,
                     unsigned msg_prio, const struct timespec *abs_timeout);
ssize_t mq_timedreceive(mqd_t mqdes, char *msg_ptr, size_t msg_len,
                        unsigned *msg_prio, const struct timespec *abs_timeout);
int     mq_getattr(mqd_t mqdes, struct mq_attr *attr);
int     mq_setattr(mqd_t mqdes, const struct mq_attr *newattr, struct mq_attr *oldattr);
int     mq_notify(mqd_t mqdes, const struct sigevent *sevp);
int     mq_close(mqd_t mqdes);
int     mq_unlink(const char *name);
```

### Ім'я й відкриття

Ім'я має єдину чинну форму: скісна риска, а за нею від одного до `NAME_MAX` (255) символів **без** скісних рисок. Різні порушення дають різні помилки: зайві риски всередині — `EACCES`, сама лише `/` — `ENOENT`, решта викривлень — `EINVAL`.

Повертається `mqd_t`, і на Linux це справжній файловий дескриптор — звідси в переліку помилок `mq_open` беруться `EMFILE` і `ENFILE`, яких у System V бути не могло: черга витрачає той самий ресурс, що й відкритий файл, і рахується в `RLIMIT_NOFILE`. Стандарт цього не вимагає, тож арифметика з `mqd_t` як з числом непортативна.

| `oflag` | Дія |
|---|---|
| рівно один із `O_RDONLY`, `O_WRONLY`, `O_RDWR` | напрямок; обов'язковий |
| `O_CREAT` | створити, якщо нема; вмикає аргументи `mode` й `attr` |
| `O_EXCL` | разом з `O_CREAT` — впасти з `EEXIST`, якщо черга вже існує |
| `O_NONBLOCK` | `mq_send` і `mq_receive` не сплять, а повертають `EAGAIN` |
| `O_CLOEXEC` | закрити дескриптор при `execve` (Linux від 2.6.26) |

```c
struct mq_attr {
    long mq_flags;    /* 0 або O_NONBLOCK; mq_open ігнорує */
    long mq_maxmsg;   /* скільки повідомлень уміщає черга */
    long mq_msgsize;  /* стеля довжини ОДНОГО повідомлення */
    long mq_curmsgs;  /* скільки лежить зараз; mq_open ігнорує */
};
```

`attr` беруть до уваги **лише в мить фактичного створення**. Якщо черга вже існує, поля тихо ігноруються, і процес дістає чужу геометрію. `attr == NULL` при створенні означає типові `msg_default` × `msgsize_default`.

### Передача

- `msg_len` у `mq_send` мусить бути **не більшим** за `mq_msgsize` черги, інакше `EMSGSIZE`.
- `msg_len` у `mq_receive` мусить бути **не меншим** за `mq_msgsize`, інакше теж `EMSGSIZE`: буфер приймача міряють за геометрією черги, а не за довжиною того, що в ній лежить. Повертається справжня довжина повідомлення.
- `mq_receive` знімає найстаріше з-поміж найвищих за пріоритетом. Вибирати нічого не можна.
- `msg_prio` — від 0 до `sysconf(_SC_MQ_PRIO_MAX) - 1` (на Linux 0…32767); у прийманні це **вихідний** аргумент, дозволено `NULL`.
- `abs_timeout` — абсолютна мить за годинником `CLOCK_REALTIME`, а не тривалість. Уже минула мить дає негайний `ETIMEDOUT`.
- На відміну від System V, ці виклики **перезапускаються**, якщо обробник сигналу поставлено з `SA_RESTART`.

| Помилка | Коли |
|---|---|
| `EMSGSIZE` | повідомлення довше за `mq_msgsize` (надсилання) або буфер коротший за `mq_msgsize` (приймання) |
| `EAGAIN` | черга повна (надсилання) чи порожня (приймання) і чинний `O_NONBLOCK` |
| `ETIMEDOUT` | `abs_timeout` минув, а місця чи повідомлення так і не з'явилося |
| `EBADF` | недійсний `mqdes` або черга відкрита не в той бік |
| `EINTR` | виклик перервав обробник сигналу |
| `EINVAL` | зіпсований `abs_timeout` (від'ємні поля або `tv_nsec` поза 0…999999999) |

Помилки `mq_open`: `EACCES`, `EEXIST`, `EINVAL`, `EMFILE`, `ENAMETOOLONG`, `ENFILE`, `ENOENT`, `ENOMEM`, `ENOSPC` (найімовірніше вперлися в `queues_max`).

### Атрибути й сповіщення

`mq_getattr` заповнює всі чотири поля, зокрема `mq_curmsgs`. `mq_setattr` міняє **тільки** `O_NONBLOCK` у `mq_flags`; решту полів у `newattr` ігнорує мовчки, і геометрію наявної черги змінити не може ніхто. Ненульовий `oldattr` віддає знімок атрибутів до зміни. Помилки — `EBADF` і `EINVAL` (у `mq_flags` є щось, крім `O_NONBLOCK`).

```c
struct sigevent {
    int    sigev_notify;                         /* SIGEV_NONE | SIGEV_SIGNAL | SIGEV_THREAD */
    int    sigev_signo;                          /* номер сигналу для SIGEV_SIGNAL */
    union  sigval sigev_value;                   /* дані, що прийдуть у si_value */
    void (*sigev_notify_function)(union sigval); /* для SIGEV_THREAD */
    void  *sigev_notify_attributes;              /* pthread_attr_t * або NULL */
};
```

| `sigev_notify` | Що робить ядро |
|---|---|
| `SIGEV_NONE` | реєструє процес і не сповіщає нічим — місце зайняте, інші дістануть `EBUSY` |
| `SIGEV_SIGNAL` | шле `sigev_signo`; у `siginfo_t` приходить `si_code == SI_MESGQ`, `si_pid` і `si_uid` відправника та `si_value` ([реальночасові сигнали](book:unix-linux/realtime-signals) — черга сигналів і структура `siginfo_t`, з якої обробник дізнається деталі події) |
| `SIGEV_THREAD` | викликає `sigev_notify_function` як стартову функцію нового потоку; glibc робить це в просторі користувача через сирий netlink-сокет і власний допоміжний потік |

`sevp == NULL` знімає власну реєстрацію. Правила реєстрації: реєстрант **один** на чергу (друга спроба — `EBUSY`), сповіщення **одноразове** (після спрацювання реєстрації вже нема) і **по краю** — лише коли повідомлення надходить у порожню чергу й ніхто в цю мить не спить у `mq_receive`. Помилки: `EBADF`, `EBUSY`, `EINVAL`, `ENOMEM`.

`mq_close` відпускає дескриптор і заразом знімає реєстрацію на сповіщення, якщо вона була саме через цей дескриптор. `mq_unlink` прибирає ім'я негайно, а сам об'єкт зникає, коли закриється останній дескриптор; помилки — `EACCES`, `ENAMETOOLONG`, `ENOENT`.

### Файлова система

```
mkdir /dev/mqueue
mount -t mqueue none /dev/mqueue
```

На каталозі автоматично ставиться sticky-біт. Після монтування `ls` перелічує черги, `chmod` міняє права, `rm` рівносильне `mq_unlink`, а читання файла черги показує її стан:

```
QSIZE:129   NOTIFY:0   SIGNO:10   NOTIFY_PID:8260
```

`QSIZE` — байтів даних у всіх повідомленнях черги; `NOTIFY_PID` — PID зареєстрованого на сповіщення (0, якщо нікого); `NOTIFY` — спосіб: 0 = `SIGEV_SIGNAL`, 1 = `SIGEV_NONE`, 2 = `SIGEV_THREAD`; `SIGNO` — номер сигналу для `SIGEV_SIGNAL`.

## Межі

| System V | Типово | Що обмежує | Тюнер |
|---|---|---|---|
| `MSGMAX` | 8192 | тіло одного повідомлення, байтів | `/proc/sys/kernel/msgmax` |
| `MSGMNB` | 16384 | початкове `msg_qbytes` нової черги | `/proc/sys/kernel/msgmnb` |
| `MSGMNI` | 32000 (від Linux 3.19) | скільки черг у просторі імен IPC | `/proc/sys/kernel/msgmni` |

Типовий `MSGMAX` рівно вдвічі менший за `MSGMNB` — тож у порожню чергу гарантовано влазять принаймні два найбільші повідомлення.

| POSIX, `/proc/sys/fs/mqueue/` | Типово | Що обмежує |
|---|---|---|
| `msg_max` | 10 (мінімум 1) | стелю `mq_maxmsg`; тверда межа `HARD_MSGMAX` = 65536 від Linux 3.5 |
| `msgsize_max` | 8192 (мінімум 128) | стелю `mq_msgsize`; тверда межа `HARD_MSGSIZEMAX` = 16777216 (16 МіБ) від Linux 3.5 |
| `msg_default` | 10 | `mq_maxmsg`, коли `attr == NULL` (від Linux 3.5) |
| `msgsize_default` | 8192 | `mq_msgsize`, коли `attr == NULL` (від Linux 3.5) |
| `queues_max` | 256 | скільки черг у просторі імен |

`msg_max` і `msgsize_max` стримують непривілейований процес; із `CAP_SYS_RESOURCE` їх можна перевищити, але тверді межі лишаються твердими. Усі ці лічильники окремі в кожному просторі імен IPC ([простори імен](book:unix-linux/namespaces) — ядро тримає кілька незалежних наборів однакових ресурсів, і процес бачить лише свій).

Крім системних стель є ще й особиста — `RLIMIT_MSGQUEUE` на **реального** користувача ([обмеження ресурсів](book:unix-linux/resource-limits) — м'які й тверді ліміти процесу, які показує `ulimit` і читає `getrlimit`). Обліковують не зайняте, а обіцяне при створенні:

```
байтів = mq_maxmsg · sizeof(struct msg_msg)
       + min(mq_maxmsg, MQ_PRIO_MAX) · sizeof(struct posix_msg_tree_node)   ← службове
       + mq_maxmsg · mq_msgsize                                             ← дані

типова стеля (ulimit -q) = 819200 байтів
```

Службовий доданок стоїть тут не заради точності, а щоб ніхто не створив мільйон нульових повідомлень задарма; чинний він від Linux 3.5, до того був простіший `mq_maxmsg · sizeof(struct msg_msg *)`. Перевищення ліміту `mq_open` повертає як **`EMFILE`** — назва оманлива, до кількості відкритих дескрипторів це не має жодного стосунку.
