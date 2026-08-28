package main

import (
	"fmt"
	"sync"
	"time"
)

type SourceBranch int

const (
	BranchControl SourceBranch = iota
	BranchCandidate
)

type TransactionResult struct {
	CorrelationID string
	AccountID     string
	AmountCents   int64
	Currency      string
	StatusCode    string
	EmittedAt     time.Time
}

type DiffVerdict int

const (
	VerdictExactMatch DiffVerdict = iota
	VerdictSemanticMismatch
	VerdictMissingPartner
)

type DiffReport struct {
	CorrelationID  string
	Verdict        DiffVerdict
	Details        string
	ProcessingSkew time.Duration
}

func CompareTransactions(ctrl, cand TransactionResult) DiffReport {
	skew := cand.EmittedAt.Sub(ctrl.EmittedAt)
	if skew < 0 {
		skew = -skew
	}

	report := DiffReport{
		CorrelationID:  ctrl.CorrelationID,
		ProcessingSkew: skew,
	}

	if ctrl.AccountID != cand.AccountID {
		report.Verdict = VerdictSemanticMismatch
		report.Details = fmt.Sprintf("Account mismatch: %s != %s", ctrl.AccountID, cand.AccountID)
		return report
	}

	if ctrl.Currency != cand.Currency {
		report.Verdict = VerdictSemanticMismatch
		report.Details = fmt.Sprintf("Currency mismatch: %s != %s", ctrl.Currency, cand.Currency)
		return report
	}

	if ctrl.StatusCode != cand.StatusCode {
		report.Verdict = VerdictSemanticMismatch
		report.Details = fmt.Sprintf("Status mismatch: %s != %s", ctrl.StatusCode, cand.StatusCode)
		return report
	}

	if ctrl.AmountCents != cand.AmountCents {
		report.Verdict = VerdictSemanticMismatch
		report.Details = fmt.Sprintf("Amount mismatch: %d != %d", ctrl.AmountCents, cand.AmountCents)
		return report
	}

	report.Verdict = VerdictExactMatch
	report.Details = "OK"
	return report
}

type pendingSlot struct {
	control   *TransactionResult
	candidate *TransactionResult
	firstSeen time.Time
}

type SlidingReconciliationWindow struct {
	mu        sync.Mutex
	slots     map[string]*pendingSlot
	windowTTL time.Duration
}

func NewSlidingWindow(ttl time.Duration) *SlidingReconciliationWindow {
	return &SlidingReconciliationWindow{
		slots:     make(map[string]*pendingSlot),
		windowTTL: ttl,
	}
}

func (w *SlidingReconciliationWindow) Ingest(
	branch SourceBranch,
	res TransactionResult,
	onDiff func(DiffReport),
) {
	var readyCtrl, readyCand *TransactionResult
	cid := res.CorrelationID

	w.mu.Lock()
	slot, exists := w.slots[cid]
	if !exists {
		slot = &pendingSlot{firstSeen: time.Now()}
		w.slots[cid] = slot
	}

	if branch == BranchControl {
		slot.control = &res
	} else {
		slot.candidate = &res
	}

	if slot.control != nil && slot.candidate != nil {
		readyCtrl = slot.control
		readyCand = slot.candidate
		delete(w.slots, cid)
	}
	w.mu.Unlock()

	// Звірка без утримання м'ютекса
	if readyCtrl != nil && readyCand != nil {
		report := CompareTransactions(*readyCtrl, *readyCand)
		onDiff(report)
	}
}

func (w *SlidingReconciliationWindow) SweepExpired(
	onTimeout func(cid string, missing SourceBranch),
) {
	now := time.Now()
	var timedOut []struct {
		cid     string
		missing SourceBranch
	}

	w.mu.Lock()
	for cid, slot := range w.slots {
		if now.Sub(slot.firstSeen) > w.windowTTL {
			missing := BranchCandidate
			if slot.candidate != nil && slot.control == nil {
				missing = BranchControl
			}
			timedOut = append(timedOut, struct {
				cid     string
				missing SourceBranch
			}{cid, missing})
			delete(w.slots, cid)
		}
	}
	w.mu.Unlock()

	for _, item := range timedOut {
		onTimeout(item.cid, item.missing)
	}
}
