package main

import (
	"fmt"
	"time"
)

// CallContext — протокольно-нейтральний контекст виклику прикладного ядра.
// Він ізолює домен від мережевих заголовків, реквестів HTTP чи структур брокерів повідомлень,
// передаючи лише наскрізні метадані: суб'єкта дії, наскрізний TraceID та часову мітку виклику.
type CallContext struct {
	SubjectID string    // Ідентифікатор суб'єкта або сервісу, що ініціював операцію
	TraceID   string    // Наскрізний ідентифікатор трасування (Correlation / Trace ID)
	Timestamp time.Time // Часова мітка отримання запиту на межі драйвуючого адаптера
}

// ChangeTemperatureCommand — незмінний Command DTO, що виражає намір зміни температури в системі.
// DTO містить виключно доменні примітиви без прив'язки до формату серіалізації чи транспорту.
type ChangeTemperatureCommand struct {
	ZoneID            string  // Унікальний ідентифікатор зони клімат-контролю
	TargetTemperature float64 // Бажане значення температури в градусах Цельсія
	IdempotencyKey    string  // Ключ ідемпотентності для запобігання дублюванню операцій
}

// TemperatureResult — чистий об'єкт успішного результату виконання операції прикладного ядра.
// Надає знімки попереднього й нового стану зони для подальшої серіалізації адаптерами.
type TemperatureResult struct {
	ZoneID              string    // Ідентифікатор оновленої зони
	PreviousTemperature float64   // Попередня температура в зоні (°C)
	CurrentTemperature  float64   // Нова актуальна температура в зоні (°C)
	UpdatedAt           time.Time // Час фіксації змін у сховищі ядра
}

// DomainErrorCode — типізований машинно-читабельний код доменної помилки.
type DomainErrorCode string

const (
	// ErrCodeZoneNotFound сигналізує про відсутність вказаної зони в системі.
	ErrCodeZoneNotFound DomainErrorCode = "ZONE_NOT_FOUND"

	// ErrCodeTemperatureOutOfRange сигналізує про вихід за межі допустимого діапазону (15–30 °C).
	ErrCodeTemperatureOutOfRange DomainErrorCode = "TEMPERATURE_OUT_OF_RANGE"

	// ErrCodeStepTooLarge сигналізує про перевищення максимального кроку зміни за одну операцію.
	ErrCodeStepTooLarge DomainErrorCode = "STEP_TOO_LARGE"

	// ErrCodeZoneLocked сигналізує про аварійне або сервісне блокування зони (Safety Lock).
	ErrCodeZoneLocked DomainErrorCode = "ZONE_LOCKED"

	// ErrCodeInvalidInput сигналізує про порожні або некоректні поля вхідної команди.
	ErrCodeInvalidInput DomainErrorCode = "INVALID_INPUT"
)

// DomainError — типізована помилка предметної області.
// Поєднує семантичний код помилки для протокольного мапінгу та зрозумілий людям опис відхилення.
type DomainError struct {
	Code    DomainErrorCode
	Message string
}

// Error реалізує інтерфейс error стандартної бібліотеки Go.
func (e *DomainError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

// NewDomainError створює новий екземпляр доменної помилки з форматуванням повідомлення.
func NewDomainError(code DomainErrorCode, format string, a ...any) *DomainError {
	return &DomainError{
		Code:    code,
		Message: fmt.Sprintf(format, a...),
	}
}

// TemperatureUseCase — контракт вхідного драйвуючого порту (Driving / Inbound Port).
// Він фіксує технологічно-нейтральну межу прикладного ядра: бізнес-сценарій зміни температури
// доступний будь-яким адаптерам виключно через цей метод.
type TemperatureUseCase interface {
	Execute(ctx CallContext, cmd ChangeTemperatureCommand) (TemperatureResult, error)
}
