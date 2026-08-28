package commands

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// ── Сигнали оголошуємо РАЗ при старті: це assert-и, що чекають на трафік ──
var (
	// R+E: одна серія — і частота, і помилки; розрізняє їх мітка outcome.
	// Мітки лише ОБМЕЖЕНІ: команд десятки, наслідків чотири. НІЯКОГО device.
	commands = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "dh_device_commands_total",
		Help: "Команди пристроям за типом і наслідком.",
	}, []string{"command", "outcome"})

	// D: розподіл тривалості. Кошики нарізані навколо цілі SLO — 300 мс.
	latency = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "dh_device_command_seconds",
		Help:    "Тривалість обробки команди пристрою, секунди.",
		Buckets: []float64{0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5},
	}, []string{"command"})

	// Інваріант у проді: не assert, що валить сервіс, а лічильник «неможливого».
	invariant = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "dh_invariant_violation_total",
		Help: "Порушення інваріантів, помічені на гарячому шляху.",
	}, []string{"name"})
)

// DeviceGateway — той самий шов, у який тест вставляв дублер.
type DeviceGateway interface {
	Send(ctx context.Context, deviceID string, cmd Command) (Ack, error)
	Ping(ctx context.Context) error // для readiness
}

type Command struct {
	Name string `json:"name"` // "heat" | "set_target" | "reboot" — обмежена множина
	Arg  int    `json:"arg,omitempty"`
}

type Ack struct {
	Battery int `json:"battery"` // рівень, який відрапортував пристрій: інваріант 0..100
}

var (
	ErrTimeout  = errors.New("пристрій не відповів")
	ErrRejected = errors.New("пристрій відхилив команду")
)

type API struct {
	Devices DeviceGateway
	Log     *slog.Logger
}

func (a *API) SendCommand(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	tenant := tenantFromCtx(r.Context()) // орендар — з автентифікації, НЕ з тіла запиту
	deviceID := r.PathValue("id")        // маршрутизатор net/http, Go 1.22+

	var cmd Command
	if err := json.NewDecoder(r.Body).Decode(&cmd); err != nil {
		http.Error(w, "поганий запит", http.StatusBadRequest)
		return
	}

	ack, err := a.Devices.Send(r.Context(), deviceID, cmd)
	outcome := classify(err) // "ok" | "timeout" | "rejected" | "error"
	elapsed := time.Since(start)

	// D — гістограма: тривалість по ТИПУ команди (мітка обмежена).
	latency.WithLabelValues(cmd.Name).Observe(elapsed.Seconds())
	// R+E — лічильник: +1 до серії (команда, наслідок).
	commands.WithLabelValues(cmd.Name, outcome).Inc()

	// Інваріант як assert у проді: 0..100. Порушено — порахуй і затисни, НЕ падай.
	if outcome == "ok" && (ack.Battery < 0 || ack.Battery > 100) {
		invariant.WithLabelValues("battery_range").Inc()
		a.Log.Error("invariant.broken",
			"name", "battery_range", "tenant", tenant, "device", deviceID, "got", ack.Battery)
		ack.Battery = clamp(ack.Battery)
	}

	// Приклад-тест, записаний із проду: один рядок = повний контекст одного запиту.
	// В події — СТАБІЛЬНІ ІДЕНТИФІКАТОРИ, не e-mail і не імʼя.
	a.Log.Info("device.command",
		"tenant", tenant,
		"device", deviceID,
		"command", cmd.Name,
		"outcome", outcome,
		"latency_ms", elapsed.Milliseconds(),
	)

	writeResult(w, outcome, ack)
}

// classify зводить помилку шва до обмеженого набору наслідків — це й тримає
// кардинальність метрики малою: мітка outcome ніколи не «розповзеться».
func classify(err error) string {
	switch {
	case err == nil:
		return "ok"
	case errors.Is(err, ErrTimeout):
		return "timeout"
	case errors.Is(err, ErrRejected):
		return "rejected"
	default:
		return "error"
	}
}

func clamp(v int) int {
	if v < 0 {
		return 0
	}
	if v > 100 {
		return 100
	}
	return v
}

func writeResult(w http.ResponseWriter, outcome string, ack Ack) {
	status := map[string]int{"ok": 200, "rejected": 409, "timeout": 504}[outcome]
	if status == 0 {
		status = 500
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(ack)
}
