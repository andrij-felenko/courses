package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"time"
)

// CLIHandler — драйвуючий консольний адаптер на базі пакета flag.
// Транслює аргументи запуску в команду ядра та транслює результат у термінальний вивід
// і стандартні POSIX-коди завершення процесу:
//   0 — Успішне виконання операції
//   1 — Помилка валідації або доменне відхилення бізнес-правил
//   2 — Системний збій, синтаксична помилка або некоректні прапорці запуску
type CLIHandler struct {
	useCase TemperatureUseCase
}

// NewCLIHandler інстанціює консольний драйвуючий адаптер.
func NewCLIHandler(useCase TemperatureUseCase) *CLIHandler {
	return &CLIHandler{
		useCase: useCase,
	}
}

// Run розбирає аргументи командного рядка, викликає ядро та повертає POSIX-код виходу.
func (c *CLIHandler) Run(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("climate-cli", flag.ContinueOnError)
	fs.SetOutput(stderr)

	zoneID := fs.String("zone", "", "Ідентифікатор зони клімат-контролю (обов'язковий)")
	targetTemp := fs.Float64("temp", 0.0, "Бажана температура в °C (обов'язковий)")
	subject := fs.String("user", "cli-operator", "Ідентифікатор користувача або скрипта автоматизації")
	idempotency := fs.String("idempotency", "", "Ключ ідемпотентності (опціонально, генерується автоматично)")

	if err := fs.Parse(args); err != nil {
		fmt.Fprintf(stderr, "[CLI] Помилка синтаксису прапорців: %v\n", err)
		return 2
	}

	if *zoneID == "" {
		fmt.Fprintln(stderr, "[CLI] Системна помилка: обов'язковий аргумент -zone не вказано")
		fs.Usage()
		return 2
	}

	// Перевірка явної присутності прапорця -temp
	tempSpecified := false
	fs.Visit(func(f *flag.Flag) {
		if f.Name == "temp" {
			tempSpecified = true
		}
	})
	if !tempSpecified {
		fmt.Fprintln(stderr, "[CLI] Системна помилка: обов'язковий аргумент -temp не вказано")
		fs.Usage()
		return 2
	}

	idempKey := *idempotency
	if idempKey == "" {
		idempKey = fmt.Sprintf("cli-%s-%d", *zoneID, time.Now().UnixNano())
	}

	callCtx := CallContext{
		SubjectID: *subject,
		TraceID:   fmt.Sprintf("cli-trace-%d", time.Now().UnixNano()),
		Timestamp: time.Now(),
	}

	cmd := ChangeTemperatureCommand{
		ZoneID:            *zoneID,
		TargetTemperature: *targetTemp,
		IdempotencyKey:    idempKey,
	}

	// Виклик технологічно-нейтрального вхідного порту
	result, err := c.useCase.Execute(callCtx, cmd)
	if err != nil {
		var domErr *DomainError
		if errors.As(err, &domErr) {
			// Доменне відхилення ядра -> POSIX код 1
			fmt.Fprintf(stderr, "[CLI] ДОМЕННА ВІДМОВА [%s]: %s\n", domErr.Code, domErr.Message)
			return 1
		}
		// Системна або непередбачена помилка -> POSIX код 2
		fmt.Fprintf(stderr, "[CLI] СИСТЕМНА ПОМИЛКА: %v\n", err)
		return 2
	}

	// Успішне завершення -> POSIX код 0
	fmt.Fprintf(
		stdout,
		"[CLI] УСПІХ: Зона '%s' оновлена | Температура: %.1f °C -> %.1f °C | Оновлено: %s\n",
		result.ZoneID,
		result.PreviousTemperature,
		result.CurrentTemperature,
		result.UpdatedAt.Format(time.RFC3339),
	)
	return 0
}
