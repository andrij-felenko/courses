# ⚙️ NotificationGate: три фільтри й обхід критичного в одному робочому вузлі

Ми розібрали три сита нарізно — дедуп прибирає копії, злиття збирає бурю в дайджест, throttling накладає стелю на темп, а над усім цим критичне ріже наскрізь. Нарізно кожне зрозуміле. А от разом, в одному процесі, під двома інстансами, з таймерами, що мусять пережити перезапуск, і двома різними годинниками — вони сплітаються в клубок, де кожна пастка ховається саме на стику. Тож зберімо `NotificationGate` — один вхід, крізь який проходить кожне сповіщення, — так, щоб **кожна з пасток теми стала окремим тестом, який падає, поки код неправильний**. Мова тут — Go: таймери, конкурентність і темп — рівно те, під що його робили; серце вузла продублюю вкладкою на TypeScript, бо той самий `Admit` часто живе у стеку застосунку.

## Задача

Один метод `Admit(n)` вирішує долю сповіщення й повертає рішення. Усередині — конвеєр **дедуп → злиття → throttling** плюс пріоритетна смуга. Стан фільтрів (ключі дедупу, буфери груп, відра жетонів) живе **не в пам'яті процесу**, а у спільному сховищі — інакше два інстанси відправника фільтрують наосліп кожен свій шматок трафіку, і дублі з бурями просочуються між ними. У процесі лишається одне: таймер тієї групи, яку цей інстанс **відкрив**. Годинників теж два, і плутати їх дорого: відро й TTL міряють **тривалості** (годинник сховища), а тихі години — **час доби в житті людини** (настінний, у її поясі).

![Два інстанси Gate над однією рамкою спільного сховища Redis; у ній чотири рядки стану — дедуп-ключі (SET NX EX), буфер злиття (RPUSH, довжина 1 = власник), відра жетонів (годинник сховища), тихі години (пояс користувача). У пам'яті інстанса — лише таймер озброєної групи. Внизу застереження: стан у пам'яті процесу = кожен інстанс сліпий на чужий трафік.](img/gate-state.svg)
*Стан трьох фільтрів — не в пам'яті інстанса, а у спільному сховищі: дедуп-ключі, буфер злиття, відра жетонів. У процесі лишається тільки таймер відкритої групи. Годинник відра — самого сховища; тихі години — місцевий пояс людини.*

## Ідея

Найважливіше рішення — **порядок**, і воно вже прийняте темою: спершу найдешевше (прибрати буквальні копії), тоді згрупувати вціліле в дайджести, і лише тоді накласти стелю на **дайджести**, а не на сирі події. Тому throttling у коді сидить не на вході, а **на виході злиття** — у момент, коли таймер групи спрацював і ми зводимо буфер у один рядок. А над усім — перша ж гілка `Admit`: критичне не заходить у конвеєр узагалі.

Другий стрижень — **атомарність**. Кожна операція над спільним станом мусить бути неподільною, бо саме на подільності народжуються всі гонки: два інстанси, що незалежно «перевірили, тоді зробили», дійдуть однакового висновку й обидва зроблять те, що мав зробити один. Тому весь стан ховається за інтерфейсом `Store`, кожен метод якого — **одна атомарна дія** сховища (у проді — Redis; тут атомарність грає однопотоковість або мютекс).

Почнімо з даних. Сповіщення несе свою ідентичність і — це несуча колона всієї теми — **клас критичності від джерела**, не від пайплайну:

