package heartbeat

import (
	"context"
	"hash/fnv"
	"math/rand"
	"time"
)

// Зерно — від імені вузла, а не від годинника.
func seedFrom(nodeID string) int64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte(nodeID))
	return int64(h.Sum64())
}

func nextInterval(period time.Duration, rng *rand.Rand) time.Duration {
	return time.Duration(float64(period) * (0.5 + rng.Float64())) // [0.5·T, 1.5·T]
}

// Ticker тут не годиться принципово: у нього період сталий, а нам потрібен
// новий випадковий інтервал щоразу. Тому Timer із явним Reset.
func Run(ctx context.Context, period time.Duration, nodeID string, send func()) {
	rng := rand.New(rand.NewSource(seedFrom(nodeID)))
	timer := time.NewTimer(nextInterval(period, rng)) // перший інтервал теж випадковий
	defer timer.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-timer.C:
			send()
			timer.Reset(nextInterval(period, rng))
		}
	}
}
