# ⚙️ Завантажити місію, зчитати назад і не збрехати собі: робочий завантажувач на pymavlink і C

## Задача: залити маршрут так, щоб на борту він був саме той

Ти склав місію — п'ять-шість пунктів: злетіти, пройти дві точки, скинути вантаж, повернутися. Тепер її треба **покласти в борт**, а перед першим `arm` — **переконатися**, що борт зберіг рівно те, що ти задумав. Здавалося б, дрібниця: у [pymavlink](root:embedded/pymavlink) є `mav.mission_item_int_send(...)` (а в C — `mavlink_msg_mission_item_int_pack(...)` плюс надіслати буфер) — виклич його для кожної точки, і готово.

Спробуй так — і рано чи пізно апарат полетить не туди. Причина в тому, що між твоїм скриптом і бортом лежить **радіоканал**, а не функція. Пакети губляться, дублюються, приходять не в тому порядку. Якщо ти просто «вистрілиш» шість `MISSION_ITEM_INT` поспіль у сокет, борт може прийняти чотири з них, пропустити пункт #2 через збитий пакет — і зібрати в пам'яті маршрут із дірою. Або, ще підступніше, прийняти всі шість, але не в тому порядку, і покласти точку C туди, де мала бути A. Скрипт відпрацює без єдиної помилки, друкне «готово» — а місія на борту буде спотворена, і ти цього **не побачиш**, поки апарат не рушить.

Тому задача формулюється жорсткіше, ніж «надіслати». Треба:

1. **Завантажити** місію так, щоб борт зібрав її строго по порядку й без дірок, з підтвердженням у кінці.
2. **Зчитати назад** те, що реально лежить у борті (а не те, що ми «мали б» надіслати).
3. **Звірити** кожен пункт із задумом — координати, висоту, систему відліку висоти — до того, як дозволити старт.
4. **Спостерігати** в реальному часі, на якому пункті стоїть місія в польоті.

І кожен із цих кроків мусить бути **стійким до втрати пакета** — інакше перший загублений байт або зіпсує маршрут, або підвісить скрипт назавжди. Базовий крок капстоуна показав, що завантаження місії — це рукостискання; детальний розбір показав, чому воно надійне навіть на дірявому каналі. Тут ми втілюємо це рукостискання в **робочий код**, який ти справді запустиш проти свого борту, — і показуємо його **двома мовами одразу**: на pymavlink (як ти напишеш це на землі за ноутбуком) і на MAVLink C library (як той самий протокол виглядає в прошивці чи на компаньйон-компі, де pymavlink немає). Логіка стан-машини — та сама; різниця лише в тому, скільки чорної роботи бібліотека робить за тебе.

> 🔧 **Навіщо це.** «Залив і полетів» без зчитування назад — це політ наосліп. Дві хвилини звірки на землі економлять годину пошуку «чому дрон полетів не туди» — і, цілком імовірно, сам апарат. Помилка в координаті чи в системі висоти на землі коштує **нуль**; та сама помилка в повітрі коштує апарата й, можливо, чужого вікна. Цей скрипт переносить усі тихі помилки завантаження туди, де вони безпечні, — на екран твого ноутбука перед стартом.

## Ідея: рукостискання — це не «надіслати», а цикл «запит → чекай → підтверди»

Ключовий зсув, без якого код не складеться правильно. Завантаження місії — **не** односторонній потік «GCS → борт». Це **діалог**, у якому провідну роль веде **борт**, а не земля. Земля лише оголошує, скільки буде пунктів, а далі — **борт сам просить** кожен наступний пункт за його номером `seq`, і земля лише **відповідає** на запити.

Порядок такий (він звірений із офіційним [протоколом місій MAVLink](root:embedded/mavlink-from-ground) — деталі механіки й історію переходу на цілочислові координати розібрано в основній статті капстоуна):

```
GCS  → борт : MISSION_COUNT (усього 6)
борт → GCS  : MISSION_REQUEST_INT (дай #0)   ← борт КЕРУЄ темпом
GCS  → борт : MISSION_ITEM_INT   (ось #0)
борт → GCS  : MISSION_REQUEST_INT (дай #1)
GCS  → борт : MISSION_ITEM_INT   (ось #1)
        …    (борт САМ просить кожен наступний)
борт → GCS  : MISSION_ACK (MAV_MISSION_ACCEPTED) — прийняв усі 6
```

Чому це надійно, а «вистрілити потоком» — ні? Бо **надійність тримає той, хто зберігає результат** — борт. Якщо запит на #1 не дійшов до землі, борт **повторить** запит #1 і не рушить далі, доки не отримає пункт. Якщо земля відповість пунктом #3, коли борт чекав #2, борт його **відкине** й перепитає саме #2. Список у пам'яті борту фізично **не може** зібратися з дірками чи не по порядку — він добудовується монотонно, по одному, з явним `MISSION_ACK` наприкінці. Це та сама дисципліна «підтвердь, що дійшло», що й у [надійному циклі команд](root:embedded/mavlink-commands/proj-command-ack-loop.md), який ти вже писав.

Але тут з'являється деталь, від якої залежить, чи скрипт узагалі працездатний: **час**. Борт очікує відповідь не вічно. Протокол задає таймаути явно: на кожен запит пункту — **250 мс** очікування, і **до 5** повторів, після чого операція **скасовується** й місія на борті лишається **попередньою** (не піврозібраною). Симетрично й наш бік мусить мати таймаути: коли ми чекаємо запит від борту або чекаємо пункт при зчитуванні назад, ми **не** можемо блокуватися назавжди — бо тоді один загублений пакет підвисить скрипт мертво.

![Завантаження одного пункту як стан-машина: запит → чекати 250 мс → прийшов потрібний seq (далі) або таймаут/чужий seq (повтор); після 5 марних повторів — скасувати](/root/course/embedded/capstone-autonomous-mission/img/upload-loop.svg)
*Кожен пункт проходить цей цикл. **ЗАПИТ** — надіслати `MISSION_REQUEST_INT(seq)`. **ЧЕКАЮ** — прийняти відповідь із таймаутом 250 мс, збільшивши лічильник спроб. Прийшов потрібний `seq` (зелена стрілка) — зберегти й просити наступний (синя стрілка вгору). Тиша за таймаут або пункт із **не тим** номером (червона стрілка вниз) — повторити **той самий** запит. П'ять марних повторів поспіль — **скасувати** операцію: краще лишити на борті стару цілу місію, ніж півзібрану нову. Уся стійкість до втрати пакетів — у цих трьох стрілках назад.*

