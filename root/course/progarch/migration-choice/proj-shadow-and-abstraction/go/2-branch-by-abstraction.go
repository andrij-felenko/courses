package abstraction

import (
	"errors"
	"sync/atomic"
)

type TariffContext struct {
	DeviceID      uint64
	KilowattHours float64
	ZoneCode      uint32
}

type CalculationResult struct {
	TotalCost  float64
	TariffName string
}

// 1. Abstraction Interface
type TariffCalculator interface {
	Calculate(ctx TariffContext) (CalculationResult, error)
}

// 2. Legacy Implementation
type LegacyTariffCalculator struct{}

func (l *LegacyTariffCalculator) Calculate(ctx TariffContext) (CalculationResult, error) {
	if ctx.KilowattHours < 0 {
		return CalculationResult{}, errors.New("negative kWh")
	}
	cost := ctx.KilowattHours * 2.45
	if ctx.ZoneCode == 2 {
		cost *= 0.5
	}
	return CalculationResult{TotalCost: cost, TariffName: "Legacy-Flat-v1"}, nil
}

// 3. New Implementation
type DynamicGridTariffCalculator struct{}

func (d *DynamicGridTariffCalculator) Calculate(ctx TariffContext) (CalculationResult, error) {
	if ctx.KilowattHours < 0 {
		return CalculationResult{}, errors.New("negative kWh")
	}
	baseRate := 2.80
	if ctx.ZoneCode == 2 {
		baseRate = 1.20
	}
	cost := ctx.KilowattHours * baseRate
	if ctx.KilowattHours > 500.0 {
		cost += (ctx.KilowattHours - 500.0) * 0.40
	}
	return CalculationResult{TotalCost: cost, TariffName: "DynamicGrid-v2"}, nil
}

// 4. Branch Router з атомарним прапорцем
type TariffServiceBoundary struct {
	legacy TariffCalculator
	newEng TariffCalculator
	useNew atomic.Bool
}

func NewTariffServiceBoundary() *TariffServiceBoundary {
	return &TariffServiceBoundary{
		legacy: &LegacyTariffCalculator{},
		newEng: &DynamicGridTariffCalculator{},
	}
}

func (b *TariffServiceBoundary) SetUseNewEngine(enable bool) {
	b.useNew.Store(enable)
}

func (b *TariffServiceBoundary) ProcessBilling(ctx TariffContext) (CalculationResult, error) {
	if b.useNew.Load() {
		return b.newEng.Calculate(ctx)
	}
	return b.legacy.Calculate(ctx)
}
