# ⚙️ Межовий адаптер: обидві течії й тест, що глушить хмару

Стаття намалювала **форму**: порт `CloudLink`, ескіз `NetworkCloud` із бюджетом, повтором і ключем, дворядковий рефлекс звірки. Ескіз чесний щодо наміру й німий щодо найважчого — де фізично живе буфер звітів, скільки коштує «фактично раз» на дроті, що саме стається, коли хмара гасне **посеред** потоку. Тут ми доберемо адаптер до кінця, щоб він **працював**, а тоді зробимо те, чого ескіз не вміє ніколи: уб'ємо хмару в найгіршу мить і подивимось. Обіцянку, яку треба заслужити кодом, а не словом, сформулюймо просто: **вхідні двері відчиняються далі**, а коли канал вертається — **кожен звіт лягає рівно раз**, і в порядку правди, а не в порядку прибуття пакетів.

Ідея всього проєкту в одному реченні: **один адаптер за портом, дві течії з протилежною поставою і тест, що доводить — життєвий контур не залежить від дроту структурно, а не за обіцянкою.** Мова тут — стек-мови розподіленого бекенду: Go (його `context`-дедлайни, ґорутини й канали для флашера — рідні саме для цієї задачі) і TypeScript (той самий адаптер ідіоматично на промісах), обидва вкладками. Спершу — спільний словник і два порти:

:::tabs
```ts
// пакет boundary. Домен — три речі, що течуть крізь межу.
type Command = { key: string; kind: string; dev: string; arg?: string }; // key = ключ ідемпотентності
type Result  = { ok: boolean; note: string };
type Report  = { dev: string; field: string; value: string; ts: number }; // ts = ВЛАСНА мітка відліку

// Порт, що бачить логіка хаба (та сама форма, що в статті).
interface CloudLink {
  send(cmd: Command): Promise<Result>; // команда: синхронно, «фактично раз»
  emit(rep: Report): void;             // звіт: у буфер і назад, не чекаючи мережі
}

// Те, що фізично лягає в мережу. НЕнадійне: таймаут, обрив, тиша.
interface Wire {
  postCmd(cmd: Command, signal?: AbortSignal): Promise<Result>;
  postReport(rep: Report, signal?: AbortSignal): Promise<void>;
  getState(dev: string, signal?: AbortSignal): Promise<string>;
}
class Unreachable extends Error {} // справжній Wire перекладає сюди обрив/таймаут fetch
```
```go
// пакет boundary; import: context, errors, fmt, sync, sync/atomic, time,
//                          "math/rand/v2" (як rand), testing.
type Command struct {
	Key, Kind, Dev, Arg string // Key = ключ ідемпотентності, СТАЛИЙ крізь усі повтори
}
type Result struct{ OK bool; Note string }
type Report struct {
	Dev, Field, Value string
	TS                int64 // ВЛАСНА мітка часу відліку; строго зростає per (Dev,Field)
}

// Порт, що бачить логіка хаба (та сама форма, що в статті).
type CloudLink interface {
	Send(ctx context.Context, cmd Command) (Result, error) // команда: синхронно, «фактично раз»
	Emit(rep Report)                                        // звіт: у буфер, не чекаючи мережі
}

// Те, що фізично лягає в мережу. НЕнадійне: таймаут, обрив, тиша.
type Wire interface {
	PostCmd(ctx context.Context, cmd Command) (Result, error)
	PostReport(ctx context.Context, rep Report) error
	GetState(ctx context.Context, dev string) (string, error)
}

var ErrUnreachable = errors.New("хмара недосяжна") // єдине, що вільно повторювати
```
:::

Зверни увагу на дві межі, а не одну. `CloudLink` — те, що бачить логіка; `Wire` — те, що справді торкається дроту, і воно наскрізь ненадійне. Уся мережева чесність оселяється **між** ними, в адаптері. Це не педантизм: саме цей поділ дасть нам за хвилину змогу «вимкнути хмару» в тесті, підмінивши лише `Wire`, і не зачепити ані рядка логіки.

## Бік хмари: два дедупи, з яких народжується «раз»

Почнемо з дальшого берега, бо там ховається половина правди, яку клієнт сам забезпечити не може. Клієнт, що кличе крізь мережу, після таймауту **не знає** різниці між двома світами: «не дійшло» і «дійшло, виконалось, а відповідь загубилась». Розрізнити їх звідси неможливо — це і є [тиша як третя доля виклику](root:progarch/partial-failure). Тому єдиний чесний хід клієнта — **повторити**: якщо не дійшло, повтор рятує; якщо дійшло, повтор нашкодить, і з цим уже мусить розібратися той, хто виконує. Так народжується пара: клієнт дає «щонайменше раз», а виконавець згортає дублі до ефекту «рівно раз». Ця сума й зветься [доставкою «фактично раз»](book:programming/delivery-guarantees) — не магія на дроті, а **at-least-once + дедуп** на боці того, хто діє. Жодна половина сама по собі не «раз».

