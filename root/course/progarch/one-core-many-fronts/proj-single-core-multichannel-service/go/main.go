package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http/httptest"
	"sync"
	"time"
)

// CompositionRoot — композиційний корінь застосунку.
// Збирає систему воєдино: ініціалізує прикладне ядро TemperatureService, монтує до нього
// три незалежні драйвуючі адаптери (CLIHandler, HTTPHandler, QueueConsumer) та управляє
// узгодженим життєвим циклом системи без застосування прихованого глобального стану.
type CompositionRoot struct {
	service       *TemperatureService
	httpHandler   *HTTPHandler
	cliHandler    *CLIHandler
	queueConsumer *QueueConsumer
	inboundQueue  chan QueueMessage
	dlqQueue      chan QueueMessage
	retryQueue    chan QueueMessage
	cancelFunc    context.CancelFunc
	wg            sync.WaitGroup
}

// NewCompositionRoot створює систему, налаштовує зони клімат-контролю та пов'язує компоненти.
func NewCompositionRoot() *CompositionRoot {
	// 1. Початковий стан зон клімат-контролю
	initialZones := []*ZoneState{
		{
			ID:          "living-room",
			CurrentTemp: 20.0,
			MinTemp:     15.0,
			MaxTemp:     30.0,
			MaxStep:     5.0,
			IsLocked:    false,
		},
		{
			ID:          "bedroom",
			CurrentTemp: 18.0,
			MinTemp:     15.0,
			MaxTemp:     30.0,
			MaxStep:     4.0,
			IsLocked:    false,
		},
		{
			ID:          "server-room",
			CurrentTemp: 19.0,
			MinTemp:     15.0,
			MaxTemp:     25.0,
			MaxStep:     2.0,
			IsLocked:    true,
			LockReason:  "активовано протокол пожежної безпеки та консервації клімату",
		},
	}

	// 2. Інстанціювання чистого прикладного ядра
	service := NewTemperatureService(initialZones)

	// Ядро експортує технологічно-нейтральний контракт вхідного порту
	var useCase TemperatureUseCase = service

	// 3. Інстанціювання драйвуючих адаптерів
	httpHandler := NewHTTPHandler(useCase)
	cliHandler := NewCLIHandler(useCase)

	// Канали для взаємодії з асинхронним адаптером черги
	inboundQueue := make(chan QueueMessage, 10)
	dlqQueue := make(chan QueueMessage, 10)
	retryQueue := make(chan QueueMessage, 10)

	queueConsumer := NewQueueConsumer(useCase, inboundQueue, dlqQueue, retryQueue, 3)

	return &CompositionRoot{
		service:       service,
		httpHandler:   httpHandler,
		cliHandler:    cliHandler,
		queueConsumer: queueConsumer,
		inboundQueue:  inboundQueue,
		dlqQueue:      dlqQueue,
		retryQueue:    retryQueue,
	}
}

// Start запускає фонові процеси системи (горутини черги тощо).
func (cr *CompositionRoot) Start(ctx context.Context) {
	workerCtx, cancel := context.WithCancel(ctx)
	cr.cancelFunc = cancel
	cr.queueConsumer.Start(workerCtx, &cr.wg)
}

// Stop виконує узгоджене коректне зупинення (graceful shutdown) компонентів.
func (cr *CompositionRoot) Stop() {
	if cr.cancelFunc != nil {
		cr.cancelFunc()
	}
	close(cr.inboundQueue)
	cr.wg.Wait()
}

