package main

import (
	"math"
	"sync"
	"time"
)

// ZoneState — внутрішня доменна сутність стану зони клімат-контролю.
// Зберігає актуальну температуру, межі безпечного регулювання та прапорець захисного блокування.
type ZoneState struct {
	ID          string  // Ідентифікатор зони (наприклад, "living-room", "server-room")
	CurrentTemp float64 // Поточна температура (°C)
	MinTemp     float64 // Мінімально допустима безпечна температура (15.0 °C)
	MaxTemp     float64 // Максимально допустима безпечна температура (30.0 °C)
	MaxStep     float64 // Максимально допустимий крок зміни за одну команду
	IsLocked    bool    // Прапорець блокування безпеки (Safety Lock)
	LockReason  string  // Причина блокування (наприклад, "пожежна тривога", "техогляд")
}

// TemperatureService — прикладне ядро системи, що реалізує контракт TemperatureUseCase.
// Інкапсулює непорушні доменні правила й бізнес-інваріанти, захищаючи їх від розмивання між фронтами.
// Стан зон є потокобезпечним завдяки використанню sync.RWMutex.
type TemperatureService struct {
	mu             sync.RWMutex
	zones          map[string]*ZoneState
	idempotencyLog map[string]TemperatureResult
}

// NewTemperatureService інстанціює прикладний сервіс із заданою конфігурацією зон.
func NewTemperatureService(initialZones []*ZoneState) *TemperatureService {
	zonesMap := make(map[string]*ZoneState, len(initialZones))
	for _, z := range initialZones {
		clone := *z
		zonesMap[z.ID] = &clone
	}
	return &TemperatureService{
		zones:          zonesMap,
		idempotencyLog: make(map[string]TemperatureResult),
	}
}

// Execute виконує зміну температури, строго контролюючи всі бізнес-інваріанти предметної області.
func (s *TemperatureService) Execute(ctx CallContext, cmd ChangeTemperatureCommand) (TemperatureResult, error) {
	// Базова валідація команди на рівні порту
	if cmd.ZoneID == "" {
		return TemperatureResult{}, NewDomainError(ErrCodeInvalidInput, "ідентифікатор зони не може бути порожнім")
	}
	if cmd.IdempotencyKey == "" {
		return TemperatureResult{}, NewDomainError(ErrCodeInvalidInput, "ключ ідемпотентності є обов'язковим для надійного виконання")
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	// 1. Перевірка ідемпотентності: якщо команда вже виконувалася, повертаємо збережений знімок
	if cachedResult, exists := s.idempotencyLog[cmd.IdempotencyKey]; exists {
		return cachedResult, nil
	}

	// 2. Інваріант: перевірка існування зони в реєстрі
	zone, exists := s.zones[cmd.ZoneID]
	if !exists {
		return TemperatureResult{}, NewDomainError(
			ErrCodeZoneNotFound,
			"зону клімат-контролю '%s' не знайдено в системі",
			cmd.ZoneID,
		)
	}

	// 3. Інваріант: блокування безпеки (Safety Lock)
	if zone.IsLocked {
		return TemperatureResult{}, NewDomainError(
			ErrCodeZoneLocked,
			"зона '%s' заблокована протоколом безпеки: %s",
			zone.ID,
			zone.LockReason,
		)
	}

	// 4. Інваріант: допустимий діапазон температур (15.0 - 30.0 °C)
	if cmd.TargetTemperature < zone.MinTemp || cmd.TargetTemperature > zone.MaxTemp {
		return TemperatureResult{}, NewDomainError(
			ErrCodeTemperatureOutOfRange,
			"цільова температура %.1f °C виходить за межі допустимого діапазону [%.1f - %.1f °C]",
			cmd.TargetTemperature,
			zone.MinTemp,
			zone.MaxTemp,
		)
	}

	// 5. Інваріант: максимальний крок зміни за одну команду
	delta := math.Abs(cmd.TargetTemperature - zone.CurrentTemp)
	if delta > zone.MaxStep {
		return TemperatureResult{}, NewDomainError(
			ErrCodeStepTooLarge,
			"зміна температури на %.1f °C перевищує максимально дозволений крок %.1f °C (поточна: %.1f °C)",
			delta,
			zone.MaxStep,
			zone.CurrentTemp,
		)
	}

	// Зміна стану зони
	prevTemp := zone.CurrentTemp
	zone.CurrentTemp = cmd.TargetTemperature
	now := time.Now()

	result := TemperatureResult{
		ZoneID:              zone.ID,
		PreviousTemperature: prevTemp,
		CurrentTemperature:  zone.CurrentTemp,
		UpdatedAt:           now,
	}

	// Фіксація операції в лозі ідемпотентності
	s.idempotencyLog[cmd.IdempotencyKey] = result

	return result, nil
}

// GetZoneState повертає незмінний знімок стану зони для діагностики та перевірки.
func (s *TemperatureService) GetZoneState(zoneID string) (ZoneState, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	zone, exists := s.zones[zoneID]
	if !exists {
		return ZoneState{}, false
	}
	return *zone, true
}