Хмара тримає для цього дві маленькі пам'яті. Для команд — таблицю бачених [ключів ідемпотентності](book:programming/idempotency): той самий ключ удруге повертає **кешований** результат, не повторюючи дії. Для звітів — по одній найсвіжішій **власній мітці часу** на кожне (пристрій, поле): усе, що прийшло з міткою не новішою за бачену, — або дубль повтору, або спізнілий [реордер](root:progarch/duplicates-and-reorder), і в обох випадках його треба тихо відкинути. Дивовижа в тім, що **одне** порівняння `ts ≤ бачене` ловить обидві біди разом:

:::tabs
```ts
// ── БІК ХМАРИ: тут живе дедуп — друга половина «фактично раз». ──
class CloudServer {
  private seen   = new Map<string, Result>(); // ключ ідемпотентності → кешований результат
  private lastTS = new Map<string, number>(); // dev|field → найсвіжіша бачена мітка
  private state  = new Map<string, string>(); // dev → востаннє почуте значення
  executed = 0;                               // скільки КОМАНД реально виконано
  applied  = 0;                               // скільки ЗВІТІВ реально застосовано

  // Команда: той самий ключ → той самий результат, дію НЕ повторюємо.
  handleCmd(cmd: Command): Result {
    const hit = this.seen.get(cmd.key);
    if (hit) return hit;                       // ДУБЛЬ повтору — нічого не робимо
    this.executed++;                           // виконуємо РІВНО раз
    if (cmd.kind === "setState") this.state.set(cmd.dev, cmd.arg ?? "");
    const r: Result = { ok: true, note: `виконано ${cmd.kind}` };
    this.seen.set(cmd.key, r);
    return r;
  }

  // Звіт: одне правило ловить і дубль, і спізнілий реордер.
  handleReport(rep: Report): void {
    const k = `${rep.dev}|${rep.field}`;
    if (rep.ts <= (this.lastTS.get(k) ?? 0)) return; // ≤ бачене → дубль АБО старіший реордер
    this.lastTS.set(k, rep.ts);                      // свіжіша мітка виграла
    this.state.set(rep.dev, rep.value);
    this.applied++;
  }
  get(dev: string): string { return this.state.get(dev) ?? ""; }
}
```
```go
// ── БІК ХМАРИ: тут живе дедуп — друга половина «фактично раз». ──
type CloudServer struct {
	mu       sync.Mutex
	seen     map[string]Result // ключ ідемпотентності → кешований результат
	lastTS   map[string]int64  // dev|field → найсвіжіша бачена мітка
	state    map[string]string // dev → востаннє почуте значення
	executed int               // скільки КОМАНД реально виконано
	applied  int               // скільки ЗВІТІВ реально застосовано
}
func NewCloudServer() *CloudServer {
	return &CloudServer{seen: map[string]Result{}, lastTS: map[string]int64{}, state: map[string]string{}}
}

// Команда: той самий ключ → той самий результат, дію НЕ повторюємо.
func (s *CloudServer) HandleCmd(cmd Command) Result {
	s.mu.Lock()
	defer s.mu.Unlock()
	if r, ok := s.seen[cmd.Key]; ok {
		return r // ДУБЛЬ повтору — нічого не робимо
	}
	s.executed++ // виконуємо РІВНО раз
	if cmd.Kind == "setState" {
		s.state[cmd.Dev] = cmd.Arg
	}
	r := Result{OK: true, Note: "виконано " + cmd.Kind}
	s.seen[cmd.Key] = r
	return r
}

// Звіт: одне правило ловить і дубль, і спізнілий реордер.
func (s *CloudServer) HandleReport(rep Report) {
	s.mu.Lock()
	defer s.mu.Unlock()
	k := rep.Dev + "|" + rep.Field
	if rep.TS <= s.lastTS[k] { // ≤ бачене → дубль АБО старіший реордер
		return
	}
	s.lastTS[k] = rep.TS // свіжіша мітка виграла
	s.state[rep.Dev] = rep.Value
	s.applied++
}
func (s *CloudServer) State(dev string) string { s.mu.Lock(); defer s.mu.Unlock(); return s.state[dev] }
func (s *CloudServer) Applied() int            { s.mu.Lock(); defer s.mu.Unlock(); return s.applied }
```
:::

