package entitlements

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type FeatureKey string
type MetricKey string

const (
	FeatureSSO               FeatureKey = "sso"
	FeatureCustomDomains     FeatureKey = "custom_domains"
	FeatureAuditLogs         FeatureKey = "audit_logs"
	FeatureAdvancedAnalytics FeatureKey = "advanced_analytics"
	FeatureExportCSV         FeatureKey = "export_csv"

	MetricMonthlyAPICalls MetricKey = "monthly_api_calls"
	MetricStorageBytes    MetricKey = "storage_bytes"
	MetricMonthlyReports  MetricKey = "monthly_reports"
)

type SubscriptionStatus string

const (
	StatusActive   SubscriptionStatus = "active"
	StatusTrialing SubscriptionStatus = "trialing"
	StatusPastDue  SubscriptionStatus = "past_due"
	StatusCanceled SubscriptionStatus = "canceled"
	StatusUnpaid   SubscriptionStatus = "unpaid"
)

type PlanDefinition struct {
	ID       string
	Name     string
	Features map[FeatureKey]bool
	Limits   map[string]int64
	Quotas   map[MetricKey]int64
}

type AddonDefinition struct {
	ID               string
	FeatureOverrides map[FeatureKey]bool
	LimitIncrements  map[string]int64
	QuotaIncrements  map[MetricKey]int64
}

type TenantContract struct {
	TenantID               string
	PlanID                 string
	ActiveAddonIDs         []string
	CustomFeatureOverrides map[FeatureKey]bool
	CustomLimitOverrides   map[string]int64
	CustomQuotaOverrides   map[MetricKey]int64
	Status                 SubscriptionStatus
	GracePeriodEndsAt      *time.Time
	UpdatedAt              time.Time
}

type EffectiveSnapshot struct {
	TenantID   string
	Version    int64
	Features   map[FeatureKey]bool
	Limits     map[string]int64
	Quotas     map[MetricKey]int64
	IsReadOnly bool
	ComputedAt time.Time
}

type QuotaReservationResult struct {
	Allowed       bool
	ReservationID string
	CurrentUsage  int64
	Limit         int64
	Remaining     int64
}

type IContractStore interface {
	GetPlan(ctx context.Context, planID string) (*PlanDefinition, error)
	GetAddon(ctx context.Context, addonID string) (*AddonDefinition, error)
	GetTenantContract(ctx context.Context, tenantID string) (*TenantContract, error)
}

type IQuotaStore interface {
	CheckAndReserve(ctx context.Context, tenantID string, metric MetricKey, amount, limit int64, windowSec int) (bool, int64, string, error)
	Release(ctx context.Context, tenantID string, metric MetricKey, reservationID string, amount int64) error
	GetUsage(ctx context.Context, tenantID string, metric MetricKey) (int64, error)
}

type cacheEntry struct {
	snapshot  *EffectiveSnapshot
	expiresAt time.Time
}

type EntitlementEngine struct {
	contractStore IContractStore
	quotaStore    IQuotaStore
	l1Cache       map[string]cacheEntry
	mu            sync.RWMutex
	l1TTL         time.Duration
}

func NewEntitlementEngine(cs IContractStore, qs IQuotaStore) *EntitlementEngine {
	return &EntitlementEngine{
		contractStore: cs,
		quotaStore:    qs,
		l1Cache:       make(map[string]cacheEntry),
		l1TTL:         15 * time.Second,
	}
}

