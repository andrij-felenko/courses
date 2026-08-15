# ⚙️ Маленький монітор і робітник: кістяк, який компілюється

Це працездатний кістяк пари «привілейований монітор + непривілейований робітник» на C — щоб побачити не ідею поділу, а те, з чого він насправді складається: протокол сталого розміру, автомат станів у моніторі, клітка довкола робітника і передача вже відкритого [дескриптора](book:unix-linux/file-descriptor) через сокет. Домен тут — самі системні виклики, тому мова одна.

Задача навмисно маленька, але містить обидві звичні потреби. Демон обслуговує з'єднання; розбирає мережевий протокол робітник, а привілеїв йому потрібно рівно два: **перевірити пароль** за закритим файлом тіней і **дістати відкритий журнал сесії**, який лежить у теці, куди йому не можна. Обидві дії виконує монітор, назовні віддаючи «так/ні» і один дескриптор.

Збирається так: `cc -O2 -Wall -o privsepd privsepd.c -lcrypt`. Потрібен Linux 4.14 або новіший (через `SECCOMP_RET_KILL_PROCESS`) і x86-64 — число архітектури у фільтрі прив'язане до платформи. Блоки нижче йдуть у порядку читання й у файлі склеюються так само.

## Протокол: три числа й жодного імені файлу

```c
#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <crypt.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <shadow.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define WORKER_UID 4242u        /* обліковка тільки для цього демона */
#define WORKER_GID 4242u
#define MAX_USER   32
#define MAX_PW     128

enum { OP_AUTH = 1, OP_LOGFD = 2 };
enum { REQ_OK = 0, REQ_EOF = 1, REQ_ERR = 2 };

struct req {                    /* сталий розмір: 172 байти, завжди */
    uint32_t op;
    uint32_t user_len;
    uint32_t pw_len;
    char     user[MAX_USER];
    char     pw[MAX_PW];
};

struct resp { uint32_t status; };   /* 0 — так, 1 — ні; більше нічого */

static void die(const char *what);
static void cage(uid_t uid, gid_t gid);
static void monitor(int sock);
static void worker(int sock);
static int  recv_req(int sock, struct req *rq);
static int  send_req(int sock, const struct req *rq);
static int  send_resp(int sock, uint32_t status, int fd);
static int  recv_resp(int sock, struct resp *rs, int *fd);
static int  pick_user(const struct req *rq, char *user, uid_t *uid, gid_t *gid);
static int  check_password(const char *user, const char *pw, uint32_t len);
static int  open_session_log(uid_t uid);

static void die(const char *what)
{
    fprintf(stderr, "privsepd: %s: %s\n", what, strerror(errno));
    _exit(70);
}
```

У запиті немає ні шляху, ні прапорців, ні номера дескриптора — нічого, чим робітник міг би обрати об'єкт. Ім'я користувача є, бо інакше монітор не знає, чий пароль перевіряти, і саме тому воно обмежене тридцятьма двома байтами й береться рівно один раз. Довжини присутні, але жодна з них нічого не виділяє: вони лише кажуть, скільки байтів у полі сталого розміру справжні, і монітор порівнює їх із розміром поля, а не вірить.

Обидві половини — це один виконуваний файл, тому про вирівнювання полів і порядок байтів думати не треба: структуру розкладає той самий компілятор. Якби робітник був окремою програмою, довелося б писати явне пакування — і саме там з'являється розбір, від якого ми втікаємо.

## Народження пари

```c
int main(void)
{
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv) != 0)
        die("socketpair");

    pid_t pid = fork();
    if (pid < 0) die("fork");

    if (pid == 0) {              /* робітник */
        close(sv[0]);
        cage(WORKER_UID, WORKER_GID);
        worker(sv[1]);
        _exit(0);
    }

    close(sv[1]);                /* монітор не тримає кінця робітника */
    monitor(sv[0]);              /* ЛИШЕ ТУТ уперше торкаємося таємниць */
    int st;
    waitpid(pid, &st, 0);
    return 0;
}
```

`SOCK_SEQPACKET` тут не примха. Потоковий сокет віддав би байти без меж, і кожен бік мусив би сам збирати повідомлення з шматків — тобто мати цикл дочитування, лічильник і перевірку, що дочитано саме стільки; це той самий розбір ворожого вводу, лише всередині монітора. Пакетний сокет [домену Unix](book:unix-linux/unix-domain-sockets) зберігає межі: одне `send` — одне `recv`, тому «частково прочитаного запиту» просто не існує, а не той розмір миттєво означає «не наш».