Перевірмо обидва правила руч, кожне окремим сюжетом. Спершу команда: дві доставки одного ключа — а двері відчиняються раз.

```go
srv := NewCloudServer()
r1 := srv.HandleCmd(Command{Key: "cmd-7", Kind: "open", Dev: "lock-42"}) // виконано
r2 := srv.HandleCmd(Command{Key: "cmd-7", Kind: "open", Dev: "lock-42"}) // ДУБЛЬ повтору
fmt.Println(r1 == r2, srv.executed) // true 1  ← той самий результат, двері відчинено раз
```

Тепер звіт — і дивись, як **те саме** правило `ts ≤ бачене` відсіює і старіший відлік, що приплентався пізніше, і точний дубль повтору:

```go
srv := NewCloudServer()
srv.HandleReport(Report{Dev: "s", Field: "temp", Value: "21°", TS: 3}) // застосовано
srv.HandleReport(Report{Dev: "s", Field: "temp", Value: "19°", TS: 2}) // СПІЗНІЛИЙ (2<3) → ігнор
srv.HandleReport(Report{Dev: "s", Field: "temp", Value: "21°", TS: 3}) // ДУБЛЬ    (3=3) → ігнор
fmt.Println(srv.State("s"), srv.Applied()) // 21° 1  ← остання правда, застосовано раз
```

Оце й уся хитрість «свіжіша за власною міткою». Ми не намагаємось відновити **порядок відправлення** — це безнадійно, пакети йдуть як хочуть. Ми питаємо лише «чи новіша ця правда за ту, що я вже маю», і відповідь дає мітка, яку **сам пристрій** поставив у мить відліку. Старіший відлік, що дійшов пізніше, тим самим програє автоматично; повтор, що несе ту саму мітку, — теж. Одне порівняння, дві біди.

> 🔧 **Навіщо це.** «Фактично раз» — не властивість каналу, а **договір двох берегів**: клієнт зобов'язується повторювати (бо інакше загублене не долетить), сервер зобов'язується дедуплікувати (бо інакше повторене здвоїться). Якщо в системі є ретраї, але немає дедупу, — у тебе не «фактично раз», а «інколи двічі», і воно вистрелить рівно тоді, коли команда неідемпотентна. Тримай дедуп-пам'ять там, де відбувається **дія**, і рівно настільки довго, наскільки клієнт здатен повторювати.

## Бік хаба: команда чекає, звіт не чекає нікого

Тепер ближчий берег — сам адаптер. Дві течії розходяться в ньому фізично, і найкраще це видно на тому, **чи є там `await` на мережу**. Команда синхронна: хтось дивиться на крутилку, тож `send` мусить дочекатися відповіді — з [бюджетом часу на монотонному годиннику](root:progarch/concurrency-and-clocks/proj-monotonic-deadline.md) і [повтором із відступом та джитером](book:programming/retries-backoff), причому ключ **сталий** крізь усі спроби, бо новий ключ на кожну спробу зламав би дедуп на тім боці. А звіт — навпаки: гарячий шлях удома не сміє блокуватися на дроті ані на мить, тож `emit` кладе відлік у **локальний буфер** і негайно повертає; окремий фоновий флашер досилає, коли зможе. Це і є [store-and-forward](book:programming/delivery-guarantees): віддав у чергу — і живи далі.