func (e *EntitlementEngine) ResolveSnapshot(ctx context.Context, tenantID string) (*EffectiveSnapshot, error) {
	contract, err := e.contractStore.GetTenantContract(ctx, tenantID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch tenant contract: %w", err)
	}
	if contract == nil {
		return e.defaultFreeSnapshot(tenantID), nil
	}

	basePlan, err := e.contractStore.GetPlan(ctx, contract.PlanID)
	if err != nil || basePlan == nil {
		return nil, fmt.Errorf("base plan not found: %s", contract.PlanID)
	}

	features := make(map[FeatureKey]bool)
	for k, v := range basePlan.Features {
		features[k] = v
	}
	limits := make(map[string]int64)
	for k, v := range basePlan.Limits {
		limits[k] = v
	}
	quotas := make(map[MetricKey]int64)
	for k, v := range basePlan.Quotas {
		quotas[k] = v
	}

	// 2. Накладання докупованих пакетів (Addons)
	for _, addonID := range contract.ActiveAddonIDs {
		addon, err := e.contractStore.GetAddon(ctx, addonID)
		if err != nil || addon == nil {
			continue
		}
		for k, v := range addon.FeatureOverrides {
			features[k] = v
		}
		for k, v := range addon.LimitIncrements {
			limits[k] += v
		}
		for k, v := range addon.QuotaIncrements {
			quotas[k] += v
		}
	}

	// 3. Накладання індивідуальних винятків (Overrides)
	for k, v := range contract.CustomFeatureOverrides {
		features[k] = v
	}
	for k, v := range contract.CustomLimitOverrides {
		limits[k] = v
	}
	for k, v := range contract.CustomQuotaOverrides {
		quotas[k] = v
	}

	// 4. Перевірка платіжного статусу
	now := time.Now()
	isReadOnly := false
	if contract.Status == StatusPastDue {
		if contract.GracePeriodEndsAt == nil || contract.GracePeriodEndsAt.Before(now) {
			isReadOnly = true
		}
	} else if contract.Status == StatusCanceled || contract.Status == StatusUnpaid {
		isReadOnly = true
	}

	snapshot := &EffectiveSnapshot{
		TenantID:   tenantID,
		Version:    contract.UpdatedAt.UnixNano(),
		Features:   features,
		Limits:     limits,
		Quotas:     quotas,
		IsReadOnly: isReadOnly,
		ComputedAt: now,
	}

	e.mu.Lock()
	e.l1Cache[tenantID] = cacheEntry{
		snapshot:  snapshot,
		expiresAt: now.Add(e.l1TTL),
	}
	e.mu.Unlock()

	return snapshot, nil
}

func (e *EntitlementEngine) GetEffectiveSnapshot(ctx context.Context, tenantID string) (*EffectiveSnapshot, error) {
	e.mu.RLock()
	entry, found := e.l1Cache[tenantID]
	e.mu.RUnlock()

	if found && time.Now().Before(entry.expiresAt) {
		return entry.snapshot, nil
	}
	return e.ResolveSnapshot(ctx, tenantID)
}

func (e *EntitlementEngine) InvalidateCache(tenantID string) {
	e.mu.Lock()
	delete(e.l1Cache, tenantID)
	e.mu.Unlock()
}

func (e *EntitlementEngine) CheckFeature(ctx context.Context, tenantID string, feature FeatureKey) (bool, error) {
	snap, err := e.GetEffectiveSnapshot(ctx, tenantID)
	if err != nil {
		return false, err
	}
	if snap.IsReadOnly {
		return false, nil
	}
	return snap.Features[feature], nil
}

func (e *EntitlementEngine) CheckAndReserveQuota(
	ctx context.Context,
	tenantID string,
	metric MetricKey,
	amount int64,
	windowSec int,
) (*QuotaReservationResult, error) {
	snap, err := e.GetEffectiveSnapshot(ctx, tenantID)
	if err != nil {
		return nil, err
	}
	if snap.IsReadOnly {
		return &QuotaReservationResult{Allowed: false}, nil
	}

	limit, exists := snap.Quotas[metric]
	if !exists || limit <= 0 {
		return &QuotaReservationResult{Allowed: false, Limit: 0}, nil
	}

	allowed, newUsage, resID, err := e.quotaStore.CheckAndReserve(ctx, tenantID, metric, amount, limit, windowSec)
	if err != nil {
		return nil, err
	}

	if !allowed {
		return &QuotaReservationResult{
			Allowed:      false,
			CurrentUsage: newUsage,
			Limit:        limit,
			Remaining:    0,
		}, nil
	}

	rem := limit - newUsage
	if rem < 0 {
		rem = 0
	}

	return &QuotaReservationResult{
		Allowed:       true,
		ReservationID: resID,
		CurrentUsage:  newUsage,
		Limit:         limit,
		Remaining:     rem,
	}, nil
}

func (e *EntitlementEngine) ReleaseQuota(ctx context.Context, tenantID string, metric MetricKey, resID string, amount int64) error {
	return e.quotaStore.Release(ctx, tenantID, metric, resID, amount)
}

func (e *EntitlementEngine) defaultFreeSnapshot(tenantID string) *EffectiveSnapshot {
	return &EffectiveSnapshot{
		TenantID: tenantID,
		Version:  1,
		Features: map[FeatureKey]bool{
			FeatureSSO:               false,
			FeatureCustomDomains:     false,
			FeatureAuditLogs:         false,
			FeatureAdvancedAnalytics: false,
			FeatureExportCSV:         true,
		},
		Limits: map[string]int64{
			"max_projects": 3,
			"max_seats":    2,
		},
		Quotas: map[MetricKey]int64{
			MetricMonthlyAPICalls: 1000,
			MetricStorageBytes:    100 * 1024 * 1024,
			MetricMonthlyReports:  5,
		},
		IsReadOnly: false,
		ComputedAt: time.Now(),
	}
}
