# ⚙️ Власна служба userdb: реєстр застосунку як користувачі системи

Нижче — робоча служба на C і на Python, яка віддає користувачів, що не лежать у жодному файлі: вони існують лише в реєстрі стороннього застосунку, а після її запуску `id`, `ls -l` і `systemd-run --uid=` бачать їх такими самими, як усіх інших.

## Реєстр, який не хоче ставати файлом

Хай є ферма збірок: десяток проєктів, і кожен збирається від власного користувача — щоб артефакти мали різних власників, щоб `ps` показував, чия саме робота з'їдає процесор, щоб зірваний скрипт одного проєкту нічого не дописав у теку іншого. Проєкти заводять і закривають щотижня, а список їх уже є — у базі самої ферми.

Очевидний хід — кликати `useradd` на кожен проєкт — робить `/etc/passwd` копією цієї бази. Копію доводиться тримати однаковою на всіх машинах ферми; після закриття проєкту в ній лишається рядок, якого ніхто не прибере; а редагують цей файл ще й руками. Кожна з трьох бід — наслідок одного: дані розмножили.

Потрібне протилежне: реєстр лишається там, де він є, а система питає його щоразу, коли треба перекласти ім'я в номер або номер в ім'я. Саме це й дає userdb — джерелом стає не файл, а працюючий процес.

## Два рішення до першого рядка коду

Механіка протоколу вміщується в абзац: зв'язати сокет `AF_UNIX`/`SOCK_STREAM` у теці `/run/systemd/userdb/` під іменем своєї служби, прочитати з нього об'єкт [JSON](book:programming/json-format), закінчений нульовим байтом, і надіслати назад такий самий. Складне не тут.

Складні два рішення, які потім міняти дорого.

**Перше: відповідність імені й номера мусить бути чистою функцією в обидва боки.** Питати будуть і так, і так: `ls -l` прийде з номером і захоче ім'я, `chown` — навпаки. Якщо ці два переклади робить окрема таблиця, вона рано чи пізно розійдеться сама з собою, і в системі з'явиться користувач, у якого `id -u` дає одне число, а власник його ж домівки — інше. Тому в прикладі ім'я — це `proj-` плюс назва проєкту, а номер — початок діапазону плюс місце в реєстрі: обидва переклади рахуються, а не шукаються.

**Друге: номери беруться з діапазону, який на цій машині не виданий нікому.** Служба нічого не «резервує» — вона просто заявляє номери. І розсудити її з тим, хто заявить ті самі числа, нікому: джерела опитують паралельно, черги, у якій одне перекрило б інше, немає, — на одне число просто знайдеться два різні імені, а котре з них покаже `ls -l`, залежатиме від того, чия відповідь надійшла першою. Тому діапазон вирізає адміністратор наперед; тут це 55000…55999.

## Уся служба

Код читається згори вниз: розбір повідомлення, засвідчений UID співрозмовника, три гілки за іменем методу. Перевірки в ньому стоять у певному порядку, і порядок цей не випадковий.

Спершу — засвідчений UID: він знадобиться ще до того, як стане ясно, про що питають, і взяти його можна лише з самого з'єднання. Далі — `service`: параметр обов'язковий, і його значення мусить збігтися з іменем сокета, до якого клієнт під'єднався. Перевірка здається порожньою формальністю рівно доти, доки запит не перешле посередник: тоді вона єдина відрізняє «питають мене» від «мене переплутали з кимось», і відповідь на другий випадок — `BadService`, а не чужий запис. І лише третьою йде сама вимога: ім'я, номер або перелік.