:::tabs
```ts
class NetworkCloud implements CloudLink {
  private buf: Report[] = [];
  private wake?: () => void;
  constructor(private wire: Wire) {}

  // КОМАНДА: бюджет часу + повтор із джитером; ключ СТАЛИЙ крізь спроби.
  async send(cmd: Command): Promise<Result> {
    const deadline = performance.now() + 10_000; // монотонний бюджет, НЕ Date.now()
    for (let attempt = 0; ; attempt++) {
      const left = deadline - performance.now();
      if (left <= 0) throw new Unreachable();               // бюджет вичерпано
      const ac = new AbortController();
      const timer = setTimeout(() => ac.abort(), left);     // таймаут спроби = залишок бюджету
      try {
        return await this.wire.postCmd(cmd, ac.signal);     // той самий cmd.key щоразу
      } catch (e) {
        if (!(e instanceof Unreachable)) throw e;           // не мережа — не повторюємо
        const wait = Math.random() * Math.min(3000, 100 * 2 ** attempt); // повний джитер
        if (performance.now() + wait > deadline) throw new Unreachable();
        await sleep(wait);
      } finally {
        clearTimeout(timer);
      }
    }
  }

  // ЗВІТ (гарячий шлях): у буфер і НЕГАЙНО назад — мережі не торкаємось.
  emit(rep: Report): void {
    this.buf.push(rep);
    this.wake?.();            // штовхнути флашер, якщо він дрімає
    this.wake = undefined;
  }

  // Фоновий флашер: доки хмара мовчить — тримає; ожила — досилає по черзі.
  async flushLoop(signal: AbortSignal): Promise<void> {
    while (!signal.aborted) {
      await this.drain();
      await new Promise<void>((res) => {                    // чекати сигналу АБО 500 мс
        this.wake = res;
        const t = setTimeout(res, 500);
        signal.addEventListener("abort", () => { clearTimeout(t); res(); }, { once: true });
      });
    }
  }

  private async drain(): Promise<void> {
    while (this.buf.length > 0) {
      const head = this.buf[0];                             // не знімаємо, поки не підтверджено
      const ac = new AbortController();
      const timer = setTimeout(() => ac.abort(), 2000);
      try {
        await this.wire.postReport(head, ac.signal);
      } catch {
        return;                                             // хмара мовчить/ACK не дійшов — лишаємо
      } finally {
        clearTimeout(timer);
      }
      this.buf.shift();                                     // ACK отримано — АЖ ТЕПЕР знімаємо голову
    }
  }

  pending(): number { return this.buf.length; }
  readState(dev: string): Promise<string> { return this.wire.getState(dev, AbortSignal.timeout(2000)); }
}
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
```
```go
type NetworkCloud struct {
	wire Wire
	mu   sync.Mutex
	buf  []Report      // черга непідтверджених звітів (FIFO)
	sig  chan struct{} // будильник флашера
}
func NewNetworkCloud(w Wire) *NetworkCloud { return &NetworkCloud{wire: w, sig: make(chan struct{}, 1)} }

// КОМАНДА: бюджет часу + повтор із відступом і джитером; ключ СТАЛИЙ крізь спроби.
func (c *NetworkCloud) Send(ctx context.Context, cmd Command) (Result, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second) // монотонний дедлайн
	defer cancel()
	const base, capD = 100 * time.Millisecond, 3 * time.Second
	for attempt := 0; ; attempt++ {
		res, err := c.wire.PostCmd(ctx, cmd) // той самий cmd.Key щоразу
		if err == nil || !errors.Is(err, ErrUnreachable) {
			return res, err // успіх або невиправна помилка — не повторюємо
		}
		w := base << attempt
		if w <= 0 || w > capD { // <=0 ловить переповнення зсуву на великому attempt
			w = capD
		}
		wait := time.Duration(rand.Int64N(int64(w))) // повний джитер: рівномірно [0, вікно)
		if dl, ok := ctx.Deadline(); ok && time.Until(dl) < wait {
			return res, fmt.Errorf("бюджет вичерпано: %w", err) // не спати за дедлайн
		}
		select {
		case <-time.After(wait):
		case <-ctx.Done():
			return res, ctx.Err()
		}
	}
}

// ЗВІТ (гарячий шлях): у буфер і НЕГАЙНО назад — мережі не торкаємось.
func (c *NetworkCloud) Emit(rep Report) {
	c.mu.Lock()
	c.buf = append(c.buf, rep)
	c.mu.Unlock()
	select {
	case c.sig <- struct{}{}: // штовхнути флашер, не блокуючись
	default:
	}
}

// Фоновий флашер: доки хмара мовчить — тримає; ожила — досилає по черзі.
func (c *NetworkCloud) FlushLoop(ctx context.Context) {
	tick := time.NewTicker(500 * time.Millisecond)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-c.sig: // прокинувся на новому звіті
		case <-tick.C: // …або сам, раз на 500 мс
		}
		c.drain(ctx)
	}
}

func (c *NetworkCloud) drain(ctx context.Context) {
	for {
		c.mu.Lock()
		if len(c.buf) == 0 {
			c.mu.Unlock()
			return
		}
		head := c.buf[0] // лише флашер знімає з голови → голова стабільна
		c.mu.Unlock()

		sendCtx, cancel := context.WithTimeout(ctx, 2*time.Second)
		err := c.wire.PostReport(sendCtx, head)
		cancel()
		if err != nil {
			return // хмара мовчить/ACK не дійшов — лишаємо в буфері, спробуємо пізніше
		}
		c.mu.Lock()
		c.buf = c.buf[1:] // ACK отримано — АЖ ТЕПЕР знімаємо голову
		c.mu.Unlock()
	}
}

func (c *NetworkCloud) Pending() int { c.mu.Lock(); defer c.mu.Unlock(); return len(c.buf) }
func (c *NetworkCloud) ReadState(ctx context.Context, dev string) (string, error) {
	return c.wire.GetState(ctx, dev)
}
```
:::