func main() {
	fmt.Println("================================================================================")
	fmt.Println(" АРХІТЕКТУРА: Одне ядро, кілька фронтів (Hexagonal / Ports and Adapters)")
	fmt.Println("================================================================================")

	// Ініціалізація компонентів у композиційному корені
	root := NewCompositionRoot()
	ctx := context.Background()
	root.Start(ctx)
	defer root.Stop()

	// -------------------------------------------------------------------------
	// ФРОНТ 1: Консольний адаптер (CLI)
	// -------------------------------------------------------------------------
	fmt.Println("\n>>> [1/3] ТЕСТУВАННЯ ДРАЙВУЮЧОГО АДАПТЕРА CLI (adapter_cli.go) <<<")

	var stdout, stderr bytes.Buffer

	// 1.1 Успішний виклик CLI (код повернення 0)
	fmt.Println("1.1 Виклик CLI з валідними параметрами (встановлення 22.5 °C для living-room):")
	code := root.cliHandler.Run([]string{"-zone=living-room", "-temp=22.5", "-user=admin-alex"}, &stdout, &stderr)
	fmt.Printf("Код завершення: %d\n%s", code, stdout.String())
	stdout.Reset()
	stderr.Reset()

	// 1.2 Виклик CLI з порушенням доменного інваріанта (крок завеликий: 22.5 -> 29.0 > maxStep 5.0)
	fmt.Println("1.2 Виклик CLI з перевищенням кроку зміни температури (доменне відхилення, код 1):")
	code = root.cliHandler.Run([]string{"-zone=living-room", "-temp=29.0", "-user=admin-alex"}, &stdout, &stderr)
	fmt.Printf("Код завершення: %d\n%s", code, stderr.String())
	stdout.Reset()
	stderr.Reset()

	// 1.3 Виклик CLI з відсутнім обов'язковим прапорцем (системна помилка аргументів, код 2)
	fmt.Println("1.3 Виклик CLI з пропущеним обов'язковим прапорцем -zone (код 2):")
	code = root.cliHandler.Run([]string{"-temp=20.0"}, &stdout, &stderr)
	fmt.Printf("Код завершення: %d (помилка синтаксису аргументів коректно перехоплена)\n", code)
	stdout.Reset()
	stderr.Reset()

	// -------------------------------------------------------------------------
	// ФРОНТ 2: Веб-адаптер REST API (HTTP net/http)
	// -------------------------------------------------------------------------
	fmt.Println("\n>>> [2/3] ТЕСТУВАННЯ ДРАЙВУЮЧОГО АДАПТЕРА HTTP REST (adapter_http.go) <<<")

	// Тестовий HTTP сервер на базі зареєстрованого обработчика
	server := httptest.NewServer(root.httpHandler)
	defer server.Close()

	client := server.Client()

	// 2.1 Успішний HTTP POST запит (200 OK)
	fmt.Println("2.1 Успішний HTTP POST запит для зони bedroom (встановлення 21.0 °C):")
	reqBody := `{"target_temperature": 21.0, "idempotency_key": "http-req-1"}`
	resp, err := client.Post(
		server.URL+"/api/v1/zones/bedroom/temperature",
		"application/json",
		bytes.NewBufferString(reqBody),
	)
	if err != nil {
		fmt.Printf("Помилка виконання HTTP запиту: %v\n", err)
	} else {
		body, _ := io.ReadAll(resp.Body)
		_ = resp.Body.Close()
		fmt.Printf("HTTP Статус: %d OK\nВідповідь JSON: %s\n", resp.StatusCode, string(body))
	}

	// 2.2 HTTP запит з неприпустимим значенням (35.0 °C > max 30.0 °C -> RFC 7807 Problem Details 422)
	fmt.Println("2.2 HTTP запит з температурою за межами діапазону (35.0 °C -> 422 Unprocessable Entity):")
	reqBodyInvalid := `{"target_temperature": 35.0, "idempotency_key": "http-req-2"}`
	respInvalid, err := client.Post(
		server.URL+"/api/v1/zones/bedroom/temperature",
		"application/json",
		bytes.NewBufferString(reqBodyInvalid),
	)
	if err != nil {
		fmt.Printf("Помилка виконання HTTP запиту: %v\n", err)
	} else {
		body, _ := io.ReadAll(respInvalid.Body)
		_ = respInvalid.Body.Close()
		fmt.Printf("HTTP Статус: %d Unprocessable Entity\nContent-Type: %s\nProblem Details RFC 7807: %s\n",
			respInvalid.StatusCode, respInvalid.Header.Get("Content-Type"), string(body))
	}

	// 2.3 HTTP запит до заблокованої зони server-room (423 Locked)
	fmt.Println("2.3 HTTP запит до заблокованої безпекою зони (server-room -> 423 Locked):")
	reqBodyLocked := `{"target_temperature": 20.0, "idempotency_key": "http-req-3"}`
	respLocked, err := client.Post(
		server.URL+"/api/v1/zones/server-room/temperature",
		"application/json",
		bytes.NewBufferString(reqBodyLocked),
	)
	if err != nil {
		fmt.Printf("Помилка виконання HTTP запиту: %v\n", err)
	} else {
		body, _ := io.ReadAll(respLocked.Body)
		_ = respLocked.Body.Close()
		fmt.Printf("HTTP Статус: %d Locked\nProblem Details RFC 7807: %s\n",
			respLocked.StatusCode, string(body))
	}

	// -------------------------------------------------------------------------
	// ФРОНТ 3: Асинхронний адаптер споживача черги (Queue Consumer)
	// -------------------------------------------------------------------------
	fmt.Println("\n>>> [3/3] ТЕСТУВАННЯ АСИНХРОННОГО АДАПТЕРА ЧЕРГИ (adapter_queue.go) <<<")

	// 3.1 Валідне повідомлення з черги -> ACK
	ackChan := make(chan struct{})
	validPayload, _ := json.Marshal(queuePayloadDTO{
		ZoneID:            "bedroom",
		TargetTemperature: 22.0,
		IdempotencyKey:    "queue-event-101",
	})
	msgValid := QueueMessage{
		ID:      "msg-101",
		Payload: validPayload,
		Attempt: 1,
		Headers: map[string]string{
			"Trace-ID":   "trace-iot-101",
			"Subject-ID": "sensor-hub",
		},
		AckChan: ackChan,
	}

	fmt.Println("3.1 Відправка валідного повідомлення в канал черги...")
	root.inboundQueue <- msgValid

	select {
	case <-ackChan:
		fmt.Println("Клієнт черги отримав підтвердження ACK!")
	case <-time.After(500 * time.Millisecond):
		fmt.Println("Таймаут очікування ACK")
	}

	// 3.2 Невалідне з точки зору бізнес-правил повідомлення (температура 10.0 °C < 15.0 °C)
	// Повинно відправитися безпосередньо в DLQ (Dead Letter Queue) без повторів
	invalidPayload, _ := json.Marshal(queuePayloadDTO{
		ZoneID:            "bedroom",
		TargetTemperature: 10.0, // Менше ніж minTemp 15.0 °C
		IdempotencyKey:    "queue-event-102",
	})
	msgInvalid := QueueMessage{
		ID:      "msg-102",
		Payload: invalidPayload,
		Attempt: 1,
		Headers: map[string]string{
			"Trace-ID":   "trace-iot-102",
			"Subject-ID": "faulty-sensor",
		},
	}

	fmt.Println("\n3.2 Відправка неприпустимого за доменними правилами повідомлення (10.0 °C)...")
	root.inboundQueue <- msgInvalid

	select {
	case dlqMsg := <-root.dlqQueue:
		fmt.Printf("Отримано повідомлення в DLQ!\n  ID: %s\n  Причина: %s\n",
			dlqMsg.ID, dlqMsg.DropReason)
	case <-time.After(500 * time.Millisecond):
		fmt.Println("Таймаут очікування DLQ")
	}

	// -------------------------------------------------------------------------
	// ПІДСУМОК СТАНУ ЯДРА
	// -------------------------------------------------------------------------
	fmt.Println("\n================================================================================")
	fmt.Println(" ПІДСУМКОВИЙ СТАН ДОМЕННОГО ЯДРА ПІСЛЯ ВИКЛИКІВ З УСІХ ТРЬОХ ТОЧОК ВХОДУ")
	fmt.Println("================================================================================")
	for _, zoneID := range []string{"living-room", "bedroom", "server-room"} {
		state, _ := root.service.GetZoneState(zoneID)
		fmt.Printf("Зона '%-12s': Температура = %5.1f °C | Заблокована = %-5t | Межі: [%.1f - %.1f °C]\n",
			state.ID, state.CurrentTemp, state.IsLocked, state.MinTemp, state.MaxTemp)
	}

	fmt.Println("\nВисновок: Єдине прикладне ядро TemperatureService автономно захищає всі бізнес-правила,")
	fmt.Println("а три тонкі драйвуючі адаптери (CLI, HTTP, Queue) симетрично транслюють різні протоколи,")
	fmt.Println("запобігаючи розмиванню й дрейфу доменної логіки по точках входу.")
}
