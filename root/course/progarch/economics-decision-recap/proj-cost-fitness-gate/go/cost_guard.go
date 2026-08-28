// cost_guard.go — Сторож бюджету Unit Cost у CI/CD конвеєрі

package main

import (
	"fmt"
	"sort"
)

type ResourceUsage struct {
	CpuMs       float64
	DbQueries   int
	MemoryMb    float64
	EgressBytes int64
}

type CloudPricing struct {
	CostPerCpuMs    float64 // $ / ms CPU
	CostPerDbQuery  float64 // $ / query
	CostPerEgressGb float64 // $ / GB
}

type BudgetConfig struct {
	MaxUnitCostUsd   float64 // Максимальна вартість 1,000 запитів
	MaxRegressionPct float64 // Поріг регресії у відсотках
	MinSampleRuns    int     // Мінімальна кількість вимірів
}

type TestProfile struct {
	Endpoint        string
	BaselineCostUsd float64
	Runs            []ResourceUsage
}

type GuardVerdict struct {
	Ok              bool
	Endpoint        string
	CurrentCostUsd  float64
	BaselineCostUsd float64
	DeltaPct        float64
	Message         string
}

type CostFitnessGuard struct {
	Pricing CloudPricing
	Config  BudgetConfig
}

func NewCostFitnessGuard(p CloudPricing, c BudgetConfig) *CostFitnessGuard {
	return &CostFitnessGuard{Pricing: p, Config: c}
}

func (g *CostFitnessGuard) CalculateSingleCost(u ResourceUsage) float64 {
	cpuCost := u.CpuMs * g.Pricing.CostPerCpuMs
	dbCost := float64(u.DbQueries) * g.Pricing.CostPerDbQuery
	egressGb := float64(u.EgressBytes) / (1024.0 * 1024.0 * 1024.0)
	egressCost := egressGb * g.Pricing.CostPerEgressGb

	return cpuCost + dbCost + egressCost
}

func (g *CostFitnessGuard) CalculateUnitCostPerK(runs []ResourceUsage) float64 {
	if len(runs) == 0 {
		return 0
	}

	costs := make([]float64, len(runs))
	for i, r := range runs {
		costs[i] = g.CalculateSingleCost(r)
	}

	sort.Float64s(costs)

	// Відсікаємо 10% найгірших викидів при достатній вибірці
	validCount := len(costs)
	if validCount >= 5 {
		validCount = int(float64(len(costs)) * 0.9)
	}

	var sum float64
	for i := 0; i < validCount; i++ {
		sum += costs[i]
	}

	avgSingle := sum / float64(validCount)
	return avgSingle * 1000.0
}

func (g *CostFitnessGuard) EvaluateCommit(p TestProfile) GuardVerdict {
	if len(p.Runs) < g.Config.MinSampleRuns {
		return GuardVerdict{
			Ok:       false,
			Endpoint: p.Endpoint,
			Message:  fmt.Sprintf("[ERROR] Недостатньо вимірів: %d з необхідних %d", len(p.Runs), g.Config.MinSampleRuns),
		}
	}

	currentCostUsd := g.CalculateUnitCostPerK(p.Runs)
	var deltaPct float64
	if p.BaselineCostUsd > 0 {
		deltaPct = ((currentCostUsd - p.BaselineCostUsd) / p.BaselineCostUsd) * 100.0
	}

	if currentCostUsd > g.Config.MaxUnitCostUsd {
		return GuardVerdict{
			Ok:              false,
			Endpoint:        p.Endpoint,
			CurrentCostUsd:  currentCostUsd,
			BaselineCostUsd: p.BaselineCostUsd,
			DeltaPct:        deltaPct,
			Message:         fmt.Sprintf("[FAIL] %s: Unit Cost $%.4f/1k перевищує ліміт $%.4f", p.Endpoint, currentCostUsd, g.Config.MaxUnitCostUsd),
		}
	}

	if deltaPct > g.Config.MaxRegressionPct {
		return GuardVerdict{
			Ok:              false,
			Endpoint:        p.Endpoint,
			CurrentCostUsd:  currentCostUsd,
			BaselineCostUsd: p.BaselineCostUsd,
			DeltaPct:        deltaPct,
			Message:         fmt.Sprintf("[FAIL] %s: Регресія Unit Cost +%.1f%% перевищує поріг +%.1f%% (база: $%.4f, поточна: $%.4f)", p.Endpoint, deltaPct, g.Config.MaxRegressionPct, p.BaselineCostUsd, currentCostUsd),
		}
	}

	return GuardVerdict{
		Ok:              true,
		Endpoint:        p.Endpoint,
		CurrentCostUsd:  currentCostUsd,
		BaselineCostUsd: p.BaselineCostUsd,
		DeltaPct:        deltaPct,
		Message:         fmt.Sprintf("[PASS] %s: Unit Cost $%.4f/1k (динаміка: %+.1f%%)", p.Endpoint, deltaPct),
	}
}