```go
package gate

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"sync"
	"time"
)

// Severity — клас критичності. Його проставляє ДЖЕРЕЛО події, не фільтр.
type Severity int

const (
	Info     Severity = iota // «прошивку оновлено» — агресивно зливаємо, тісна стеля
	Warning                  // «пристрій офлайн» — звичайний конвеєр
	Critical                 // дим · злом · протікання — в обхід усього, негайно
)

// Notification — одне ЛОГІЧНЕ сповіщення (не спроба доставки).
type Notification struct {
	Recipient string    // до кого (id користувача)
	Event     string    // ідентичність ПОДІЇ: "door-open@2026-07-11T07:14" (до хвилини!)
	Class     string    // тема для злиття: "connectivity", "security", "firmware"…
	Channel   string    // "push" | "feed" | "email"
	Severity  Severity
	At        time.Time // час події — для рядка дайджесту
	Text      string    // готовий рядок однієї події
	Holds     int       // скільки разів це вже притримали (для драбини throttling)
}

// Ключ дедупу — відбиток СМИСЛУ: кому + про яку подію + яким каналом.
// Номера спроби тут НЕМА (інакше ретрай матиме інший ключ і дубль просочиться).
func dedupKey(n Notification) string {
	return "dedup:" + sha1hex(n.Recipient+"|"+n.Event+"|"+n.Channel)
}

// Ключ групи — навмисне ГРУБШИЙ: усе, що людина сприйме як одну тему.
func groupKey(n Notification) string {
	return "grp:" + n.Recipient + "|" + n.Class + "|" + n.Channel
}

func sha1hex(s string) string { h := sha1.Sum([]byte(s)); return hex.EncodeToString(h[:]) }
```

Зверни увагу на різницю двох ключів — у ній уся [ідемпотентність](topic:sf-distributed/idempotency), повернута назовні: емісія має бути ідемпотентною, скільки б разів пайплайн не спробував відіслати ту саму новину. Ключ дедупу вузький і несе `Event` (з часом до хвилини), тож «двері о 07:14» і «двері о 17:03» — різні. Ключ групи широкий і несе лише `Class`, тож сорок різних «офлайн» одного дому склеяться. Одне поле — `Event` проти `Class` — і визначає, що вважати «тим самим».

## Спільне сховище як контракт

Ось інтерфейс стану. Кожен метод — атомарна операція; імена в дужках — прямий відповідник Redis, щоб було видно, звідки береться неподільність:

```go
// Store — спільний стан фільтрів. Кожен метод АТОМАРНИЙ: саме це рятує від гонок.
type Store interface {
	// SetNX: поставити ключ, лише якщо його ще нема. true = МИ перші.
	// Redis: SET key val NX EX ttl → OK або nil.
	SetNX(ctx context.Context, key string, ttl time.Duration) (bool, error)

	// Append: додати у список групи, повернути НОВУ довжину. 1 = ми відкрили групу.
	// Redis: RPUSH group item → ціле (довжина списку ПІСЛЯ додавання).
	Append(ctx context.Context, group string, item []byte, ttl time.Duration) (int, error)

	// Drain: забрати весь список групи й видалити його — за один неподільний крок.
	// Redis: LRANGE+DEL в одному Lua-скрипті.
	Drain(ctx context.Context, group string) ([][]byte, error)

	// Take: списати 1 жетон із відра (user,channel), якщо є.
	// Годинник для дозрівання — САМОГО сховища (Redis TIME), а не інстанса.
	Take(ctx context.Context, bucket string, burst, refillPerSec float64) (bool, error)

	// --- Довговічний індекс дедлайнів: щоб таймери груп пережили перезапуск. ---

	// MarkDue: записати (чи оновити) мить флашу групи в індексі за часом.
	// Redis: ZADD due <оцінка = unix-мить-флашу> <група>.
	MarkDue(ctx context.Context, group string, at time.Time) error

	// DueGroups: усі групи, чий дедлайн уже настав (оцінка ≤ now).
	// Redis: ZRANGEBYSCORE due -inf <now> → зріз груп.
	DueGroups(ctx context.Context, now time.Time) ([]string, error)

	// ClearDue: прибрати групу з індексу після вдалого флашу (щоб не флашити вдруге).
	// Redis: ZREM due <група>.
	ClearDue(ctx context.Context, group string) error
}
```

