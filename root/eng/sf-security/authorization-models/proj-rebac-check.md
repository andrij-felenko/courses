# ⚙️ Перевірка на зв'язках у коді: обхід графа, цикли, межа глибини

<preknowlist>
- [Теорія графів](root:math-combinatorics/graph-theory) — вершини, ребра, шлях, цикл, досяжність однієї вершини з іншої. Уся перевірка нижче зводиться саме до питання про досяжність.
</preknowlist>

Зберімо перевірку доступу для моделі на зв'язках власноруч — від сирих фактів у сховищі до робочої функції, яка на питання «чи може Ада редагувати `doc:api`?» іде графом і повертає «так» або «ні». Писати її варто самому з однієї причини: доки код ховає готовий рушій, здається, що перевірка — це один запит. Коли пишеш сам, видно, що це цикл, який ходить у сховище кілька разів поспіль, і що двома рядками в цьому циклі вирішується і його швидкість, і те, чи він взагалі колись зупиниться.

## Задача

Ось усе, що знає система про наш документ. Ада — учасниця групи інженерів. Група інженерів цілком входить у групу ядра. Редагувати кореневу теку можуть учасники групи ядра. Тека `specs` лежить у корені. Документ `api` лежить у `specs`.

Питання: чи може Ада редагувати `doc:api`?

Відповідь, очевидно, «так» — але зверни увагу, чого в цьому сховищі **немає**. Немає рядка «Ада може редагувати doc:api». І не буде: він народжується з ланцюжка інших фактів, жоден із яких сам по собі про Аду й документ не говорить. Тому звичний хід «зроби запит і прочитай право» не має до чого звернутися: права як збереженої величини не існує. Є факти про зв'язки — а право доводиться щоразу **виводити** заново.

Ось із чого його виводити.

## Ребро: один факт про зв'язок

Факт записують трійкою — об'єкт, відношення, суб'єкт:

```
⟨object⟩#⟨relation⟩@⟨subject⟩

⟨object⟩  ::= ⟨namespace⟩:⟨id⟩          doc:api, folder:root, group:eng
⟨subject⟩ ::= ⟨user id⟩ | ⟨object⟩#⟨relation⟩
```