Найтонше місце тут — **коли саме знімати голову з буфера**. Спокуса: відправив — зняв. Але ж «відправив» і «долетіло та підтвердилось» — не те саме. Тому `drain` тримає голову доти, доки не дістане **успішний** ACK; якщо `postReport` повернув помилку — байдуже, хмара мовчить чи ACK згубився дорогою назад, — голова лишається, і наступний прохід пошле її знову. Оце й породжує at-least-once: те, що вже долетіло, але чий ACK утопився, ми чесно надішлемо вдруге — а хмара, як ми щойно бачили, впізнає дубль за міткою й застосує раз. Ось де дві половини змикаються в одне.

Зверни ще увагу, що зняття голови безпечне без зайвих замків саме тому, що **знімає лише флашер**: `emit` завжди дописує в хвіст, тож голова не рухається під ним, поки один флашер її обробляє. Це не випадковість, а умова коректності — про неї згадаємо в пастках.

## Рефлекс звірки: наполегливість замість обіцянки

Лишилась третя деталь — фоновий цикл, що жене «бажане» в «почуте». Стаття вивела його потребу; тут він працює по-справжньому, спираючись на вже готовий `send`. Уся сіль — у **сталому ключі наміру** `set-<dev>-<desired>`: доки бажане не змінилось, усі повтори звірки несуть той самий ключ, тож хмара їх дедуплікує й дію не задвоює; а щойно застосунок захотів іншого — ключ інший, і новий намір проб'ється.

:::tabs
```ts
type Twin = { dev: string; desired: string; reported: string };

// Рефлекс звірки: не гарантія, а наполегливість. Кликати періодично у фоні.
async function reconcile(cloud: NetworkCloud, tw: Twin): Promise<void> {
  if (tw.reported !== tw.desired) {                 // хмара й дім розійшлися
    const key = `set-${tw.dev}-${tw.desired}`;      // сталий ключ наміру → повтор не задвоїть
    await cloud.send({ key, kind: "setState", dev: tw.dev, arg: tw.desired });
  }
  tw.reported = await cloud.readState(tw.dev);      // перечитай, що хмара тепер чує
}
```
```go
type Twin struct{ Dev, Desired, Reported string }

// Рефлекс звірки: не гарантія, а наполегливість. Кликати періодично у фоні.
func (c *NetworkCloud) Reconcile(ctx context.Context, tw *Twin) error {
	if tw.Reported != tw.Desired { // хмара й дім розійшлися — дошли бажане
		key := "set-" + tw.Dev + "-" + tw.Desired // СТАЛИЙ ключ наміру → повтор не задвоїть
		if _, err := c.Send(ctx, Command{Key: key, Kind: "setState", Dev: tw.Dev, Arg: tw.Desired}); err != nil {
			return err // не збіглося цього разу — спробуємо в наступному циклі
		}
	}
	got, err := c.ReadState(ctx, tw.Dev) // перечитай, що хмара тепер чує
	if err != nil {
		return err
	}
	tw.Reported = got
	return nil
}
```
:::

Цикл нічого не «гарантує» в мить виклику — він лише **наполягає**, і тому переживає будь-який збій: не долетіло цього разу — долетить наступного, бо намір записаний у `desired` і не стирається. Це і є [кінцева узгодженість](book:programming/eventual-consistency) у мініатюрі, і саме тому об'єкт `Twin`, що тримає бажане й почуте замість справжнього стану, — зерно [цифрового близнюка дому](root:progarch/dh-replicas).

## Тест, що вимикає світло посеред потоку

Тепер — доказ. Ми підмінюємо лише `Wire` фейком, який уміє дві речі: «замовкнути» (`silent`) і один-єдиний раз «загубити ACK» уже застосованого звіту — щоб у потоці **справді** народився дубль, а не лише в уяві. А життєвий контур — `Hub.Press` — навмисне не має **жодного** посилання на `Wire`: він клацає локальний стан і кладе звіт у буфер. Це та сама [деградація з гідністю, що стала структурою](book:programming/graceful-degradation): контур не залежить від дроту не тому, що ми дописали `catch`, а тому, що дроту просто **немає на його шляху** — і це видно з типів.