Найтонше рішення сховане в `Take`: годинник **не передаємо**. Відро в спільному сховищі мусить дозрівати за годинником, з яким **згодні всі інстанси**, — а власний монотонний годинник процесу з монотонним годинником сусіда непорівнянний. Redis відповідає командою `TIME` (unix-секунди плюс мікросекунди його власного годинника), і саме її бере розрахунок доливання. Це той самий закон [монотонного проти настінного часу для тривалостей](topic:sf-apps/monotonic-vs-wall-time), лише піднятий на рівень кластера: усередині процесу — монотонний, у спільному відрі — єдиний годинник сховища.

## Серце: Admit

Тепер вхід. Це найважливіші двадцять рядків усього вузла, тож — двома мовами:

:::tabs
```go
type Outcome int

const (
	Delivered Outcome = iota // пішло зараз: критичне в обхід або готовий дайджест
	Buffered                 // лягло в буфер злиття, чекає вікна
	Dropped                  // дубль або відкинуто драбиною
)

type Decision struct {
	Outcome Outcome
	Reason  string
}

// Admit — ЄДИНИЙ вхід. Рішення про одне сповіщення.
func (g *Gate) Admit(ctx context.Context, n Notification) (Decision, error) {
	// 0. Критичне ріже наскрізь: в обхід дедупу, злиття й throttling.
	//    Дедуп для нього НАВМИСНЕ не робимо — краще зайва копія, ніж проковтнута тривога.
	if n.Severity == Critical {
		if err := g.deliver(ctx, n); err != nil {
			return Decision{}, err
		}
		return Decision{Delivered, "critical-bypass"}, nil
	}

	// 1. Дедуп: перший, хто застовпив ключ, — шле; решта тихо мовчить.
	first, err := g.store.SetNX(ctx, dedupKey(n), g.dedupTTL(n))
	if err != nil {
		return Decision{}, err
	}
	if !first {
		return Decision{Dropped, "duplicate"}, nil
	}

	// 2. Злиття: кладемо у СПІЛЬНИЙ буфер групи. Хто дістав довжину 1 —
	//    той відкрив групу й ЄДИНИЙ озброює таймер (атомарний вибір власника).
	item, _ := json.Marshal(n)
	size, err := g.store.Append(ctx, groupKey(n), item, 2*g.window)
	if err != nil {
		return Decision{}, err
	}
	if size == 1 {
		g.arm(groupKey(n), n.Class)
	}
	return Decision{Buffered, "coalescing"}, nil
}
```
```ts
enum Severity { Info, Warning, Critical }

interface Notification {
  recipient: string;
  event: string;    // ідентичність події: "door-open@2026-07-11T07:14"
  cls: string;      // тема для злиття
  channel: string;
  severity: Severity;
  at: number;       // час події, ms
  holds?: number;
}

type Decision = { outcome: "delivered" | "buffered" | "dropped"; reason: string };

class Gate {
  async admit(n: Notification): Promise<Decision> {
    // 0. Критичне — в обхід усього; дедуп навмисне НЕ робимо.
    if (n.severity === Severity.Critical) {
      await this.deliver(n);
      return { outcome: "delivered", reason: "critical-bypass" };
    }

    // 1. Дедуп: SET dk NX PX ttl → false, якщо ключ уже є.
    const first = await this.store.setNX(dedupKey(n), this.dedupTTL(n));
    if (!first) return { outcome: "dropped", reason: "duplicate" };

    // 2. Злиття: RPUSH у групу; довжина 1 ⇒ ми власник таймера.
    const size = await this.store.append(groupKey(n), JSON.stringify(n), 2 * this.window);
    if (size === 1) this.arm(groupKey(n), n.cls);
    return { outcome: "buffered", reason: "coalescing" };
  }
}
```
:::

Прочитай гілку `0` ще раз — вона перша не випадково. Критичне доставляється **до** того, як код узагалі торкнеться дедупу чи буфера; для нього ми свідомо ризикуємо зайвою копією, бо ціна проковтнутої пожежної тривоги незмірна з ціною подвоєного «дим!». Це та сама залізна межа, що [оплачена розплавленою зоною Три-Майл-Айленда](root:progarch/notification-dedup-throttle/hist-alert-fatigue.md): фільтр без пріоритету — зброя, наведена на власний сигнал тривоги.