Отже, ідея коду в одному реченні: **не «надіслати список», а прокрутити для кожного пункту маленьку стан-машину «запит → чекай із таймаутом → підтвердь або повтори», і симетрично — при зчитуванні назад**. Далі — власне код, який це робить, шматок за шматком.

## Крок 0: зʼєднання і спільні помічники

Почнімо з фундаменту. Підключаємося до борту й чекаємо перший `HEARTBEAT` — доки він не прийшов, ми не знаємо `target_system` (номер системи борту), а без нього всі повідомлення підуть «у нікуди».

І тут одразу видно головну різницю між двома мовами. У Python усю чорну роботу — відкрити сокет, розібрати потік байтів на повідомлення, дочекатися потрібного типу з таймаутом — робить за тебе **pymavlink**, тому Крок 0 короткий. У C цієї бібліотеки-помічника немає: сокет, розбір байтів через `mavlink_parse_char` і очікування з таймаутом на `select` доводиться написати **руками — один раз, у фундаменті**, і далі ними користуватися. Тому C-версія Кроку 0 довша: вона показує те, що pymavlink ховає під капотом. Наш головний помічник — `recv_match`: «чекати повне повідомлення потрібного типу, але не довше за таймаут» — рівно те, що в pymavlink зветься `recv_match(type=..., timeout=...)`.

:::tabs
```py
#!/usr/bin/env python3
# mission_upload_verify.py — завантажити місію, зчитати назад, звірити, стежити.
# Реальний pymavlink; запускати на землі проти борту (SITL чи справжнього).
from pymavlink import mavutil

# Підключення. Приклади рядка:
#   'udpin:0.0.0.0:14550'      — слухати SITL / mavproxy
#   'com7'  (Windows) / '/dev/ttyUSB0'  — телеметрійний радіомодем
#   baud=57600 для типового радіо; для USB baud ігнорується.
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

# Без цього target_system/target_component невідомі — чекаємо перший HEARTBEAT.
master.wait_heartbeat()
print(f"звʼязок є: system={master.target_system} component={master.target_component}")

TSYS = master.target_system
TCMP = master.target_component
MTYPE = mavutil.mavlink.MAV_MISSION_TYPE_MISSION   # звичайна місія (не гео/ралі)
```
```cpp
// mission_upload_verify.c — завантажити місію, зчитати назад, звірити, стежити.
// Той самий протокол, що й на pymavlink, але руками на MAVLink C library — так
// його пишуть у прошивці чи на компаньйон-компі, де pymavlink немає.
// Збірка: cc mission_upload_verify.c -I<тека_згенерованих_mavlink_заголовків> -lm
#include <mavlink/common/mavlink.h>   // згенеровані mavlink_msg_* (діалект common)
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>

#define SYSID  255                        // наш id як наземної станції (звично 255)
#define COMPID MAV_COMP_ID_MISSIONPLANNER
#define MTYPE  MAV_MISSION_TYPE_MISSION    // звичайна місія (не гео/ралі)

static int sock;
static struct sockaddr_in peer;           // куди відповідати: звідки прийшов пакет
static uint8_t TSYS, TCMP;                // id борту — дізнаємось із HEARTBEAT

static double now(void) {                 // монотонний час у секундах
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void open_udp(const char *ip, int port) {   // 'udpin' у pymavlink — це воно
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in a = {0};
    a.sin_family = AF_INET; a.sin_addr.s_addr = inet_addr(ip); a.sin_port = htons(port);
    bind(sock, (struct sockaddr*)&a, sizeof(a));
}

static void send_msg(mavlink_message_t *m) {        // спакувати й надіслати борту
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, m);
    sendto(sock, buf, len, 0, (struct sockaddr*)&peer, sizeof(peer));
}

// Головний помічник: чекати повне повідомлення з msgid ∈ want[], але НЕ довше timeout.
// Це C-відповідник pymavlink-івського recv_match(type=..., timeout=...).
static int recv_match(const uint8_t *want, int nwant,
                      mavlink_message_t *out, double timeout) {
    double deadline = now() + timeout;
    mavlink_message_t msg; mavlink_status_t st;
    for (;;) {
        double left = deadline - now();
        if (left <= 0) return 0;                    // таймаут — саме те, що рятує від зависання
        fd_set r; FD_ZERO(&r); FD_SET(sock, &r);
        struct timeval tv = { (long)left, (long)((left - (long)left) * 1e6) };
        if (select(sock + 1, &r, NULL, NULL, &tv) <= 0) return 0;
        uint8_t b[512]; socklen_t sl = sizeof(peer);
        int n = recvfrom(sock, b, sizeof(b), 0, (struct sockaddr*)&peer, &sl);
        for (int i = 0; i < n; i++)                 // згодувати байти парсеру
            if (mavlink_parse_char(MAVLINK_COMM_0, b[i], &msg, &st))   // зібрався кадр?
                for (int w = 0; w < nwant; w++)
                    if (msg.msgid == want[w]) { *out = msg; return 1; }
    }
}

static void wait_heartbeat(void) {        // без цього TSYS/TCMP невідомі
    mavlink_message_t hb;
    const uint8_t want[] = { MAVLINK_MSG_ID_HEARTBEAT };
    while (!recv_match(want, 1, &hb, 5.0)) { }      // чекати, поки не прийде
    TSYS = hb.sysid; TCMP = hb.compid;
    printf("звʼязок є: system=%u component=%u\n", TSYS, TCMP);
}
```
:::