:::tabs
```ts
class FakeWire implements Wire {
  silent = false;
  dropAckOnce = false;
  constructor(private srv: CloudServer) {}
  async postCmd(cmd: Command): Promise<Result> {
    if (this.silent) throw new Unreachable();
    return this.srv.handleCmd(cmd);
  }
  async postReport(rep: Report): Promise<void> {
    if (this.silent) throw new Unreachable();                 // хмара мовчить
    this.srv.handleReport(rep);                                // дійшло й ЗАСТОСОВАНО
    if (this.dropAckOnce) { this.dropAckOnce = false; throw new Unreachable(); } // …а ACK загублено
  }
  async getState(dev: string): Promise<string> {
    if (this.silent) throw new Unreachable();
    return this.srv.get(dev);
  }
}

class Hub {                                                    // життєвий контур: кнопка → замок
  lock = "closed";
  private tick = 0;
  constructor(private cloud: NetworkCloud) {}
  press(open: boolean): void {                                // жодного await, жодного Wire — локально
    this.lock = open ? "open" : "closed";
    this.cloud.emit({ dev: "lock-42", field: "lock", value: this.lock, ts: ++this.tick });
  }
}

test("межа переживає тишу хмари", async () => {
  const srv = new CloudServer();
  const wire = new FakeWire(srv);
  wire.dropAckOnce = true;                                     // озброїмо один загублений ACK
  const cloud = new NetworkCloud(wire);
  const ac = new AbortController();
  const flushing = cloud.flushLoop(ac.signal);
  const hub = new Hub(cloud);

  const N = 20;
  let pendingMid = 0;
  for (let i = 1; i <= N; i++) {
    if (i === 5)  wire.silent = true;                          // ← хмара впала ПОСЕРЕД потоку
    if (i === 14) pendingMid = cloud.pending();                // буфер тримає непідтверджені
    if (i === 15) wire.silent = false;                         // ← зв'язок вернувся
    hub.press(i % 2 === 0);
    await sleep(2);                                            // хай флашер устигне щось доставити
  }

  const want = N % 2 === 0 ? "open" : "closed";
  expect(hub.lock).toBe(want);                                // 1) контур не здригнувся
  expect(pendingMid).toBeGreaterThan(0);                      // 2) store-and-forward тримав звіти

  const t0 = performance.now();                               // 3) чекаємо, поки буфер долетить
  while (cloud.pending() > 0 && performance.now() - t0 < 5000) await sleep(10);
  expect(cloud.pending()).toBe(0);
  expect(srv.applied).toBe(N);                                // 4) кожен звіт застосовано РІВНО раз
  expect(srv.get("lock-42")).toBe(want);                      // 5) хмара догнала дім

  ac.abort();
  await flushing;
});
```
```go
// Фейковий Wire: можна «вимкнути» (silent) і один раз «загубити ACK» звіту.
type fakeWire struct {
	srv         *CloudServer
	silent      atomic.Bool
	dropAckOnce atomic.Bool // раз: звіт застосовано, але ACK не повернено → хаб повторить
}
func (w *fakeWire) PostCmd(ctx context.Context, cmd Command) (Result, error) {
	if w.silent.Load() {
		return Result{}, ErrUnreachable
	}
	return w.srv.HandleCmd(cmd), nil
}
func (w *fakeWire) PostReport(ctx context.Context, rep Report) error {
	if w.silent.Load() {
		return ErrUnreachable // хмара мовчить — доставки нема
	}
	w.srv.HandleReport(rep) // дійшло й ЗАСТОСОВАНО
	if w.dropAckOnce.CompareAndSwap(true, false) {
		return ErrUnreachable // …але ACK загублено → хаб вважатиме невдачею й повторить
	}
	return nil
}
func (w *fakeWire) GetState(ctx context.Context, dev string) (string, error) {
	if w.silent.Load() {
		return "", ErrUnreachable
	}
	return w.srv.State(dev), nil
}

// Життєвий контур: кнопка → хаб → замок. Жодного посилання на Wire — суто локальний.
type Hub struct {
	cloud *NetworkCloud
	mu    sync.Mutex
	lock  string
	tick  int64
}
func (h *Hub) Press(open bool) {
	h.mu.Lock()
	if open {
		h.lock = "open"
	} else {
		h.lock = "closed"
	}
	h.tick++
	rep := Report{Dev: "lock-42", Field: "lock", Value: h.lock, TS: h.tick}
	h.mu.Unlock()
	h.cloud.Emit(rep) // замок уже клацнув; звіт лише кладемо в буфер
}
func (h *Hub) Lock() string { h.mu.Lock(); defer h.mu.Unlock(); return h.lock }

func TestBoundarySurvivesSilence(t *testing.T) {
	srv := NewCloudServer()
	wire := &fakeWire{srv: srv}
	wire.dropAckOnce.Store(true) // озброїмо один загублений ACK — щоб виник СПРАВЖНІЙ дубль
	cloud := NewNetworkCloud(wire)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go cloud.FlushLoop(ctx)
	hub := &Hub{cloud: cloud}

	const N = 20
	pendingMid := 0
	for i := 1; i <= N; i++ {
		switch i {
		case 5:
			wire.silent.Store(true) // ← хмара впала ПОСЕРЕД потоку
		case 14:
			pendingMid = cloud.Pending() // буфер має тримати непідтверджені
		case 15:
			wire.silent.Store(false) // ← зв'язок вернувся
		}
		hub.Press(i%2 == 0)
		time.Sleep(2 * time.Millisecond) // хай флашер устигне щось доставити до тиші
	}

	// 1) Життєвий контур не здригнувся: локальний стан = останнє натискання.
	want := "closed"
	if N%2 == 0 {
		want = "open"
	}
	if got := hub.Lock(); got != want {
		t.Fatalf("контур удома здригнувся: lock=%q, чекали %q", got, want)
	}
	// 2) Store-and-forward справді тримав звіти, поки хмара мовчала.
	if pendingMid == 0 {
		t.Fatalf("буфер мав тримати звіти під час тиші, а він порожній")
	}
	// 3) Зв'язок вернувся — чекаємо, поки буфер долетить.
	deadline := time.Now().Add(5 * time.Second)
	for cloud.Pending() > 0 && time.Now().Before(deadline) {
		time.Sleep(5 * time.Millisecond)
	}
	if p := cloud.Pending(); p != 0 {
		t.Fatalf("буфер не спорожнів: лишилось %d", p)
	}
	// 4) Кожен звіт застосовано РІВНО раз (попри тишу й один загублений ACK).
	if srv.Applied() != N {
		t.Fatalf("«фактично раз» порушено: застосовано %d, а натискань %d", srv.Applied(), N)
	}
	// 5) Хмара догнала дім.
	if got := srv.State("lock-42"); got != want {
		t.Fatalf("хмара не збіглася з домом: %q проти %q", got, want)
	}
}
```
:::