### Атомарний вибір власника таймера

Рядок `if size == 1` — тихий герой цього коду. Наївний варіант напрошується сам: «перевірити, чи група вже відкрита; якщо ні — створити й озброїти таймер». І саме він ламається під двома інстансами. Обидва майже одночасно питають «група є?» — обидва бачать «нема» — обидва озброюють таймер. За одну групу спрацюють **два** таймери, і людина дістане **два** дайджести замість одного. Це рівно та гонка, що чигає на всяке злиття між інстансами: спільний стан без атомарності.

Рятунок — не питати «є?», а **зробити й подивитися на відповідь**. `RPUSH` повертає нову довжину списку атомарно; отже, рівно один інстанс — той, чий запис створив список, — побачить `1`. Він і власник. Решта дістануть `2`, `3`, … і просто долучать своє в буфер. Вибір власника не потребує окремого замка — він **піджаком** сидить на тій самій атомарній операції, що й запис у буфер.

![Дві панелі. Верхня «Наївно: перевір-тоді-дій» — інстанси A і B обидва читають «групи нема», обидва створюють буфер і озброюють таймер, праворуч червоне «2 таймери → 2 дайджести». Нижня «Атомарно: RPUSH повертає довжину» — A дістає 1 і стає власником, B дістає 2 і лише додає, праворуч зелене «1 таймер → 1 дайджест».](img/coalesce-race.svg)
*Наївне «перевір-тоді-дій» дає двом інстансам однаковий висновок «групи ще нема» — і два таймери, два дайджести. Атомарний RPUSH сам обирає власника: рівно один інстанс бачить довжину 1.*

> 🔧 **Навіщо це.** Щоразу, коли твій код каже «перевір, чи вже є, — і як нема, зроби», спитай: а що, як цей самий код виконується двічі водночас на двох машинах? Якщо відповідь «обидва пройдуть перевірку й обидва зроблять» — тобі потрібна **одна** атомарна операція, що поєднує перевірку з дією й повертає, хто був перший (`SET NX`, `RPUSH`, `INCR`, compare-and-swap). Вибір власника таймера — саме такий випадок: не «спитати й вирішити», а «зробити й прочитати відповідь».

## Злиття, throttling і драбина — на виході

Таймер спрацював. Тепер зводимо буфер у дайджест і **аж тут** накладаємо стелю — на зведення, не на сирі події. Порядок годинників у цьому методі — окрема історія:

```go
func (g *Gate) arm(group, class string) {
	// g.sched — інжектований планувальник (у проді time.AfterFunc; у тесті — ручний).
	t := g.sched(g.window, func() { _ = g.flush(context.Background(), group, class) })
	g.timers.Store(group, t)
}

func (g *Gate) flush(ctx context.Context, group, class string) error {
	g.timers.Delete(group)
	raw, err := g.store.Drain(ctx, group) // забрати й очистити буфер за один крок
	if err != nil || len(raw) == 0 {
		return err
	}
	batch := make([]Notification, 0, len(raw))
	for _, b := range raw {
		var n Notification
		if json.Unmarshal(b, &n) == nil {
			batch = append(batch, n)
		}
	}
	user, channel := batch[0].Recipient, batch[0].Channel

	// Тихі години — настінний МІСЦЕВИЙ час користувача (не UTC, не монотонний!).
	if g.quiet(user, g.now()) {
		return g.rebuffer(ctx, batch) // притримати до ранку → спокійний ранковий дайджест
	}

	// Стеля темпу — на пару (user,channel). Годинник відра — самого сховища.
	ok, err := g.store.Take(ctx, "tb:"+user+":"+channel, g.burst, g.rate)
	if err != nil {
		return err
	}
	if !ok {
		return g.ladder(ctx, class, batch) // порожнє відро → драбина, не мовчазне «відкинути»
	}
	return g.deliver(ctx, digest(class, batch, g.render, channel))
}

func digest(class string, batch []Notification, render func(string, []Notification) string, channel string) Notification {
	return Notification{
		Recipient: batch[0].Recipient,
		Channel:   channel,
		Severity:  Warning,
		At:        batch[len(batch)-1].At,
		Text:      render(class, batch), // "40 пристроїв втратили зв'язок" — робота шаблонів
	}
}
```

