// user_repository.go — Подвійне читання з відкатом на Go
package repository

import (
	"context"
	"fmt"
)

type UserStore interface {
	Get(ctx context.Context, key string) (string, error)
}

type MetricsCollector interface {
	IncLegacyFallback()
	IncPrimaryHit()
}

type UserRepository struct {
	store   UserStore
	metrics MetricsCollector
}

func (r *UserRepository) FetchUser(ctx context.Context, tenantID, userID string) (string, error) {
	// 1. Спроба вичитати за новим багатоорендним ключем (v2)
	newKey := fmt.Sprintf("tenant:%s:user:%s", tenantID, userID)
	data, err := r.store.Get(ctx, newKey)
	if err == nil && data != "" {
		r.metrics.IncPrimaryHit()
		return data, nil
	}

	// 2. Fallback: якщо запис ще не мігровано бекфілом, читаємо за старим ключем v1
	legacyKey := fmt.Sprintf("user:%s", userID)
	legacyData, legErr := r.store.Get(ctx, legacyKey)
	if legErr == nil && legacyData != "" {
		r.metrics.IncLegacyFallback() // Фіксуємо факт роботи через застаріле сховище
		return legacyData, nil
	}

	return "", fmt.Errorf("user not found: %s", userID)
}