П'ять тверджень, і кожне ловить окрему обіцянку модуля. Пройдімось, **чому** кожне мусить справдитись.

**Контур не здригнувся** (§1). Половину потоку — натискання 5…14 — хмара лежить. А `Press` жодного разу не блокується, бо він лише пише в пам'ять і кладе відлік у буфер; локальний `lock` слухняно доходить до останнього натискання. Найсильніший тут доказ навіть не в асерті, а в **типі**: `Hub` не тримає `Wire`, тож компілятор не дав би контуру заблокуватись на мережі, навіть якби ми схотіли. Деградація стала структурою.

**Буфер тримав** (§2). На 14-му натисканні, у розпал тиші, `pending()` більший за нуль — звіти 5…14 (і ті з 1…4, що не встигли долетіти) чекають у черзі, а не гинуть і не валять хаб. Це той самий store-and-forward у дії.

**Фактично раз** (§4) — серце тесту. Кожне натискання карбує відлік зі **строго новішою** міткою (`tick` іде 1…20), тож на своїй першій доставці кожен застосовується рівно раз, а будь-яка повторна доставка несе не новішу мітку й відсівається. Наш навмисно загублений ACK **справді** змусив хаб надіслати один звіт удруге — і `applied` усе одно дорівнює рівно `N`. Ба більше: `pending()` спадає до нуля лише тоді, коли **кожну** голову підтверджено, а голова з утопленим ACK підтверджується аж після того, як її дубль дедуплікували, — тож сама умова «буфер порожній» уже гарантує, що дедуп спрацював.

**Хмара догнала дім** (§5). Коли черга спорожніла, `state` на хмарі дорівнює останньому домашньому `lock`. Розбіжність, що зяяла всю тишу, зійшлася сама, щойно канал ожив, — без жодного ручного втручання.