Два годинники в одному методі — і в цьому вся сіль. `g.quiet(user, g.now())` питає **час доби в житті людини**: чи зараз між 23:00 і 7:00 **в її поясі**? Тут потрібен настінний місцевий час, бо йдеться про сон конкретної родини, не про сервер у UTC. А `g.store.Take` міряє **тривалість** між дайджестами — і бере годинник сховища, спільний для інстансів. Переплутати їх — тиха катастрофа: візьмеш wall-clock для відра, і стрибок NTP чи перехід на літній час зробить відро то безмежним, то замкненим; візьмеш UTC для тихих годин, і розбудиш Київ о другій ночі, бо на сервері десята ранку.

Порожнє відро — не привід відкинути. `ladder` спускається щаблями, і кожен нижчий гірший за попередній, тож відкидання — аж останнє й лише для дрібного:

```go
const maxHolds = 1 // притримати щонайбільше стільки разів, тоді щабель нижче

// ladder — драбина при порожньому відрі: притримати → знизити канал → відкинути.
func (g *Gate) ladder(ctx context.Context, class string, batch []Notification) error {
	switch {
	case batch[0].Holds < maxHolds:
		// Щабель 1: притримати й злити в НАСТУПНИЙ дайджест (throttling → злиття).
		return g.rebuffer(ctx, batch)
	case anyAtLeast(batch, Warning):
		// Щабель 2: знизити канал — не push (світить екран), а тихий запис у стрічці.
		return g.deliver(ctx, digest(class, batch, g.render, "feed"))
	default:
		// Щабель 3: відкинути — лише info, що не варте чекати. Лишаємо слід у метриці.
		g.metricDropped(len(batch))
		return nil
	}
}

// rebuffer — кладемо назад у буфер (кожному +1 притримання); наступне вікно забере.
func (g *Gate) rebuffer(ctx context.Context, batch []Notification) error {
	for i := range batch {
		batch[i].Holds++
		item, _ := json.Marshal(batch[i])
		size, err := g.store.Append(ctx, groupKey(batch[i]), item, 2*g.window)
		if err != nil {
			return err
		}
		if size == 1 {
			g.arm(groupKey(batch[i]), batch[i].Class)
		}
	}
	return nil
}

func anyAtLeast(batch []Notification, s Severity) bool {
	for _, n := range batch {
		if n.Severity >= s {
			return true
		}
	}
	return false
}
```

`rebuffer` — це throttling, що ввічливо **перетікає у злиття**: надлишок за темпом не гине, він стає матеріалом наступного зведення. Той самий шлях обслуговує й тихі години — притримане до ранку просто чекає на своє вікно. Обмеження `maxHolds` рятує від нескінченного притримання: якщо відро вперто порожнє, ми не тримаємо вічно, а спускаємось на тихіший канал. Це той самий рух, що [злиття однакових запитів у польоті](topic:sf-distributed/request-coalescing) робить для навантаження, лише націлений на терпимість людини — а сама стеля темпу є [обмеженням швидкості](topic:sf-security/rate-limiting), наведеним на увагу замість на API.

## Таймери, що переживають перезапуск

Один рядок вище — `g.sched(g.window, …)` — ховає найпідступнішу пастку вузла. `time.AfterFunc` живе в пам'яті **того** інстанса, що відкрив групу. Якщо процес перезапуститься до спрацювання таймера, таймер помре разом із ним — а буфер у сховищі лишиться, притримані сповіщення зависнуть, і людина не дізнається нічого. Таймер у пам'яті — це **швидкий шлях**, а не джерело правди.

