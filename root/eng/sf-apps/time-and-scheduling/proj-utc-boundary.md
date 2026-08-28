# ⚙️ Обіг через межу: настінний час → мить → база → напис назад

Ось повний код одного обігу часу в сервісі нагадувань — від поля форми до рядка в базі й назад до напису на екрані кожного читача, — і разом із ним два дні на рік, коли переклад «настінний час → мить» дає не одну відповідь, а жодної або дві.

---

## Що має працювати

Оксана в Києві створює нагадування на 25 жовтня 2026 року, 03:30. Ярема в Токіо доданий до цього нагадування спостерігачем: у своєму списку він має побачити ту саму подію, підписану своїм годинником. Наприкінці місяця Оксана відкриває звіт «що спрацювало 25 жовтня» — за свою добу, а не за добу сервера.

Сервер стоїть у Франкфурті, база — у Вірджинії, розробник відкриває ноутбук у Львові. Жоден із цих трьох поясів не має стосунку до жодної з трьох відповідей — і саме тому так легко не помітити, як вони туди потрапляють: пояс процесу бібліотеки підставляють мовчки, коли ви не сказали, який брати.

## Дві межі й чисте ядро

Усередині сервіс оперує лише миттями: `number` мілісекунд, `Instant`, `datetime` з `tzinfo=UTC`. Мить не має зони й не потребує її — це точка на світовій осі. Настінний час живе рівно у двох місцях: там, де розбирають ввід, і там, де малюють вивід. Між ними його немає взагалі.

Звідси інваріант, який варто вміти перевіряти оглядом коду: **у ядрі не існує настінного значення без зони поруч**. Якщо десь у сервісному шарі з'явився `LocalDateTime`, наївний `datetime` чи рядок `"2026-10-25 03:30"` без сусіднього поля зони, — це вже помилка, просто ще не спрацювала.

Далі три шматки коду по одному на ділянку обігу: вхідна межа, сховище, вихідна межа. Потім окремо звіт — бо «доба користувача» виявиться не одиницею часу, а проміжком митей, і не завжди двадцятичотиригодинним.

## Вхідна межа: рядок без зони — ще не час

Найкоротший шлях від форми до бази виглядає так: узяти рядок з тіла запиту й дати його конструкторові дати. Ось що з цього виходить.

**Пастка: рядок без зони мовчки бере пояс процесу.**

```
рядок із форми:   "2026-06-01T09:00"      (людина мала на увазі Київ)

у контейнері без змінної TZ (UTC):  → 2026-06-01T09:00Z
на сервері у Франкфурті (+02:00):   → 2026-06-01T07:00Z
на ноутбуці розробника (+03:00):    → 2026-06-01T06:00Z  ← випадково правильно
```

Один рядок дає три різні миті — розбіжність до трьох годин, залежно від того, де запустили процес. Найгірше тут не сама помилка, а те, що на машині розробника її не видно: його ноутбук стоїть у тому самому поясі, що й тестовий користувач, тож локально все сходиться. Розходитися воно починає рівно при переїзді в продакшн і виглядає як «нагадування приходять не тоді».

Ліки — сувора вимога до підпису функції: **переклад не має права дивитися на пояс процесу**. Зона приходить окремим аргументом і подорожує в парі з настінним часом, від браузера до бази. Тіло запиту виглядає так:

```json
{ "local": "2026-10-25T03:30", "zone": "Europe/Kyiv" }
```

Клієнт бере назву зони не з припущень, а з системи: у браузері це `Intl.DateTimeFormat().resolvedOptions().timeZone`. Зсув `+03:00` у тілі запиту не потрібен — він виводиться з пари «настінний час + зона», а от зворотний вивід неможливий: зі зсуву зони не дістати.

### Переклад — це не функція

Тепер головне про вхідну межу. Пара «настінний час + зона» не завжди дає одну мить.

```
Europe/Kyiv, 2026 (за правилами чинної tz-бази)

29 березня, 01:00 UTC:   03:00 (+02:00)  →  04:00 (+03:00)
    настінних 03:00…03:59 того дня не існує — жодної миті
25 жовтня,  01:00 UTC:   04:00 (+03:00)  →  03:00 (+02:00)
    настінні 03:00…03:59 трапляються двічі — дві миті
```

Оксанине нагадування на 03:30 впало рівно в друге вікно. Йому відповідають дві миті: `2026-10-25T00:30Z` і `2026-10-25T01:30Z`, між ними година реального часу, і обидві мають повне право називатися «25 жовтня, 03:30 за Києвом».

Ці вікна не завжди годинні й не завжди нічні. На острові Лорд-Гау (Lord Howe, зона `Australia/Lord_Howe`) стрілки переводять на пів години: 4 жовтня 2026 року настінних 02:00…02:29 не існує, а 5 квітня настінні 01:30…01:59 трапляються двічі. У Сантьяго (`America/Santiago`) стрибок припадає на північ: 6 вересня 2026 року місцевої 00:00 просто не буває — і код, що будує «початок доби» як 00:00, дістає неіснуючий час на рівному місці.

Отже, у функції перекладу три можливі відповіді, і разом із миттю вона мусить повертати, яка з трьох це була:

- **одна мить** — звичайний випадок;
- **діра**: жодної миті. Розумна політика — зсунути вперед на довжину діри, тобто взяти зсув, що діяв *до* переходу. Для 03:30 у Києві це дасть 04:30;
- **накладання**: дві миті. Розумна політика — узяти першу, тобто знову той зсув, що діяв *до* переходу.

