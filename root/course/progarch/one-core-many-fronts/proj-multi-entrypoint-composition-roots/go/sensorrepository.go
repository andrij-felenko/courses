package core

import "context"

// Outbound port: інтерфейс сховища сенсорів
type SensorRepository interface {
	SaveCalibration(ctx context.Context, sensorID string, offset float64) error
}

// Inbound port: сценарій використання калібрування
type CalibrateSensorUseCase struct {
	repo SensorRepository
}

func NewCalibrateSensorUseCase(repo SensorRepository) *CalibrateSensorUseCase {
	return &CalibrateSensorUseCase{repo: repo}
}

func (uc *CalibrateSensorUseCase) Execute(ctx context.Context, sensorID string, offset float64) error {
	if offset < -10.0 || offset > 10.0 {
		return ErrCalibrationOutOfRange
	}
	return uc.repo.SaveCalibration(ctx, sensorID, offset)
}
