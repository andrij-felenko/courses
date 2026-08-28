// fitness_checker.go — Статичний перевірник меж контекстів та зчеплення команд у Go
package main

import (
	"fmt"
	"os"
)

type DependencyEdge struct {
	SourceTeam       string
	SourceContext    string
	TargetContext    string
	ImportedSymbol   string
	IsPublicContract bool
}

type Violation struct {
	Team        string
	Description string
	Severity    string
}

type ArchitectureFitnessChecker struct {
	maxEfferentCoupling int
	dependencies        []DependencyEdge
}

func NewFitnessChecker(maxEfferent int) *ArchitectureFitnessChecker {
	return &ArchitectureFitnessChecker{
		maxEfferentCoupling: maxEfferent,
		dependencies:        make([]DependencyEdge, 0),
	}
}

func (c *ArchitectureFitnessChecker) AddDependency(edge DependencyEdge) {
	c.dependencies = append(c.dependencies, edge)
}

func (c *ArchitectureFitnessChecker) EvaluateRules() []Violation {
	var violations []Violation

	// Перевірка 1: Приватні імпорти
	for _, dep := range c.dependencies {
		if !dep.IsPublicContract && dep.SourceContext != dep.TargetContext {
			violations = append(violations, Violation{
				Team: dep.SourceTeam,
				Description: fmt.Sprintf("Порушення межі контексту: Команда '%s' в '%s' імпортує приватний '%s' з '%s'.",
					dep.SourceTeam, dep.SourceContext, dep.ImportedSymbol, dep.TargetContext),
				Severity: "CRITICAL",
			})
		}
	}

	// Перевірка 2: Еферентне зчеплення Ce
	outgoing := make(map[string]map[string]bool)
	for _, dep := range c.dependencies {
		if dep.SourceContext != dep.TargetContext {
			if _, exists := outgoing[dep.SourceContext]; !exists {
				outgoing[dep.SourceContext] = make(map[string]bool)
			}
			outgoing[dep.SourceContext][dep.TargetContext] = true
		}
	}

	for ctx, targets := range outgoing {
		if len(targets) > c.maxEfferentCoupling {
			violations = append(violations, Violation{
				Team: ctx + "_owner",
				Description: fmt.Sprintf("Перевищення когнітивного навантаження: Контекст '%s' залежить від %d контекстів (ліміт: %d).",
					ctx, len(targets), c.maxEfferentCoupling),
				Severity: "WARNING",
			})
		}
	}

	return violations
}

func main() {
	checker := NewFitnessChecker(2)

	checker.AddDependency(DependencyEdge{"PaymentsTeam", "BillingContext", "DeviceContext", "dh/devices/contract", true})
	checker.AddDependency(DependencyEdge{"PaymentsTeam", "BillingContext", "TelemetryContext", "dh/telemetry/internal/db", false})
	checker.AddDependency(DependencyEdge{"PaymentsTeam", "BillingContext", "AuthContext", "dh/auth/token", true})
	checker.AddDependency(DependencyEdge{"PaymentsTeam", "BillingContext", "NotificationContext", "dh/notify/alert", true})

	violations := checker.EvaluateRules()
	hasCritical := false

	fmt.Println("=== Результати запуску Architecture Fitness Gate (Go) ===")
	for _, v := range violations {
		fmt.Printf("[%s] Команда: %s\n    %s\n", v.Severity, v.Team, v.Description)
		if v.Severity == "CRITICAL" {
			hasCritical = true
		}
	}

	if hasCritical {
		fmt.Fprintln(os.Stderr, "\nCI/CD GATE FAILED: Виявлено критичні порушення соціотехнічних меж!")
		os.Exit(1)
	}
	fmt.Println("\nCI/CD GATE PASSED.")
}