Обидві політики — одне правило: **бери зсув, що діяв до переходу**. Це не збіг. У дірі зсув зростає, тож менший (доперехідний) зсув відносить мить далі вперед; у накладанні зсув спадає, тож більший (доперехідний) зсув дає раніше з двох входжень. Одна фраза покриває обидва дні на рік.

Лишається механіка: як узагалі дізнатися, який зсув діяв до переходу, не маючи доступу до таблиці переходів? Через саму зону. Візьміть зсув, що діє за добу *до* цього настінного часу, і зсув, що діє за добу *після*: між ними лежать усі зсуви, які тут узагалі можливі, бо двічі на добу правила не міняються. Кожен із них дає кандидата-мить. Кандидат дійсний тоді й лише тоді, коли зона на цій миті показує саме той зсув, з якого його порахували, — тобто напис повертається сам у себе. Дійсних кандидатів рівно стільки, скільки відповідей: нуль, один або два.

:::tabs
```ts
// Межа: настінний час ↔ мить. Тільки стандартний Intl, без залежностей.
type Wall = { y: number; mo: number; d: number; h: number; mi: number };
type Kind = "exact" | "gap" | "ambiguous";
type Resolved = { instant: number; kind: Kind };   // instant — мілісекунди епохи

const MINUTE = 60_000;
const DAY = 24 * 60 * MINUTE;

// Побудова форматувальника коштує на порядок дорожче за саме форматування — кешуємо.
const fmtCache = new Map<string, Intl.DateTimeFormat>();
function cachedFmt(key: string, make: () => Intl.DateTimeFormat): Intl.DateTimeFormat {
  let f = fmtCache.get(key);
  if (!f) { f = make(); fmtCache.set(key, f); }
  return f;
}

/** Зсув зони для КОНКРЕТНОЇ миті: читаємо мить у зоні й дивимось,
 *  наскільки цей напис розійшовся з написом у UTC. */
function zoneOffset(instant: number, zone: string): number {
  const p = cachedFmt("parts|" + zone, () => new Intl.DateTimeFormat("en-GB", {
    timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  })).formatToParts(new Date(instant));
  const g = (t: string) => Number(p.find((x) => x.type === t)!.value);
  const asUTC = Date.UTC(g("year"), g("month") - 1, g("day"),
                         g("hour"), g("minute"), g("second"));
  return asUTC - Math.floor(instant / 1000) * 1000;
}

/** Настінний час + зона → мить. Каже, скільки відповідей насправді було. */
function resolveLocal(w: Wall, zone: string): Resolved {
  const asIfUTC = Date.UTC(w.y, w.mo - 1, w.d, w.h, w.mi);
  // єдині два зсуви, які тут узагалі можуть діяти
  const before = zoneOffset(asIfUTC - DAY, zone);
  const after = zoneOffset(asIfUTC + DAY, zone);

  const valid: number[] = [];
  for (const off of before === after ? [before] : [before, after]) {
    const t = asIfUTC - off;
    if (zoneOffset(t, zone) === off) valid.push(t);   // напис повернувся сам у себе
  }
  if (valid.length === 1) return { instant: valid[0], kind: "exact" };
  if (valid.length === 2) return { instant: Math.min(...valid), kind: "ambiguous" };
  return { instant: asIfUTC - Math.min(before, after), kind: "gap" };
}

/** Мить → напис у зоні читача: «2026-10-25 03:30 GMT+03:00». */
function formatInZone(instant: number, zone: string): string {
  return cachedFmt("out|" + zone, () => new Intl.DateTimeFormat("sv-SE", {
    timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", timeZoneName: "longOffset",
  })).format(new Date(instant));
}

/** Півзакритий проміжок [від, до) — доба користувача на осі митей. */
function dayBounds(y: number, mo: number, d: number, zone: string): [number, number] {
  const next = new Date(Date.UTC(y, mo - 1, d + 1));   // межу місяця й року перескочить саме
  return [
    resolveLocal({ y, mo, d, h: 0, mi: 0 }, zone).instant,
    resolveLocal({ y: next.getUTCFullYear(), mo: next.getUTCMonth() + 1,
                   d: next.getUTCDate(), h: 0, mi: 0 }, zone).instant,
  ];
}
```
```python
# -*- coding: utf-8 -*-
"""Межа: настінний час ↔ мить. Стандартна бібліотека, Python 3.9+."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def resolve_local(wall: datetime, zone: str) -> tuple[datetime, str]:
    """wall — НАЇВНИЙ настінний час (без tzinfo). Мить у UTC і вид збігу."""
    tz = ZoneInfo(zone)
    before = wall.replace(tzinfo=tz, fold=0)   # зсув, що діяв ДО переходу
    after = wall.replace(tzinfo=tz, fold=1)    # зсув, що діє ПІСЛЯ
    instant = before.astimezone(UTC)

    if before.utcoffset() == after.utcoffset():
        return instant, "exact"
    if instant.astimezone(tz).replace(tzinfo=None) != wall:
        return instant, "gap"          # напис не повернувся сам у себе
    return instant, "ambiguous"        # обидва прочитання дійсні, узяли перше


def format_in_zone(instant: datetime, zone: str) -> str:
    """Мить → напис у зоні читача: «2026-10-25 03:30 +0300»."""
    return instant.astimezone(ZoneInfo(zone)).strftime("%Y-%m-%d %H:%M %z")


def day_bounds(day: date, zone: str) -> tuple[datetime, datetime]:
    """Півзакритий проміжок [від, до) — доба користувача на осі митей."""
    lo, _ = resolve_local(datetime.combine(day, time(0, 0)), zone)
    hi, _ = resolve_local(datetime.combine(day + timedelta(days=1), time(0, 0)), zone)
    return lo, hi
```
```java
// Межа: настінний час ↔ мить. java.time, без залежностей.
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.time.zone.ZoneRules;
import java.util.List;

enum Kind { EXACT, GAP, AMBIGUOUS }

record Resolved(Instant instant, Kind kind) {}

final class Boundary {
    private static final DateTimeFormatter OUT =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm XXX");

    /** wall — настінний час без зони. Каже, скільки митей йому відповідало. */
    static Resolved resolveLocal(LocalDateTime wall, String zone) {
        ZoneRules rules = ZoneId.of(zone).getRules();
        List<ZoneOffset> valid = rules.getValidOffsets(wall);
        if (valid.size() == 1)
            return new Resolved(wall.toInstant(valid.get(0)), Kind.EXACT);
        // два дійсні зсуви — перший у списку той, що діяв ДО переходу
        if (valid.size() == 2)
            return new Resolved(wall.toInstant(valid.get(0)), Kind.AMBIGUOUS);
        // порожньо — діра; ZonedDateTime.of сам зсуває вперед на її довжину
        return new Resolved(ZonedDateTime.of(wall, ZoneId.of(zone)).toInstant(), Kind.GAP);
    }

    /** Мить → напис у зоні читача: «2026-10-25 03:30 +03:00». */
    static String formatInZone(Instant instant, String zone) {
        return instant.atZone(ZoneId.of(zone)).format(OUT);
    }

    /** Півзакритий проміжок [від, до) — доба користувача на осі митей. */
    static Instant[] dayBounds(LocalDate day, String zone) {
        return new Instant[] {
            resolveLocal(day.atStartOfDay(), zone).instant(),
            resolveLocal(day.plusDays(1).atStartOfDay(), zone).instant()
        };
    }
}
```
```c
/* Межа: настінний час ↔ мить, ISO-8601 та високосні секунди на C99. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

enum resolve_kind {
    RESOLVE_EXACT,
    RESOLVE_GAP,
    RESOLVE_AMBIGUOUS
};

struct wall_time {
    int year;
    int month;   /* 1..12 */
    int day;     /* 1..31 */
    int hour;    /* 0..23 */
    int minute;  /* 0..59 */
    int second;  /* 0..60 (60 = високосна секунда) */
    int ms;      /* 0..999 */
    bool is_leap_second;
};

struct resolved_time {
    int64_t instant_epoch_ms;
    enum resolve_kind kind;
};

struct iso8601_parsed {
    struct wall_time wall;
    int offset_minutes;
    bool has_offset;
    bool is_utc;
    bool valid;
};

/* Алгоритм перетворення календарних днів у мить від епохи 1970-01-01 */
static inline int64_t days_from_civil(int y, unsigned m, unsigned d) {
    y -= m <= 2;
    const int64_t era = (y >= 0 ? y : y - 399) / 400;
    const unsigned yoe = (unsigned)(y - era * 400);
    const unsigned doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
    const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (int64_t)doe - 719468;
}

static inline void civil_from_days(int64_t z, int *y, unsigned *m, unsigned *d) {
    z += 719468;
    const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const unsigned doe = (unsigned)(z - era * 146097);
    const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    const int y_candidate = (int)yoe + (int)era * 400;
    const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const unsigned mp = (5 * doy + 2) / 153;
    *d = doy - (153 * mp + 2) / 5 + 1;
    *m = mp < 10 ? mp + 3 : mp - 9;
    *y = y_candidate + (*m <= 2);
}

static inline bool is_leap_year(int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

static inline int days_in_month(int y, int m) {
    static const int d[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2 && is_leap_year(y)) return 29;
    return (m >= 1 && m <= 12) ? d[m - 1] : 0;
}

/* Імітація читання таблиці переходів зони для миті UTC */
static int64_t zone_offset_ms(int64_t instant_ms, const char *zone) {
    if (strcmp(zone, "Europe/Kyiv") == 0) {
        /* Межі літнього часу 2026: 29 березня 01:00Z .. 25 жовтня 01:00Z */
        int64_t march_trans = days_from_civil(2026, 3, 29) * 86400000LL + 3600000LL;
        int64_t oct_trans   = days_from_civil(2026, 10, 25) * 86400000LL + 3600000LL;
        if (instant_ms >= march_trans && instant_ms < oct_trans) {
            return 3 * 3600000LL; /* UTC+3 */
        }
        return 2 * 3600000LL;     /* UTC+2 */
    }
    if (strcmp(zone, "Asia/Tokyo") == 0) {
        return 9 * 3600000LL;     /* UTC+9 */
    }
    return 0;
}

/* Парсер рядка ISO-8601 з перевіркою коректності та підтримкою 60-ї секунди */
struct iso8601_parsed parse_iso8601(const char *str) {
    struct iso8601_parsed res;
    memset(&res, 0, sizeof(res));
    if (!str) return res;

    int y = 0, mo = 0, d = 0, h = 0, mi = 0, s = 0;
    int off_h = 0, off_mi = 0;
    char tz_sign = '\0';

    int matched = sscanf(str, "%4d-%2d-%2dT%2d:%2d:%2d", &y, &mo, &d, &h, &mi, &s);
    if (matched < 5) return res;

    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo)) return res;
    if (h < 0 || h > 23 || mi < 0 || mi > 59) return res;
    if (s < 0 || s > 60) return res;

    res.wall.year = y;
    res.wall.month = mo;
    res.wall.day = d;
    res.wall.hour = h;
    res.wall.minute = mi;
    res.wall.second = (s == 60) ? 59 : s;
    res.wall.ms = 0;
    res.wall.is_leap_second = (s == 60);

    const char *tz_ptr = strchr(str, 'Z');
    if (tz_ptr) {
        res.is_utc = true;
        res.has_offset = true;
        res.offset_minutes = 0;
    } else if ((tz_ptr = strchr(str, '+')) || (tz_ptr = strrchr(str, '-'))) {
        if (sscanf(tz_ptr, "%c%2d:%2d", &tz_sign, &off_h, &off_mi) >= 2) {
            res.has_offset = true;
            res.offset_minutes = (off_h * 60 + off_mi) * (tz_sign == '-' ? -1 : 1);
        }
    }
    res.valid = true;
    return res;
}

/* Настінний час + назва зони → мить і тип розв'язку */
struct resolved_time resolve_local(struct wall_time w, const char *zone) {
    int64_t days = days_from_civil(w.year, (unsigned)w.month, (unsigned)w.day);
    int64_t as_if_utc = days * 86400000LL + (int64_t)w.hour * 3600000LL 
                        + (int64_t)w.minute * 60000LL + (int64_t)w.second * 1000LL + w.ms;
    const int64_t day_ms = 86400000LL;

    int64_t before = zone_offset_ms(as_if_utc - day_ms, zone);
    int64_t after  = zone_offset_ms(as_if_utc + day_ms, zone);

    int64_t valid_instants[2];
    int valid_count = 0;

    int64_t candidate1 = as_if_utc - before;
    if (zone_offset_ms(candidate1, zone) == before) {
        valid_instants[valid_count++] = candidate1;
    }

    if (before != after) {
        int64_t candidate2 = as_if_utc - after;
        if (zone_offset_ms(candidate2, zone) == after) {
            valid_instants[valid_count++] = candidate2;
        }
    }

    struct resolved_time res;
    if (valid_count == 1) {
        res.instant_epoch_ms = valid_instants[0];
        res.kind = RESOLVE_EXACT;
    } else if (valid_count == 2) {
        res.instant_epoch_ms = (valid_instants[0] < valid_instants[1]) ? valid_instants[0] : valid_instants[1];
        res.kind = RESOLVE_AMBIGUOUS;
    } else {
        int64_t min_off = (before < after) ? before : after;
        res.instant_epoch_ms = as_if_utc - min_off;
        res.kind = RESOLVE_GAP;
    }
    return res;
}

/* Форматування миті в настінний напис читача */
void format_in_zone(int64_t instant_ms, const char *zone, char *buf, size_t buf_size) {
    int64_t off = zone_offset_ms(instant_ms, zone);
    int64_t local_ms = instant_ms + off;
    int64_t days = local_ms / 86400000LL;
    int64_t time_ms = local_ms % 86400000LL;
    if (time_ms < 0) { days--; time_ms += 86400000LL; }

    int y; unsigned m, d;
    civil_from_days(days, &y, &m, &d);
    int h = (int)(time_ms / 3600000LL);
    int mi = (int)((time_ms % 3600000LL) / 60000LL);
    int s = (int)((time_ms % 60000LL) / 1000LL);

    int off_min = (int)(off / 60000LL);
    char sign = (off_min >= 0) ? '+' : '-';
    if (off_min < 0) off_min = -off_min;

    snprintf(buf, buf_size, "%04d-%02u-%02u %02d:%02d:%02d %c%02d:%02d",
             y, m, d, h, mi, s, sign, off_min / 60, off_min % 60);
}

/* Обчислення меж календарної доби користувача на осі митей */
void day_bounds(int y, int mo, int d, const char *zone, int64_t *out_start, int64_t *out_end) {
    struct wall_time w_start = { .year = y, .month = mo, .day = d, .hour = 0, .minute = 0, .second = 0, .ms = 0, .is_leap_second = false };
    int64_t next_days = days_from_civil(y, (unsigned)mo, (unsigned)d) + 1;
    int ny; unsigned nm, nd;
    civil_from_days(next_days, &ny, &nm, &nd);
    struct wall_time w_end = { .year = ny, .month = (int)nm, .day = (int)nd, .hour = 0, .minute = 0, .second = 0, .ms = 0, .is_leap_second = false };

    *out_start = resolve_local(w_start, zone).instant_epoch_ms;
    *out_end   = resolve_local(w_end, zone).instant_epoch_ms;
}
```
```cpp
// Межа: настінний час ↔ мить, ISO-8601 та високосні секунди на C++20.
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <chrono>
#include <charconv>
#include <algorithm>
#include <vector>
#include <array>

namespace time_boundary {

enum class ResolveKind { Exact, Gap, Ambiguous };

struct WallTime {
    int year{1970};
    int month{1};
    int day{1};
    int hour{0};
    int minute{0};
    int second{0};
    int ms{0};
    bool is_leap_second{false};
};

struct ResolvedTime {
    std::chrono::sys_time<std::chrono::milliseconds> instant;
    ResolveKind kind{ResolveKind::Exact};
};

struct Iso8601Result {
    WallTime wall;
    std::optional<std::chrono::minutes> offset;
    bool is_utc{false};
    bool valid{false};
};

constexpr bool is_leap_year(int y) noexcept {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

constexpr int days_in_month(int y, int m) noexcept {
    constexpr std::array<int, 12> kDays{31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (m == 2 && is_leap_year(y)) return 29;
    return (m >= 1 && m <= 12) ? kDays[m - 1] : 0;
}

// Запит зсуву зони для конкретної точки на осі UTC
inline std::chrono::milliseconds zone_offset(std::chrono::sys_time<std::chrono::milliseconds> instant,
                                             std::string_view zone) {
    if (zone == "Europe/Kyiv") {
        using namespace std::chrono;
        auto march_trans = sys_days{2026y/March/29} + 1h;
        auto oct_trans   = sys_days{2026y/October/25} + 1h;
        if (instant >= march_trans && instant < oct_trans) {
            return hours{3};
        }
        return hours{2};
    }
    if (zone == "Asia/Tokyo") {
        return std::chrono::hours{9};
    }
    return std::chrono::milliseconds{0};
}

// Неблокуючий парсер ISO-8601 без динамічних алокацій
inline Iso8601Result parse_iso8601(std::string_view sv) noexcept {
    Iso8601Result res;
    if (sv.size() < 10) return res;

    auto parse_int = [](std::string_view s, int& out) noexcept -> bool {
        auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), out);
        return ec == std::errc{} && ptr == s.data() + s.size();
    };

    int y = 0, mo = 0, d = 0;
    if (!parse_int(sv.substr(0, 4), y) || sv[4] != '-' ||
        !parse_int(sv.substr(5, 2), mo) || sv[7] != '-' ||
        !parse_int(sv.substr(8, 2), d)) {
        return res;
    }

    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo)) return res;

    res.wall.year = y;
    res.wall.month = mo;
    res.wall.day = d;

    if (sv.size() == 10) {
        res.valid = true;
        return res;
    }

    if (sv[10] != 'T' && sv[10] != ' ') return res;
    std::string_view time_part = sv.substr(11);
    if (time_part.size() < 5) return res;

    int h = 0, mi = 0, s = 0;
    if (!parse_int(time_part.substr(0, 2), h) || time_part[2] != ':' ||
        !parse_int(time_part.substr(3, 2), mi)) {
        return res;
    }

    if (h < 0 || h > 23 || mi < 0 || mi > 59) return res;
    res.wall.hour = h;
    res.wall.minute = mi;

    size_t offset_pos = 5;
    if (time_part.size() >= 8 && time_part[5] == ':') {
        if (!parse_int(time_part.substr(6, 2), s)) return res;
        if (s < 0 || s > 60) return res;
        res.wall.second = (s == 60) ? 59 : s;
        res.wall.is_leap_second = (s == 60);
        offset_pos = 8;
    }

    if (offset_pos < time_part.size()) {
        std::string_view tz_sub = time_part.substr(offset_pos);
        if (tz_sub == "Z" || tz_sub == "z") {
            res.is_utc = true;
            res.offset = std::chrono::minutes{0};
        } else if (tz_sub.starts_with('+') || tz_sub.starts_with('-')) {
            int off_h = 0, off_m = 0;
            int sign = tz_sub[0] == '-' ? -1 : 1;
            if (tz_sub.size() >= 6 && tz_sub[3] == ':' &&
                parse_int(tz_sub.substr(1, 2), off_h) &&
                parse_int(tz_sub.substr(4, 2), off_m)) {
                res.offset = std::chrono::minutes{sign * (off_h * 60 + off_m)};
            }
        }
    }

    res.valid = true;
    return res;
}

// Настінний час + назва зони → мить і діагностика переходу
inline ResolvedTime resolve_local(const WallTime& w, std::string_view zone) {
    using namespace std::chrono;
    auto ymd = year{w.year} / month{static_cast<unsigned>(w.month)} / day{static_cast<unsigned>(w.day)};
    sys_days sd{ymd};
    auto as_if_utc = sd + hours{w.hour} + minutes{w.minute} + seconds{w.second} + milliseconds{w.ms};

    auto before = zone_offset(as_if_utc - 24h, zone);
    auto after  = zone_offset(as_if_utc + 24h, zone);

    std::vector<sys_time<milliseconds>> valid;
    auto test_candidate = [&](milliseconds off) {
        auto cand = as_if_utc - off;
        if (zone_offset(cand, zone) == off) {
            valid.push_back(cand);
        }
    };

    test_candidate(before);
    if (before != after) test_candidate(after);

    if (valid.size() == 1) {
        return ResolvedTime{.instant = valid[0], .kind = ResolveKind::Exact};
    }
    if (valid.size() == 2) {
        return ResolvedTime{.instant = std::min(valid[0], valid[1]), .kind = ResolveKind::Ambiguous};
    }
    return ResolvedTime{.instant = as_if_utc - std::min(before, after), .kind = ResolveKind::Gap};
}

// Форматування миті в настінний напис читача
inline std::string format_in_zone(std::chrono::sys_time<std::chrono::milliseconds> instant,
                                  std::string_view zone) {
    using namespace std::chrono;
    auto off = zone_offset(instant, zone);
    auto local_time = instant + off;
    auto dp = floor<days>(local_time);
    year_month_day ymd{dp};
    auto tod = make_time(local_time - dp);

    int off_min = static_cast<int>(duration_cast<minutes>(off).count());
    char sign = off_min >= 0 ? '+' : '-';
    if (off_min < 0) off_min = -off_min;

    auto pad2 = [](int v) -> std::string {
        return v < 10 ? "0" + std::to_string(v) : std::to_string(v);
    };

    std::string out;
    out.reserve(32);
    out += std::to_string(static_cast<int>(ymd.year())) + "-";
    out += pad2(static_cast<unsigned>(ymd.month())) + "-";
    out += pad2(static_cast<unsigned>(ymd.day())) + " ";
    out += pad2(static_cast<int>(tod.hours().count())) + ":";
    out += pad2(static_cast<int>(tod.minutes().count())) + ":";
    out += pad2(static_cast<int>(tod.seconds().count())) + " ";
    out += sign;
    out += pad2(off_min / 60) + ":";
    out += pad2(off_min % 60);
    return out;
}

// Обчислення меж календарної доби користувача на осі митей
inline std::pair<std::chrono::sys_time<std::chrono::milliseconds>,
                 std::chrono::sys_time<std::chrono::milliseconds>>
day_bounds(std::chrono::year_month_day day, std::string_view zone) {
    using namespace std::chrono;
    WallTime start_w{static_cast<int>(day.year()), static_cast<int>(static_cast<unsigned>(day.month())),
                     static_cast<int>(static_cast<unsigned>(day.day())), 0, 0, 0, 0, false};
    
    sys_days next_sd = sys_days{day} + days{1};
    year_month_day next_day{next_sd};
    WallTime end_w{static_cast<int>(next_day.year()), static_cast<int>(static_cast<unsigned>(next_day.month())),
                   static_cast<int>(static_cast<unsigned>(next_day.day())), 0, 0, 0, 0, false};

    return {resolve_local(start_w, zone).instant, resolve_local(end_w, zone).instant};
}

} // namespace time_boundary
```
:::

