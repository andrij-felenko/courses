package main

import (
	"errors"
	"fmt"
)

type Decision int

const (
	Continue Decision = iota
	Promote
	RollbackBurnRate
	RollbackLatency
)

type WindowMetrics struct {
	TotalRequests uint64
	ErrorRequests uint64
	LatencyP99Ms  float64
}

type CanarySample struct {
	ShortWindow WindowMetrics
	LongWindow  WindowMetrics
}

type SystemConfig struct {
	TargetSLO         float64
	MaxBurnRateShort  float64
	MaxBurnRateLong   float64
	MaxLatencyRatio   float64
	MinSampleRequests uint64
}

func calcErrorRate(m WindowMetrics) float64 {
	if m.TotalRequests == 0 {
		return 0.0
	}
	return float64(m.ErrorRequests) / float64(m.TotalRequests)
}

func EvaluateCanary(cfg SystemConfig, baseline, canary CanarySample) (Decision, error) {
	if canary.ShortWindow.TotalRequests < cfg.MinSampleRequests {
		return Continue, nil
	}

	eSLO := 1.0 - cfg.TargetSLO
	if eSLO <= 0.0 {
		return Continue, errors.New("invalid SLO config")
	}

	errShort := calcErrorRate(canary.ShortWindow)
	errLong := calcErrorRate(canary.LongWindow)

	burnShort := errShort / eSLO
	burnLong := errLong / eSLO

	if burnShort >= cfg.MaxBurnRateShort && burnLong >= cfg.MaxBurnRateLong {
		return RollbackBurnRate, nil
	}

	if baseline.ShortWindow.LatencyP99Ms > 0.0 {
		ratio := canary.ShortWindow.LatencyP99Ms / baseline.ShortWindow.LatencyP99Ms
		if ratio > cfg.MaxLatencyRatio {
			return RollbackLatency, nil
		}
	}

	return Continue, nil
}

func main() {
	cfg := SystemConfig{
		TargetSLO:         0.9999,
		MaxBurnRateShort:  14.4,
		MaxBurnRateLong:   14.4,
		MaxLatencyRatio:   1.25,
		MinSampleRequests: 1000,
	}

	baseline := CanarySample{
		ShortWindow: WindowMetrics{TotalRequests: 50000, ErrorRequests: 1, LatencyP99Ms: 45.0},
		LongWindow:  WindowMetrics{TotalRequests: 600000, ErrorRequests: 10, LatencyP99Ms: 44.0},
	}

	badCanary := CanarySample{
		ShortWindow: WindowMetrics{TotalRequests: 5000, ErrorRequests: 25, LatencyP99Ms: 48.0},
		LongWindow:  WindowMetrics{TotalRequests: 10000, ErrorRequests: 50, LatencyP99Ms: 47.0},
	}

	decision, err := EvaluateCanary(cfg, baseline, badCanary)
	if err == nil && decision == RollbackBurnRate {
		fmt.Println("[CRITICAL] Canary Rollback: High Burn Rate Detected!")
	}
}
