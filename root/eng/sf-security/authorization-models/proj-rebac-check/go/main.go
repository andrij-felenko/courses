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