Усі п'ять реалізацій (TypeScript, Python, Java, C99, C++20) на однакових входах дають однакові відповіді — і саме такий набір входів варто закріпити тестами:

```
Europe/Kyiv         2026-06-01 09:00  →  2026-06-01T06:00:00Z   exact
Europe/Kyiv         2026-03-29 03:30  →  2026-03-29T01:30:00Z   gap
                       назад у зоні:      2026-03-29 04:30 +03:00
Europe/Kyiv         2026-10-25 03:30  →  2026-10-25T00:30:00Z   ambiguous
                       назад у зоні:      2026-10-25 03:30 +03:00
                       друге входження:   2026-10-25T01:30:00Z  (+02:00)
America/Santiago    2026-09-06 00:00  →  2026-09-06T04:00:00Z   gap
                       назад у зоні:      2026-09-06 01:00 −03:00
Australia/Lord_Howe 2026-10-04 02:00  →  2026-10-03T15:30:00Z   gap   (діра 30 хв)
Australia/Lord_Howe 2026-04-05 01:30  →  2026-04-04T14:30:00Z   ambiguous
```

> 🔧 **Навіщо це.** `kind` — не діагностика для журналу, а розвилка інтерфейсу. Коли людина ставить нагадування на 03:30 у ніч весняного переходу, чесна відповідь — не мовчазна здогадка сервера, а питання: «цієї години того дня не буде, перенести на 04:30?». Мовчазна політика потрібна лише там, де спитати нема кого: імпорт з файлу, міграція, машинний потік. Функція, яка повертає саму лише мить, забирає цей вибір у того, хто її викликав, — і забирає назавжди.