Один нюанс, який ловить новачків: `MISSION_REQUEST_INT` — це запит **від борту до нас**, і його `msgname` у pymavlink — рядок `'MISSION_REQUEST_INT'`. Але деякі прошивки (залежно від версії) шлють запит **старим** повідомленням `MISSION_REQUEST` (без `_INT`). Щоб бути стійким, при очікуванні запиту ми ловитимемо **обидва** типи — у Python перелічимо обидва рядки в `type=[...]`, у C — обидва `MAVLINK_MSG_ID_...` у масиві `want[]`. Це не параноя — це відповідь на реальну неоднорідність польових прошивок, і саме така дрібниця відрізняє скрипт, що «працює в мене на SITL», від скрипта, що працює й на чужому борті.

## Крок 1: завантаження з рукостисканням

Тепер серце. На вхід — список пунктів; кожен пункт я подаю простим записом (у Python — словником, у C — маленькою структурою `wp_t`), щоб не тонути в аргументах:

:::tabs
```py
# Пункт місії у зручному вигляді. Координати — ЦІЛІ, в одиницях 1e-7 градуса!
# (Чому цілі, а не float — див. пастку нижче; коротко: float дав би метрову
#  похибку ще на землі.)
#   (seq, frame, command, param1..4, lat_int, lon_int, alt_m, autocontinue)
def wp(seq, command, lat_deg, lon_deg, alt_m,
       frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
       p1=0.0, p2=0.0, p3=0.0, p4=0.0, autocontinue=1):
    return dict(seq=seq, frame=frame, command=command,
                p1=p1, p2=p2, p3=p3, p4=p4,
                x=int(round(lat_deg * 1e7)),   # градуси → ціле 1e-7°, ОДИН раз
                y=int(round(lon_deg * 1e7)),
                z=float(alt_m), autocontinue=autocontinue)

# Приклад місії для коптера: зліт 15 м → точка A → точка B → RTL.
HOME_LAT, HOME_LON = 50.4501, 30.5234    # десь у Києві, для прикладу
mission = [
    wp(0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, HOME_LAT,          HOME_LON,          15.0),
    wp(1, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, HOME_LAT + 0.0004, HOME_LON,          15.0),
    wp(2, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, HOME_LAT + 0.0004, HOME_LON + 0.0006, 15.0),
    wp(3, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0),
]
```
```cpp
// Пункт місії у зручному вигляді. Координати — ЦІЛІ, в одиницях 1e-7 градуса!
// (Чому цілі, а не float — див. пастку нижче; коротко: float дав би метрову
//  похибку ще на землі.)
typedef struct {
    uint16_t seq, command;
    uint8_t  frame, autocontinue;
    float    p1, p2, p3, p4, z;
    int32_t  x, y;                        // 1e-7 градуса — ЦІЛІ
} wp_t;

// Конструктор пункту: градуси → цілі 1e-7° рівно ОДИН раз, тут, при складанні.
static wp_t wp(uint16_t seq, uint16_t command, double lat_deg, double lon_deg, float alt_m) {
    wp_t w = {0};
    w.seq = seq; w.command = command;
    w.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    w.autocontinue = 1;
    w.x = (int32_t)lround(lat_deg * 1e7);  // градуси → ціле 1e-7°, ОДИН раз
    w.y = (int32_t)lround(lon_deg * 1e7);
    w.z = alt_m;
    return w;
}

// Приклад місії для коптера: зліт 15 м → точка A → точка B → RTL.
#define N 4
static wp_t mission[N];
static void build_mission(void) {
    const double HL = 50.4501, HN = 30.5234;   // десь у Києві, для прикладу
    mission[0] = wp(0, MAV_CMD_NAV_TAKEOFF,          HL,          HN,          15.0f);
    mission[1] = wp(1, MAV_CMD_NAV_WAYPOINT,         HL + 0.0004, HN,          15.0f);
    mission[2] = wp(2, MAV_CMD_NAV_WAYPOINT,         HL + 0.0004, HN + 0.0006, 15.0f);
    mission[3] = wp(3, MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,           0,           0.0f);
}
```
:::

Зверни увагу на перетворення координати в ціле — `int(round(lat_deg * 1e7))` у Python, `lround(lat_deg * 1e7)` у C — **всередині** `wp`: воно відбувається **один раз**, при складанні пункту, і далі координата живе цілою (`x`, `y`) аж до відправки. Це не косметика — це головний запобіжник від метрової похибки, і ми до нього ще повернемось у пастках.

Тепер сам цикл завантаження. Він точно відтворює стан-машину з рисунка — і в обох мовах структура однакова, бо однаковий протокол:

