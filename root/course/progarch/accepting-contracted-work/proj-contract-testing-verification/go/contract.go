package main

import (
	"encoding/json"
	"fmt"
	"os"
	"reflect"
)

// RequestExpectation описує очікувані споживачем параметри HTTP-запиту.
type RequestExpectation struct {
	Method  string            `json:"method"`
	Path    string            `json:"path"`
	Headers map[string]string `json:"headers,omitempty"`
	Body    any               `json:"body,omitempty"`
}

// ResponseExpectation фіксує обов'язкові вимоги до відповіді провайдера.
type ResponseExpectation struct {
	Status  int               `json:"status"`
	Headers map[string]string `json:"headers,omitempty"`
	Body    any               `json:"body,omitempty"`
}

// Interaction представляє одиничний тестовий сценарій взаємодії (кейс контракту).
type Interaction struct {
	Description   string              `json:"description"`
	ProviderState string              `json:"provider_state"`
	Request       RequestExpectation  `json:"request"`
	Response      ResponseExpectation `json:"response"`
}

// Contract — повна контрактна угода між замовником і підрядником із набором тестових взаємодій.
type Contract struct {
	Consumer     string        `json:"consumer"`
	Provider     string        `json:"provider"`
	Version      string        `json:"version"`
	Interactions []Interaction `json:"interactions"`
}

// NewContract ініціалізує новий об'єкт контракту.
func NewContract(consumer, provider, version string) *Contract {
	return &Contract{
		Consumer:     consumer,
		Provider:     provider,
		Version:      version,
		Interactions: make([]Interaction, 0),
	}
}

// AddInteraction додає зафіксовану взаємодію до специфікації контракту.
func (c *Contract) AddInteraction(interaction Interaction) {
	c.Interactions = append(c.Interactions, interaction)
}

// SaveToFile серіалізує специфікацію контракту у форматований JSON-файл на диску.
func (c *Contract) SaveToFile(filepath string) error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("помилка маршалінгу контракту в JSON: %w", err)
	}
	return os.WriteFile(filepath, data, 0644)
}

// LoadContractFromFile зчитує та десеріалізує специфікацію контракту з JSON-файлу.
func LoadContractFromFile(filepath string) (*Contract, error) {
	data, err := os.ReadFile(filepath)
	if err != nil {
		return nil, fmt.Errorf("не вдалося прочитати файл контракту %s: %w", filepath, err)
	}
	var contract Contract
	if err := json.Unmarshal(data, &contract); err != nil {
		return nil, fmt.Errorf("помилка парсингу JSON контракту: %w", err)
	}
	return &contract, nil
}

// NormalizeJSON перетворює довільну Go-структуру в канонічні типи JSON (map[string]any, []any, float64 тощо).
func NormalizeJSON(val any) (any, error) {
	if val == nil {
		return nil, nil
	}
	data, err := json.Marshal(val)
	if err != nil {
		return nil, err
	}
	var normalized any
	if err := json.Unmarshal(data, &normalized); err != nil {
		return nil, err
	}
	return normalized, nil
}

// MatchJSON виконує структурну валідацію за принципом толерантного читача (Tolerant Reader).
// Провайдер зобов'язаний надати всі очікувані споживачем поля відповідних типів.
// Додаткові поля, надіслані провайдером, ігноруються й не ламають сумісність.
func MatchJSON(expected, actual any, path string) []string {
	var diffs []string

	if expected == nil {
		return diffs
	}

	if actual == nil {
		return append(diffs, fmt.Sprintf("поле '%s': очікувалось значення, отримано null", path))
	}

	switch exp := expected.(type) {
	case map[string]any:
		actMap, ok := actual.(map[string]any)
		if !ok {
			return append(diffs, fmt.Sprintf("поле '%s': очікувався JSON-об'єкт, отримано %T", path, actual))
		}
		for key, expVal := range exp {
			fieldPath := key
			if path != "" {
				fieldPath = path + "." + key
			}
			actVal, exists := actMap[key]
			if !exists {
				diffs = append(diffs, fmt.Sprintf("поле '%s': обов'язкове поле відсутнє у відповіді провайдера", fieldPath))
				continue
			}
			diffs = append(diffs, MatchJSON(expVal, actVal, fieldPath)...)
		}

	case []any:
		actSlice, ok := actual.([]any)
		if !ok {
			return append(diffs, fmt.Sprintf("поле '%s': очікувався масив, отримано %T", path, actual))
		}
		if len(exp) > len(actSlice) {
			diffs = append(diffs, fmt.Sprintf("поле '%s': очікувалось щонайменше %d елементів, отримано %d", path, len(exp), len(actSlice)))
		}
		for i := 0; i < len(exp) && i < len(actSlice); i++ {
			elemPath := fmt.Sprintf("%s[%d]", path, i)
			diffs = append(diffs, MatchJSON(exp[i], actSlice[i], elemPath)...)
		}

	case float64:
		actNum, ok := actual.(float64)
		if !ok {
			return append(diffs, fmt.Sprintf("поле '%s': очікувалось число, отримано %T", path, actual))
		}
		if exp != actNum {
			diffs = append(diffs, fmt.Sprintf("поле '%s': очікувалось значення %.2f, отримано %.2f", path, exp, actNum))
		}

	case string:
		actStr, ok := actual.(string)
		if !ok {
			return append(diffs, fmt.Sprintf("поле '%s': очікувався рядок, отримано %T", path, actual))
		}
		if exp != actStr {
			diffs = append(diffs, fmt.Sprintf("поле '%s': очікувався рядок %q, отримано %q", path, exp, actStr))
		}

	case bool:
		actBool, ok := actual.(bool)
		if !ok {
			return append(diffs, fmt.Sprintf("поле '%s': очікувалось булеве значення, отримано %T", path, actual))
		}
		if exp != actBool {
			diffs = append(diffs, fmt.Sprintf("поле '%s': очікувалось %v, отримано %v", path, exp, actBool))
		}

	default:
		if !reflect.DeepEqual(expected, actual) {
			diffs = append(diffs, fmt.Sprintf("поле '%s': значення не збігаються (%v != %v)", path, expected, actual))
		}
	}

	return diffs
}