Правда мусить жити там само, де буфер, — у сховищі. Дедлайн кожної групи кладемо в спільний **індекс за часом**: упорядкований набір, де оцінка — мить флашу. Окремий підмітальник у **кожному** інстансі періодично питає в цього індексу групи, чий дедлайн уже сплив, і флашить ту, яку вдалося атомарно застовпити (щоб флашив рівно один):

```go
// Довговічний варіант: дедлайн — у спільному індексі, а не лише в пам'яті.
func (g *Gate) armDurable(ctx context.Context, group, class string) {
	// Кладемо мить флашу в індекс за часом (ZADD). Переживе перезапуск інстанса.
	_ = g.store.MarkDue(ctx, group, g.now().Add(g.window))
	// Локальний таймер лишаємо як швидкий шлях; спрацювавши — сам прибирає дедлайн.
	g.timers.Store(group, g.sched(g.window, func() {
		g.flushDue(context.Background(), group, class)
	}))
}

// flushDue — флаш плюс прибирання дедлайну з індексу (ZREM). Спільний для
// швидкого шляху (локальний таймер) і підмітальника, тож індекс чиститься в обох.
func (g *Gate) flushDue(ctx context.Context, group, class string) {
	if err := g.flush(ctx, group, class); err == nil {
		_ = g.store.ClearDue(ctx, group) // зведено успішно → більше не спливе
	}
}

// sweep — крутиться в КОЖНОМУ інстансі. Бере з індексу прострочені групи й флашить
// ту, яку вдалося застовпити АТОМАРНО (claim), щоб флашив лише один інстанс.
func (g *Gate) sweep(ctx context.Context) {
	due, err := g.store.DueGroups(ctx, g.now()) // групи, чий дедлайн у індексі сплив
	if err != nil {
		return
	}
	for _, group := range due {
		claimed, _ := g.store.SetNX(ctx, "flushing:"+group, 30*time.Second)
		if claimed {
			g.flushDue(ctx, group, classOf(group))
		}
	}
}
```

Три операції над індексом тримають механізм цілим, і всі три вже стоять у коді: `armDurable` кладе групу в `ZSET` командою `ZADD` з оцінкою-дедлайном, `sweep` вибирає прострочене через `ZRANGEBYSCORE`, а `flushDue` після вдалого зведення прибирає групу `ZREM`-ом — інакше та сама група спливала б підмітальнику знову й знову. Пам'ять інстанса стає прискорювачем, а не єдиним носієм долі притриманих сповіщень: падіння одного інстанса більше нічого не губить, бо підмітальник сусіда добере його групи з індексу. І та сама атомарність, що обирала власника таймера, тепер обирає, хто саме флашить, — `SET NX` на ключі `flushing:`; а оскільки сам `flush` спорожняє буфер атомарним `Drain`, то навіть якщо швидкий таймер і підмітальник збіжаться на одній групі, дайджест піде один.

## Тест критичного — першим

Тема наказала: гілку критичного пиши й **тестуй першою**, бо ціна помилки на ній — не роздратування, а біда. Тож перший тест перевіряє найголовніше — що критичне проходить навіть тоді, коли **все** мало б його зупинити: навіть як точний дубль, навіть коли б відро було порожнє.

```go
var t0 = time.Date(2026, 7, 11, 3, 0, 0, 0, time.UTC)

func TestCriticalBypassesEverything(t *testing.T) {
	st := newMemStore(func() time.Time { return t0 })
	var sent []Notification
	g := newGate(st, func(_ context.Context, out Notification) error {
		sent = append(sent, out)
		return nil
	})

	fire := Notification{Recipient: "petrenko", Event: "smoke@03:00",
		Class: "safety", Channel: "push", Severity: Critical}

	_, _ = g.Admit(context.Background(), fire)
	_, _ = g.Admit(context.Background(), fire) // та сама подія ВДРУГЕ — критичне не дедупимо

	if len(sent) != 2 {
		t.Fatalf("критичне мусить доставитись обидва рази (в обхід дедупу), а пішло %d", len(sent))
	}
}
```

