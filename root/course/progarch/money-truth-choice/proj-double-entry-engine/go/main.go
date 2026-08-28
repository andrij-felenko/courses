package ledger

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"sort"
)

type Direction string

const (
	Debit  Direction = "DEBIT"
	Credit Direction = "CREDIT"
)

type EntryIntent struct {
	AccountID   int64
	Dir         Direction
	AmountCents int64
}

type TransactionRequest struct {
	IdempotencyKey string
	Description    string
	Entries        []EntryIntent
}

var (
	ErrUnbalanced    = errors.New("debit and credit sums do not match")
	ErrEmpty         = errors.New("entries cannot be empty")
	ErrInvalidAmount = errors.New("amount must be positive")
)

type Engine struct {
	db *sql.DB
}

func NewEngine(db *sql.DB) *Engine {
	return &Engine{db: db}
}

// ValidateBalance перевіряє інваріант ∑ Debit == ∑ Credit
func ValidateBalance(entries []EntryIntent) error {
	if len(entries) == 0 {
		return ErrEmpty
	}
	var totalDebit, totalCredit int64
	for _, e := range entries {
		if e.AmountCents <= 0 {
			return ErrInvalidAmount
		}
		if e.Dir == Debit {
			totalDebit += e.AmountCents
		} else if e.Dir == Credit {
			totalCredit += e.AmountCents
		}
	}
	if totalDebit == 0 || totalDebit != totalCredit {
		return ErrUnbalanced
	}
	return nil
}

// PostTransaction виконує атомарне проведення з впорядкованим блокуванням рахунків
func (e *Engine) PostTransaction(ctx context.Context, req TransactionRequest) (int64, error) {
	if err := ValidateBalance(req.Entries); err != nil {
		return 0, err
	}

	// Збираємо та сортуємо унікальні ID рахунків для запобігання deadlocks
	accountMap := make(map[int64]bool)
	for _, entry := range req.Entries {
		accountMap[entry.AccountID] = true
	}
	sortedIDs := make([]int64, 0, len(accountMap))
	for id := range accountMap {
		sortedIDs = append(sortedIDs, id)
	}
	sort.Slice(sortedIDs, func(i, j int) bool { return sortedIDs[i] < sortedIDs[j] })

	tx, err := e.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return 0, err
	}
	defer tx.Rollback()

	// Захоплюємо замки FOR UPDATE у визначеному порядку
	for _, accID := range sortedIDs {
		var dummy int64
		err := tx.QueryRowContext(ctx, "SELECT id FROM accounts WHERE id = $1 FOR UPDATE", accID).Scan(&dummy)
		if err != nil {
			return 0, fmt.Errorf("failed to lock account %d: %w", accID, err)
		}
	}

	// Реєстрація транзакції
	var txID int64
	err = tx.QueryRowContext(ctx,
		"INSERT INTO transactions (idempotency_key, description) VALUES ($1, $2) RETURNING id",
		req.IdempotencyKey, req.Description,
	).Scan(&txID)
	if err != nil {
		return 0, fmt.Errorf("failed to insert transaction: %w", err)
	}

	// Вставка проводжень
	stmt, err := tx.PrepareContext(ctx,
		"INSERT INTO ledger_entries (transaction_id, account_id, direction, amount_cents) VALUES ($1, $2, $3, $4)",
	)
	if err != nil {
		return 0, err
	}
	defer stmt.Close()

	for _, entry := range req.Entries {
		_, err = stmt.ExecContext(ctx, txID, entry.AccountID, entry.Dir, entry.AmountCents)
		if err != nil {
			return 0, fmt.Errorf("failed to insert ledger entry: %w", err)
		}
	}

	if err := tx.Commit(); err != nil {
		return 0, err
	}

	return txID, nil
}
