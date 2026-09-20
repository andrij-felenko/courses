package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"
)

// QueueMessage — структура повідомлення асинхронної черги подій регулювання температури.
type QueueMessage struct {
	ID         string            `json:"id"`          // Унікальний ідентифікатор повідомлення в черзі
	Payload    []byte            `json:"payload"`     // Сире JSON-тіло корисного навантаження
	Attempt    int               `json:"attempt"`     // Лічильник спроб обробки повідомлення
	Headers    map[string]string `json:"headers"`     // Метадані повідомлення (TraceID, Subject тощо)
	AckChan    chan struct{}     `json:"-"`           // Канал підтвердження успішної обробки (ACK)
	NackChan   chan error        `json:"-"`           // Канал повідомлення про збій для повторної спроби (NACK)
	DeadLetter bool              `json:"dead_letter"` // Ознака відправлення в чергу недійсних повідомлень (DLQ)
	DropReason string            `json:"drop_reason"` // Семантична причина відхилення повідомлення
}

// queuePayloadDTO — структура десеріалізації сирого тіла повідомлення з черги.
type queuePayloadDTO struct {
	ZoneID            string  `json:"zone_id"`
	TargetTemperature float64 `json:"target_temperature"`
	IdempotencyKey    string  `json:"idempotency_key"`
}

// QueueConsumer — асинхронний драйвуючий адаптер черги повідомлень на базі горутин і каналів.
// Вичитує повідомлення з вхідного каналу, транслює їх у команди вхідного порту та керує життєвим циклом:
// ACK (успіх), NACK (тимчасовий збій, повернення в чергу) або DLQ (детерміновані доменні відхилення).
type QueueConsumer struct {
	useCase    TemperatureUseCase
	inbound    <-chan QueueMessage
	dlq        chan<- QueueMessage
	retryQueue chan<- QueueMessage
	maxRetries int
}

// NewQueueConsumer конфігурує новий адаптер споживача черги.
func NewQueueConsumer(
	useCase TemperatureUseCase,
	inbound <-chan QueueMessage,
	dlq chan<- QueueMessage,
	retryQueue chan<- QueueMessage,
	maxRetries int,
) *QueueConsumer {
	return &QueueConsumer{
		useCase:    useCase,
		inbound:    inbound,
		dlq:        dlq,
		retryQueue: retryQueue,
		maxRetries: maxRetries,
	}
}

// Start запускає горутину споживача черги з контролем життєвого циклу через context.Context.
func (qc *QueueConsumer) Start(ctx context.Context, wg *sync.WaitGroup) {
	wg.Add(1)
	go func() {
		defer wg.Done()
		for {
			select {
			case <-ctx.Done():
				return
			case msg, ok := <-qc.inbound:
				if !ok {
					return
				}
				qc.processMessage(msg)
			}
		}
	}()
}

// processMessage виконує обробку одного повідомлення та реалізує семантику квитування.
func (qc *QueueConsumer) processMessage(msg QueueMessage) {
	// 1. Десеріалізація корисного навантаження
	var dto queuePayloadDTO
	if err := json.Unmarshal(msg.Payload, &dto); err != nil {
		// Фатальна помилка формату JSON: повтор ніколи не допоможе -> маршрутизуємо в DLQ
		msg.DeadLetter = true
		msg.DropReason = fmt.Sprintf("Пошкоджений JSON: %v", err)
		qc.routeToDLQ(msg)
		return
	}

	// 2. Витяг метаданих і побудова CallContext
	traceID := msg.Headers["Trace-ID"]
	if traceID == "" {
		traceID = fmt.Sprintf("queue-trace-%s", msg.ID)
	}
	subjectID := msg.Headers["Subject-ID"]
	if subjectID == "" {
		subjectID = "iot-sensor-hub"
	}

	callCtx := CallContext{
		SubjectID: subjectID,
		TraceID:   traceID,
		Timestamp: time.Now(),
	}

	idempKey := dto.IdempotencyKey
	if idempKey == "" {
		idempKey = fmt.Sprintf("queue-msg-%s", msg.ID)
	}

	cmd := ChangeTemperatureCommand{
		ZoneID:            dto.ZoneID,
		TargetTemperature: dto.TargetTemperature,
		IdempotencyKey:    idempKey,
	}

	// 3. Виклик вхідного порту
	result, err := qc.useCase.Execute(callCtx, cmd)
	if err == nil {
		// УСПІХ -> ACK: сповіщаємо брокер про успішну обробку
		if msg.AckChan != nil {
			close(msg.AckChan)
		}
		fmt.Printf("[QUEUE] ACK: Повідомлення %s успішно опрацьовано (зона '%s': %.1f -> %.1f °C)\n",
			msg.ID, result.ZoneID, result.PreviousTemperature, result.CurrentTemperature)
		return
	}

	// 4. Семантичний аналіз помилки: доменна проти системної
	var domErr *DomainError
	if errors.As(err, &domErr) {
		// Доменні відхилення (неприпустима температура, заблокована зона) є бізнес-правилами ядра.
		// Повторення не змінить стан системи без зміни вхідних даних -> маршрутизація в DLQ без retry.
		msg.DeadLetter = true
		msg.DropReason = fmt.Sprintf("Доменне відхилення [%s]: %s", domErr.Code, domErr.Message)
		qc.routeToDLQ(msg)
		return
	}

	// 5. Тимчасовий збій (інфраструктурна або мережева помилка) -> NACK з обмеженням спроб
	if msg.Attempt < qc.maxRetries {
		msg.Attempt++
		if msg.NackChan != nil {
			msg.NackChan <- err
		}
		fmt.Printf("[QUEUE] NACK: Тимчасовий збій для повідомлення %s (спроба %d/%d): %v. Повернення в чергу.\n",
			msg.ID, msg.Attempt, qc.maxRetries, err)
		if qc.retryQueue != nil {
			qc.retryQueue <- msg
		}
	} else {
		// Вичерпано ліміт повторних спроб -> відправлення в DLQ
		msg.DeadLetter = true
		msg.DropReason = fmt.Sprintf("Вичерпано ліміт спроб доставки (%d): %v", qc.maxRetries, err)
		qc.routeToDLQ(msg)
	}
}

// routeToDLQ направляє відхилене повідомлення в Dead Letter Queue.
func (qc *QueueConsumer) routeToDLQ(msg QueueMessage) {
	fmt.Printf("[QUEUE] DLQ: Повідомлення %s направлено в DLQ! Причина: %s\n", msg.ID, msg.DropReason)
	if qc.dlq != nil {
		select {
		case qc.dlq <- msg:
		default:
			fmt.Printf("[QUEUE] УВАГА: Буфер DLQ заповнений, повідомлення %s скинуто\n", msg.ID)
		}
	}
}