### Високосні секунди та 60-та секунда в ISO-8601

Окремий крайовий випадок на вхідній межі — високосна секунда (leap second). Всесвітній координований час (UTC) прив'язаний до міжнародного атомного часу (TAI), але періодично коригується Міжнародною службою обертання Землі (IERS), щоб не розходитися з астрономічним часом обертання планети UT1 більш ніж на 0.9 секунди.

Коли додається позитивна високосна секунда, остання хвилина доби містить не 60, а 61 секунду: `23:59:60`. Стандарт ISO-8601 прямо дозволяє запис на кшталт `2016-12-31T23:59:60Z`.

Тут виникає фундаментальний розрив між ISO-8601 та стандартом POSIX `time_t`:
1. **POSIX не визнає високосних секунд.** Стандарт POSIX вимагає, щоб кожна доба складалася рівно з 86400 секунд (`24 × 60 × 60`). Через це в системному годиннику Linux секунда `23:59:60` або дублює секунду `23:59:59` (годинник робить крок назад `86399 → 86399`), або зависає на одну секунду. Стрибок назад руйнує монотонність і провокує стан гонитви (race conditions) у розподілених блокуваннях і базах даних.
2. **Парсери падають або спотворюють дані.** Наївна валідація, що вимагає `second <= 59`, відхиляє валідний ISO-8601 рядок. Якщо ж рядок розбирає C-функція `strptime` або наївний числовий парсер без прапорця `is_leap_second`, значення `60` переповнює хвилину або відкидається.