Далі — гонка, серце злиття між інстансами. Два **різні** Gate над **одним** сховищем приймають події тієї самої групи «наче одночасно». Правильний код дасть **один** дайджест; наївний «перевір-тоді-дій» дав би два, і тест би це впіймав:

```go
func TestCoalesceRaceGivesOneDigest(t *testing.T) {
	st := newMemStore(func() time.Time { return t0 }) // ОДНЕ спільне сховище

	var mu sync.Mutex
	digests := 0
	deliver := func(_ context.Context, _ Notification) error {
		mu.Lock()
		digests++
		mu.Unlock()
		return nil
	}
	schedA, schedB := &fakeSched{}, &fakeSched{}
	a := newGateWith(st, deliver, schedA.schedule)
	b := newGateWith(st, deliver, schedB.schedule)

	off := func(id string) Notification {
		return Notification{Recipient: "petrenko", Event: "offline:" + id,
			Class: "connectivity", Channel: "push", Severity: Warning}
	}
	ctx := context.Background()
	_, _ = a.Admit(ctx, off("lamp"))  // A: RPUSH→1 → власник, озброїв таймер у schedA
	_, _ = b.Admit(ctx, off("lock"))  // B: RPUSH→2 → лише додав
	_, _ = a.Admit(ctx, off("therm")) // A: RPUSH→3 → лише додав

	schedA.fireAll() // доганяємо вікно власника
	schedB.fireAll() // у B нема озброєних таймерів — і добре

	if digests != 1 {
		t.Fatalf("та сама група мала дати 1 дайджест, дала %d", digests)
	}
}
```

Дві дрібниці роблять ці тести можливими. По-перше, **годинник інжектовано**: `newMemStore` бере функцію часу, тож дозрівання відра й TTL детерміновані, без реального очікування. По-друге, **планувальник інжектовано** через `fakeSched`, що замість справжнього таймера збирає функції й вистрілює їх на команду — інакше тест злиття залежав би від настінного часу й став би крихким. Це загальний урок: таймер і годинник — не глобальні `time.Now`/`time.AfterFunc`, а залежності, які тест підмінює. Ось стенд-ін сховища, де мютекс грає роль однопотокової атомарності Redis:

```go
type memStore struct {
	mu    sync.Mutex
	keys  map[string]time.Time
	lists map[string][][]byte
	tb    map[string]*tokbucket
	due   map[string]time.Time // ІНДЕКС ДЕДЛАЙНІВ: група → мить флашу (аналог ZSET)
	now   func() time.Time      // ГОДИННИК СХОВИЩА (спільний для всіх інстансів)
}

type tokbucket struct {
	tokens float64
	last   time.Time
}

func (s *memStore) SetNX(_ context.Context, k string, ttl time.Duration) (bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if exp, ok := s.keys[k]; ok && s.now().Before(exp) {
		return false, nil // ключ іще живий → ми не перші
	}
	s.keys[k] = s.now().Add(ttl)
	return true, nil
}

func (s *memStore) Append(_ context.Context, g string, item []byte, _ time.Duration) (int, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lists[g] = append(s.lists[g], item)
	return len(s.lists[g]), nil // довжина ПІСЛЯ додавання — як RPUSH
}

func (s *memStore) Drain(_ context.Context, g string) ([][]byte, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := s.lists[g]
	delete(s.lists, g)
	return out, nil
}

func (s *memStore) Take(_ context.Context, key string, burst, rate float64) (bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	b := s.tb[key]
	if b == nil {
		b = &tokbucket{tokens: burst, last: s.now()}
		s.tb[key] = b
	}
	b.tokens += s.now().Sub(b.last).Seconds() * rate // дозрів за годинником СХОВИЩА
	if b.tokens > burst {
		b.tokens = burst
	}
	b.last = s.now()
	if b.tokens >= 1 {
		b.tokens--
		return true, nil
	}
	return false, nil
}

// Індекс дедлайнів: у Redis це ZSET, тут — мапа група→мить, скан під мютексом.
func (s *memStore) MarkDue(_ context.Context, group string, at time.Time) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.due[group] = at // ZADD due <at> group
	return nil
}

func (s *memStore) DueGroups(_ context.Context, now time.Time) ([]string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	var out []string
	for group, deadline := range s.due { // ZRANGEBYSCORE due -inf now
		if !deadline.After(now) {
			out = append(out, group)
		}
	}
	return out, nil
}

func (s *memStore) ClearDue(_ context.Context, group string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.due, group) // ZREM due group
	return nil
}
```

