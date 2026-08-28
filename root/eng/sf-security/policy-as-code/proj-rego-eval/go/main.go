package main

import (
	"context"
	"fmt"
	"log"

	"github.com/open-policy-agent/opa/rego"
)

type UserContext struct {
	User string `json:"user"`
	Role string `json:"role"`
	MFA  bool   `json:"mfa"`
}

type RequestContext struct {
	Method string      `json:"method"`
	Path   string      `json:"path"`
	User   UserContext `json:"user"`
}

func checkAuthorization(ctx context.Context, req RequestContext) (bool, error) {
	// Попередня підготовка та компіляція AST запиту
	query, err := rego.New(
		rego.Query("data.authz.allow"),
		rego.Module("authz.rego", `
			package authz
			import future.keywords.if
			default allow := false

			# Адміністратор з увімкненим MFA має повний доступ
			allow if {
				input.user.role == "admin"
				input.user.mfa == true
			}

			# Звичайний спостерігач має доступ лише на читання
			allow if {
				input.method == "GET"
				input.user.role == "viewer"
			}
		`),
	).PrepareForEval(ctx)
	if err != nil {
		return false, fmt.Errorf("помилка компіляції політики: %w", err)
	}

	// Виконання оцінки для конкретного входу (потокобезпечно)
	results, err := query.Eval(ctx, rego.EvalInput(req))
	if err != nil {
		return false, fmt.Errorf("помилка виконання запиту: %w", err)
	}

	if len(results) > 0 && len(results[0].Expressions) > 0 {
		if allowed, ok := results[0].Expressions[0].Value.(bool); ok {
			return allowed, nil
		}
	}

	return false, nil
}

func main() {
	ctx := context.Background()
	req := RequestContext{
		Method: "POST",
		Path:   "/api/v1/transfer",
		User: UserContext{
			User: "alice",
			Role: "admin",
			MFA:  true,
		},
	}

	allowed, err := checkAuthorization(ctx, req)
	if err != nil {
		log.Fatalf("Збій перевірки: %v", err)
	}

	if allowed {
		fmt.Println("Вердикт PDP: Доступ надано (200 OK)")
	} else {
		fmt.Println("Вердикт PDP: Доступ заборонено (403 Forbidden)")
	}
}