:::tabs
```c
/* projectdb.c — служба userdb: реєстр проєктів застосунку як користувачі системи.
 *   зібрати:   gcc -O2 -Wall -o projectdb projectdb.c
 *   запустити: sudo ./projectdb
 *   спитати:   userdbctl user proj-kernel
 *              varlinkctl call /run/systemd/userdb/com.example.Projects \
 *                io.systemd.UserDatabase.GetUserRecord \
 *                '{"userName":"proj-kernel","service":"com.example.Projects"}'
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#define SERVICE    "com.example.Projects"
#define SOCKPATH   "/run/systemd/userdb/" SERVICE
#define UID_BASE   55000u      /* діапазон, не виданий на цій машині нікому */
#define DEPLOY_KEY "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIexample ci@build"

/* Реєстр застосунку. У житті — читається з його бази; тут сталий масив. */
static const char *const projects[] = { "kernel", "toolchain", "docs" };
#define N_PROJECTS (sizeof projects / sizeof projects[0])

/* Ім'я ↔ номер: чиста функція в обидва боки, тому розійтися нема чому. */
static long index_by_name(const char *name)
{
    if (strncmp(name, "proj-", 5) != 0) return -1;
    for (size_t i = 0; i < N_PROJECTS; i++)
        if (strcmp(name + 5, projects[i]) == 0) return (long) i;
    return -1;
}
static long index_by_uid(unsigned long long uid)
{
    if (uid < UID_BASE || uid >= UID_BASE + N_PROJECTS) return -1;
    return (long) (uid - UID_BASE);
}

/* ── Вузький вибирач полів верхнього рівня ────────────────────────────────
   Свідоме спрощення прикладу: не розуміє екранованих лапок і вкладеності.
   Служба, яку ставлять у систему, бере повноцінний розбирач JSON — або
   одразу sd-varlink із libsystemd, де розбір і рамка вже написані. */
static const char *field(const char *msg, const char *key)
{
    char pat[64];
    int n = snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(msg, pat);
    if (!p) return NULL;
    p += n;
    while (*p == ' ') p++;
    if (*p++ != ':') return NULL;
    while (*p == ' ') p++;
    return p;
}
static int field_str(const char *msg, const char *key, char *out, size_t n)
{
    const char *p = field(msg, key);
    if (!p || *p != '"') return 0;
    const char *e = strchr(++p, '"');
    if (!e || (size_t) (e - p) >= n) return 0;
    memcpy(out, p, (size_t) (e - p));
    out[e - p] = '\0';
    return 1;
}
static long long field_num(const char *msg, const char *key)
{
    const char *p = field(msg, key);
    return (p && *p >= '0' && *p <= '9') ? strtoll(p, NULL, 10) : -1;
}
static int field_true(const char *msg, const char *key)
{
    const char *p = field(msg, key);
    return p && strncmp(p, "true", 4) == 0;
}

/* ── Надсилання ───────────────────────────────────────────────────────────
   Одне повідомлення Varlink — це об'єкт JSON і нульовий байт-роздільник. */
static int send_msg(int fd, const char *json)
{
    size_t len = strlen(json) + 1;                  /* разом із роздільником */
    for (size_t off = 0; off < len; ) {
        ssize_t k = write(fd, json + off, len - off);
        if (k < 0) { if (errno == EINTR) continue; return -1; }
        off += (size_t) k;
    }
    return 0;
}
static int send_error(int fd, const char *name)
{
    char buf[192];
    snprintf(buf, sizeof buf, "{\"error\":\"%s\",\"parameters\":{}}", name);
    return send_msg(fd, buf);
}

/* Секцію privileged дістає власник запису або root; решті її вирізають —
   і саме тому поруч їде incomplete: «тобі показали не все». */
static int send_user(int fd, size_t i, uid_t peer, int continues)
{
    unsigned uid = (unsigned) (UID_BASE + i);
    int owner = (peer == 0 || peer == (uid_t) uid);
    char buf[1024];
    snprintf(buf, sizeof buf,
        "{\"parameters\":{\"record\":{"
            "\"userName\":\"proj-%s\","
            "\"realName\":\"Проєкт %s\","
            "\"disposition\":\"system\","
            "\"service\":\"" SERVICE "\","
            "\"uid\":%u,\"gid\":%u,"
            "\"homeDirectory\":\"/var/lib/projects/%s\","
            "\"shell\":\"/usr/sbin/nologin\"%s"
        "},\"incomplete\":%s}%s}",
        projects[i], projects[i], uid, uid, projects[i],
        owner ? ",\"privileged\":{\"sshAuthorizedKeys\":[\"" DEPLOY_KEY "\"]}" : "",
        owner ? "false" : "true",
        continues ? ",\"continues\":true" : "");
    return send_msg(fd, buf);
}
static int send_group(int fd, size_t i, int continues)
{
    char buf[512];
    snprintf(buf, sizeof buf,
        "{\"parameters\":{\"record\":{"
            "\"groupName\":\"proj-%s\","
            "\"disposition\":\"system\","
            "\"service\":\"" SERVICE "\","
            "\"gid\":%u"
        "},\"incomplete\":false}%s}",
        projects[i], (unsigned) (UID_BASE + i),
        continues ? ",\"continues\":true" : "");
    return send_msg(fd, buf);
}

/* За яким ключем питають: індекс, −1 (такого немає) або −2 (просять перелік). */
static long resolve(const char *msg, const char *name_key, const char *num_key)
{
    char name[128];
    if (field_str(msg, name_key, name, sizeof name)) return index_by_name(name);
    long long n = field_num(msg, num_key);
    if (n >= 0) return index_by_uid((unsigned long long) n);
    return -2;
}

static int serve(int fd)
{
    struct ucred cred;
    socklen_t clen = sizeof cred;
    if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &clen) < 0) return -1;
    uid_t peer = cred.uid;         /* вписало ядро в мить connect(); не підробиш */

    char msg[4096];
    size_t len = 0;
    for (;;) {                     /* читаємо, доки не трапиться роздільник */
        ssize_t k = read(fd, msg + len, sizeof msg - 1 - len);
        if (k <= 0) return -1;
        len += (size_t) k;
        if (memchr(msg, '\0', len)) break;
        if (len == sizeof msg - 1) return -1;      /* завелике повідомлення */
    }

    char method[128], service[128];
    if (!field_str(msg, "method", method, sizeof method))
        return send_error(fd, "org.varlink.service.InvalidParameter");

    /* service обов'язковий і мусить збігтися з іменем нашого сокета: так
       запит, пересланий не туди, помирає одразу, а не відповідає чужим. */
    if (!field_str(msg, "service", service, sizeof service) ||
        strcmp(service, SERVICE) != 0)
        return send_error(fd, "io.systemd.UserDatabase.BadService");

    if (strcmp(method, "io.systemd.UserDatabase.GetUserRecord") == 0) {
        long i = resolve(msg, "userName", "uid");
        if (i == -2) {                       /* ні імені, ні номера — перелік */
            if (!field_true(msg, "more"))    /* одна відповідь його не вмістить */
                return send_error(fd, "org.varlink.service.InvalidParameter");
            for (size_t k = 0; k < N_PROJECTS; k++)
                send_user(fd, k, peer, k + 1 < N_PROJECTS);
            return 0;
        }
        if (i < 0) return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");
        return send_user(fd, (size_t) i, peer, 0);
    }

    if (strcmp(method, "io.systemd.UserDatabase.GetGroupRecord") == 0) {
        long i = resolve(msg, "groupName", "gid");
        if (i == -2) {
            if (!field_true(msg, "more"))
                return send_error(fd, "org.varlink.service.InvalidParameter");
            for (size_t k = 0; k < N_PROJECTS; k++)
                send_group(fd, k, k + 1 < N_PROJECTS);
            return 0;
        }
        if (i < 0) return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");
        return send_group(fd, (size_t) i, 0);
    }

    /* Проєкт сидить лише у власній первинній групі, а первинне членство цим
       викликом не повідомляють. Порожньої вдалої відповіді тут не буває. */
    if (strcmp(method, "io.systemd.UserDatabase.GetMemberships") == 0)
        return send_error(fd, "io.systemd.UserDatabase.NoRecordFound");

    return send_error(fd, "org.varlink.service.MethodNotFound");
}

int main(void)
{
    unlink(SOCKPATH);                       /* лишок від попереднього запуску */

    int srv = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (srv < 0) { perror("socket"); return 1; }

    struct sockaddr_un a = { .sun_family = AF_UNIX };
    strncpy(a.sun_path, SOCKPATH, sizeof a.sun_path - 1);
    if (bind(srv, (struct sockaddr *) &a, sizeof a) < 0) { perror("bind"); return 1; }

    /* Питати може будь-хто: що саме показати, вирішує не режим файлу,
       а засвідчений UID співрозмовника. */
    if (chmod(SOCKPATH, 0666) < 0) { perror("chmod"); return 1; }
    if (listen(srv, 64) < 0) { perror("listen"); return 1; }

    for (;;) {
        int fd = accept4(srv, NULL, NULL, SOCK_CLOEXEC);
        if (fd < 0) { if (errno == EINTR) continue; perror("accept"); return 1; }
        serve(fd);          /* законно по черзі: жодна гілка нікого не чекає */
        close(fd);
    }
}
```
```python
#!/usr/bin/env python3
"""projectdb.py — та сама служба, коротше: реєстр проєктів як користувачі.
   запустити: sudo python3 projectdb.py
   спитати:   userdbctl user proj-kernel
"""
import json, os, socket, struct

SERVICE    = "com.example.Projects"
SOCKPATH   = "/run/systemd/userdb/" + SERVICE
UID_BASE   = 55000                 # діапазон, не виданий на цій машині нікому
PROJECTS   = ["kernel", "toolchain", "docs"]
DEPLOY_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIexample ci@build"


def resolve(p, name_key, num_key):
    """Індекс проєкту, None (такого немає) або "all" (просять перелік)."""
    if name_key in p:
        n = p[name_key]
        tail = n[5:] if n.startswith("proj-") else None
        return PROJECTS.index(tail) if tail in PROJECTS else None
    if num_key in p:
        i = p[num_key] - UID_BASE
        return i if 0 <= i < len(PROJECTS) else None
    return "all"


def user_record(i, peer):
    uid = UID_BASE + i
    rec = {
        "userName": f"proj-{PROJECTS[i]}",
        "realName": f"Проєкт {PROJECTS[i]}",
        "disposition": "system",
        "service": SERVICE,
        "uid": uid, "gid": uid,
        "homeDirectory": f"/var/lib/projects/{PROJECTS[i]}",
        "shell": "/usr/sbin/nologin",
    }
    owner = peer in (0, uid)              # власник запису або root
    if owner:
        rec["privileged"] = {"sshAuthorizedKeys": [DEPLOY_KEY]}
    return {"record": rec, "incomplete": not owner}


def group_record(i):
    return {"record": {"groupName": f"proj-{PROJECTS[i]}", "disposition": "system",
                       "service": SERVICE, "gid": UID_BASE + i},
            "incomplete": False}


def send(conn, obj):
    conn.sendall(json.dumps(obj).encode() + b"\0")     # роздільник — нульовий байт


def error(conn, name):
    send(conn, {"error": name, "parameters": {}})


def stream(conn, make, n):
    for k in range(n):
        reply = {"parameters": make(k)}
        if k + 1 < n:
            reply["continues"] = True                  # ще не остання
        send(conn, reply)


def serve(conn):
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    _pid, peer, _gid = struct.unpack("3i", raw)        # засвідчено ядром

    buf = b""
    while b"\0" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return
        buf += chunk
    call = json.loads(buf.split(b"\0", 1)[0])
    p = call.get("parameters") or {}

    if p.get("service") != SERVICE:
        return error(conn, "io.systemd.UserDatabase.BadService")

    method = call.get("method")

    if method == "io.systemd.UserDatabase.GetUserRecord":
        i = resolve(p, "userName", "uid")
        if i == "all":
            if not call.get("more"):
                return error(conn, "org.varlink.service.InvalidParameter")
            return stream(conn, lambda k: user_record(k, peer), len(PROJECTS))
        if i is None:
            return error(conn, "io.systemd.UserDatabase.NoRecordFound")
        return send(conn, {"parameters": user_record(i, peer)})

    if method == "io.systemd.UserDatabase.GetGroupRecord":
        i = resolve(p, "groupName", "gid")
        if i == "all":
            if not call.get("more"):
                return error(conn, "org.varlink.service.InvalidParameter")
            return stream(conn, group_record, len(PROJECTS))
        if i is None:
            return error(conn, "io.systemd.UserDatabase.NoRecordFound")
        return send(conn, {"parameters": group_record(i)})

    if method == "io.systemd.UserDatabase.GetMemberships":
        return error(conn, "io.systemd.UserDatabase.NoRecordFound")

    error(conn, "org.varlink.service.MethodNotFound")


if __name__ == "__main__":
    if os.path.exists(SOCKPATH):
        os.unlink(SOCKPATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCKPATH)
    os.chmod(SOCKPATH, 0o666)          # хто питає — будь-хто; що почує — за peer
    srv.listen(64)
    while True:
        conn, _ = srv.accept()
        with conn:
            try:
                serve(conn)
            except Exception:          # зіпсований запит не валить служби
                pass
```
:::

