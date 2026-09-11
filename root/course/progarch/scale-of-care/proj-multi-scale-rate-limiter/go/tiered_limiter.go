package main

import (
	"context"
	"fmt"
)

// TieredLimiter синтезує два масштаби турботи: процесорний та розподілений.
type TieredLimiter struct {
	local   *AtomicTokenBucket
	cluster *RedisLimiter
}

// NewTieredLimiter створює двошаровий обмежувач навантаження.
func NewTieredLimiter(local *AtomicTokenBucket, cluster *RedisLimiter) *TieredLimiter {
	return &TieredLimiter{
		local:   local,
		cluster: cluster,
	}
}

// Allow спочатку відсікає сплески локально, і лише валідний трафік спрямовує у мережу.
func (t *TieredLimiter) Allow(ctx context.Context, key string, tokens int64) (Decision, error) {
	// 1-й рівень оборони: наносекундна перевірка в локальній пам'яті
	localDecision, err := t.local.Allow(ctx, key, tokens)
	if err != nil || !localDecision.Allowed {
		localDecision.Reason = fmt.Sprintf("Рівень 1 (Локальний): %s", localDecision.Reason)
		return localDecision, err
	}

	// 2-й рівень оборони: узгодження квоти між репліками сервісу
	clusterDecision, err := t.cluster.Allow(ctx, key, tokens)
	if err != nil && clusterDecision.IsFallback && t.cluster.fallback == FailClosed {
		return clusterDecision, err
	}

	clusterDecision.Reason = fmt.Sprintf("Рівень 2 (Кластер): %s", clusterDecision.Reason)
	return clusterDecision, nil
}