У промислових системах застосовують дві взаємодоповнюючі стратегії:
- **Згладжування (Leap Smearing):** Сервери NTP (наприклад Google Public NTP чи AWS Time Sync Service) не вставляють секунду `23:59:60`, а розмазують додаткову секунду впродовж 24 годин довкола півночі, сповільнюючи хід годинника на 11.57 ppm. Для застосунку день лишається 86400-секундним, а `second == 60` у внутрішні структури ніколи не надходить.
- **Явна підтримка на межі розбору:** Якщо сервіс приймає зовнішній ISO-8601 потік (наприклад, астрономічні або фінансові телеметричні пакети), парсер зобов'язаний розпізнавати `23:59:60`, встановлювати прапорець `is_leap_second` і зводити мить до останньої мілісекунди доби `23:59:59.999` для сумісності з POSIX-епохою, зберігаючи прапорець для зворотного бездоганного форматування в ISO-8601.

## Сховище: істина й похідне в одному рядку

```sql
CREATE TABLE reminder (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     bigint      NOT NULL,
    title       text        NOT NULL,

    -- ІСТИНА: те, що сказала людина
    local_wall  timestamp   NOT NULL,   -- без зони: «2026-10-25 03:30»
    zone        text        NOT NULL,   -- 'Europe/Kyiv' — назва зони, не зсув

    -- ПОХІДНЕ: те, за чим сканує планувальник
    fire_at     timestamptz NOT NULL,
    fired_at    timestamptz,            -- NULL, доки не спрацювало
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX reminder_due  ON reminder (fire_at) WHERE fired_at IS NULL;
CREATE INDEX reminder_span ON reminder (user_id, fire_at);
```

