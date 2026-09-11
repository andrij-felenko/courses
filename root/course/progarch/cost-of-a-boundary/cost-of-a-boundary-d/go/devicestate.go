package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// DeviceState представляє стан сенсора чи регулятора в системі Digital Home
type DeviceState struct {
	DeviceID          string
	TargetTemperature int
	IsActive          bool
}

// DeviceAutomation — чистий шов (seam), що ізолює бізнес-логіку від способу виклику
type DeviceAutomation interface {
	UpdateState(ctx context.Context, id string, temp int, active bool) (DeviceState, error)
}

// LocalDeviceAutomation — реалізація всередині модульного моноліту (спільна пам'ять, транзакційність)
type LocalDeviceAutomation struct {
	mu    sync.Mutex
	state DeviceState
}

func NewLocalDeviceAutomation() *LocalDeviceAutomation {
	return &LocalDeviceAutomation{
		state: DeviceState{DeviceID: "thermostat-zone-1", TargetTemperature: 20, IsActive: true},
	}
}

func (l *LocalDeviceAutomation) UpdateState(_ context.Context, id string, temp int, active bool) (DeviceState, error) {
	// Атомарне оновлення в пам'яті процесу під блокуванням
	l.mu.Lock()
	defer l.mu.Unlock()

	l.state.DeviceID = id
	l.state.TargetTemperature = temp
	l.state.IsActive = active

	// Наносекундне виконання: немає серіалізації, мережі та дескрипторів
	return l.state, nil
}

// RemoteDeviceAdapter — адаптер через межу мережі (RPC, DTO, затримка, ризик відмов)
type RemoteDeviceAdapter struct {
	counter uint64
}

func NewRemoteDeviceAdapter() *RemoteDeviceAdapter {
	return &RemoteDeviceAdapter{}
}

func (r *RemoteDeviceAdapter) UpdateState(ctx context.Context, id string, temp int, active bool) (DeviceState, error) {
	// Імітація латентності серіалізації та мережевого прогону
	select {
	case <-time.After(15 * time.Millisecond):
	case <-ctx.Done():
		return DeviceState{}, ctx.Err()
	}

	// Імітація часткової відмови для перевірки стійкості
	if atomic.AddUint64(&r.counter, 1)%50 == 0 {
		return DeviceState{}, errors.New("мережевий таймаут перетину межі RPC")
	}

	return DeviceState{DeviceID: id, TargetTemperature: temp, IsActive: active}, nil
}

// BoundaryMode позначає еволюційний статус архітектурної межі
type BoundaryMode int32

const (
	ModeDirectLocal   BoundaryMode = 0 // Модульний моноліт: прямий виклик у пам'яті
	ModeDualRunShadow BoundaryMode = 1 // Тіньовий подвійний запуск: локальний відповідає, віддалений звіряється
	ModeCanaryRemote  BoundaryMode = 2 // Канарковий реліз: відсоток трафіку йде через мережу з бекапом
	ModeDirectRemote  BoundaryMode = 3 // Повне розрізання: 100% трафіку йде через віддалену межу
)

// EvolutionaryBoundaryDispatcher керує перекроюванням межі в реальному часі
type EvolutionaryBoundaryDispatcher struct {
	local            DeviceAutomation
	remote           DeviceAutomation
	mode             int32
	canaryPercentage uint32
}

func NewEvolutionaryDispatcher(local, remote DeviceAutomation) *EvolutionaryBoundaryDispatcher {
	return &EvolutionaryBoundaryDispatcher{
		local:            local,
		remote:           remote,
		mode:             int32(ModeDirectLocal),
		canaryPercentage: 0,
	}
}

func (d *EvolutionaryBoundaryDispatcher) SetMode(mode BoundaryMode, canaryPct uint32) {
	atomic.StoreUint32(&d.canaryPercentage, canaryPct)
	atomic.StoreInt32(&d.mode, int32(mode))
}

func (d *EvolutionaryBoundaryDispatcher) UpdateState(ctx context.Context, id string, temp int, active bool) (DeviceState, error) {
	currentMode := BoundaryMode(atomic.LoadInt32(&d.mode))

	switch currentMode {
	case ModeDirectLocal:
		// Пряме звернення в моноліті — нульовий потрійний податок
		return d.local.UpdateState(ctx, id, temp, active)

	case ModeDualRunShadow:
		// Обслуговуємо користувача гарантовано через локальну реалізацію
		localResult, err := d.local.UpdateState(ctx, id, temp, active)
		if err != nil {
			return localResult, err
		}

		// У фоновій ґорутині відправляємо тіньовий запит через віддалену межу
		go func(expected DeviceState) {
			shadowCtx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
			defer cancel()

			remoteResult, rErr := d.remote.UpdateState(shadowCtx, id, temp, active)
			if rErr != nil {
				log.Printf("[Тіньова помилка віддаленої межі]: %v", rErr)
				return
			}
			if remoteResult.TargetTemperature != expected.TargetTemperature {
				log.Printf("[Тіньова розбіжність] Очікували %d, отримали %d для %s",
					expected.TargetTemperature, remoteResult.TargetTemperature, id)
			}
		}(localResult)

		return localResult, nil

	case ModeCanaryRemote:
		pct := atomic.LoadUint32(&d.canaryPercentage)
		if rand.Uint32()%100 < pct {
			// Направляємо канаркову частку трафіку на віддалений сервіс
			remoteResult, rErr := d.remote.UpdateState(ctx, id, temp, active)
			if rErr == nil {
				return remoteResult, nil
			}
			// Якщо віддалена межа відмовила — миттєво страхуємося локальним викликом
			log.Printf("[Канарковий збій -> Відкат до локального]: %v", rErr)
		}
		return d.local.UpdateState(ctx, id, temp, active)

	case ModeDirectRemote:
		// Компонент остаточно розрізано за новою мережевою межею
		return d.remote.UpdateState(ctx, id, temp, active)
	}

	return d.local.UpdateState(ctx, id, temp, active)
}