![Три доріжки під спільною віссю з 20 натискань. Угорі — життєвий контур: двадцять рівних зелених рисок, підпис «усі локальні й миттєві, повз мережу». Посередині — смуга каналу: зелено «онлайн» до 5-го, бурштиново «ХМАРА МОВЧИТЬ» з 5-го по 15-й, знову зелено далі. Унизу — стовпчики глибини буфера: нульові до тиші, ростуть під час тиші до десяти, спадають до нуля по поверненні зв'язку. Плашка: один звіт дійшов двічі, дедуп за міткою застосував його раз. Підсумок: контур не здригнувся, звіти долетіли фактично раз](/root/course/progarch/dh-distribution-crossing/img/silence-test.svg)
*Уся хронологія в одному кадрі: контур удома цокає рівно й незалежно, канал гасне на десять натискань, буфер набрякає й порожніє, а один справжній дубль хмара застосовує рівно раз. Тест не переказує обіцянку — він її виконує.*

## Складність і пастки

Адаптер працює, і саме тому час назвати місця, де він зрадить, якщо перенести його в прод дослівно. Кожна пастка вже стелила комусь нічну зміну.

**Буфер у пам'яті забуває саме тоді, коли найпотрібніший.** Наш `buf` живе в оперативці. Вимкнули хабові живлення посеред тиші — і всі непідтверджені звіти зникли, тобто store-and-forward не пережив рівно тієї події, задля якої існує. У проді черга звітів має лягати на диск (SQLite, лог-файл, вбудований WAL), а не лише в RAM. І вона мусить мати **стелю**: телеметрія росте швидше, ніж мовчить хмара, тож потрібна політика переповнення — для звітів звичайно «викидай найстаріше» (свіжа правда цінніша), а не «рости без краю, доки хаб не задихнеться».

**Монотонність мітки — на совісті пристрою, і її легко втратити.** Правило «свіжіша виграє» надійне рівно настільки, наскільки надійне джерело `ts`. Якщо це настінний годинник пристрою, то стрибок NTP чи перезавантаження можуть кинути його **назад** — і тоді законний новіший відлік дістане меншу мітку, ніж уже бачена, і хмара відкине його **назавжди** («застряглий найсвіжіший»). Тому мітка має бути монотонною per-поле: лічильник відліків, що тільки зростає, або гібридна мітка (годинник + лічильник). І `lastTS` на хмарі мусить бути **довговічним** — переживе перезапуск сервера, інакше після рестарту хмара знову прийме давно застарілі повтори як свіжину.

**Дедуп-пам'ять із коротшою пам'яттю, ніж горизонт повторів, — тиха діра у «фактично раз».** Якщо сервер забуває бачені ключі (надто малий TTL, перезапуск) раніше, ніж клієнт перестає повторювати, то спізнілий ретрай застане чисту пам'ять — і команду виконають удруге. Правило: **час життя дедуп-запису ≥ найбільший можливий горизонт ретраїв клієнта**, а для критичних команд дедуп-таблиця має бути персистентною, а не в мапі одного процесу.

**Ідемпотентність дії — не те саме, що дедуп повідомлення.** Наш `setState("closed")` ідемпотентний за природою: застосуй його двічі — замок однаково зачинений, тож навіть пропущений дедуп нешкідливий. Але «перемкни» чи «додай яскравості на 10» **не** такі: там дубль справді зсуває стан. Ніколи не будуй «фактично раз» на **відносній** команді — спершу зроби її абсолютною (передавай цільовий стан, а не приріст), а вже тоді покладайся на ключ. Ключ рятує від подвійної **доставки**, а не від подвійного **сенсу**.

**Порядок тримає лише один флашер на один канал.** Наш `drain` знімає з голови коректно без CAS саме тому, що знімає його **єдина** ґорутина, поки `Emit` лише дописує в хвіст. Запусти два флашери на той самий буфер — і зникне як інваріант стабільної голови (зіпсуться `buf[1:]`/`shift`, [це вже гонка](book:programming/data-races-locks)), так і FIFO-порядок доставки. Якщо масштабуєшся на кілька каналів чи паралельний флаш — не сподівайся на порядок транспорту взагалі: покладайся тільки на серверне правило мітки, що й так терпить [будь-яке переупорядкування](root:progarch/duplicates-and-reorder).

**Ключ звірки мусить нести намір, а не мить.** `set-<dev>-<desired>` сталий, поки бажане те саме, — тому повтори звірки хмара дедуплікує, а не задвоює. Але зроби ключ, скажімо, з часу чи лічильника циклу — і кожен оберт звірки стане «новою» командою, ти завалиш хмару фантомними записами й уб'єш саму ідею тихого доганяння. Ключ кодує **що ми хочемо**, а не **коли спитали**.

І остання, найтихіша думка. Ми звели весь [ланцюг оман про мережу](book:programming/distributed-fallacies) до жмені дуже конкретного коду: бюджет на монотонному годиннику, сталий ключ, буфер із відкладеним зняттям голови, одне порівняння мітки на дальшому березі. Жодної магії — самі дисципліни, кожна на своєму місці. А тест, що глушить хмару, — не формальність: він єдиний перетворює обіцянку «переживе розрив» із наміру на властивість, яку видно очима. Бо в розподілених системах те, чого ти **не** пробував зламати навмисно, зламається за тебе — і неодмінно о третій ночі.