:::tabs
```py
def upload_mission(master, items, timeout=0.25, max_retries=5):
    """Завантажити список пунктів рукостисканням. True — борт прийняв (ACK)."""
    n = len(items)

    # 1. Оголосити кількість. Далі темп задає БОРТ своїми запитами.
    master.mav.mission_count_send(TSYS, TCMP, n, MTYPE)

    # 2. Відповідати на запити борту, доки не роздамо всі пункти.
    #    Борт САМ вирішує, який seq просити наступним (зазвичай по порядку,
    #    але при втраті пакета — перепитує той самий).
    sent = 0
    retries = 0
    while sent < n:
        # Чекаємо запит пункту — від борту. Ловимо ОБИДВІ форми: _INT і стару.
        req = master.recv_match(
            type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'],
            blocking=True, timeout=timeout)

        if req is None:                      # тиша: пакет загубився в той чи той бік
            retries += 1
            if retries > max_retries:
                print("завантаження: борт мовчить — скасовую")
                return False
            # Не сидимо склавши руки: повторно оголосимо count, щоб струснути діалог.
            master.mav.mission_count_send(TSYS, TCMP, n, MTYPE)
            continue

        retries = 0                          # прийшов запит — лічильник тиші скинуто
        seq = req.seq
        if seq >= n:                         # борт просить неіснуючий пункт — ігноруємо
            continue

        it = items[seq]                      # віддаємо саме той seq, що просять
        master.mav.mission_item_int_send(
            TSYS, TCMP, it['seq'], it['frame'], it['command'],
            0,                               # current
            it['autocontinue'],
            it['p1'], it['p2'], it['p3'], it['p4'],
            it['x'], it['y'], it['z'], MTYPE)
        sent = max(sent, seq + 1)            # відстежуємо найдальший відданий

    # 3. Дочекатися фінального підтвердження.
    ack = master.recv_match(type='MISSION_ACK', blocking=True, timeout=3)
    if ack is None:
        print("завантаження: немає MISSION_ACK — борт не підтвердив")
        return False
    if ack.type != mavutil.mavlink.MAV_MISSION_ACCEPTED:   # ACCEPTED == 0
        print(f"завантаження: борт відхилив, код MAV_MISSION_RESULT={ack.type}")
        return False
    print(f"завантаження: борт прийняв усі {n} пунктів (ACK=ACCEPTED)")
    return True
```
```cpp
// 1 — борт прийняв усі пункти (ACK). Точно та сама стан-машина, що в Python.
int upload_mission(const wp_t *items, uint16_t n) {
    mavlink_message_t msg;
    // 1. Оголосити кількість. Далі темп задає БОРТ своїми запитами.
    mavlink_msg_mission_count_pack(SYSID, COMPID, &msg, TSYS, TCMP, n, MTYPE);
    send_msg(&msg);

    // 2. Відповідати на запити борту, доки не роздамо всі пункти. Ловимо ОБИДВІ форми.
    const uint8_t want_req[] = { MAVLINK_MSG_ID_MISSION_REQUEST_INT,
                                 MAVLINK_MSG_ID_MISSION_REQUEST };
    uint16_t sent = 0; int retries = 0;
    while (sent < n) {
        if (!recv_match(want_req, 2, &msg, 0.25)) {   // тиша: пакет загубився
            if (++retries > 5) { puts("завантаження: борт мовчить — скасовую"); return 0; }
            mavlink_msg_mission_count_pack(SYSID, COMPID, &msg, TSYS, TCMP, n, MTYPE);
            send_msg(&msg);                            // струснути діалог
            continue;
        }
        retries = 0;                                  // прийшов запит — тишу скинуто
        uint16_t seq;                                 // борт САМ називає, який seq дати
        if (msg.msgid == MAVLINK_MSG_ID_MISSION_REQUEST_INT) {
            mavlink_mission_request_int_t q;
            mavlink_msg_mission_request_int_decode(&msg, &q); seq = q.seq;
        } else {
            mavlink_mission_request_t q;
            mavlink_msg_mission_request_decode(&msg, &q); seq = q.seq;
        }
        if (seq >= n) continue;                       // просить неіснуючий — ігноруємо

        const wp_t *it = &items[seq];                 // віддаємо саме той seq, що просять
        mavlink_msg_mission_item_int_pack(SYSID, COMPID, &msg, TSYS, TCMP,
            it->seq, it->frame, it->command,
            0,                                        // current
            it->autocontinue,
            it->p1, it->p2, it->p3, it->p4,
            it->x, it->y, it->z, MTYPE);
        send_msg(&msg);
        if (seq + 1 > sent) sent = seq + 1;           // відстежуємо найдальший відданий
    }

    // 3. Дочекатися фінального підтвердження.
    const uint8_t want_ack[] = { MAVLINK_MSG_ID_MISSION_ACK };
    if (!recv_match(want_ack, 1, &msg, 3.0)) {
        puts("завантаження: немає MISSION_ACK — борт не підтвердив"); return 0;
    }
    mavlink_mission_ack_t ack; mavlink_msg_mission_ack_decode(&msg, &ack);
    if (ack.type != MAV_MISSION_ACCEPTED) {           // ACCEPTED == 0
        printf("завантаження: борт відхилив, код MAV_MISSION_RESULT=%u\n", ack.type);
        return 0;
    }
    printf("завантаження: борт прийняв усі %u пунктів (ACK=ACCEPTED)\n", n);
    return 1;
}
```
:::

Прочитаймо це місце, де ховається краса. Ми **не** женемо пункти потоком у своєму темпі — ми **відповідаємо** на `seq`, який називає борт. Якщо запит на пункт не дійшов до нас (`recv_match` повернув «нічого»), ми не зависаємо: спрацьовує таймаут `0.25` с, ми рахуємо тишу й, щоб зрушити діалог, повторно шлемо `MISSION_COUNT` — це змушує борт заново попросити те, на чому він застряг. Якщо ж борт просить `seq`, який ми вже давали (бо **наш** попередній `ITEM_INT` загубився), ми спокійно віддаємо його **знову** — жодного стану «вже надіслано, більше не дам». Уся стійкість — у тому, що ми віддаємо **те, що просять, стільки разів, скільки просять**, поки не прийде `ACK`.

Порівняй це з наївним «`for it in mission: mission_item_int_send(...)`» (у C — той самий цикл `for` з `..._pack` і `send_msg`). Наївний варіант ігнорує запити борту зовсім, стріляє в порожнечу й сподівається. На SITL по локальному UDP (де втрат немає) він навіть спрацює — і саме тому так багато прикладів у мережі саме такі. Але на реальному радіо 57600 бод із втратами він збирає биту місію. Наш цикл працює **однаково** і там, і там.

## Крок 2: зчитати назад те, що реально в борті

Місію залито. Тепер — **головна страховка**: вивантажити її з борту й побачити на власні очі. Механіка дзеркальна до завантаження, тільки ролі помінялися: тепер **ми** оголошуємо намір читати (`MISSION_REQUEST_LIST`), борт відповідає `MISSION_COUNT`, а далі **ми** просимо кожен пункт і чекаємо `MISSION_ITEM_INT` — з тими самими таймаутами й повторами.

