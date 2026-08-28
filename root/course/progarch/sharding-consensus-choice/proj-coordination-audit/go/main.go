package dh

import (
	"context"
	"sort"
	"sync"
	"time"
)

// Core — крихітне сильно-узгоджене KV (etcd / ZooKeeper / Chubby усередині).
// КОЖЕН його виклик коштує раунд до живої більшості — тож у гарячий шлях воно НЕ лізе.
type Core interface {
	Get(ctx context.Context, key string) (val string, rev int64, err error)
	// CAS: записати val, лише якщо поточна ревізія ключа == expect (0 = «ключа ще нема»).
	CAS(ctx context.Context, key, val string, expect int64, ttl time.Duration) (rev int64, ok bool, err error)
	Watch(ctx context.Context, key string) <-chan Event // потік змін ключа
}
type Event struct{ Val string; Rev int64 }

// ── DATA PLANE — гарячий шлях. Маршрут читаємо з ЛОКАЛЬНОГО кешу: 0 раундів у ядро. ──
type ShardMap struct {
	mu    sync.RWMutex
	epoch int64    // ревізія ядра, з якої знято мапу — fencing проти застарілого кешу
	hi    []uint64 // верхні межі діапазонів home_id, відсортовані
	shard []string // shard[i] обслуговує діапазон, що кінчається на hi[i]
}

// Route — чистий локальний пошук: жодної мережі, жодного консенсусу. Наносекунди.
func (m *ShardMap) Route(homeID uint64) (shard string, epoch int64) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	i := sort.Search(len(m.hi), func(i int) bool { return m.hi[i] >= homeID })
	return m.shard[i], m.epoch
}

// Refresh — рідкісний фон: оновлюємо кеш, ЛИШЕ коли ядро повідомить про зміну мапи.
func (m *ShardMap) Refresh(ctx context.Context, core Core) {
	for ev := range core.Watch(ctx, "/dh/shard-map") { // трапляється при ребалансі, не на запит
		hi, shard := parseMap(ev.Val) // парсер мапи — тривіальний, тіло опущено
		m.mu.Lock()
		m.hi, m.shard, m.epoch = hi, shard, ev.Rev
		m.mu.Unlock()
	}
}

// ── CONTROL PLANE — лідер нічних джоб. Раунд на здобуття лізи + рідкі поновлення. ──
func RunAsLeader(ctx context.Context, core Core, me string, job func(context.Context)) {
	const ttl = 10 * time.Second
	const key = "/dh/leader/night-jobs"
	for ctx.Err() == nil {
		if _, rev, _ := core.Get(ctx, key); rev == 0 { // вакансія — пробуємо зайняти
			if newRev, ok, _ := core.CAS(ctx, key, me, 0, ttl); ok {
				lead(ctx, core, key, me, newRev, ttl, job) // ми лідер
			}
		}
		time.Sleep(ttl / 3) // не лідер — зазираємо зрідка, не жаримо ядро
	}
}

// lead поновлює лізу CAS-ом «я → я» і крутить job, поки тримаємо ключ.
func lead(ctx context.Context, core Core, key, me string, rev int64, ttl time.Duration, job func(context.Context)) {
	jobCtx, stop := context.WithCancel(ctx)
	defer stop()
	go job(jobCtx) // РОБОТА лідера (ребаланс шардів) — локальна, ядро її не бачить
	tick := time.NewTicker(ttl / 3) // поновлюємо втричі частіше за строк
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-tick.C:
			newRev, ok, err := core.CAS(ctx, key, me, rev, ttl) // «я досі я»
			if err != nil || !ok {
				return // втратили лізу (пауза/мережа) — job спиниться разом зі stop()
			}
			rev = newRev
		}
	}
}