Про `timestamptz` варто знати те, чого не видно з назви: **він не зберігає зону**. Вісім байтів, роздільність мікросекунда, всередині — мить, зведена до UTC. Зону в назві типу згадано лише тому, що вона бере участь у перетворенні на вході й на виході: вхідний літерал розуміють у зоні сеансу, вихідний рядок малюють у зоні сеансу. Сам рядок таблиці про Київ нічого не знає — саме тому зона живе окремою колонкою.

Наслідок практичний: два клієнти з різними `SET TIME ZONE` побачать з одного рядка різні написи, і жоден з них не буде «тим, що в базі». Тому з'єднання застосунку тримають на `UTC`, а форматуванням займається код виводу, де зона читача відома. Драйвер за такої дисципліни поводиться прозоро: `Instant`, `datetime` з `tzinfo=UTC` чи `Date` прив'язуються до `timestamptz` без жодних рядкових перетворень.

Другий тип — `timestamp` без зони — теж потрібен, але лише для `local_wall`: там справді лежить настінний напис, який без сусідньої колонки `zone` не означає жодної миті. Ця пара — істина; `fire_at` — похідне від неї, і чому саме так, стане ясно нижче.

Оператор `AT TIME ZONE`, яким спокусливо все це робити в SQL, працює в обидва боки, і напрямок задає тип аргументу: над `timestamptz` він дає `timestamp` (настінний напис у зоні), над `timestamp` — `timestamptz` (тлумачить напис як такий, що заданий у цій зоні). Один оператор, дві протилежні дії — сплутати їх легко, а помітити важко, бо обидва варіанти компілюються.

