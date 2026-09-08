package main

import (
	"fmt"
	"os"
	"strings"
)

// createSampleContract створює еталонний контракт замовника BillingService до підрядника OrdersProvider.
func createSampleContract() *Contract {
	contract := NewContract("BillingService", "OrdersProvider", "1.0.0")

	// Сценарій 1: Створення замовлення
	contract.AddInteraction(Interaction{
		Description:   "Створення нового замовлення на послугу",
		ProviderState: "сховище замовлень готове до запису",
		Request: RequestExpectation{
			Method: "POST",
			Path:   "/orders",
			Headers: map[string]string{
				"Content-Type": "application/json",
			},
			Body: map[string]any{
				"customer_name": "ТОВ Рога і Копита",
				"amount":        1500.50,
				"currency":      "UAH",
			},
		},
		Response: ResponseExpectation{
			Status: 201,
			Headers: map[string]string{
				"Content-Type": "application/json",
			},
			Body: map[string]any{
				"id":            "ord-101",
				"customer_name": "ТОВ Рога і Копита",
				"amount":        1500.50,
				"currency":      "UAH",
				"status":        "PENDING",
			},
		},
	})

	// Сценарій 2: Отримання деталей замовлення
	contract.AddInteraction(Interaction{
		Description:   "Отримання деталей замовлення за ідентифікатором ord-101",
		ProviderState: "замовлення ord-101 існує в системі підрядника",
		Request: RequestExpectation{
			Method: "GET",
			Path:   "/orders/ord-101",
		},
		Response: ResponseExpectation{
			Status: 200,
			Headers: map[string]string{
				"Content-Type": "application/json",
			},
			Body: map[string]any{
				"id":            "ord-101",
				"customer_name": "ТОВ Рога і Копита",
				"amount":        1500.50,
				"currency":      "UAH",
				"status":        "PENDING",
			},
		},
	})

	return contract
}

// printReport виводить відформатований звіт про верифікацію контракту в консоль CI/CD.
func printReport(report *VerificationReport) {
	divider := strings.Repeat("─", 70)
	fmt.Println(divider)
	fmt.Printf("Контракт: %s -> %s (версія: %s)\n", report.Consumer, report.Provider, report.Version)
	fmt.Printf("Всього взаємодій: %d | Успішно: %d | Помилок: %d\n", report.Total, report.Passed, report.Failed)
	fmt.Println(divider)

	for idx, res := range report.Results {
		statusSign := "[+] УСПІХ"
		if !res.Success {
			statusSign = "[x] ВІДХИЛЕНО"
		}
		fmt.Printf("  %d. %s: %s\n", idx+1, statusSign, res.Description)
		fmt.Printf("     Передумова (State): %s\n", res.ProviderState)
		if !res.Success {
			for _, errStr := range res.Errors {
				fmt.Printf("     ! Порушення: %s\n", errStr)
			}
		}
	}
	fmt.Println(divider)
}

func main() {
	banner := strings.Repeat("═", 70)
	fmt.Println(banner)
	fmt.Println("  АВТОМАТИЗОВАНЕ ПРИЙМАННЯ ЗАМОВЛЕНОГО КОДУ (CDCT QUALITY GATE)")
	fmt.Println("  Контроль якості та сумісності API підрядника з вимогами замовника")
	fmt.Println(banner)

	contractFile := "order_contract.json"
	var contract *Contract

	// 1. Отримання контракту (зі згенерованого тестами файлу або еталонного)
	if _, err := os.Stat(contractFile); err == nil {
		loaded, err := LoadContractFromFile(contractFile)
		if err == nil {
			contract = loaded
			fmt.Printf("\n[КРОК 1] Завантажено узгоджений контракт замовника з файлу: %s\n", contractFile)
		}
	}

	if contract == nil {
		contract = createSampleContract()
		_ = contract.SaveToFile(contractFile)
		fmt.Printf("\n[КРОК 1] Сформовано та експортовано контракт споживача: %s\n", contractFile)
	}

	fmt.Printf("         Споживач (Замовник): %s\n", contract.Consumer)
	fmt.Printf("         Провайдер (Підрядник): %s\n", contract.Provider)
	fmt.Printf("         Кількість зафіксованих взаємодій: %d\n", len(contract.Interactions))

	// 2. ДЕМОНСТРАЦІЯ 1: Приймання дефектної версії сервісу підрядника
	fmt.Println("\n[КРОК 2] Приймальне тестування версії підрядника v1.1-defective...")
	brokenProvider := NewBrokenProviderServer()
	verifierBroken := NewProviderVerifier(brokenProvider)

	// Реєстрація хендлерів стану для налаштування тестових даних
	verifierBroken.RegisterStateHandler("сховище замовлень готове до запису", func() error {
		return brokenProvider.SetupState("сховище замовлень готове до запису")
	})
	verifierBroken.RegisterStateHandler("замовлення ord-101 існує в системі підрядника", func() error {
		return brokenProvider.SetupState("замовлення ord-101 існує в системі підрядника")
	})

	reportBroken := verifierBroken.VerifyContract(contract)
	printReport(reportBroken)

	if reportBroken.Failed > 0 {
		fmt.Println("  ВЕРДИКТ CI QUALITY GATE: ЗБІРКУ ЗАБЛОКОВАНО!")
		fmt.Println("  Причина: код підрядника містить несумісні зміни схеми відповідей (зміна назви поля,")
		fmt.Println("  пропущений статус). Акт приймання робіт відхилено до усунення дефектів.")
	}

	// 3. ДЕМОНСТРАЦІЯ 2: Приймання виправленої та сумісної версії підрядника
	fmt.Println("\n[КРОК 3] Повторне приймальне тестування виправленої версії підрядника v1.2-compliant...")
	compliantProvider := NewProviderServer()
	verifierCompliant := NewProviderVerifier(compliantProvider)

	verifierCompliant.RegisterStateHandler("сховище замовлень готове до запису", func() error {
		return compliantProvider.SetupState("сховище замовлень готове до запису")
	})
	verifierCompliant.RegisterStateHandler("замовлення ord-101 існує в системі підрядника", func() error {
		return compliantProvider.SetupState("замовлення ord-101 існує в системі підрядника")
	})

	reportCompliant := verifierCompliant.VerifyContract(contract)
	printReport(reportCompliant)

	if reportCompliant.Failed == 0 {
		fmt.Println("  ВЕРДИКТ CI QUALITY GATE: РОБОТУ ПІДРЯДНИКА УСПІШНО ПРИЙНЯТО!")
		fmt.Println("  Всі вимоги контракту замовника задоволено. Реліз допущено до автоматичного")
		fmt.Println("  розгортання в продуктивне середовище без ризику інтеграційних аварій.")
	}

	fmt.Println("\n" + banner)
	fmt.Println("  Демонстрацію конвеєра приймання чужого коду завершено.")
	fmt.Println(banner)
}