:::tabs
```py
def download_mission(master, timeout=0.25, max_retries=5):
    """Зчитати ПОТОЧНУ місію з борту. Повертає список MISSION_ITEM_INT або None."""
    # 1. Попросити борт назвати кількість.
    master.mav.mission_request_list_send(TSYS, TCMP, MTYPE)
    cnt = master.recv_match(type='MISSION_COUNT', blocking=True, timeout=3)
    if cnt is None:
        print("зчитування: борт не назвав MISSION_COUNT")
        return None
    n = cnt.count
    print(f"зчитування: борт каже, у нього {n} пунктів")

    # 2. Просити кожен seq по порядку, з таймаутом і обмеженим числом повторів.
    items = [None] * n
    for seq in range(n):
        tries = 0
        while True:
            master.mav.mission_request_int_send(TSYS, TCMP, seq, MTYPE)
            it = master.recv_match(type='MISSION_ITEM_INT',
                                   blocking=True, timeout=timeout)
            # приймаємо лише ТОЙ пункт, який просили (чужий seq — відкинути й перепитати)
            if it is not None and it.seq == seq:
                items[seq] = it
                break
            tries += 1
            if tries >= max_retries:
                print(f"зчитування: пункт #{seq} не приходить — здаюся")
                return None          # НЕ повертаємо частковий список — він бреше

    # 3. Закрити діалог підтвердженням (ввічливість + сигнал борту «все взяв»).
    master.mav.mission_ack_send(TSYS, TCMP,
                                mavutil.mavlink.MAV_MISSION_ACCEPTED, MTYPE)
    return items
```
```cpp
// Зчитати ПОТОЧНУ місію з борту в out[] (місткість cap). *out_n — скільки пунктів.
// 1 — успіх; 0 — не вдалося (і тоді out[] НЕ містить часткового списку — він бреше).
int download_mission(mavlink_mission_item_int_t *out, uint16_t cap, uint16_t *out_n) {
    mavlink_message_t msg;
    // 1. Попросити борт назвати кількість.
    mavlink_msg_mission_request_list_pack(SYSID, COMPID, &msg, TSYS, TCMP, MTYPE);
    send_msg(&msg);
    const uint8_t want_cnt[] = { MAVLINK_MSG_ID_MISSION_COUNT };
    if (!recv_match(want_cnt, 1, &msg, 3.0)) { puts("зчитування: немає MISSION_COUNT"); return 0; }
    mavlink_mission_count_t mc; mavlink_msg_mission_count_decode(&msg, &mc);
    uint16_t n = mc.count;
    if (n > cap) { puts("зчитування: місія більша за буфер"); return 0; }
    printf("зчитування: борт каже, у нього %u пунктів\n", n);

    // 2. Просити кожен seq по порядку, з таймаутом і обмеженим числом повторів.
    const uint8_t want_item[] = { MAVLINK_MSG_ID_MISSION_ITEM_INT };
    for (uint16_t seq = 0; seq < n; seq++) {
        int ok = 0;
        for (int tries = 0; tries < 5 && !ok; tries++) {
            mavlink_msg_mission_request_int_pack(SYSID, COMPID, &msg, TSYS, TCMP, seq, MTYPE);
            send_msg(&msg);
            mavlink_message_t r;
            if (recv_match(want_item, 1, &r, 0.25)) {   // таймаут рятує від вічного чекання
                mavlink_mission_item_int_t it; mavlink_msg_mission_item_int_decode(&r, &it);
                if (it.seq == seq) { out[seq] = it; ok = 1; }   // лише ТОЙ, що просили
            }
        }
        if (!ok) {                                      // здався — НЕ віддаємо частковий список
            printf("зчитування: пункт #%u не приходить — здаюся\n", seq); return 0;
        }
    }
    // 3. Закрити діалог підтвердженням (ввічливість + сигнал борту «все взяв»).
    mavlink_msg_mission_ack_pack(SYSID, COMPID, &msg, TSYS, TCMP, MAV_MISSION_ACCEPTED, MTYPE);
    send_msg(&msg);
    *out_n = n;
    return 1;
}
```
:::

Тут кожен рядок захисту несе вагу, і найважливіші — три. По-перше, **таймаут** на очікуванні пункту: у Python це `timeout=timeout` на `recv_match`, у C — той самий таймаут усередині `recv_match` через `select`. **Без** нього перший же загублений `ITEM_INT` підвісив би цикл назавжди («чекай, поки не прийде», а він може не прийти ніколи, бо при зчитуванні темп задаємо **ми**, і борт сам не повторить). По-друге, `it.seq == seq` (в обох мовах): борт міг надіслати не той пункт (запізнілу відповідь на попередній запит) — ми беремо **лише** очікуваний, чужий відкидаємо й перепитуємо. По-третє, і найголовніше: якщо після `max_retries` пункт так і не прийшов, ми повертаємо «нічого» (`None` / `0`), **а не** півсписок. Півсписок — це найгірше, що можна віддати наступному кроку: він виглядає як список, у нього можна тицьнути пальцем — і він **бреше** про вміст місії. Про цю пастку — окремо нижче, вона того варта.

## Крок 3: звірити зчитане з задумом

Список у руках. Тепер — момент істини: збігається він із тим, що ми **задумали**? І звіряти треба не з тим, що ми «мали б надіслати» (ту саму помилку, якщо вона в задумі, ми лише повторимо), а з **явним еталоном** — незалежним описом того, куди апарат має летіти.