## Вихідна межа: у кожного свій напис

Зворотний бік коштує один виклик і не має жодних розгалужень: мить існує завжди й читається в будь-якій зоні однозначно.

```
мить у базі:                       2026-10-25T00:30:00Z

Оксана,  zone='Europe/Kyiv'   →  2026-10-25 03:30 +03:00
Ярема,   zone='Asia/Tokyo'    →  2026-10-25 09:30 +09:00
журнал,  zone='UTC'           →  2026-10-25 00:30 +00:00
```

Правило виводу єдине: зона береться з профілю читача, а не з рядка даних. Одне нагадування — стільки написів, скільки очей на нього дивиться. І жоден із цих написів не зберігають: збережений рядок «03:30» був би тим самим замерзлим настінним часом, від якого весь цей обіг і рятує.

## Звіт: доба — це проміжок митей

«Скільки нагадувань спрацювало 25 жовтня» звучить як питання про день, але база не знає днів — вона знає миті. Тому звіт має спершу перекласти день у пару меж, і зробити це тим самим `resolveLocal`, що й вхідну межу.

```
dayBounds(2026, 10, 25, "Europe/Kyiv")
    від:  2026-10-24T21:00:00Z     (місцева 00:00)
    до:   2026-10-25T22:00:00Z     (місцева 00:00 наступного дня)
    у проміжку 25 годин реального часу
```

![Три календарні доби киянина як проміжки на осі митей: 23, 24 і 25 годин](/root/eng/sf-apps/time-and-scheduling/img/user-day.svg)
*Календарна доба — проміжок митей, і його довжина залежить від дня; порівняння працює лише як півзакритий проміжок.*

Обидві межі рахують однаково — як місцеву північ відповідного дня, — і саме тому сусідні доби стикаються без дірок і накладань. Кінець доби — не «23:59:59.999», яке довелося б підбирати під роздільність типу, а рівно початок наступної, узятий строго менше. Півзакритий проміжок `[від, до)` тут не стильова забаганка: із `BETWEEN`, що включає обидва кінці, нагадування, поставлене рівно на місцеву північ, потрапить у два сусідні звіти водночас.

Так само не можна будувати вікно як «початок доби плюс 24 години». 25 жовтня 2026-го таке вікно обірветься за годину до кінця київської доби, і остання година зі звіту випаде; 29 березня, навпаки, воно захопить зайву годину наступного дня.

```sql
-- ✓ межі порахував застосунок; над колонкою немає жодного виразу
SELECT count(*) FROM reminder
 WHERE user_id = $1
   AND fire_at >= $2       -- 2026-10-24 21:00:00+00
   AND fire_at <  $3;      -- 2026-10-25 22:00:00+00

-- ✗ вираз над колонкою: значення треба порахувати для кожного рядка таблиці
SELECT count(*) FROM reminder
 WHERE user_id = $1
   AND (fire_at AT TIME ZONE 'Europe/Kyiv')::date = DATE '2026-10-25';
```

