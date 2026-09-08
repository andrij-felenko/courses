package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
)

// StateSetupHandler описує функцію підготовки стану сервера перед перевіркою взаємодії.
type StateSetupHandler func() error

// InteractionResult містить детальний результат перевірки одиничного сценарію контракту.
type InteractionResult struct {
	Description   string
	ProviderState string
	Success       bool
	Errors        []string
}

// VerificationReport акумулює результати перевірки всіх взаємодій контракту.
type VerificationReport struct {
	Consumer string
	Provider string
	Version  string
	Total    int
	Passed   int
	Failed   int
	Results  []InteractionResult
}

// ProviderVerifier автоматизує перевірку реалізації сервісу підрядника на відповідність контракту замовника.
type ProviderVerifier struct {
	handler       http.Handler
	stateHandlers map[string]StateSetupHandler
}

// NewProviderVerifier ініціалізує новий рушій верифікації для заданого HTTP-обробника.
func NewProviderVerifier(handler http.Handler) *ProviderVerifier {
	return &ProviderVerifier{
		handler:       handler,
		stateHandlers: make(map[string]StateSetupHandler),
	}
}

// RegisterStateHandler прив'язує функцію підготовки стану до його назви у контракті.
func (v *ProviderVerifier) RegisterStateHandler(state string, handler StateSetupHandler) {
	v.stateHandlers[state] = handler
}

// VerifyContract проганяє всі взаємодії контракту проти реального HTTP-обробника через ResponseRecorder.
func (v *ProviderVerifier) VerifyContract(contract *Contract) *VerificationReport {
	report := &VerificationReport{
		Consumer: contract.Consumer,
		Provider: contract.Provider,
		Version:  contract.Version,
		Total:    len(contract.Interactions),
		Results:  make([]InteractionResult, 0, len(contract.Interactions)),
	}

	for _, interaction := range contract.Interactions {
		result := v.verifyInteraction(interaction)
		if result.Success {
			report.Passed++
		} else {
			report.Failed++
		}
		report.Results = append(report.Results, result)
	}

	return report
}

// verifyInteraction виконує перевірку одного конкретного пункту контракту.
func (v *ProviderVerifier) verifyInteraction(interaction Interaction) InteractionResult {
	result := InteractionResult{
		Description:   interaction.Description,
		ProviderState: interaction.ProviderState,
		Success:       true,
		Errors:        make([]string, 0),
	}

	// 1. Налаштування стану провайдера
	if interaction.ProviderState != "" {
		setupFn, found := v.stateHandlers[interaction.ProviderState]
		if !found {
			result.Success = false
			result.Errors = append(result.Errors, fmt.Sprintf("відсутній обробник стану: %q", interaction.ProviderState))
			return result
		}
		if err := setupFn(); err != nil {
			result.Success = false
			result.Errors = append(result.Errors, fmt.Sprintf("помилка ініціалізації стану %q: %v", interaction.ProviderState, err))
			return result
		}
	}

	// 2. Підготовка HTTP-запиту на основі специфікації контракту
	var reqBodyBytes []byte
	if interaction.Request.Body != nil {
		data, err := json.Marshal(interaction.Request.Body)
		if err != nil {
			result.Success = false
			result.Errors = append(result.Errors, fmt.Sprintf("не вдалося серіалізувати тіло запиту: %v", err))
			return result
		}
		reqBodyBytes = data
	}

	httpReq := httptest.NewRequest(interaction.Request.Method, interaction.Request.Path, bytes.NewReader(reqBodyBytes))
	for hKey, hVal := range interaction.Request.Headers {
		httpReq.Header.Set(hKey, hVal)
	}

	// 3. Виконання запиту через тестовий рекордер без реального відкриття сокетів
	recorder := httptest.NewRecorder()
	v.handler.ServeHTTP(recorder, httpReq)

	// 4. Перевірка коду відповіді
	if recorder.Code != interaction.Response.Status {
		result.Success = false
		result.Errors = append(result.Errors, fmt.Sprintf("HTTP-статус: очікувалось %d, отримано %d", interaction.Response.Status, recorder.Code))
	}

	// 5. Перевірка обов'язкових HTTP-заголовків
	for expHKey, expHVal := range interaction.Response.Headers {
		actHVal := recorder.Header().Get(expHKey)
		if actHVal == "" {
			result.Success = false
			result.Errors = append(result.Errors, fmt.Sprintf("заголовок %q: відсутній у відповіді", expHKey))
		} else if !strings.Contains(strings.ToLower(actHVal), strings.ToLower(expHVal)) {
			result.Success = false
			result.Errors = append(result.Errors, fmt.Sprintf("заголовок %q: очікувалось %q, отримано %q", expHKey, expHVal, actHVal))
		}
	}

	// 6. Структурна валідація тіла відповіді (Tolerant Reader JSON matching)
	if interaction.Response.Body != nil {
		if recorder.Body.Len() == 0 {
			result.Success = false
			result.Errors = append(result.Errors, "тіло відповіді порожнє, хоча очікувалися дані")
		} else {
			var actualBody any
			if err := json.Unmarshal(recorder.Body.Bytes(), &actualBody); err != nil {
				result.Success = false
				result.Errors = append(result.Errors, fmt.Sprintf("відповідь не є валідним JSON: %v", err))
			} else {
				expectedNorm, _ := NormalizeJSON(interaction.Response.Body)
				diffs := MatchJSON(expectedNorm, actualBody, "")
				if len(diffs) > 0 {
					result.Success = false
					result.Errors = append(result.Errors, diffs...)
				}
			}
		}
	}

	return result
}