Ціна відповіді тут стала: пошук за іменем чи номером — це порівняння з коротким масивом, без жодного звертання до диска чи мережі, а перелік коштує рівно стільки, скільки в реєстрі записів. Саме тому цикл в одному потоці, що обслуговує з'єднання одне за одним, — не спрощення заради прикладу, а законна конструкція.

![Одне з'єднання: від connect() до останнього нульового байта](/reference/unix-linux/permissions/userdb-varlink/img/request-life.svg)

*Три перевірки й три можливі закінчення, і жодне з них нічого не чекає ззовні.*

## Чому перелік — потік, а не масив

Запит без імені й без номера означає «перелічи всіх». Відповіддю міг би бути масив записів усередині одного об'єкта — так зробили б, якби писали це вперше. Varlink робить інакше: виклик із прапорцем `more` дозволяє відповісти багато разів, і кожна відповідь несе один запис та позначку `continues`, доки не прийде остання — уже без позначки.

Різниця виявляється на великих джерелах. Служба, що віддає мережевий каталог на десятки тисяч записів, за масивом мусила б скласти весь список у пам'яті, перш ніж написати перший байт; потоком вона віддає запис тоді, коли він у неї з'явився. А клієнтові, якому досить першого збігу, вистачить закрити з'єднання — за решту він не платить.

Звідси й дрібниця, помітна в коді: у відповіді немає жодного номера запиту. Varlink відповідає в тому самому порядку, у якому дістав виклики, і на з'єднанні, що несе рівно один виклик, зіставляти нема чого — тому служба пише відповідь просто в той самий дескриптор і закриває його.

## Число, яке не можна перебрехати

`getsockopt(SO_PEERCRED)` віддає структуру, яку ядро заповнило в мить `connect()` з облікових даних того, хто під'єднався. Це не параметр виклику й не поле в JSON: клієнт не бере в цьому участі, тож не може ні підмінити своє число, ні пропустити його. [Сокети домену Unix](book:unix-linux/unix-domain-sockets) — з'єднання через файл, де ядро саме засвідчує другому боку, хто на тому кінці, — уміють це самі, тому засвідчення тут коштує один рядок і не потребує жодного протоколу автентифікації.

Звідси випливає річ, яка спершу лякає: файл-сокет має режим `0666`, і відкрити його може будь-хто. Це не діра. Права на сокет відповідають на питання «кому дозволено питати», а засвідчений UID — на інше питання, «скільки йому сказати». Сам systemd робить так само: сокет `systemd-userdbd` теж має `SocketMode=0666`.

І ще одне, що в такому коді проґавлюють майже завжди: `incomplete` треба виставляти навіть тоді, коли здається, ніби нема кому. Розробник запускає службу від `root` і питає її від `root` — секцію `privileged` йому віддають щоразу, і забутий `incomplete` ніде не видно. Помилка виявиться на чужій машині й виглядатиме як «у проєкту зник ключ».

## Чотири способи зіпсувати робочу службу

**Відповідь не має права чекати.** Найприродніший наступний крок — піти по дані просто в базу ферми, бо реєстр же живе саме там. Він і робить службу вузьким місцем усієї машини: черга з'єднань перетворюється на чергу за кожним звертанням по імені, а звертання по імені трапляється в `ls`, у `ps` і в кожному вході в систему. Лікування не в тому, щоб зробити читання [неблокуючим](book:unix-linux/blocking-and-nonblocking): цим ви лише розмажете те саме чекання по всіх з'єднаннях одразу. Лікування — тримати в пам'яті знімок реєстру й оновлювати його окремим потоком, а відповідь щоразу складати з того, що вже є.

**Служба мусить бути на місці раніше за всіх, хто питає імена.** Питання «як звати цей номер» виникає задовго до того, як піднялася мережа: в initramfs, у найпершій фазі завантаження, у процесі, який саме складає з себе привілеї. Демон, запущений після всього, на ці запити просто не встигне. Правильний хід — не стартувати раніше, а віддати сокет менеджеру служб: за [активації за сокетом](book:unix-linux/socket-activation) файл існує з моменту, коли піднято юніт сокета, а з'єднання, що прийшли до старту демона, ядро тримає в черзі.

```ini
# /etc/systemd/system/projectdb.socket
[Unit]
Description=Реєстр проєктів як джерело userdb
DefaultDependencies=no
Before=sockets.target

[Socket]
ListenStream=/run/systemd/userdb/com.example.Projects
SocketMode=0666

[Install]
WantedBy=sockets.target
```

Програма тоді не зв'язує сокет сама, а бере готовий успадкований дескриптор — перший переданий має номер 3.

**Не питати назад класичний перемикач імен.** Спокуса всередині служби виглядає невинно: узяти `getpwnam()`, щоб перевірити, чи ім'я не зайняте, або `getgrnam()`, щоб дізнатися групу. Наслідок — кільце. Бібліотека C піде в модуль `nss-systemd`, той — у мультиплексор userdb, мультиплексор — назад у наш-таки сокет, а ми в цю мить сидимо в `serve()` й нікого не приймаємо: служба чекає сама на себе. Правило просте — усередині служби, що віддає записи, імена лишаються рядками, номери числами, і жодних питань до [класичної бази](book:unix-linux/user-database-nss) звідси не ставлять.

**Методів три, а не один.** Служба, що відповідає лише на `GetUserRecord`, виглядає працездатною рівно доти, доки хтось не набере `id proj-kernel`: після імені користувача йому потрібні групи. Перелічувати себе служба не зобов'язана — і якщо не вміє, каже це прямо, помилкою `EnumerationNotSupported`, бо порожній список виглядав би як повний. А от відповідати на всі три виклики зобов'язана, і «нічого не знайшов» мусить бути помилкою `NoRecordFound`. Різниця між «додаткових груп у цього користувача немає» і «служба не зрозуміла запиту» — це те, за чим клієнт відрізняє знання від мовчання.