Ще одне видно з цього короткого `main`: `monitor()` викликано **після** `fork`. Якби файл тіней читали раніше — хай навіть у прогріву кешу, — копія хешів опинилася б у пам'яті робітника, і поділ обернувся б на декорацію.

## Клітка

```c
static void install_seccomp(void)
{
#define ALLOW(nr) \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (nr), 0, 1), \
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)

    struct sock_filter code[] = {
        /* номери викликів мають сенс лише разом з архітектурою */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        ALLOW(__NR_read),    ALLOW(__NR_write),
        ALLOW(__NR_recvmsg), ALLOW(__NR_sendmsg),
        ALLOW(__NR_sendto),  /* glibc-івський send() на x86-64 — це sendto */
        ALLOW(__NR_close),   ALLOW(__NR_rt_sigreturn),
        ALLOW(__NR_exit_group),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };
#undef ALLOW
    struct sock_fprog prog = { .len = sizeof code / sizeof code[0], .filter = code };
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog, 0, 0) != 0)
        die("seccomp");
}

static void cage(uid_t uid, gid_t gid)
{
    /* 1. Клітку ставимо, поки ще є права її поставити. */
    if (chroot("/var/empty") != 0 || chdir("/") != 0) die("chroot");

    /* 2. Обмежувальний набір знімаємо, доки в дії ще є CAP_SETPCAP. */
    for (int cap = 0; cap <= 63; cap++)
        prctl(PR_CAPBSET_DROP, cap, 0, 0, 0);   /* EINVAL на неіснуючих — очікувано */
    prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0);

    /* 3. Групи — ПЕРЕД uid: без root setgroups уже не спрацює. */
    if (setgroups(0, NULL) != 0)      die("setgroups");
    if (setresgid(gid, gid, gid) != 0) die("setresgid");
    if (setresuid(uid, uid, uid) != 0) die("setresuid");

    /* 4. Не вірити, а перевірити: повернення має бути неможливим. */
    if (setresuid(0, 0, 0) == 0) { errno = 0; die("uid still root"); }
    uid_t r, e, s;
    if (getresuid(&r, &e, &s) != 0 || r != uid || e != uid || s != uid) die("uid");

    /* 5. Жодного нового привілею навіть через чужий setuid-файл. */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) die("no_new_privs");
    install_seccomp();
}
```

Порядок тут не стилістичний, а обов'язковий, і кожен рядок стоїть на своєму місці з конкретної причини: [`chroot`](book:unix-linux/chroot) і зняття обмежувального набору [можливостей](book:unix-linux/capabilities) вимагають привілею, тому мусять статися до його втрати; `setgroups` — теж, інакше додаткові групи лишаться при робітникові назавжди. Порожня тека `/var/empty` — не вигадка прикладу: саме її для цього тримає `sshd`.

Перевірка «спробуй повернутися» коштує один системний виклик і ловить цілий клас помилок — від переплутаного порядку `setresgid`/`setresuid` до забутого суперкористувача, що лишився збереженим ідентифікатором.

Фільтр [seccomp](book:unix-linux/seccomp-filtering) з восьми дозволів виглядає підозріло коротким, і це чесна ознака: після клітки робітник у цьому кістяку вміє лише читати, писати й розмовляти сокетом. Справжній перелік збирають трасуванням, і в ньому неодмінно знайдеться щось несподіване — як `sendto`, у який перетворюється невинний `send()`.

## Цикл монітора

