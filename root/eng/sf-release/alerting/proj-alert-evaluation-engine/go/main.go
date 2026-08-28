package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sort"
	"time"
)

type AlertState int

const (
	StateInactive AlertState = iota
	StatePending
	StateFiring
	StateResolved
)

func (s AlertState) String() string {
	return [...]string{"INACTIVE", "PENDING", "FIRING", "RESOLVED"}[s]
}

type AlertRule struct {
	Name            string
	Labels          map[string]string
	ForDuration     time.Duration
	State           AlertState
	StateChangeTime time.Time
	Fingerprint     string
}

func NewAlertRule(name string, labels map[string]string, forDuration time.Duration) *AlertRule {
	labels["alertname"] = name
	rule := &AlertRule{
		Name:        name,
		Labels:      labels,
		ForDuration: forDuration,
		State:       StateInactive,
	}
	rule.Fingerprint = rule.computeFingerprint()
	return rule
}

func (r *AlertRule) computeFingerprint() string {
	keys := make([]string, 0, len(r.Labels))
	for k := range r.Labels {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	h := sha256.New()
	for _, k := range keys {
		h.Write([]byte(k + ":" + r.Labels[k] + ";"))
	}
	return hex.EncodeToString(h.Sum(nil))[:16]
}

func (r *AlertRule) Evaluate(conditionMet bool, now time.Time, notify func(r *AlertRule, reason string)) {
	switch r.State {
	case StateInactive:
		if conditionMet {
			if r.ForDuration == 0 {
				r.State = StateFiring
				r.StateChangeTime = now
				notify(r, "Triggered immediately")
			} else {
				r.State = StatePending
				r.StateChangeTime = now
			}
		}
	case StatePending:
		if !conditionMet {
			r.State = StateInactive
			r.StateChangeTime = now
		} else if now.Sub(r.StateChangeTime) >= r.ForDuration {
			r.State = StateFiring
			r.StateChangeTime = now
			notify(r, "Sustained across for-duration")
		}
	case StateFiring:
		if !conditionMet {
			r.State = StateResolved
			r.StateChangeTime = now
			notify(r, "Normalized")
			r.State = StateInactive
		}
	case StateResolved:
		if conditionMet {
			r.State = StatePending
		} else {
			r.State = StateInactive
		}
		r.StateChangeTime = now
	}
}

func main() {
	rule := NewAlertRule("HighCPU", map[string]string{"host": "prod-app-01"}, 2*time.Second)
	now := time.Now()

	notify := func(r *AlertRule, reason string) {
		fmt.Printf("[DISPATCH] Alert: %s | State: %s | Fingerprint: %s | Reason: %s\n",
			r.Name, r.State, r.Fingerprint, reason)
	}

	fmt.Println("--- Step 1: Condition Met (Pending) ---")
	rule.Evaluate(true, now, notify)

	fmt.Println("\n--- Step 2: Time elapsed (Firing) ---")
	rule.Evaluate(true, now.Add(3*time.Second), notify)

	fmt.Println("\n--- Step 3: Condition cleared (Resolved) ---")
	rule.Evaluate(false, now.Add(5*time.Second), notify)
}