:::tabs
```py
def decode_item(it):
    """MISSION_ITEM_INT → людські величини. Цілі 1e-7° → градуси."""
    return dict(
        seq=it.seq,
        command=it.command,
        lat=it.x * 1e-7,          # ЦІЛЕ 1e-7 градуса → градуси
        lon=it.y * 1e-7,
        alt=it.z,                 # метри — але в ЯКІЙ системі? каже it.frame
        frame=it.frame)

def verify_mission(items, expected, tol_m=0.5):
    """Звірити зчитану місію з еталоном. expected — список тих самих кортежів wp().
       Друкує таблицю; повертає True, якщо все збіглося в межах допуску."""
    # Пастка №3 у зародку: звіряти можна ЛИШЕ повний список.
    if items is None or len(items) != len(expected):
        got = 0 if items is None else len(items)
        print(f"звірка НЕМОЖЛИВА: зчитано {got}, а задумано {len(expected)} — "
              f"список неповний, будь-яка звірка тут бреше")
        return False

    print(f"{'#':>2}  {'команда':<16} {'lat':>12} {'lon':>12} "
          f"{'alt':>7} {'frame':>6}  результат")
    ok_all = True
    # 1 градус широти ≈ 111 111 м; для довготи множимо на cos(широти).
    import math
    DEG_M = 111_111.0
    for it, exp in zip(items, expected):
        d = decode_item(it)
        # горизонтальна відстань між зчитаним і задуманим, у метрах
        dlat_m = (d['lat'] - exp['x'] * 1e-7) * DEG_M
        dlon_m = (d['lon'] - exp['y'] * 1e-7) * DEG_M * math.cos(math.radians(d['lat']))
        dist_m = math.hypot(dlat_m, dlon_m)

        bad = []
        if d['command'] != exp['command']:      bad.append("команда")
        if d['frame']   != exp['frame']:        bad.append("frame(висота!)")
        if dist_m       > tol_m:                bad.append(f"зсув {dist_m:.2f}м")
        if abs(d['alt'] - exp['z']) > tol_m:    bad.append("висота")

        mark = "OK" if not bad else "✗ " + ", ".join(bad)
        if bad: ok_all = False
        print(f"{d['seq']:>2}  {d['command']:<16} {d['lat']:>12.7f} {d['lon']:>12.7f} "
              f"{d['alt']:>7.1f} {d['frame']:>6}  {mark}")
    return ok_all
```
```cpp
// Звірити зчитану місію з еталоном. 1 — усе збіглося в межах допуску.
// Цілі 1e-7° декодуються назад у градуси прямо тут, множенням на 1e-7.
int verify_mission(const mavlink_mission_item_int_t *items, int n_read,
                   const wp_t *expected, int n_exp, double tol_m) {
    // Пастка №3 у зародку: звіряти можна ЛИШЕ повний список.
    if (n_read != n_exp) {
        printf("звірка НЕМОЖЛИВА: зчитано %d, а задумано %d — "
               "список неповний, будь-яка звірка тут бреше\n", n_read, n_exp);
        return 0;
    }
    printf("%2s  %-16s %12s %12s %7s %6s  результат\n",
           "#", "команда", "lat", "lon", "alt", "frame");
    const double DEG_M = 111111.0;      // 1° широти ≈ 111 111 м
    int ok_all = 1;
    for (int i = 0; i < n_exp; i++) {
        const mavlink_mission_item_int_t *it = &items[i];
        double lat = it->x * 1e-7, lon = it->y * 1e-7;   // ЦІЛЕ 1e-7° → градуси
        // горизонтальна відстань між зчитаним і задуманим, у метрах (для довготи — ×cos)
        double dlat_m = (it->x - expected[i].x) * 1e-7 * DEG_M;
        double dlon_m = (it->y - expected[i].y) * 1e-7 * DEG_M * cos(lat * M_PI / 180.0);
        double dist_m = hypot(dlat_m, dlon_m);

        char why[64] = ""; int bad = 0;
        if (it->command != expected[i].command) { bad = 1; strcat(why, "команда "); }
        if (it->frame   != expected[i].frame)   { bad = 1; strcat(why, "frame(висота!) "); }
        if (dist_m      > tol_m)                { bad = 1; strcat(why, "зсув "); }
        if (fabs(it->z - expected[i].z) > tol_m){ bad = 1; strcat(why, "висота "); }
        if (bad) ok_all = 0;
        printf("%2u  %-16u %12.7f %12.7f %7.1f %6u  %s\n",
               it->seq, it->command, lat, lon, (double)it->z, it->frame,
               bad ? why : "OK");
    }
    return ok_all;
}
```
:::

Три речі, які ця звірка ловить і які **не видно** на екрані наземної станції. **Координати** — декодовані з цілих назад у градуси й порівняні за реальною відстанню в метрах (а не «чи однакові числа»: два майже однакові числа можуть різнитися на метри). **Система висоти** (`frame`) — бо `30` у кадрі «над стартом» і `30` у кадрі «над рівнем моря» — це різниця в сотні метрів, і плутанина кадрів дає найтихіші, найнебезпечніші помилки (детальний розбір цифри — в основній статті). **Висота** — саме число `alt` (`z`). Порівняння за **відстанню з допуском** `tol_m` замість точної рівності — теж свідоме: після кругообігу через борт число може відрізнятися в останньому знаку, і жорстке `==` дало б хибну тривогу; піврозмаху метра допуску досить, щоб спіймати справжню помилку й не чіплятися до шуму.

Тепер зберімо весь конвеєр в один прохід — саме так ти його й запускатимеш перед польотом. У Python зʼєднання вже стоїть на модульному рівні (Крок 0), тож драйвер — це блок `__main__`; у C воно живе у функціях, тож `main` спершу відкриває сокет і чекає `HEARTBEAT`, а тоді жене той самий ланцюг:

:::tabs
```py
if __name__ == '__main__':
    if not upload_mission(master, mission):
        raise SystemExit("завантаження провалилося — не армимося")

    readback = download_mission(master)
    if not verify_mission(readback, mission):
        raise SystemExit("звірка не збіглася — НЕ армимося, шукаємо різницю")

    print("\nмісія на борті збігається із задумом — можна армитися.")
```
```cpp
int main(void) {
    open_udp("0.0.0.0", 14550);          // слухати SITL / телеметрію
    wait_heartbeat();                    // дізнатися TSYS/TCMP
    build_mission();

    if (!upload_mission(mission, N)) {
        fputs("завантаження провалилося — не армимося\n", stderr); return 1;
    }

    mavlink_mission_item_int_t readback[64]; uint16_t got = 0;
    if (!download_mission(readback, 64, &got)) {
        fputs("не зчиталося — не армимося\n", stderr); return 1;
    }
    if (!verify_mission(readback, got, mission, N, 0.5)) {
        fputs("звірка не збіглася — НЕ армимося, шукаємо різницю\n", stderr); return 1;
    }

    puts("\nмісія на борті збігається із задумом — можна армитися.");
    return 0;
}
```
:::

Логіка «або-або» тут не для краси. Провалилося завантаження — виходимо, не читаємо. Не збіглася звірка — виходимо гучно (Python `raise`, C — код повернення `1` і повідомлення в `stderr`), **не** дозволяючи собі жодного `arm`. Скрипт мовчки завершується успіхом **лише** тоді, коли борт підтвердив прийом **і** зчитане назад збіглося з еталоном пункт за пунктом. Оце і є «дві хвилини звірки, що економлять апарат».

## Крок 4: живий монітор прогресу в польоті