```c
static void monitor(int sock)
{
    enum { ST_HELLO, ST_AUTHED, ST_SPENT } st = ST_HELLO;
    int tries = 0;
    char user[MAX_USER] = "";
    uid_t uid = 0; gid_t gid = 0;
    struct req rq;

    for (;;) {
        if (recv_req(sock, &rq) != REQ_OK) break;   /* EOF або будь-яка дивина */

        if (rq.op == OP_AUTH) {
            if (st != ST_HELLO || ++tries > 3) break;
            if (!pick_user(&rq, user, &uid, &gid)) { send_resp(sock, 1, -1); continue; }
            if (check_password(user, rq.pw, rq.pw_len)) {
                st = ST_AUTHED;
                send_resp(sock, 0, -1);
            } else {
                send_resp(sock, 1, -1);
            }
        } else if (rq.op == OP_LOGFD) {
            if (st != ST_AUTHED) break;             /* до автентифікації — ні */
            int fd = open_session_log(uid);
            if (fd < 0) { send_resp(sock, 1, -1); continue; }
            send_resp(sock, 0, fd);
            close(fd);                              /* своя копія моніторові не потрібна */
            st = ST_SPENT;                          /* удруге теж ні */
        } else {
            break;                                  /* невідома дія — розмова закінчена */
        }
    }
    close(sock);
}
```

Автомат тут — не оздоба, а половина захисту. Три стани дають рівно те, чого не дає перелік перевірок усередині обробників: **`OP_LOGFD` фізично не має гілки, досяжної зі стану `ST_HELLO`**. Робітник може слати запити в будь-якому порядку скільки завгодно разів — жодна послідовність не приведе його до дескриптора без успішної відповіді на пароль. Лічильник спроб і перехід `ST_SPENT` замикають те саме з іншого боку: канал не перетворюється ні на підбирач паролів, ні на роздавач дескрипторів.

Будь-яка несподіванка тут закінчується виходом із циклу, а не спробою «оговтатися». Це навмисно: розірвана сесія коштує нападникові нового з'єднання, а монітор, що продовжує розмову після незрозумілого повідомлення, — це монітор, стан якого нападник щойно почав вивчати.

```c
static int recv_req(int sock, struct req *rq)
{
    struct iovec iov = { .iov_base = rq, .iov_len = sizeof *rq };
    union { char b[CMSG_SPACE(sizeof(int) * 8)]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = cm.b, .msg_controllen = sizeof cm.b };
    ssize_t n;
    do { n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC); } while (n < 0 && errno == EINTR);

    if (n == 0) return REQ_EOF;                        /* робітник помер — кінець сесії */
    if (n < 0)  return REQ_ERR;
    if (n != (ssize_t)sizeof *rq) return REQ_ERR;      /* межі зберігає SEQPACKET */
    if (msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return REQ_ERR;

    /* Робітник не має права слати дескриптори. Прийшли — закрити й розірвати. */
    int hostile = 0;
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c; c = CMSG_NXTHDR(&msg, c)) {
        hostile = 1;
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS) {
            size_t k = (c->cmsg_len - CMSG_LEN(0)) / sizeof(int);
            for (size_t i = 0; i < k; i++) {
                int fd;
                memcpy(&fd, CMSG_DATA(c) + i * sizeof(int), sizeof fd);
                close(fd);
            }
        }
    }
    return hostile ? REQ_ERR : REQ_OK;
}
```

Місце під вісім дескрипторів у моніторі, який їх не приймає, — це не марнотратство, а пастка з приманкою. Робітник, захоплений нападником, може слати дескриптори тисячами, аби вичерпати таблицю монітора; ми їх приймаємо, лічимо, закриваємо й на цьому закінчуємо сесію, замість покладатися на те, що ядро само викине непроханий вантаж.

## Передача дескриптора

```c
static int send_resp(int sock, uint32_t status, int fd)
{
    struct resp rs = { .status = status };
    struct iovec iov = { .iov_base = &rs, .iov_len = sizeof rs };
    union { char b[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1 };

    if (fd >= 0) {
        memset(cm.b, 0, sizeof cm.b);
        msg.msg_control    = cm.b;
        msg.msg_controllen = sizeof cm.b;            /* SPACE — з вирівнюванням */
        struct cmsghdr *c = CMSG_FIRSTHDR(&msg);
        c->cmsg_level = SOL_SOCKET;
        c->cmsg_type  = SCM_RIGHTS;
        c->cmsg_len   = CMSG_LEN(sizeof(int));       /* LEN — без вирівнювання */
        memcpy(CMSG_DATA(c), &fd, sizeof fd);
    }
    ssize_t n;
    do { n = sendmsg(sock, &msg, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
    return n == (ssize_t)sizeof rs ? 0 : -1;
}

static int recv_resp(int sock, struct resp *rs, int *fd)
{
    *fd = -1;
    struct iovec iov = { .iov_base = rs, .iov_len = sizeof *rs };
    union { char b[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = cm.b, .msg_controllen = sizeof cm.b };
    ssize_t n;
    do { n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC); } while (n < 0 && errno == EINTR);

    if (n != (ssize_t)sizeof *rs) return -1;         /* 0 = монітор пішов */
    if (msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return -1;

    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c; c = CMSG_NXTHDR(&msg, c)) {
        if (c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS) return -1;
        if (c->cmsg_len != CMSG_LEN(sizeof(int)))    return -1;   /* рівно один */
        memcpy(fd, CMSG_DATA(c), sizeof *fd);
    }
    return 0;
}
```