Читається як речення: «`doc:api#owner@ada`» — Ада власниця документа api. Такий текстовий запис ужив Google, описуючи Zanzibar 2019 року на конференції USENIX ATC (*документований факт*: стаття «Zanzibar: Google's Consistent, Global Authorization System», Ruoming Pang та співавтори); ми беремо його як є, бо він короткий і точний.

Уся сіль — в останньому рядку граматики. Суб'єктом може бути не лише конкретна людина, а **інший об'єкт із відношенням**: `doc:readme#viewer@group:eng#member` означає «читачі readme — це учасники групи eng». Такий складений суб'єкт називають множиною користувачів (англ. *userset*). І щойно суб'єкт сам може виявитися множиною, сховище фактів перестає бути списком і стає графом: вершина — це множина `object#relation`, листок — конкретна людина, а кожен збережений факт — ребро.

Наші п'ять фактів у цьому записі:

```
group:eng#member@ada                       Ада — учасниця group:eng
group:core#member@group:eng#member         уся group:eng вкладена в group:core
folder:root#editor@group:core#member       редактори кореня — учасники group:core
folder:specs#parent@folder:root#...        specs лежить у root
doc:api#parent@folder:specs#...            api лежить у specs
```

Три крапки в останніх двох рядках — теж із запису Zanzibar: там, де відношення суб'єкта не має значення (важлива сама тека, а не якась її множина), пишуть `#...`. Це позначка «тут відношення байдуже», і код її просто не читає.

## Правила: ребра, яких ніхто не зберігав

П'яти фактів для відповіді все ще замало. Між `doc:api` й `folder:specs` є `parent`, але `parent` — це не право; ніде не сказано, що редактор теки вміє редагувати те, що в ній лежить. Це знання загальне, воно про **всі** документи одразу, а не про наш. Тому його не зберігають фактом, а описують правилом.

Правил, які нас цікавлять, рівно два види.

**Похідне відношення** — на тому самому об'єкті інше відношення: «усі редактори водночас є читачами». Ребро всередині однієї вершини, у сховище по нього ходити не треба.

**Прохід за зв'язком** — піти по відношенню `parent` до батьківського об'єкта й спитати вже **там** інше відношення: «редактори моєї теки — теж мої редактори». Це те саме успадкування, за яким доступ тече згори вниз по дереву тек, і саме воно робить перевірку багатокроковою.

Чому не зберегти ці ребра фактами? Бо правило справджується для кожного об'єкта простору імен, а таких об'єктів мільярди: довелося б класти по факту на кожен документ, і — гірше — змінити політику одним рухом стало б неможливо. Правило пишуть раз, і воно накриває всіх.

## Ідея: це задача про досяжність

Тепер питання складається саме. Перевірка `можна?(Ада, editor, doc:api)` — це питання «чи досяжна вершина `ada` з вершини `doc:api#editor`, якщо ребрами вважати і збережені факти, і ті, що дописують правила». Автори Zanzibar сформулювали це для вкладених груп так само прямо: членство в групі — задача про досяжність у графі, де вершини — це групи й люди, а ребра — пряме членство.

Досяжність шукають [пошуком у ширину](root:sf-algorithms/breadth-first-search) — по одному рівню за раз, від початкової вершини вшир. Обхід у глибину дав би ту саму відповідь, і саме так виглядає наївна рекурсивна реалізація. Але тут форма обходу — не питання смаку, бо кожне ребро коштує **походу в сховище**, а не розіменування вказівника.

Ось звідки беруться обидва рішення, на яких тримається код нижче.

**Ходити рівнями.** Усі вершини одного рівня треба прочитати в один і той самий момент — отже, їхні ключі можна скласти в одну пачку й забрати **одним** запитом. Тоді ширина рівня перестає коштувати часу: хоч одна вершина в ньому, хоч двісті — це той самий один похід. Рекурсивний обхід у глибину такої змоги не дає: він доходить до дна однією гілкою, і кожне ребро на шляху — окремий запит.

**Пам'ятати розкрите.** Одну й ту саму вершину граф підсуває знову й знову: тека, до якої ведуть два різні шляхи; група, що трапляється в десятку документів. Розкривати її вдруге — марна робота. А коли у зв'язках трапиться цикл, то не просто марна: без пам'яті обхід ходитиме по колу, доки його щось не спинить.

> 🔧 **Навіщо це.** Форма цього циклу — і є бюджет затримки твого API. Перевірка стоїть на кожному запиті, тож її час додається до кожного запиту, і поки решта коду міряється мікросекундами, тут ідеться про походи в мережу. Обхід рівнями перетворює «стільки запитів, скільки ребер» на «стільки запитів, скільки рівнів» — а рівнів у здоровій ієрархії одиниці, тоді як ребер бувають сотні. Це не оптимізація наостанок: це вибір форми, після якого решта або вкладається в бюджет, або ні.

## Робочий код

Чотири узгоджені за поведінкою реалізації — на TypeScript, Go, C99 та C++20. Кожна містить повну модель даних, декларативні правила, сховище фактів із пакетним читанням (`readMany`), локальне замикання за похідними відношеннями без походів у сховище, пошук у ширину рівнями, мемоізацію відвіданих вершин та межу глибини, а також модульні тести перевірки дозволів.

:::tabs
```ts
// ── Модель даних: вершина, ребро, факт ──────────────────────────────────────

/** Вершина графа: множина «усі, хто має relation до object». */
type Userset = { object: string; relation: string };

/** Те, на що вказує ребро: або конкретна людина (листок), або інша вершина. */
type Subject = { user: string } | Userset;

type Tuple = { object: string; relation: string; subject: Subject };

const key = (u: { object: string; relation: string }) => `${u.object}#${u.relation}`;
const isUser = (s: Subject): s is { user: string } => "user" in s;

// ── Правила: ребра, яких у сховищі немає ────────────────────────────────────
type Rule =
  | { kind: "this" }                              // те, що справді лежить у сховищі
  | { kind: "computed"; relation: string }        // той самий object, інше відношення
  | { kind: "walk"; via: string; then: string };  // піти за зв'язком і спитати там

/** namespace → relation → об'єднання правил. */
type Config = Record<string, Record<string, Rule[]>>;

const config: Config = {
  group: { member: [{ kind: "this" }] },
  folder: {
    parent: [{ kind: "this" }],
    editor: [{ kind: "this" }, { kind: "walk", via: "parent", then: "editor" }],
    viewer: [{ kind: "this" }, { kind: "computed", relation: "editor" },
             { kind: "walk", via: "parent", then: "viewer" }],
  },
  doc: {
    parent: [{ kind: "this" }],
    editor: [{ kind: "this" }, { kind: "walk", via: "parent", then: "editor" }],
    viewer: [{ kind: "this" }, { kind: "computed", relation: "editor" },
             { kind: "walk", via: "parent", then: "viewer" }],
  },
};

// невідомий namespace чи relation — нуль правил, тобто відмова за замовчанням
const rulesFor = (u: Userset): Rule[] =>
  config[u.object.split(":")[0]]?.[u.relation] ?? [];

// ── Сховище: читає ПАЧКУ ключів одним походом ───────────────────────────────
interface Store {
  readMany(keys: Userset[]): Promise<Map<string, Subject[]>>;
}

class MemoryStore implements Store {
  private idx = new Map<string, Subject[]>();
  trips = 0;                                   // скільки разів ми сходили у сховище
  constructor(tuples: Tuple[]) {
    for (const t of tuples) {
      if (!this.idx.has(key(t))) this.idx.set(key(t), []);
      this.idx.get(key(t))!.push(t.subject);
    }
  }
  async readMany(keys: Userset[]): Promise<Map<string, Subject[]>> {
    this.trips++;                              // один похід — скільки б ключів не було
    const rows = new Map<string, Subject[]>();
    for (const k of keys) rows.set(key(k), this.idx.get(key(k)) ?? []);
    return rows;
  }
}

// ── Замикання за похідними відношеннями: у сховище НЕ ходить ────────────────
function closeComputed(frontier: Userset[]): Userset[] {
  const local = new Set<string>();             // правила теж бувають кільцем
  const out: Userset[] = [];
  const stack = [...frontier];
  while (stack.length) {
    const n = stack.pop()!;
    if (local.has(key(n))) continue;
    local.add(key(n));
    out.push(n);
    for (const r of rulesFor(n))
      if (r.kind === "computed") stack.push({ object: n.object, relation: r.relation });
  }
  return out;
}

export class DepthExceeded extends Error {}

// ── Сама перевірка: обхід графа рівнями ─────────────────────────────────────
export async function check(
  store: Store, user: string, start: Userset,
  { maxDepth = 16, memo = true } = {},
): Promise<{ allowed: boolean; depth: number; trips: number }> {
  const seen = new Set<string>([key(start)]);
  let frontier = [start];
  let trips = 0;

  for (let depth = 0; depth < maxDepth; depth++) {
    if (frontier.length === 0) return { allowed: false, depth, trips };  // граф вичерпано

    const nodes = closeComputed(frontier);

    // (1) зібрати ВСЕ, що доведеться прочитати на цьому рівні
    const want: Userset[] = [];
    const wanted = new Set<string>();
    const add = (u: Userset) => {
      if (wanted.has(key(u))) return;
      wanted.add(key(u));
      want.push(u);
    };
    for (const n of nodes)
      for (const r of rulesFor(n)) {
        if (r.kind === "this") add(n);
        if (r.kind === "walk") add({ object: n.object, relation: r.via });
      }

    // (2) один похід у сховище на весь рівень
    const rows = await store.readMany(want);
    trips++;

    // (3) розбір: знайшли — виходимо; ні — складаємо наступний рівень
    const next: Userset[] = [];
    const enqueue = (u: Userset) => {
      if (memo) {
        if (seen.has(key(u))) return;          // уже розкривали — вдруге не треба
        seen.add(key(u));
      }
      next.push(u);
    };
    for (const n of nodes)
      for (const r of rulesFor(n)) {
        if (r.kind === "this")
          for (const s of rows.get(key(n)) ?? []) {
            if (isUser(s)) { if (s.user === user) return { allowed: true, depth, trips }; }
            else enqueue(s);
          }
        if (r.kind === "walk") {
          const via = { object: n.object, relation: r.via };
          for (const s of rows.get(key(via)) ?? [])
            // збережене відношення у зв'язку ігноруємо — питаємо те, що каже правило
            if (!isUser(s)) enqueue({ object: s.object, relation: r.then });
        }
      }
    frontier = next;
  }
  throw new DepthExceeded(`${key(start)}: обхід не вклався в ${maxDepth} рівнів`);
}
```
```go
package rebac

import (
	"errors"
	"fmt"
	"strings"
)

// ── Модель даних: вершина, ребро, факт ──────────────────────────────────────

// Userset — вершина графа: множина «усі, хто має Relation до Object».
type Userset struct{ Object, Relation string }

func (u Userset) Key() string { return u.Object + "#" + u.Relation }

// Subject — те, на що вказує ребро: непорожній User — це листок графа,
// інакше Set — інша вершина, яку ще треба розкрити.
type Subject struct {
	User string
	Set  Userset
}

func (s Subject) IsUser() bool { return s.User != "" }

type Tuple struct {
	Object, Relation string
	Subject          Subject
}

// ── Правила: ребра, яких у сховищі немає ────────────────────────────────────

type RuleKind int

const (
	This     RuleKind = iota // те, що справді лежить у сховищі
	Computed                 // той самий Object, інше відношення
	Walk                     // піти за зв'язком Via і спитати там Then
)

type Rule struct {
	Kind           RuleKind
	Rel, Via, Then string
}

// Config: namespace → relation → об'єднання правил.
type Config map[string]map[string][]Rule

// ── Сховище: читає ПАЧКУ ключів одним походом ───────────────────────────────

type Store interface {
	ReadMany(keys []Userset) (map[string][]Subject, error)
}

type MemoryStore struct {
	idx   map[string][]Subject
	Trips int // скільки разів ми сходили у сховище
}

func NewMemoryStore(tuples []Tuple) *MemoryStore {
	idx := make(map[string][]Subject, len(tuples))
	for _, t := range tuples {
		k := t.Object + "#" + t.Relation
		idx[k] = append(idx[k], t.Subject)
	}
	return &MemoryStore{idx: idx}
}

func (m *MemoryStore) ReadMany(keys []Userset) (map[string][]Subject, error) {
	m.Trips++ // один похід — скільки б ключів не було
	rows := make(map[string][]Subject, len(keys))
	for _, k := range keys {
		rows[k.Key()] = m.idx[k.Key()]
	}
	return rows, nil
}

// ── Сама перевірка ──────────────────────────────────────────────────────────

var ErrDepthExceeded = errors.New("обхід не вклався в межу глибини")

type Result struct {
	Allowed bool
	Depth   int
	Trips   int
}

type Checker struct {
	Cfg      Config
	Store    Store
	MaxDepth int
	Memo     bool
}

// невідомий namespace чи relation — нуль правил, тобто відмова за замовчанням
func (c *Checker) rules(u Userset) []Rule {
	ns, _, _ := strings.Cut(u.Object, ":")
	return c.Cfg[ns][u.Relation]
}

// closeComputed — замикання за похідними відношеннями: у сховище НЕ ходить.
func (c *Checker) closeComputed(frontier []Userset) []Userset {
	local := map[string]bool{} // правила теж бувають кільцем
	out := make([]Userset, 0, len(frontier))
	stack := append([]Userset(nil), frontier...)
	for len(stack) > 0 {
		n := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if local[n.Key()] {
			continue
		}
		local[n.Key()] = true
		out = append(out, n)
		for _, r := range c.rules(n) {
			if r.Kind == Computed {
				stack = append(stack, Userset{n.Object, r.Rel})
			}
		}
	}
	return out
}

func (c *Checker) Check(user string, start Userset) (Result, error) {
	seen := map[string]bool{start.Key(): true}
	frontier := []Userset{start}
	trips := 0

	for depth := 0; depth < c.MaxDepth; depth++ {
		if len(frontier) == 0 {
			return Result{false, depth, trips}, nil // граф вичерпано — «ні»
		}
		nodes := c.closeComputed(frontier)

		// (1) зібрати ВСЕ, що доведеться прочитати на цьому рівні
		var want []Userset
		wanted := map[string]bool{}
		add := func(u Userset) {
			if wanted[u.Key()] {
				return
			}
			wanted[u.Key()] = true
			want = append(want, u)
		}
		for _, n := range nodes {
			for _, r := range c.rules(n) {
				switch r.Kind {
				case This:
					add(n)
				case Walk:
					add(Userset{n.Object, r.Via})
				}
			}
		}

		// (2) один похід у сховище на весь рівень
		rows, err := c.Store.ReadMany(want)
		if err != nil {
			return Result{}, err
		}
		trips++

		// (3) розбір: знайшли — виходимо; ні — складаємо наступний рівень
		var next []Userset
		enqueue := func(u Userset) {
			if c.Memo {
				if seen[u.Key()] { // уже розкривали — вдруге не треба
					return
				}
				seen[u.Key()] = true
			}
			next = append(next, u)
		}
		for _, n := range nodes {
			for _, r := range c.rules(n) {
				switch r.Kind {
				case This:
					for _, s := range rows[n.Key()] {
						if s.IsUser() {
							if s.User == user {
								return Result{true, depth, trips}, nil
							}
						} else {
							enqueue(s.Set)
						}
					}
				case Walk:
					via := Userset{n.Object, r.Via}
					for _, s := range rows[via.Key()] {
						if !s.IsUser() {
							// збережене відношення ігноруємо — питаємо r.Then
							enqueue(Userset{s.Set.Object, r.Then})
						}
					}
				}
			}
		}
		frontier = next
	}
	return Result{}, fmt.Errorf("%w: %s (%d рівнів)", ErrDepthExceeded, start.Key(), c.MaxDepth)
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 64
#define MAX_RULES 8
#define MAX_NODES 256
#define MAX_TUPLES 128

// ── Модель даних: вершина, суб'єкт, кортеж зв'язку ─────────────────────────

typedef struct {
    char object[MAX_NAME];
    char relation[MAX_NAME];
} Userset;

typedef struct {
    bool is_user;
    char user[MAX_NAME];
    Userset set;
} Subject;

typedef struct {
    char object[MAX_NAME];
    char relation[MAX_NAME];
    Subject subject;
} Tuple;

typedef enum {
    RULE_THIS,
    RULE_COMPUTED,
    RULE_WALK
} RuleKind;

typedef struct {
    RuleKind kind;
    char rel[MAX_NAME];
    char via[MAX_NAME];
    char then[MAX_NAME];
} Rule;

typedef struct {
    char ns[MAX_NAME];
    char rel[MAX_NAME];
    Rule rules[MAX_RULES];
    size_t rule_count;
} SchemaEntry;

typedef struct {
    SchemaEntry entries[32];
    size_t count;
} Schema;

typedef struct {
    Tuple tuples[MAX_TUPLES];
    size_t count;
    int trips;
} MemoryStore;

typedef struct {
    bool allowed;
    int depth;
    int trips;
} CheckResult;

// ── Допоміжні функції ключів та пошуку схеми ───────────────────────────────

static void make_key(char *buf, size_t sz, const char *obj, const char *rel) {
    snprintf(buf, sz, "%s#%s", obj, rel);
}

static void get_namespace(char *buf, size_t sz, const char *obj) {
    const char *colon = strchr(obj, ':');
    if (colon) {
        size_t len = (size_t)(colon - obj);
        if (len >= sz) len = sz - 1;
        strncpy(buf, obj, len);
        buf[len] = '\0';
    } else {
        strncpy(buf, obj, sz - 1);
        buf[sz - 1] = '\0';
    }
}

static const SchemaEntry* find_schema(const Schema *s, const char *ns, const char *rel) {
    for (size_t i = 0; i < s->count; i++) {
        if (strcmp(s->entries[i].ns, ns) == 0 && strcmp(s->entries[i].rel, rel) == 0) {
            return &s->entries[i];
        }
    }
    return NULL;
}

// ── Читання пачки ключів зі сховища ────────────────────────────────────────

static size_t store_read_many(MemoryStore *store, const Userset *want, size_t want_count,
                              Subject out_rows[MAX_NODES][MAX_RULES], size_t out_counts[MAX_NODES]) {
    store->trips++;
    for (size_t i = 0; i < want_count; i++) {
        out_counts[i] = 0;
        char req_key[MAX_NAME * 2];
        make_key(req_key, sizeof(req_key), want[i].object, want[i].relation);

        for (size_t t = 0; t < store->count; t++) {
            char tup_key[MAX_NAME * 2];
            make_key(tup_key, sizeof(tup_key), store->tuples[t].object, store->tuples[t].relation);
            if (strcmp(req_key, tup_key) == 0 && out_counts[i] < MAX_RULES) {
                out_rows[i][out_counts[i]++] = store->tuples[t].subject;
            }
        }
    }
    return want_count;
}

// ── Локальне замикання похідних правил: нуль походів у сховище ──────────────

static size_t close_computed(const Schema *schema, const Userset *frontier, size_t frontier_len,
                             Userset *out_nodes, size_t max_out) {
    char seen[MAX_NODES][MAX_NAME * 2];
    size_t seen_count = 0;
    Userset stack[MAX_NODES];
    size_t stack_len = 0;
    size_t out_len = 0;

    for (size_t i = 0; i < frontier_len && stack_len < MAX_NODES; i++) {
        stack[stack_len++] = frontier[i];
    }

    while (stack_len > 0) {
        Userset curr = stack[--stack_len];
        char k[MAX_NAME * 2];
        make_key(k, sizeof(k), curr.object, curr.relation);

        bool already = false;
        for (size_t i = 0; i < seen_count; i++) {
            if (strcmp(seen[i], k) == 0) { already = true; break; }
        }
        if (already) continue;

        if (seen_count < MAX_NODES) {
            strncpy(seen[seen_count++], k, sizeof(seen[0]) - 1);
        }
        if (out_len < max_out) {
            out_nodes[out_len++] = curr;
        }

        char ns[MAX_NAME];
        get_namespace(ns, sizeof(ns), curr.object);
        const SchemaEntry *se = find_schema(schema, ns, curr.relation);
        if (se) {
            for (size_t r = 0; r < se->rule_count; r++) {
                if (se->rules[r].kind == RULE_COMPUTED && stack_len < MAX_NODES) {
                    Userset next = {0};
                    strncpy(next.object, curr.object, sizeof(next.object) - 1);
                    strncpy(next.relation, se->rules[r].rel, sizeof(next.relation) - 1);
                    stack[stack_len++] = next;
                }
            }
        }
    }
    return out_len;
}

// ── Обхід графа ReBAC рівнями ───────────────────────────────────────────────

static bool check_rebac(const Schema *schema, MemoryStore *store, const char *user,
                        Userset start, int max_depth, bool memo, CheckResult *res) {
    char global_seen[MAX_NODES][MAX_NAME * 2];
    size_t global_seen_cnt = 0;

    char start_k[MAX_NAME * 2];
    make_key(start_k, sizeof(start_k), start.object, start.relation);
    strncpy(global_seen[global_seen_cnt++], start_k, sizeof(global_seen[0]) - 1);

    Userset frontier[MAX_NODES];
    size_t frontier_cnt = 1;
    frontier[0] = start;

    for (int depth = 0; depth < max_depth; depth++) {
        if (frontier_cnt == 0) {
            res->allowed = false;
            res->depth = depth;
            res->trips = store->trips;
            return true; // Граф вичерпано, чесна відмова
        }

        Userset nodes[MAX_NODES];
        size_t node_cnt = close_computed(schema, frontier, frontier_cnt, nodes, MAX_NODES);

        // (1) Зібрати ключі для батч-читання
        Userset want[MAX_NODES];
        size_t want_cnt = 0;

        for (size_t i = 0; i < node_cnt; i++) {
            char ns[MAX_NAME];
            get_namespace(ns, sizeof(ns), nodes[i].object);
            const SchemaEntry *se = find_schema(schema, ns, nodes[i].relation);
            if (!se) continue;

            for (size_t r = 0; r < se->rule_count; r++) {
                Userset req = {0};
                if (se->rules[r].kind == RULE_THIS) {
                    req = nodes[i];
                } else if (se->rules[r].kind == RULE_WALK) {
                    strncpy(req.object, nodes[i].object, sizeof(req.object) - 1);
                    strncpy(req.relation, se->rules[r].via, sizeof(req.relation) - 1);
                } else {
                    continue;
                }

                char rk[MAX_NAME * 2];
                make_key(rk, sizeof(rk), req.object, req.relation);
                bool exists = false;
                for (size_t w = 0; w < want_cnt; w++) {
                    char wk[MAX_NAME * 2];
                    make_key(wk, sizeof(wk), want[w].object, want[w].relation);
                    if (strcmp(rk, wk) == 0) { exists = true; break; }
                }
                if (!exists && want_cnt < MAX_NODES) {
                    want[want_cnt++] = req;
                }
            }
        }

        // (2) Один похід у сховище на рівень
        Subject rows[MAX_NODES][MAX_RULES];
        size_t row_counts[MAX_NODES];
        store_read_many(store, want, want_cnt, rows, row_counts);

        // (3) Обробка результатів та формування наступного фронту
        Userset next_frontier[MAX_NODES];
        size_t next_cnt = 0;

        for (size_t i = 0; i < node_cnt; i++) {
            char ns[MAX_NAME];
            get_namespace(ns, sizeof(ns), nodes[i].object);
            const SchemaEntry *se = find_schema(schema, ns, nodes[i].relation);
            if (!se) continue;

            for (size_t r = 0; r < se->rule_count; r++) {
                char search_key[MAX_NAME * 2];
                if (se->rules[r].kind == RULE_THIS) {
                    make_key(search_key, sizeof(search_key), nodes[i].object, nodes[i].relation);
                } else if (se->rules[r].kind == RULE_WALK) {
                    make_key(search_key, sizeof(search_key), nodes[i].object, se->rules[r].via);
                } else {
                    continue;
                }

                for (size_t w = 0; w < want_cnt; w++) {
                    char wk[MAX_NAME * 2];
                    make_key(wk, sizeof(wk), want[w].object, want[w].relation);
                    if (strcmp(wk, search_key) != 0) continue;

                    for (size_t row_idx = 0; row_idx < row_counts[w]; row_idx++) {
                        Subject s = rows[w][row_idx];
                        if (se->rules[r].kind == RULE_THIS) {
                            if (s.is_user) {
                                if (strcmp(s.user, user) == 0) {
                                    res->allowed = true;
                                    res->depth = depth;
                                    res->trips = store->trips;
                                    return true;
                                }
                            } else {
                                char sk[MAX_NAME * 2];
                                make_key(sk, sizeof(sk), s.set.object, s.set.relation);
                                bool seen_before = false;
                                if (memo) {
                                    for (size_t g = 0; g < global_seen_cnt; g++) {
                                        if (strcmp(global_seen[g], sk) == 0) { seen_before = true; break; }
                                    }
                                }
                                if (!seen_before && next_cnt < MAX_NODES) {
                                    if (memo && global_seen_cnt < MAX_NODES) {
                                        strncpy(global_seen[global_seen_cnt++], sk, sizeof(global_seen[0]) - 1);
                                    }
                                    next_frontier[next_cnt++] = s.set;
                                }
                            }
                        } else if (se->rules[r].kind == RULE_WALK) {
                            if (!s.is_user) {
                                Userset walked = {0};
                                strncpy(walked.object, s.set.object, sizeof(walked.object) - 1);
                                strncpy(walked.relation, se->rules[r].then, sizeof(walked.relation) - 1);

                                char wk_next[MAX_NAME * 2];
                                make_key(wk_next, sizeof(wk_next), walked.object, walked.relation);
                                bool seen_before = false;
                                if (memo) {
                                    for (size_t g = 0; g < global_seen_cnt; g++) {
                                        if (strcmp(global_seen[g], wk_next) == 0) { seen_before = true; break; }
                                    }
                                }
                                if (!seen_before && next_cnt < MAX_NODES) {
                                    if (memo && global_seen_cnt < MAX_NODES) {
                                        strncpy(global_seen[global_seen_cnt++], wk_next, sizeof(global_seen[0]) - 1);
                                    }
                                    next_frontier[next_cnt++] = walked;
                                }
                            }
                        }
                    }
                }
            }
        }

        frontier_cnt = next_cnt;
        for (size_t f = 0; f < next_cnt; f++) {
            frontier[f] = next_frontier[f];
        }
    }

    res->allowed = false;
    res->depth = max_depth;
    res->trips = store->trips;
    return false; // Перевищено межу глибини
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <variant>
#include <optional>
#include <span>
#include <memory>
#include <stdexcept>
#include <format>

// ── Модель даних: Userset, Subject, Tuple ───────────────────────────────────

struct Userset {
    std::string object;
    std::string relation;

    [[nodiscard]] std::string key() const {
        return object + "#" + relation;
    }

    bool operator==(const Userset& other) const = default;
};

struct UsersetHash {
    std::size_t operator()(const Userset& u) const noexcept {
        return std::hash<std::string>{}(u.key());
    }
};

struct Subject {
    std::variant<std::string, Userset> value;

    [[nodiscard]] bool is_user() const noexcept {
        return std::holds_alternative<std::string>(value);
    }
    [[nodiscard]] const std::string& user() const {
        return std::get<std::string>(value);
    }
    [[nodiscard]] const Userset& userset() const {
        return std::get<Userset>(value);
    }
};

struct Tuple {
    std::string object;
    std::string relation;
    Subject subject;
};

// ── Правила авторизації ─────────────────────────────────────────────────────

enum class RuleKind { This, Computed, Walk };

struct Rule {
    RuleKind kind;
    std::string rel{};
    std::string via{};
    std::string then{};

    static Rule make_this() { return {RuleKind::This}; }
    static Rule make_computed(std::string r) { return {RuleKind::Computed, std::move(r)}; }
    static Rule make_walk(std::string via, std::string then) {
        return {RuleKind::Walk, {}, std::move(via), std::move(then)};
    }
};

using Config = std::unordered_map<std::string, std::unordered_map<std::string, std::vector<Rule>>>;

inline Config default_config() {
    Config cfg;
    cfg["group"]["member"] = {Rule::make_this()};
    cfg["folder"]["parent"] = {Rule::make_this()};
    cfg["folder"]["editor"] = {Rule::make_this(), Rule::make_walk("parent", "editor")};
    cfg["folder"]["viewer"] = {Rule::make_this(), Rule::make_computed("editor"),
                               Rule::make_walk("parent", "viewer")};
    cfg["doc"]["parent"] = {Rule::make_this()};
    cfg["doc"]["editor"] = {Rule::make_this(), Rule::make_walk("parent", "editor")};
    cfg["doc"]["viewer"] = {Rule::make_this(), Rule::make_computed("editor"),
                            Rule::make_walk("parent", "viewer")};
    return cfg;
}

// ── Сховище кортежів ────────────────────────────────────────────────────────

class Store {
public:
    virtual ~Store() = default;
    virtual std::unordered_map<std::string, std::vector<Subject>> read_many(
        std::span<const Userset> keys) = 0;
};

class MemoryStore final : public Store {
private:
    std::unordered_map<std::string, std::vector<Subject>> idx_;
public:
    int trips{0};

    explicit MemoryStore(std::span<const Tuple> tuples) {
        for (const auto& t : tuples) {
            idx_[t.object + "#" + t.relation].push_back(t.subject);
        }
    }

    std::unordered_map<std::string, std::vector<Subject>> read_many(
        std::span<const Userset> keys) override {
        ++trips;
        std::unordered_map<std::string, std::vector<Subject>> result;
        for (const auto& k : keys) {
            const auto key_str = k.key();
            if (auto it = idx_.find(key_str); it != idx_.end()) {
                result[key_str] = it->second;
            } else {
                result[key_str] = {};
            }
        }
        return result;
    }
};

// ── Движок перевірки ReBAC ──────────────────────────────────────────────────

class DepthExceededException : public std::runtime_error {
public:
    explicit DepthExceededException(const std::string& msg) : std::runtime_error(msg) {}
};

struct CheckResult {
    bool allowed{false};
    int depth{0};
    int trips{0};
};

class Checker {
private:
    Config config_;
    std::shared_ptr<Store> store_;
    int max_depth_{16};
    bool memo_{true};

    [[nodiscard]] std::span<const Rule> get_rules(const Userset& u) const {
        const auto colon_pos = u.object.find(':');
        const std::string ns = (colon_pos != std::string::npos) ? u.object.substr(0, colon_pos) : u.object;
        if (auto it_ns = config_.find(ns); it_ns != config_.end()) {
            if (auto it_rel = it_ns->second.find(u.relation); it_rel != it_ns->second.end()) {
                return it_rel->second;
            }
        }
        return {};
    }

    [[nodiscard]] std::vector<Userset> close_computed(std::span<const Userset> frontier) const {
        std::unordered_set<std::string> local_seen;
        std::vector<Userset> out;
        std::vector<Userset> stack(frontier.begin(), frontier.end());

        while (!stack.empty()) {
            Userset curr = stack.back();
            stack.pop_back();

            if (local_seen.contains(curr.key())) continue;
            local_seen.insert(curr.key());
            out.push_back(curr);

            for (const auto& r : get_rules(curr)) {
                if (r.kind == RuleKind::Computed) {
                    stack.push_back(Userset{curr.object, r.rel});
                }
            }
        }
        return out;
    }

public:
    Checker(Config cfg, std::shared_ptr<Store> store, int max_depth = 16, bool memo = true)
        : config_(std::move(cfg)), store_(std::move(store)), max_depth_(max_depth), memo_(memo) {}

    [[nodiscard]] CheckResult check(std::string_view user, const Userset& start) {
        std::unordered_set<std::string> seen{start.key()};
        std::vector<Userset> frontier{start};
        int trips = 0;

        for (int depth = 0; depth < max_depth_; ++depth) {
            if (frontier.empty()) {
                return CheckResult{.allowed = false, .depth = depth, .trips = trips};
            }

            const auto nodes = close_computed(frontier);

            // (1) Зібрати всі ключі для читання
            std::vector<Userset> want;
            std::unordered_set<std::string> wanted;
            auto add_want = [&](const Userset& u) {
                if (!wanted.contains(u.key())) {
                    wanted.insert(u.key());
                    want.push_back(u);
                }
            };

            for (const auto& n : nodes) {
                for (const auto& r : get_rules(n)) {
                    if (r.kind == RuleKind::This) add_want(n);
                    if (r.kind == RuleKind::Walk) add_want(Userset{n.object, r.via});
                }
            }

            // (2) Один батч-запит у сховище
            auto rows = store_->read_many(want);
            ++trips;

            // (3) Обхід і розкриття наступного рівня
            std::vector<Userset> next_frontier;
            auto enqueue = [&](const Userset& u) {
                if (memo_) {
                    if (seen.contains(u.key())) return;
                    seen.insert(u.key());
                }
                next_frontier.push_back(u);
            };

            for (const auto& n : nodes) {
                for (const auto& r : get_rules(n)) {
                    if (r.kind == RuleKind::This) {
                        for (const auto& s : rows[n.key()]) {
                            if (s.is_user()) {
                                if (s.user() == user) {
                                    return CheckResult{.allowed = true, .depth = depth, .trips = trips};
                                }
                            } else {
                                enqueue(s.userset());
                            }
                        }
                    } else if (r.kind == RuleKind::Walk) {
                        const Userset via{n.object, r.via};
                        for (const auto& s : rows[via.key()]) {
                            if (!s.is_user()) {
                                enqueue(Userset{s.userset().object, r.then});
                            }
                        }
                    }
                }
            }

            frontier = std::move(next_frontier);
        }

        throw DepthExceededException(
            std::format("{}: обхід не вклався в {} рівнів", start.key(), max_depth_));
    }
};
```
:::

Три ключові інваріанти та два структурні вибори в цьому коді варті окремої уваги:

**1. Похідні відношення розкриваються до читання, а не після.** Функція `closeComputed` бере поточний фронт обходу і дописує туди всі зв'язки, що випливають із локальних правил виду «редактор ⟹ читач», не звертаючись до сховища. Тому таке правило коштує нуль мережевих походів — воно лише додає ключі до спільної пачки. І тому лічильник глибини рахує **тільки** справжні ребра графа, за які платять мережевим запитом. Якби похідні відношення споживали глибину, бюджет затримки з'їдала б конфігурація простору імен, а не реальні дані.

**2. Пачка збирається строго окремим проходом.** Спершу цикл (1) обходить усі вершини рівня та формує повний перелік потрібних ключів у множині `want` — і жодного разу не виконує читання. Тільки після завершення збирання виконується єдиний виклик `readMany`. Спокуса читати ключі по мірі знаходження («побачив вершину — прочитав») перетворює одну перевірку на лавину послідовних мережевих запитів.

**3. Порожній фронт — це єдине чесне «ні».** Обхід вичерпав усе досяжне піддерево і не зустрів цільового користувача. У коді немає жодної евристичної гілки, яка повертає «так» без знайденого листка, — [найменші привілеї й відмова за замовчанням](root:sf-security/least-privilege) реалізовані самою топологією алгоритму: «так» повертає рівно один `return`, і лише тоді, коли знайдено точний збіг з ідентифікатором користувача.

**4. Мемоізація відсікає надлишкові розкриття спільних піддерев.** Якщо декілька документів посилаються на одну й ту саму батьківську теку, або декілька підгруп входять до однієї спільної групи, множина `seen` реєструє ідентифікатор вершини `object#relation`. Наступні звернення до неї не породжують нових запитів у сховище на майбутніх рівнях.

**5. Розкриття зв'язків через `walk` ізолює схему від фізичного збереження.** Кортеж `folder:specs#parent@folder:root#...` нічого не знає про відношення `editor` або `viewer`. Правило перезапису простору імен самостійно транслює «якщо потрібен editor для specs, спитай editor для його parent». Це дозволяє змінювати правила авторизації в конфігурації без необхідності міграції збережених кортежів у базі даних.

## Прогін

**Умова.** У сховищі — ті самі п'ять фактів. Питаємо, чи може Ада редагувати `doc:api`, тобто чи досяжний листок `ada` з вершини `doc:api#editor`.

```
check(store, "ada", { object: "doc:api", relation: "editor" })

рівень 0  читаємо doc:api#editor, doc:api#parent            → parent: folder:specs
рівень 1  читаємо folder:specs#editor, folder:specs#parent  → parent: folder:root
рівень 2  читаємо folder:root#editor, folder:root#parent    → editor: group:core#member
рівень 3  читаємо group:core#member                         → group:eng#member
рівень 4  читаємо group:eng#member                          → ada  ✔

{ allowed: true, depth: 4, trips: 5 }
```

**Висновок.** П'ять рівнів — п'ять походів у сховище, хоч прочитано вісім різних ключів. На трьох перших рівнях код читає по два ключі одразу: і те, що лежить на самому об'єкті (раптом Аду вписали в документ напряму), і зв'язок `parent`, яким доведеться йти далі. Обидва потрібні одночасно, обидва їдуть однією пачкою.

![Перевірка «чи може ada редагувати doc:api» як обхід рівнями: п'ять горизонтальних смуг, у кожній вершина графа ліворуч і пачка ключів, які читаються одним запитом, праворуч; стрілки вниз підписані типом ребра — прохід за зв'язком parent або збережене ребро; унизу зелена рамка «у сховищі знайдено ada»](/root/eng/sf-security/authorization-models/img/rebac-walk.svg)

*Кожна смуга — один рівень і рівно один похід у сховище. Ліворуч вершина, праворуч усі ключі, які цим одним запитом читаються: ширина рівня безплатна, платить лише глибина.*

Тепер те саме питання про відношення `viewer`, у якого є похідне правило «редактор ⟹ читач»:

```
check(store, "ada", { object: "doc:api", relation: "viewer" })

рівень 0  читаємо doc:api#viewer, doc:api#editor, doc:api#parent   ← три ключі, один похід
рівень 1  читаємо folder:specs#viewer, folder:specs#editor, folder:specs#parent
рівень 2  читаємо folder:root#viewer, folder:root#editor, folder:root#parent
рівень 3  читаємо group:core#member
рівень 4  читаємо group:eng#member                                 → ada  ✔

{ allowed: true, depth: 4, trips: 5 }
```

Ключів уже одинадцять замість восьми, а походів — ті самі п'ять. Похідне правило розширило пачку, не додавши жодного запиту: рівнів від нього не побільшало.

І відмова:

```
check(store, "bob", { object: "doc:api", relation: "editor" })

... ті самі п'ять рівнів, у group:eng#member лежить лише ada ...
рівень 5  фронт порожній — розкривати більше нічого

{ allowed: false, depth: 5, trips: 5 }
```

Відмова коштує рівно стільки ж, скільки дозвіл, і це не випадковість, а властивість задачі: щоб сказати «ні», треба переконатися, що **жодного** шляху немає, тобто обійти все досяжне. «Так» може пощастити й обірватися на першому ж рівні; «ні» — ніколи.

## Розв'язання циклів, мемоізація та монотонність

Додамо в сховище зворотний зв'язок між групами:

```
group:eng#member@group:core#member          ← core і eng тепер взаємно посилаються
```

Дані з цього моменту містять цикл. Ніхто його не планував: групи вкладають одна в одну живі люди, поспіхом, з різних боків, і жодна окрема дія не виглядає помилковою. Так само трапляється з теками — досить перенести теку в її ж підтеку, і `parent` замикається сам на себе.

Спитаємо про Боба, якого в жодній із груп немає:

```
memo = true      { allowed: false, depth: 5, trips: 5 }
memo = false     DepthExceeded: doc:api#editor: обхід не вклався в 16 рівнів   (16 походів)
```

З пам'яттю розкритих вершин цикл узагалі не помітний: на рівні 3 код розкрив `group:core#member`, на рівні 4 — `group:eng#member`, а зворотне ребро вказало назад на вже розкрите й було відкинуте. Фронт спорожнів, відповідь чесна.

Без пам'яті той самий обхід перекидає одну й ту саму пару вершин туди-сюди, поки не впреться в межу глибини, — і замість «ні» користувач дістає помилку, а моніторинг бачить шістнадцять зайвих запитів на кожну таку перевірку. Дірки в безпеці тут немає: «так» не з'явилося. Але є інша біда — відмова, схожа на аварію, і навантаження, що росте разом із графом.

![Два стани того самого циклу: ліворуч, коли розкриті вершини пам'ятають, зворотне ребро між group:eng#member і group:core#member перекреслене знаком заборони й обхід дає п'ять походів та чесне «ні»; праворуч, коли пам'яті немає, те саме ребро червоне й цілісіньке, обхід ходить туди-сюди й дає шістнадцять походів та помилку глибини](/root/eng/sf-security/authorization-models/img/rebac-cycle.svg)

*Той самий цикл із двома різними запобіжниками. Пам'ять про розкрите обриває його на другому дотику; сама лише межа глибини дозволяє йому крутитися до останнього дозволеного рівня.*

### Роль пам'яті розкритих вершин проти межі глибини

Звідси головне про ці два запобіжники: **вони не замінюють один одного**.

**Пам'ять розкритих вершин** — це [мемоізація](root:sf-algorithms/memoization) виклику `check` для кожної вершини: другий раз відповідь була б та сама, тож рахувати її вдруге не треба. Вона робить обхід скінченним при будь-якому графі й перетворює можливе `bᵈ` розкриттів на щонайбільше по одному розкриттю на вершину (тобто `O(|V|)` операцій замість експоненційного вибуху).

**Межа глибини** — це не запобіжник від зациклення (його вже поставила пам'ять), а **бюджет затримки (latency budget)**. Кожен рівень коштує похід у мережу; шістнадцять рівнів — це шістнадцять послідовних походів, і навіть без жодного циклу в абсолютно чистому дереві тек така перевірка вилізе за будь-який розумний час відповіді. Межа каже: «глибший ланцюжок ми не обслуговуємо», і каже це вголос, керованою помилкою.

Обидва підходи живуть у справжніх системах, і різниця між ними повчальна. SpiceDB свідомо **не** веде списку розкритих вершин у пам'яті вузла: у розподіленому обході цей список довелося б серіалізувати й тягати мережею між вузлами кластера, а головне — пам'ять про розкрите ламає семантику, щойно в правилах з'являється виняток («читачі, **крім** заблокованих»); тому цикл там просто крутиться до межі й повертає помилку, а саму межу за замовчанням поставлено на 50 стрибків. OpenFGA, навпаки, тримає явне виявлення циклів і має власну межу глибини `resolveNodeLimit` зі значенням 25 за замовчанням, плюс окрему межу на ширину рівня — 10 вершин одночасно (*документовані значення з їхніх відкритих конфігурацій*).

### Монотонність обчислень та немонотонні оператори

Поки правила авторизації будуються виключно на операторах об'єднання (`union`), простір прав має фундаментальну властивість — **монотонність**:

```
Facts₁ ⊆ Facts₂  ⟹  Perm(Facts₁) ⊆ Perm(Facts₂)
```

Додавання будь-якого нового кортежу у сховище або виявлення альтернативного шляху до суб'єкта може лише надати користувачеві додаткові права, але ніколи не здатне скасувати вже дозволену дію. Завдяки монотонності рання відсічка за множиною `seen` є абсолютно коректною: якщо вершина вже була розкрита і не привела до цільового суб'єкта, повторний її обхід з іншої гілки гарантовано дасть той самий результат, і відкидання дубліката не порушує цілісності.

Ситуація докорінно змінюється, коли в авторизаційну схему вводяться немонотонні оператори:
- **Перетин (`intersection`)** — вимагає одночасної наявності доступу через кілька незалежних відношень (наприклад, «користувач є редактором теки І одночасно пройшов перевірку NDA»).
- **Виключення (`exclusion` / `not`)** — скасовує право для вказаної підмножини («усі учасники команди ядра, окрім тимчасово відсторонених»).

При наявності заперечень задача перевірки перестає бути простим пошуком досяжності у графі: поява циклів із запереченням (наприклад, `A = not B` та `B = not A`) створює семантичні парадокси, де істинність результату неможливо обчислити звичайним обходом у ширину. Промислові системи вирішують це або повною забороною циклів із запереченнями на етапі статичної компіляції схеми (стратифікація правил), або застосуванням тризначної логіки (Well-Founded Semantics: `true`, `false`, `unknown`), де зациклені немонотонні гілки класифікуються як недетерміновані.

## Валідація транзитивності та динамічне замикання

Транзитивність у ReBAC означає передачу дозволу крізь послідовні зв'язки в графі: якщо користувач Ада входить до групи `group:eng`, а вся група `group:eng` входить до групи `group:core`, то Ада транзитивно є учасницею `group:core`. Аналогічно для тек: дозвіл на редагування кореневого каталогу транзитивно поширюється на всі вкладені підкаталоги та файли всередині нього.

В інженерній практиці існують два взаємовиключні підходи до підтримки транзитивності:

### 1. Статична матеріалізація транзитивного замикання (Eager Closure)

При матеріалізації кожен факт про вкладеність розгортається фоновим процесом у повний набір прямих ребер. Щойно створюється зв'язок «документ `api` лежить у теці `specs`», система автоматично генерує й записує в базу даних готові кортежі для всіх потенційних редакторів і читачів усіх батьківських тек:

- **Перевага:** швидкість читання `check` максимальна — один запит за первинним індексом (`O(1)` часу), бо всі дозволи вже денормалізовані та лежать прямо на цільовому об'єкті.
- **Недолік:** колосальне множення операцій запису (write amplification). Якщо організація має 200 000 співробітників і 1 000 000 документів у спільній ієрархії, додавання однієї підгрупи до загальної групи компанії вимагає синхронного або асинхронного запису десятків мільйонів рядків у базу даних. Під час такого масового оновлення виникають тривалі блокування, зростає реплікаційне відставання, а користувачі тимчасово спостерігають неконсистентні права доступу.

### 2. Динамічне виведення під час запиту (Query-Time Graph Traversal)

Підхід Google Zanzibar та реалізованого вище рушія полягає в збереженні графа у строго нормалізованому вигляді: у сховищі тримаються лише первинні факти про прямі зв'язки (`O(1)` часу та пам'яті на будь-яку мутацію), а транзитивні ребра реконструюються динамічно під час перевірки за допомогою правил `walk` та `computed`.

- **Перевага:** будь-яка зміна структури груп чи переміщення теки займає фіксований час одного запису кортежу без необхідності перераховувати стан мільйонів залежних документів.
- **Недолік:** час відповіді перевірки залежить від глибини ієрархії `d` і вимагає обов'язкового збирання читань у пачки, щоб укластися в жорсткі часові бюджети мікросервісів.

У масштабних хмарних продуктах із мільярдами об'єктів динамічне виведення виявилося значно надійнішим, оскільки воно повністю усуває ризик каскадних відмов бази даних під час реорганізації великих каталогів.

## Просторова узгодженість, токени Zookie та проблема «нового ворога»

У глобально розподілених сховищах даних реплікація між географічними регіонами відбувається асинхронно. Це породжує відому в інженерії безпеки вразливість — **проблему «нового ворога» (New Enemy Problem)**.

### Сценарій проблеми нового ворога

1. Аліса ділиться важливою текою з Бобом у регіоні США.
2. Пізніше Аліса вирішує відкликати доступ у Боба: вона видаляє зв'язок `folder:secret#viewer@bob` у мить часу `T₁`.
3. Відразу після цього в мить `T₂` (`T₂ > T₁`) Аліса завантажує в цю теку новий надсекретний документ `doc:topsecret`.
4. Боб у регіоні Європи робить спробу відкрити `doc:topsecret`.
5. Якщо реплікація між США та Європою затрималася, європейська репліка бази вже може мати запис про створення `doc:topsecret`, але ще не отримати запис про видалення Боба з `folder:secret` (`T₁`).
6. Перевірка доступу в Європі на застарілому знімку несподівано дає Бобу дозвіл на читання документа, якого він ніколи не мав бачити.

### Механізм токенів Zookies

Для повного викорінення цієї вразливості архітектура Zanzibar ввела концепцію **Zookies** (від *Zanzibar Cookies*).

Zookie — це компактний непрозорий бінарний токен, який клієнтський додаток отримує у відповідь на будь-яку мутацію даних (зміна прав, створення документа) і передає при наступних запитах. Всередині Zookie закодовано глобально узгоджену часову мітку транзакції бази даних (наприклад, Spanner Commit Timestamp або глобальний LSN):

```
Z = ⟨snapshot_timestamp⟩
```

Коли клієнт звертається до системи авторизації з перевіркою:

```
Check(user, relation, object, zookie)
```

Движок перевірки гарантує виконання правила консистентності знімка:
1. Часова мітка виконання перевірки обирається такою, що `T_eval ≥ T(Zookie)`.
2. Усі читання фактів графа на всіх рівнях обходу виконуються строго в межах одного незмінного знімка [MVCC](root:sf-data/mvcc) на момент `T_eval`.
3. Якщо локальна репліка ще не досягла часової мітки `T(Zookie)`, запит або очікує підтягування логу реплікації, або перенаправляється на репліку зі свіжішим станом.

Завдяки Zookies система гарантує причинну узгодженість (causal consistency): операція `T₂` не може бути оцінена на стані бази, старішому за `T₁`, що повністю ліквідує феномен нового ворога без потреби в дорогих розподілених блокуваннях на кожне читання.

## Просторове кешування та індекс Leopard

У реальних системах виникає два типи авторизаційних запитів, які вимагають принципово різної організації пам'яті:

1. **Точковий запит (`Check`)** — «чи може Ада редагувати `doc:api`?». Граф обходиться від об'єкта в напрямку кореневих груп та користувачів.
2. **Зворотний запит або список об'єктів (`ListObjects` / `Expand`)** — «перелічити всі документи в системі, які Ада може переглядати».

Прямий пошук у ширину нездатний ефективно відповісти на друге питання: у системі з сотнями мільйонів документів неможливо запустити обхід від кожного документа окремо.

Для розв'язання цієї проблеми в архітектурі Zanzibar виділено спеціалізовану підсистему індексації — **Leopard**.

### Архітектура Leopard

Leopard оптимізований для обробки глибоко вкладених груп користувачів. Членство в групах змінюється відносно рідко (співвідношення читань до записів `> 10000:1`), тому Leopard у фоновому асинхронному режимі підтримує повне транзитивне замикання графів груп.

Leopard зберігає інформацію у вигляді пласких впорядкованих масивів ідентифікаторів або інтервальних міток:
- Для кожної групи `G` підтримується множина всіх груп, які транзитивно до неї входять: `Descendants(G)`.
- Для кожного користувача `U` підтримується множина всіх груп, у яких він безпосередньо перебуває: `DirectGroups(U)`.

Перевірка досяжності користувача `U` в групі `G` зводиться до швидкого перетину двох відсортованих списків у пам'яті:

```
IsMember(U, G)  ⟺  DirectGroups(U) ∩ Descendants(G) ≠ ∅
```

Часова складність такої операції на впорядкованих масивах становить `O(|A| + |B|)` або `O(log N)` при бінарному пошуку, що займає менше 10 мікросекунд на процесорне ядро.

### Багаторівнева стратегія кешування

Промисловий контур ReBAC спирається на трирівневу систему [стратегії кешування](root:sf-data/caching-strategies):

1. **Рівень L1 (In-Memory Hot Cache & Singleflight):** локальний кеш у пам'яті вузла авторизації. Зберігає результати гарячих перевірок `Check` та окремі кортежі. Запити на однаковий ключ від сотень клієнтів зливаються в один через патерн `singleflight`.
2. **Рівень L2 (Leopard Index):** розподілений індекс транзитивного членства груп, оптимізований для операцій над множинами.
3. **Рівень L3 (Dynamic Graph Walk):** розподілений рушій BFS, який обходить специфічні для об'єктів зв'язки (теки, документи, динамічні ACL) з узгодженістю за токенами Zookie.

## Складність

Уся вартість перевірки — це походи в сховище; арифметика над множинами на їхньому тлі не видна.

```
позначення
  d   — глибина: скільки рівнів довелося пройти
  N   — скільки різних ключів усього прочитано
  RTT — час одного походу у сховище (round-trip time)

по ключу за раз:   T ≈ N · RTT
рівнями, пачкою:   T ≈ d · RTT

наш прогін (ada → doc:api#viewer, RTT = 1 мс):
  N = 3 + 3 + 3 + 1 + 1 = 11 ключів
  d = 5 рівнів
  по ключу:   11 · 1 мс = 11 мс
  рівнями:     5 · 1 мс =  5 мс
```

На цьому прикладі різниця виглядає скромно. Вона перестає бути скромною, щойно граф широкий:

```
тека, на якій висить 200 груп, і в кожній групі — ще підгрупа:
  рівень 0:   1 ключ    folder:X#editor      → 200 груп
  рівень 1: 200 ключів  group:gᵢ#member      → 200 підгруп
  рівень 2: 200 ключів  group:subᵢ#member    → люди
  N = 401,  d = 3

  по ключу:  401 · 1 мс = 401 мс   ← бюджет запиту вже спалено
  рівнями:     3 · 1 мс =   3 мс
```

Ширина пішла в розмір пачки, а не в час. Ось чому обхід рівнями тут не стилістичний вибір.

Пам'ять розкритих вершин б'є по іншій осі — по кількості роботи:

```
без пам'яті, гілкування b, глибина d:  розкриттів ≤ bᵈ     (b = 10, d = 6 → 10⁶)
з пам'яттю:                            розкриттів ≤ |V|    (кожна вершина рівно раз)
```

Причому `bᵈ` виникає не лише з циклів. Досить ромба — двох різних шляхів до однієї теки, — і піддерево за нею розкривається двічі; на кількох рівнях ромбів це помножується.

## Пастки

**Не перетворюй помилку на відповідь.** Вичерпана глибина, обірваний зв'язок зі сховищем, тайм-аут — це «не знаю», а не «ні» й тим паче не «так». Повернути «так» — очевидна діра в системі безпеки. Але й тихе «ні» небезпечне: користувач бачить «доступ заборонено» там, де насправді зламався мережевий бекенд, і таку помилку важко діагностувати. Клієнтові слід повертати код помилки з відмовою, а в систему моніторингу надсилати чіткий сигнал про збій інфраструктури, що не губиться серед штатних відмов.

**Уся перевірка читає один знімок.** Наші п'ять походів — це п'ять окремих читань, розтягнутих у часі. Якщо між ними хтось перепише зв'язки, обхід збере шлях із ребер, які **разом не існували в жодну мить**. Google описав цю пастку окремим прикладом: власник забирає в людини доступ до теки, а потім туди перекладають нові документи — і та людина їх побачить, якщо перевірка не поважає порядку цих двох змін. Ліки — читати всі рівні на одному знімку бази ([MVCC](root:sf-data/mvcc) дає його майже задарма) або використовувати токени Zookie, а не «щоразу найсвіжіше».

**Скасовуй братні запити, щойно відповідь відома.** Рівень часто містить кілька гілок, а відповідь дає одна. Решта в цю мить уже нікому не потрібна — і кожна її дочитана сторінка — це зайве навантаження на сховище. У Zanzibar це названо серед помітних чинників розвантаження: побічні перевірки часто скасовують, щойно результат головної вже визначено.

**Ширина рівня вимагає лімітування.** Пачка на двісті ключів — добре. Пачка на двісті тисяч — це вже спосіб покласти сховище одним запитом від однієї людини, яку хтось додав у гігантську групу. Тому в OpenFGA поруч із межею глибини стоїть межа на кількість вершин, що розкриваються одночасно (fanout limit), яка захищає базу від перевантаження пам'яті.

**Популярні вершини стають гарячими точками.** Одна група «всі співробітники» висить у ACL половини документів — і кожна перевірка йде саме в неї. Zanzibar тримає для цього таблицю поточних читань (патерн singleflight), щоб десяток одночасних запитів на той самий ключ не перетворився на десяток походів у базу, а для найгарячіших об'єктів читає й кешує **всі** їхні зв'язки одразу, свідомо міняючи зайвий трафік на кешованість.

**Питання «що бачить ця людина?» — інший обхід.** Наш код іде від об'єкта. Обернене питання — перелічити все, до чого має доступ користувач, — вимагає йти з іншого кінця й розкривати «у яких множинах цей користувач», а це зовсім інше гілкування й інший індекс. У Zanzibar для глибоко вкладених груп це винесено в окрему підсистему Leopard, яка тримає обидва напрямки обчисленими заздалегідь (група → усі вкладені групи; людина → її прямі групи) і зводить перевірку членства до перетину двох упорядкованих множин.

Ці дрібниці не косметичні, і масштаб, на якому вони перевірені, каже сам за себе: Zanzibar на момент публікації зберігав понад два трильйони зв'язків (близько 100 терабайтів) і обслуговував понад 10 мільйонів запитів клієнтів на секунду, тримаючи 95-й процентиль затримки під 10 мілісекунд. З приблизно 200 мільйонів звернень на секунду, які на піку приймав кеш у пам'яті, до бази доходило лише 20 мільйонів читань — саме завдяки кешуванню й наполегливому збиранню читань у пачки (*дані з тієї самої статті 2019 року*). Тобто дев'ять із десяти звернень гасяться, не діставшись сховища. Форма циклу, який ми написали, і визначає, скільки їх узагалі виникає.
