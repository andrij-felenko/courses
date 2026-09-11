package boundarybench

import (
	"testing"
)

// TestAllValidators перевіряє функціональну еквівалентність усіх 6 варіантів швів:
// кожен тип межі повинен однаково коректно приймати валідне замовлення
// та повертати помилку для некоректного.
func TestAllValidators(t *testing.T) {
	direct := DirectValidator{}
	iface := NewInterfaceValidator(direct)

	channel := NewChannelValidator(100)
	defer channel.Close()

	uds, err := NewUnixSocketTransport()
	if err != nil {
		t.Fatalf("не вдалося запустити UnixSocketTransport: %v", err)
	}
	defer uds.Close()

	grpcT, err := NewGRPCTransport()
	if err != nil {
		t.Fatalf("не вдалося запустити GRPCTransport: %v", err)
	}
	defer grpcT.Close()

	httpT := NewHTTPJSONTransport()
	defer httpT.Close()

	validators := []struct {
		name      string
		validator OrderValidator
	}{
		{"DirectCall", direct},
		{"InterfaceCall", iface},
		{"ChannelQueue", channel},
		{"UnixDomainSocket", uds},
		{"GRPCProtobuf", grpcT},
		{"HTTPJSON", httpT},
	}

	validOrder := NewSampleValidOrder()
	invalidOrder := NewSampleInvalidOrder()

	for _, tc := range validators {
		t.Run(tc.name, func(t *testing.T) {
			// Перевірка успішного замовлення
			resp, err := tc.validator.Validate(validOrder)
			if err != nil {
				t.Fatalf("[%s] неочікувана помилка транспорту: %v", tc.name, err)
			}
			if !resp.Valid || resp.Error != "" {
				t.Fatalf("[%s] очікувалось Valid=true, отримано: %+v", tc.name, resp)
			}

			// Перевірка невалідного замовлення
			respInv, err := tc.validator.Validate(invalidOrder)
			if err != nil {
				t.Fatalf("[%s] неочікувана помилка транспорту: %v", tc.name, err)
			}
			if respInv.Valid || respInv.Error == "" {
				t.Fatalf("[%s] очікувалось відхилення Valid=false, отримано: %+v", tc.name, respInv)
			}
		})
	}
}

// 1. Прямий виклик функції (In-Process Direct Call)
// Базова лінія: наносекунди, 0 байт алокацій, повний inlining компілятора.
func BenchmarkDirectCall(b *testing.B) {
	v := DirectValidator{}
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}

// 2. Виклик через інтерфейс (In-Process Interface Dispatch)
// Динамічна диспетчеризація через itable, вимкнення інлайнінгу.
func BenchmarkInterfaceCall(b *testing.B) {
	v := NewInterfaceValidator(DirectValidator{})
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}

// 3. Передача через канал горутині-воркеру (In-Process Channel Queue)
// Синхронізація потоків, черга, перемикання контексту планувальника Go.
func BenchmarkChannel(b *testing.B) {
	v := NewChannelValidator(1024)
	defer v.Close()
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}

// 4. Локальний міжпроцесний сокет (IPC Unix Domain Socket)
// Системні виклики ядра OS (read/write), копіювання в буфери сокета, JSON.
func BenchmarkUnixDomainSocket(b *testing.B) {
	v, err := NewUnixSocketTransport()
	if err != nil {
		b.Fatalf("помилка запуску UDS: %v", err)
	}
	defer v.Close()
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}

// 5. Двійковий RPC через TCP (gRPC / Protobuf Framing)
// Мережевий стек TCP, двійкова серіалізація Protobuf, 5-байтовий gRPC-фреймінг.
func BenchmarkGRPCProtobuf(b *testing.B) {
	v, err := NewGRPCTransport()
	if err != nil {
		b.Fatalf("помилка запуску gRPC: %v", err)
	}
	defer v.Close()
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}

// 6. Мережевий REST-запит (HTTP/JSON Protocol)
// Повний стек HTTP/1.1: заголовки, текстовий JSON, рефлексія, парсинг.
func BenchmarkHTTPJSON(b *testing.B) {
	v := NewHTTPJSONTransport()
	defer v.Close()
	order := NewSampleValidOrder()

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		resp, err := v.Validate(order)
		if err != nil || !resp.Valid {
			b.Fatalf("помилка валідації: %v", err)
		}
	}
}