Решта тестів пишуться так само дешево, бо весь стан за інтерфейсом і час — інжектований: дедуп доводиться двома `Admit` тієї самої події (`Buffered`, тоді `Dropped`); драбина — відром на нуль жетонів і перевіркою, що `info` після одного притримання відкидається, а `warning` спадає на канал `feed`; тихі години — годинником на третю ночі, що жене все в `rebuffer`. Кожна пастка теми — окремий червоний тест, поки код неправильний.

## Складність і пастки

Уся дешевизна цих тестів прийшла з двох рішень: **стан за атомарним інтерфейсом** і **час як залежність**. Решта пасток — там, де стик двох механізмів, і кожна вже має свою відповідь у коді:

- **Надто широкий ключ дедупу глушить різні тривоги.** Ключ несе `Event` (з часом до хвилини), не самий лише тип події. Приберіть `Event` — і «двері о сьомій ранку» з'їдять «двері о п'ятій вечора» як дубль. Помилка тиха: код не падає, він мовчки ковтає справжні сповіщення, і дізнаєшся ти про це від розлюченого користувача, а не з дашборда.
- **Злиття між інстансами — гонка «обидва бачать новий ключ».** Лікується не замком навколо «перевір-тоді-дій», а тим, що `Append` **повертає** довжину: власника обирає одна атомарна операція. Тест `TestCoalesceRaceGivesOneDigest` падає рівно тоді, коли цю атомарність зламано.
- **Витік і сирітство таймерів.** Таймер у пам'яті гине з процесом, лишаючи буфер у сховищі. Дедлайн має жити у сховищі, а підмітальник у кожному інстансі — добирати прострочені групи; локальний `time.AfterFunc` — лише прискорювач. І не озброюй новий таймер на кожну подію — лише на ту, що отримала довжину `1`, інакше таймери накопичаться.
- **Критичне не дедупити геть.** Гілка `0` в `Admit` стоїть до всього; для критичного зайва копія — прийнятна ціна, проковтнута тривога — ні. Тест на це — найперший у файлі.
- **Два годинники, не переплутати.** Тривалості (відро, TTL) — монотонний годинник, а у спільному відрі — годинник самого сховища, щоб інстанси були згодні. Тихі години — настінний **місцевий** час людини в її поясі. Wall-clock у відрі ламає стелю на стрибку NTP; UTC в тихих годинах будить не в тому поясі.

Ось що дає цей вузол разом, чого не давало жодне сито окремо: сорок три сирі події нічної бурі виходять двома перериваннями — одним спокійним дайджестом і одним негайним «дим!» в обхід — а не вісімдесятьма двома. І кожен інстанс відправника фільтрує не свій наосліп узятий шматок, а спільний потік, бо весь стан живе там, де його бачать усі. Далі ці три сита стають однією ланкою наскрізного [конвеєра сповіщень Digital Homes](root:progarch/dh-notification-pipeline) — від події в домі до єдиного, вчасного, спокійного рядка на екрані родини; а дублі, які тут прибирає дедуп, народжуються ще на вході, бо канал [at-least-once і повтори там — норма](root:progarch/duplicates-and-reorder).