Дві довжини легко переплутати, і плата за плутанину різна. `CMSG_SPACE` — це скільки місця треба відвести в буфері з урахуванням вирівнювання; `CMSG_LEN` — скільки в цьому місці корисного. Занизити `msg_controllen` до `CMSG_LEN` при відправленні здебільшого зійде з рук, а от порахувати вручну — ні: розкладка залежить від платформи, і саме тому обидві величини існують як макроси.

Перевірки на боці приймача виглядають надмірними, поки не спитати, що станеться без кожної. Без `cmsg_level`/`cmsg_type` можна взяти за дескриптор шматок зовсім іншого допоміжного повідомлення. Без порівняння `cmsg_len` із `CMSG_LEN(sizeof(int))` прийом «одного» дескриптора мовчки візьме перший із десятка, а решта осядуть у таблиці назавжди. Без `MSG_CTRUNC` можна повірити обрізаному хвостові, у якому дескриптора вже немає, зате в буфері лишилися нулі — а нуль є чинним номером стандартного вводу.

## Робітник

```c
static int send_req(int sock, const struct req *rq)
{
    ssize_t n;
    do { n = send(sock, rq, sizeof *rq, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
    return n == (ssize_t)sizeof *rq ? 0 : -1;
}

static void worker(int sock)
{
    /* Тут живе весь розбір мережевого протоколу — тисячі рядків ворожого вводу.
       Нижче лише те, як ця частина розмовляє з монітором. */
    struct req rq = { .op = OP_AUTH, .user_len = 5, .pw_len = 6 };
    memcpy(rq.user, "alice", 5);
    memcpy(rq.pw, "secret", 6);

    struct resp rs;
    int fd = -1;
    if (send_req(sock, &rq) != 0) return;
    if (recv_resp(sock, &rs, &fd) != 0 || rs.status != 0) return;

    struct req q2 = { .op = OP_LOGFD };
    if (send_req(sock, &q2) != 0) return;
    if (recv_resp(sock, &rs, &fd) != 0 || rs.status != 0 || fd < 0) return;

    /* fd — уже відкритий журнал. Його імені робітник не знає й не дізнається. */
    (void)write(fd, "session started\n", 16);
    close(fd);
}
```

Три рядки з кінця й є весь зиск від передачі дескриптора. Робітник пише в журнал, не маючи ні шляху до нього, ні права його відкрити, ні можливості дописати в сусідній файл тієї ж теки: повноваження, яке він дістав, вказує на один конкретний уже відкритий об'єкт.

## Рішення монітора

```c
static int streq_ct(const char *a, const char *b)      /* без витоку по часу */
{
    size_t la = strlen(a), lb = strlen(b);
    unsigned diff = (unsigned)(la ^ lb);
    for (size_t i = 0; i < la && i < lb; i++)
        diff |= (unsigned)((unsigned char)a[i] ^ (unsigned char)b[i]);
    return diff == 0;
}

static int pick_user(const struct req *rq, char *user, uid_t *uid, gid_t *gid)
{
    if (user[0] != '\0') return 1;                     /* ім'я беруть ОДИН раз */
    if (rq->user_len == 0 || rq->user_len >= MAX_USER) return 0;
    for (uint32_t i = 0; i < rq->user_len; i++) {
        char c = rq->user[i];
        if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '-'))
            return 0;
    }
    memcpy(user, rq->user, rq->user_len);
    user[rq->user_len] = '\0';

    struct passwd *pw = getpwnam(user);                /* база — своя, не з повідомлення */
    if (!pw || pw->pw_uid == 0) { user[0] = '\0'; return 0; }   /* root крізь канал — ніколи */
    *uid = pw->pw_uid; *gid = pw->pw_gid;
    return 1;
}

static int check_password(const char *user, const char *pw, uint32_t len)
{
    if (len == 0 || len > MAX_PW) return 0;
    char attempt[MAX_PW + 1];
    memcpy(attempt, pw, len);
    attempt[len] = '\0';

    struct spwd *sp = getspnam(user);                  /* перший дотик до таємниці */
    int ok = 0;
    if (sp && sp->sp_pwdp) {
        char *got = crypt(attempt, sp->sp_pwdp);
        ok = got && streq_ct(got, sp->sp_pwdp);
    }
    explicit_bzero(attempt, sizeof attempt);
    return ok;                                         /* назовні йде рівно один біт */
}

static int open_session_log(uid_t uid)
{
    char path[64];
    snprintf(path, sizeof path, "/var/log/privsepd/%lu.log", (unsigned long)uid);
    return open(path, O_WRONLY | O_APPEND | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0600);
}
```