Місія залита й звірена, ти армився й дав старт у режимі `AUTO`. Тепер — четвертий шматок, який перетворює спостереження за апаратом здалеку на **читання його думок**: борт сам повідомляє, на якому пункті він зараз. Два повідомлення: `MISSION_CURRENT` (поточний активний `seq`) і `MISSION_ITEM_REACHED` (щойно досягнув пункт — переходить далі).

:::tabs
```py
def monitor_mission(master):
    """Живий монітор: показує активний пункт і момент його досягнення.
       Крутити паралельно польоту; Ctrl-C — вихід."""
    last_seq = None
    while True:
        msg = master.recv_match(
            type=['MISSION_CURRENT', 'MISSION_ITEM_REACHED'],
            blocking=True, timeout=1.0)
        if msg is None:
            print("… тиша від борту — перевір лінк")
            continue

        if msg.get_type() == 'MISSION_CURRENT':
            if msg.seq != last_seq:                  # індекс зрушив — покажемо перехід
                print(f"→ активний пункт місії: #{msg.seq}")
                last_seq = msg.seq
        else:  # MISSION_ITEM_REACHED
            print(f"  ✓ досягнуто #{msg.seq} — борт переходить далі")
```
```cpp
// Живий монітор: показує активний пункт і момент його досягнення.
// Крутити паралельно польоту; Ctrl-C — вихід.
void monitor_mission(void) {
    uint16_t last_seq = 0xFFFF;
    const uint8_t want[] = { MAVLINK_MSG_ID_MISSION_CURRENT,
                             MAVLINK_MSG_ID_MISSION_ITEM_REACHED };
    for (;;) {
        mavlink_message_t msg;
        if (!recv_match(want, 2, &msg, 1.0)) { puts("… тиша від борту — перевір лінк"); continue; }

        if (msg.msgid == MAVLINK_MSG_ID_MISSION_CURRENT) {
            mavlink_mission_current_t mc; mavlink_msg_mission_current_decode(&msg, &mc);
            if (mc.seq != last_seq) {                // індекс зрушив — покажемо перехід
                printf("→ активний пункт місії: #%u\n", mc.seq);
                last_seq = mc.seq;
            }
        } else {  // MISSION_ITEM_REACHED
            mavlink_mission_item_reached_t mr; mavlink_msg_mission_item_reached_decode(&msg, &mr);
            printf("  ✓ досягнуто #%u — борт переходить далі\n", mr.seq);
        }
    }
}
```
:::

Чому це саме той інструмент, який тобі найбільше знадобиться. Найчастіший збій першої автономної місії — «апарат намотує кола біля точки й не йде далі». Дивлячись на нього в небі, ти не знаєш, він «думає» чи завис. Монітор дає точний діагноз: якщо в консолі `активний пункт #2` застиг і `ITEM_REACHED #2` **не** приходить — значить, умова переходу з #2 недосяжна (класична пастка малого `WP_RADIUS` на швидкому підході, розібрана в основній статті). Ти бачиш не «дрон дурний», а конкретне «перехід #2 → #3 не спрацьовує» — і знаєш, що крутити: радіус влучення чи швидкість підходу.

> 🔧 **Навіщо це.** Пам'ять обманює, монітор — ні. Після прогону ти [розбереш повний лог](root:embedded/flight-log-analysis) — але **під час** прогону саме цей живий потік дає тобі змогу перехопити керування вчасно: бачиш, що місія застрягла чи пішла не туди, — смикаєш перемикач режиму (він [вищий за `AUTO`](root:embedded/mavlink-from-ground)) і повертаєш апарат собі, поки він не наробив біди. Монітор — це твої очі всередині автомата місії в реальному часі.

## Складність і пастки: де це валиться навіть у тих, хто «все зробив»

Скрипт вище виглядає прямолінійно, і в цьому небезпека: кожна його захисна деталь стоїть на місці **загиблого апарата** чи згаяної години. Розберемо чотири пастки, у які провалюються навіть уважні — бо перші три тихі: код без них **працює** на столі й ламається в полі.

![Три тихі пастки завантажувача — координата у float, брак таймауту, звірка часткового списку — і як їх обходить робочий код](/root/course/embedded/capstone-autonomous-mission/img/three-traps.svg)
*Кожна пастка тиха: код без запобіжника відпрацьовує без помилки на локальному SITL — і зраджує в полі. Ліворуч: координата у `float` округляється до ~метра ще на землі, до будь-якої передачі. Посередині: очікування без `timeout` висне назавжди на першому ж загубленому пакеті. Праворуч: звірка часткового списку «збігається» на тих кількох пунктах, що зчиталися, — і мовчить про решту. Праворуч у кожній колонці — рядок коду, яким робочий скрипт цю пастку знімає.*

### Пастка 1: координата, що побувала в `float`

Найпідступніша, бо вона **не** в протоколі — вона у **твоєму** коді, ще до відправки. Уяви, ти читаєш точки з CSV:

:::tabs
```py
lat = float(row[0])                        # ← float64 Python тут рятує, але...
...
master.mav.mission_item_int_send(..., int(lat * 1e7), ...)
```
```cpp
float lat = atof(row[0]);                  // ← float у C — ПРЯМО 32-бітний: зіпсовано тут
...
mavlink_msg_mission_item_int_pack(..., (int32_t)(lat * 1e7), ...);
```
:::

Здавалося б, ти чесно множиш на `1e7` і віддаєш ціле — `_INT`-протокол дотримано. Але координата **вже** пройшла через `float`. У Python тип подвійної точності (`float64`) тут насправді рятує; а от у C `float` — це прямо той **32-бітний** тип, і саме він усюди, де координата йде через 32-бітну плаваючу кому (а таких бібліотек і форматів повно): крок між представними числами на наших широтах сягає ~метра (детальне виведення цієї цифри — в основній статті капстоуна). Ти вносиш метрову похибку **власноруч**, і жоден `_INT` тебе не врятує: зіпсовано ще до множення. Для точної посадки чи зйомки з перекриттям метр — це катастрофа.