Різниця між цими двома запитами не в стилі, а в порядку складності. Перший — пошук діапазону по [індексу](root:sf-data/database-indexes) `(user_id, fire_at)`: планувальник спускається деревом до нижньої межі й читає поспіль до верхньої, тобто торкається стількох рядків, скільки поверне. Другий обчислює `AT TIME ZONE` над кожним рядком користувача, перш ніж вирішити, чи він підходить; звичайний індекс по `fire_at` для цього непридатний, бо впорядкований за іншим значенням. На тисячі нагадувань обидва здаються миттєвими, на мільйонах різниця стає різницею між звітом і таймаутом.

І остання дрібниця, на якій ловляться навіть акуратні: **різницю двох настінних часів не можна брати відніманням у їхній зоні**. Python тут поводиться підступно — віднімання двох дат з однаковою `tzinfo` рахує як для наївних, тобто за календарем:

```
a = 2026-10-25 00:00 Europe/Kyiv
b = 2026-10-26 00:00 Europe/Kyiv

b - a                                  →  1 day, 0:00:00     ← календарна різниця
b.astimezone(UTC) - a.astimezone(UTC)  →  1 day, 1:00:00     ← реальний час
```

Обидві відповіді правильні, просто на різні питання: перша — «скільки календарних діб», друга — «скільки часу насправді минуло». Правило те саме, що й скрізь: тривалість рахують на осі митей, тобто після переведення в UTC.

## Мить у майбутньому — це прогноз, а не факт

Тепер видно, навіщо в таблиці колонки `local_wall` і `zone`, коли `fire_at` уже все каже.

Мить, порахована для *минулої* події, — факт: вона сталася, її зсув відомий і незмінний. Мить, порахована для події через рік, — прогноз за чинним записом у tz-базі. Цей запис — не закон природи, а копія урядового рішення, і його міняють: країни пересувають дати переходу, скасовують перехід зовсім, змінюють базовий зсув. Кожен такий випуск tz-бази робить хибними всі збережені майбутні миті в тих зонах.

Якщо в таблиці лежить лише `fire_at`, полагодити нема з чого: назад із миті настінний час не відновити, бо для цього потрібен той самий зсув, який щойно змінився. Якщо лежить пара «настінний час + зона», лагодження — це перерахунок:

```sql
-- після оновлення tz-бази: усе, що ще не спрацювало й лежить у майбутньому
SELECT id, local_wall, zone
  FROM reminder
 WHERE fired_at IS NULL
   AND fire_at > now()
   AND zone = ANY($1);        -- лише зони, чиї правила змінив цей випуск

-- і назад, порахувавши resolveLocal(local_wall, zone) у застосунку
UPDATE reminder SET fire_at = $2 WHERE id = $1 AND fire_at <> $2;
```

Звідси й розподіл ролей у схемі. `local_wall` і `zone` — істина, її пишуть один раз при створенні. `fire_at` — кеш, і його можна перерахувати будь-коли з істини. Перевірка чесності схеми проста: викиньте похідну колонку й спробуйте відновити її з решти. Якщо не виходить — істину десь загубили.

Те саме міркування в чистішому вигляді стосується повторюваних правил: «щодня о 09:00» не має жодної миті, доки не названо день, тож зберігати там можна лише правило, а миті породжувати на льоту. Скільки в цьому тонкощів, показує [календарна математика повторюваних правил](root:sf-apps/recurrence-scheduling). Разова подія — проміжний випадок: істина настінна, мить похідна, і тому обидві лежать в одному рядку поруч.

## Ціна й дрібниці, на яких ловляться

Один переклад `resolveLocal` — це три-чотири запити зсуву до зони, кожен усередині двійковий пошук по таблиці переходів (кількасот записів на зону). Мікросекунди, і на межі запиту їх не видно. Видно інше — вартість самого форматувальника: у Node v24 побудова `Intl.DateTimeFormat` під кожен виклик коштує близько 42 мкс, тоді як форматування вже готовим — близько 3 мкс. Кеш форматувальників по зоні дає тут приблизно тринадцятикратне прискорення й коштує п'ять рядків; без нього звіт на десять тисяч рядків втрачає майже чотири десятих секунди на порожньому місці. У Python та Java об'єкт зони кешує сам рушій, тож там гострої потреби немає.

Решта — короткий перелік місць, де обіг ламається тихо.

- **Бази зон може не бути під рукою.** Windows тримає власний реєстр поясів, а не IANA-базу: `ZoneInfo("Europe/Kyiv")` у Python там падає з `ZoneInfoNotFoundError`, доки не поставлено пакунок `tzdata`. У мінімальних образах Linux те саме — без пакунка `tzdata` контейнер знає лише UTC. Код, який працює локально й падає в образі, майже завжди про це.
- **Назви зон не порівнюють рядками.** `Europe/Kiev` і `Europe/Kyiv` — та сама зона, і рушії канонізують її по-різному: Node 24 у `resolvedOptions().timeZone` зводить обидві назви до `Europe/Kiev`, java.time лишає ту, яку дали. Рівність зон перевіряють бібліотекою, а не `==`.
- **Зсув не завжди кратний годині.** Катманду живе на `+05:45`, Лорд-Гау переводить стрілки на пів години. Код, що десь ділить на 3600 або додає рівно годину «бо літній час», у цих зонах помиляється.
- **Пояс процесу не має бути частиною поведінки.** Найпростіший захист — ганяти тести з `TZ`, виставленим у якусь вигадливу зону: на островах Чатем (`Pacific/Chatham`) зсув `+12:45`, а в пору тамтешнього літнього часу `+13:45`. Усе, що мовчки спиралося на пояс машини, посиплеться одразу, а не в продакшні.