Ім'я користувача — єдине, що монітор змушений узяти з повідомлення, і тому воно проходить три сита: довжина проти розміру поля, суворий набір символів, і резолвінг через [базу користувачів](book:unix-linux/user-database-nss), яка й вирішує, чи такий обліковець існує. Далі ім'я живе у власній пам'яті монітора, а поле `user` наступних запитів просто ігнорується — інакше нападник перебирав би облікові записи, лишаючись на тих самих трьох спробах.

Шлях журналу монітор складає сам із числа, яке сам і дістав; з дроту в цей рядок не потрапляє нічого. Тому тут немає ні гонитви «перевір ім'я, потім відкрий», ні потреби у складних прапорцях розв'язання шляху — `O_NOFOLLOW` лишається просто дешевою страховкою.

## Пастки

**Таємниця, прочитана до `fork`.** Найтихіша з усіх: код виглядає розділеним, тести проходять, а ключ уже лежить у пам'яті робітника. Правило одне — жодного відкриття закритих файлів раніше за розгалуження й клітку.

**Успадковані дескриптори.** `O_CLOEXEC` тут не рятує, бо `exec` немає: усе, що було відкрито до `fork`, робітник отримує в готовому вигляді, і клітка цього не скасовує. Або закривайте зайве в дитині руками, або йдіть шляхом `sshd` і запускайте робітника окремим `exec` — тоді `O_CLOEXEC` знову працює.

**Щедрий запит.** `struct req { int op; char path[PATH_MAX]; }` перетворює монітор на послужливого root'а: об'єкт обирає той, кому ми не довіряємо. Ознака здорового протоколу проста — з описів усіх запитів видно повний перелік того, що взагалі може статися, і він скінченний.

**Нульова довжина разом із дескриптором.** Спокуса надіслати `SCM_RIGHTS` без корисних даних закінчується тим, що `recvmsg` повертає 0 — і приймач не відрізнить це від кінця файлу. Дескриптор завжди їде разом із відповіддю.

**EOF як норма, а не як помилка.** Нуль із `recvmsg` означає, що робітник помер, і це штатне завершення сесії, а не збій. Пара тримається на самому каналі: окремого нагляду за життям сусіда писати не треба, а `MSG_NOSIGNAL` рятує монітор від смерті по `SIGPIPE`, коли робітник помер саме між запитом і відповіддю.

**[Перерваний виклик](book:unix-linux/eintr-and-restart).** `EINTR` на сокеті — не помилка й не привід рвати сесію; кожен `sendmsg`/`recvmsg` тут загорнуто в цикл повтору, і це той рідкісний випадок, коли повторити треба буквально всюди.

**Мовчазна смерть від фільтра.** `SECCOMP_RET_KILL_PROCESS` убиває без пояснень, тож перший запуск під новим фільтром зазвичай виглядає як загадковий обрив на порожньому місці. Під час розробки замініть його на `SECCOMP_RET_TRAP` — сигнал принесе номер виклику, і перелік дозволів складеться за кілька ітерацій.

Ціна всієї конструкції — один додатковий процес і один обмін повідомленнями на кожну привілейовану дію. Обидві дії тут трапляються по разу за сесію, тож затримка нікого не турбує; там, де монітор просять щось робити в гарячому циклі, це вже ознака, що розріз проведено не по тому місцю.
