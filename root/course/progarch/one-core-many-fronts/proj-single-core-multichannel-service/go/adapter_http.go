package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// ProblemDetails — машинно-читабельний формат опису помилок згідно з RFC 7807.
// Надає стандартизовану структуру для веб-клієнтів із зазначенням статусу, типу та деталей відхилення.
type ProblemDetails struct {
	Type     string `json:"type"`               // URI ідентифікатор типу проблеми
	Title    string `json:"title"`              // Короткий заголовок проблеми
	Status   int    `json:"status"`             // Відповідний HTTP статус-код
	Detail   string `json:"detail"`             // Докладний опис помилки
	Instance string `json:"instance,omitempty"` // Шлях ресурсу, на якому виникла помилка
	Code     string `json:"code,omitempty"`     // Доменний код помилки прикладного ядра
	TraceID  string `json:"trace_id,omitempty"` // Ідентифікатор трасування запиту
}

// httpChangeTempRequest — вхідне транспортне DTO протоколу HTTP.
type httpChangeTempRequest struct {
	TargetTemperature *float64 `json:"target_temperature"`
	IdempotencyKey    string   `json:"idempotency_key"`
}

// httpSuccessResponse — транспортне DTO успішної відповіді REST API.
type httpSuccessResponse struct {
	ZoneID              string    `json:"zone_id"`
	PreviousTemperature float64   `json:"previous_temperature"`
	CurrentTemperature  float64   `json:"current_temperature"`
	UpdatedAt           time.Time `json:"updated_at"`
}

// HTTPHandler — драйвуючий адаптер REST API на базі стандартного net/http.
// Виконує двосторонню трансляцію: парсить вхідний HTTP-запит у доменну команду, викликає Use Case
// і мапить доменні сутності у відповідь 200 OK або помилки RFC 7807 Problem Details.
type HTTPHandler struct {
	useCase TemperatureUseCase
	mux     *http.ServeMux
}

// NewHTTPHandler створює та налаштовує новий HTTP драйвуючий адаптер.
func NewHTTPHandler(useCase TemperatureUseCase) *HTTPHandler {
	h := &HTTPHandler{
		useCase: useCase,
		mux:     http.NewServeMux(),
	}
	h.registerRoutes()
	return h
}

// registerRoutes реєструє ендпоінти адаптера в мультиплексорі.
func (h *HTTPHandler) registerRoutes() {
	h.mux.HandleFunc("/api/v1/zones/", h.handleChangeTemperature)
}

// ServeHTTP делегує обробку внутрішньому маршрутизатору, реалізуючи http.Handler.
func (h *HTTPHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	h.mux.ServeHTTP(w, r)
}