**Ліки** — залізне правило: тримай координату **цілою** в одиницях `1e-7` градуса від зчитування до відправки; у градуси переводь **лише** для друку людині. Саме тому в нашому `wp()` перетворення в ціле (`int(round(...))` / `lround(...)`) стоїть **один раз**, при складанні пункту, а не розсипане по коду; далі `x` уже ціле й таким і летить. Читаєш із CSV, де вже записано цілі, — ще краще: не чіпай їх плаваючою комою взагалі.

### Пастка 2: очікування без таймауту — вічне зависання

Друга пастка вбиває не апарат, а твій вечір. Скрізь, де ти чекаєш відповідь від борту, спокуса написати найпростіше — «просто чекай, поки прийде»:

:::tabs
```py
it = master.recv_match(type='MISSION_ITEM_INT', blocking=True)   # ← без timeout
```
```cpp
uint8_t b; mavlink_message_t msg; mavlink_status_t st;
do { recv(sock, &b, 1, 0); }                      // ← recv без таймауту: блокує вічно
while (!mavlink_parse_char(MAVLINK_COMM_0, b, &msg, &st));   // ← кадр може не прийти НІКОЛИ
```
:::

На SITL по локальному UDP це працює: пакети не губляться, відповідь завжди приходить. Але на реальному радіо один загублений `MISSION_ITEM_INT` — і «чекай, доки прийде» означає саме «чекай вічно»: борт відповів один раз, ти пакет проґавив, борт більше сам не повторить (бо при зчитуванні темп задаєш **ти**). Скрипт висне мертво, апарат стоїть армований, ти дивишся на нерухому консоль і не розумієш, що сталося.

**Ліки** — `timeout` на **кожному** очікуванні, і **лічильник повторів** навколо. У Python це `recv_match(..., timeout=timeout)`; у C — той самий дедлайн через `select` усередині нашого `recv_match`, плюс `tries < max_retries`: тиша за 250 мс — повторюємо запит; п'ять тиш поспіль — здаємося з чесним повідомленням, а не висимо. Таймаут перетворює «зависло назавжди, невідомо чому» на «пункт #3 не приходить за 5 спроб — ось діагноз».

### Пастка 3: звірка часткового списку, яка бреше

Третя пастка — найковарніша, бо вона прикидається **успіхом**. Уяви, зчитування обірвалося на трьох пунктах із шести (радіо просіло), а код звірки написано наївно:

:::tabs
```py
for it, exp in zip(items, expected):       # ← zip мовчки береться за коротший!
    ...                                     # звірили 3 пункти, усі збіглися → «OK»
```
```cpp
for (int i = 0; i < n_read; i++)           // ← циклимо по ЗЧИТАНИХ, а не по задуманих
    compare(items[i], expected[i]);        // звірили 3 з 6 → усі 3 «OK», решту не помітили
```
:::

Механізм тихий в обох мовах, лише спелінг різний. Python-івський `zip` зупиняється на **коротшому** зі списків; C-шний `for` по `n_read` циклить рівно стільки, скільки пунктів реально зчиталося. Зчиталося три — пройде три, усі три збіжаться (бо це справді перші три твоєї місії), і цикл радісно доповість «усе гаразд». А пунктів #3, #4, #5 (зокрема `RTL`!) на борті може не бути зовсім або вони можуть бути старі — і ти цього **не дізнаєшся**. Ти армишся з думкою, що звірив місію, а звірив половину.

**Ліки** — **перш ніж** будь-що звіряти, переконатися, що список **повний**: `len(items) == len(expected)` у Python, `n_read == n_exp` у C (і що список узагалі є). У нашому `verify_mission` це буквально перша перевірка, і при розбіжності — гучна відмова, а не тиха звірка. І в парі з нею — те, що `download_mission` **ніколи** не повертає частковий список: не зміг дочитати — повертає «нічого» (`None` / `0`). Дві ці перевірки замикають діру: частковий результат або не існує, або відсіюється на вході звірки. Звірка бреше рівно тоді, коли ти дозволяєш їй працювати з неповними даними, — тож не дозволяй.

### Пастка 4: неузгоджена система висоти (`frame`)

Четверта пастка не тиха — вона **видима**, якщо дивитися, — але її легко проґавити, бо на екрані наземної станції число висоти виглядає правильним. Пункт містить не лише число `z`, а й поле `frame` — **над чим** ці метри. Три звичні варіанти:

- `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT` — метри над **точкою старту** (найзвичніше; `15` = 15 м над майданчиком).
- `MAV_FRAME_GLOBAL_INT` — метри над **рівнем моря**. Якщо майданчик на 180 м над морем, то `15` тут — це «на 165 м **під** майданчиком», тобто в землю.
- `MAV_FRAME_GLOBAL_TERRAIN_ALT_INT` — метри над **рельєфом** під точкою (за картою висот).

Число однакове — `15`, — а поведінка різниться на сотні метрів. І є ще тонкість, що переслідує чужі приклади: у пунктах місій треба вживати `_INT`-варіанти кадрів (`..._RELATIVE_ALT_INT`, а **не** `..._RELATIVE_ALT`) — інакше координати трактуються як float, і ти вертаєшся в пастку 1.

**Ліки** — саме тому наша `verify_mission` звіряє **і** `alt`, **і** `frame` окремо, а декодування пункту завжди друкує номер кадру. Ти бачиш на землі не лише «висота 15», а «висота 15, кадр 6 (relative)» — і одразу помічаєш, якщо задум був абсолютний, а в борті relative (чи навпаки). Це та перевірка, якої на екрані GCS немає, а в нашому роздруку — є.

---

Збери чотири запобіжники разом — і скрипт із «працює в мене на симуляторі» стає таким, що працює на **реальному** борті через **реальне** радіо й **чесно** каже тобі перед стартом, чи можна армитися. Кожна захисна деталь — ціле замість `float`, `timeout` на кожному очікуванні, `len == len` перед звіркою, окрема перевірка `frame` — стоїть на місці конкретної тихої помилки, яка інакше вилізла б у полі, де вона коштує апарата. І байдуже, якою мовою ти це пишеш: на pymavlink за ноутбуком чи на MAVLink C library у прошивці — стан-машина «запит → чекай із таймаутом → підтвердь або повтори» й чотири запобіжники ті самі. Це і є різниця між кодом, що «надсилає місію», і кодом, якому можна довірити свій капстоун.
