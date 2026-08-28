// Go: CI Pull Request Ownership & Contract Gate
package main

import (
	"fmt"
	"strings"
)

type OwnershipMode string

const (
	ModeStrong      OwnershipMode = "STRONG"
	ModeInnerSource OwnershipMode = "INNER_SOURCE"
)

type Rule struct {
	Prefix     string
	OwnerGroup string
	Mode       OwnershipMode
}

var Rules = []Rule{
	{Prefix: "src/core/security/", OwnerGroup: "sec-team", Mode: ModeStrong},
	{Prefix: "src/services/telemetry/", OwnerGroup: "platform-team", Mode: ModeInnerSource},
	{Prefix: "api/contracts/", OwnerGroup: "arch-board", Mode: ModeStrong},
}

type PRValidationResult struct {
	Approved bool
	Reason   string
}

func ValidatePullRequest(changedFiles []string, authorTeams []string, isContractValidated bool) PRValidationResult {
	hasTeam := func(team string) bool {
		for _, t := range authorTeams {
			if t == team {
				return true
			}
		}
		return false
	}

	for _, file := range changedFiles {
		for _, rule := range Rules {
			if strings.HasPrefix(file, rule.Prefix) {
				isOwner := hasTeam(rule.OwnerGroup)
				if !isOwner {
					if rule.Mode == ModeStrong {
						return PRValidationResult{
							Approved: false,
							Reason:   fmt.Sprintf("Файл %s захищено режимом STRONG. Потрібне ревю від %s.", file, rule.OwnerGroup),
						}
					}
					if rule.Mode == ModeInnerSource && !isContractValidated {
						return PRValidationResult{
							Approved: false,
							Reason:   fmt.Sprintf("Файл %s змінено сторонньою командою без підтвердження контракту.", file),
						}
					}
				}
			}
		}
	}

	return PRValidationResult{Approved: true, Reason: "Зміни автоматично валідовано."}
}