// handleChangeTemperature обробляє запит зміни температури конкретної зони.
// Очікує запит: POST /api/v1/zones/{zoneID}/temperature
func (h *HTTPHandler) handleChangeTemperature(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		h.writeProblem(w, r, http.StatusMethodNotAllowed, "Method Not Allowed", "Дозволено лише метод POST", "")
		return
	}

	// Вилучення ідентифікатора зони з URL шляху
	path := strings.TrimPrefix(r.URL.Path, "/api/v1/zones/")
	parts := strings.Split(path, "/")
	if len(parts) < 2 || parts[1] != "temperature" || parts[0] == "" {
		h.writeProblem(w, r, http.StatusNotFound, "Endpoint Not Found", "Очікується шлях /api/v1/zones/{zone_id}/temperature", "")
		return
	}
	zoneID := parts[0]

	// Вилучення метаданих трасування із заголовків
	traceID := r.Header.Get("X-Trace-ID")
	if traceID == "" {
		traceID = fmt.Sprintf("http-trace-%d", time.Now().UnixNano())
	}
	subjectID := r.Header.Get("X-User-ID")
	if subjectID == "" {
		subjectID = "anonymous-web-user"
	}

	callCtx := CallContext{
		SubjectID: subjectID,
		TraceID:   traceID,
		Timestamp: time.Now(),
	}

	// Десеріалізація JSON корисного навантаження
	var reqPayload httpChangeTempRequest
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&reqPayload); err != nil {
		h.writeProblem(w, r, http.StatusBadRequest, "Invalid JSON", fmt.Sprintf("Помилка декодування тіла JSON: %v", err), traceID)
		return
	}

	if reqPayload.TargetTemperature == nil {
		h.writeProblem(w, r, http.StatusBadRequest, "Missing Field", "Обов'язкове поле 'target_temperature' відсутнє", traceID)
		return
	}

	idempotencyKey := reqPayload.IdempotencyKey
	if idempotencyKey == "" {
		idempotencyKey = r.Header.Get("Idempotency-Key")
	}
	if idempotencyKey == "" {
		idempotencyKey = fmt.Sprintf("auto-http-%s-%d", zoneID, time.Now().UnixNano())
	}

	// Формування чистої команди прикладного ядра
	cmd := ChangeTemperatureCommand{
		ZoneID:            zoneID,
		TargetTemperature: *reqPayload.TargetTemperature,
		IdempotencyKey:    idempotencyKey,
	}

	// Виклик вхідного порту
	result, err := h.useCase.Execute(callCtx, cmd)
	if err != nil {
		h.mapDomainErrorToHTTP(w, r, err, traceID)
		return
	}

	// Успішна відповідь 200 OK
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	_ = json.NewEncoder(w).Encode(httpSuccessResponse{
		ZoneID:              result.ZoneID,
		PreviousTemperature: result.PreviousTemperature,
		CurrentTemperature:  result.CurrentTemperature,
		UpdatedAt:           result.UpdatedAt,
	})
}

// mapDomainErrorToHTTP транслює типізовані доменні помилки у статуси HTTP та структуру RFC 7807.
func (h *HTTPHandler) mapDomainErrorToHTTP(w http.ResponseWriter, r *http.Request, err error, traceID string) {
	var domErr *DomainError
	if !errors.As(err, &domErr) {
		h.writeProblem(w, r, http.StatusInternalServerError, "Internal Server Error", "Непередбачена внутрішня помилка системи", traceID)
		return
	}

	var status int
	var title string

	switch domErr.Code {
	case ErrCodeZoneNotFound:
		status = http.StatusNotFound // 404
		title = "Зону клімат-контролю не знайдено"
	case ErrCodeZoneLocked:
		status = http.StatusLocked // 423 Locked
		title = "Зону заблоковано системою безпеки"
	case ErrCodeTemperatureOutOfRange:
		status = http.StatusUnprocessableEntity // 422 Unprocessable Entity
		title = "Температура виходить за допустимі межі"
	case ErrCodeStepTooLarge:
		status = http.StatusUnprocessableEntity // 422 Unprocessable Entity
		title = "Перевищено максимальний крок зміни"
	case ErrCodeInvalidInput:
		status = http.StatusBadRequest // 400 Bad Request
		title = "Некоректні вхідні дані"
	default:
		status = http.StatusInternalServerError
		title = "Внутрішня помилка предметної області"
	}

	problem := ProblemDetails{
		Type:     fmt.Sprintf("https://example.com/probs/%s", strings.ToLower(string(domErr.Code))),
		Title:    title,
		Status:   status,
		Detail:   domErr.Message,
		Instance: r.URL.Path,
		Code:     string(domErr.Code),
		TraceID:  traceID,
	}

	w.Header().Set("Content-Type", "application/problem+json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(problem)
}

// writeProblem записує протокольну помилку у форматі RFC 7807.
func (h *HTTPHandler) writeProblem(w http.ResponseWriter, r *http.Request, status int, title, detail, traceID string) {
	problem := ProblemDetails{
		Type:     "https://example.com/probs/http-error",
		Title:    title,
		Status:   status,
		Detail:   detail,
		Instance: r.URL.Path,
		TraceID:  traceID,
	}
	w.Header().Set("Content-Type", "application/problem+json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(problem)
}
