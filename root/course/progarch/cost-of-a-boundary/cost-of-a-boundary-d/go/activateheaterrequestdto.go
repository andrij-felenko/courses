// Контракти та логіка перетину семантичної межі мовою Go
package boundary

import (
	"context"
	"errors"
	"fmt"
)

// Вхідний DTO для перетину межі: плоска структура без інваріантів
type ActivateHeaterRequestDTO struct {
	DeviceID      string   `json:"device_id"`
	RequiredPower *float64 `json:"required_power_kw"`
}

// Валідатор на межі: заміна компіляторних перевірок накладним кодом у рантаймі
func (dto *ActivateHeaterRequestDTO) Validate() error {
	if dto.DeviceID == "" {
		return errors.New("семантична помилка: ідентифікатор пристрою не може бути порожнім")
	}
	if dto.RequiredPower == nil {
		return errors.New("семантична помилка: відсутнє обов'язкове поле потужності")
	}
	if *dto.RequiredPower <= 0.0 || *dto.RequiredPower > 15.0 {
		return fmt.Errorf("інваріант порушено: потужність %.2f кВт поза межами [0, 15]", *dto.RequiredPower)
	}
	return nil
}

// Клієнти розподілених сервісів за межею
type PowerServiceClient interface {
	ReservePower(ctx context.Context, reservationID string, kw float64) error
	ReleasePower(ctx context.Context, reservationID string) error
}

type DeviceRelayClient interface {
	SwitchOn(ctx context.Context, deviceID string) error
}

// Оркестратор саги: ручне керування компенсаціями при втраті транзакційної атомарності
type HeaterActivationSaga struct {
	powerClient PowerServiceClient
	relayClient DeviceRelayClient
}

func (s *HeaterActivationSaga) Execute(ctx context.Context, dto ActivateHeaterRequestDTO) error {
	// 1. Податок валідації DTO на межі
	if err := dto.Validate(); err != nil {
		return fmt.Errorf("відхилено на межі: %w", err)
	}

	reservationID := fmt.Sprintf("res-%s", dto.DeviceID)
	powerKW := *dto.RequiredPower

	// 2. Крок 1 саги: фіксація першої локальної транзакції
	if err := s.powerClient.ReservePower(ctx, reservationID, powerKW); err != nil {
		return fmt.Errorf("збій резервування потужності: %w", err)
	}

	// 3. Крок 2 саги: спроба увімкнення за ненадійною межею
	if err := s.relayClient.SwitchOn(ctx, dto.DeviceID); err != nil {
		// АТОМАРНІСТЬ ЗРУЙНОВАНО: вимагається явна компенсуюча транзакція
		compErr := s.powerClient.ReleasePower(context.Background(), reservationID)
		if compErr != nil {
			// Критична семантична аварія: стан системи неузгоджений
			return fmt.Errorf("катастрофічний збій компенсації: %v після помилки: %w", compErr, err)
		}
		return fmt.Errorf("операцію скасовано, виконано компенсацію потужності: %w", err)
	}

	return nil
}
