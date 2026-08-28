package queue

import (
    "context"
    "database/sql"
    "encoding/json"
    "log"
    "math"
    "math/rand"
    "time"
)

const claimSQL = `
UPDATE jobs SET run_at = now() + make_interval(secs => $2),
                attempts = attempts + 1, locked_by = $3
 WHERE id IN (SELECT id FROM jobs
               WHERE status = 'ready' AND run_at <= now()
                 AND attempts < max_attempts
               ORDER BY run_at, id LIMIT $1 FOR UPDATE SKIP LOCKED)
RETURNING id, kind, payload, attempts, max_attempts`

const lease = 60 * time.Second

type Job struct {
    ID          int64
    Kind        string
    Payload     json.RawMessage
    Attempts    int
    MaxAttempts int
}

type Handler func(context.Context, Job) error

// Run крутить одного виконавця, доки не скасують ctx.
func Run(ctx context.Context, db *sql.DB, me string, h Handler) error {
    for ctx.Err() == nil {
        jobs, err := claim(ctx, db, 1, me)
        if err != nil {
            return err
        }
        if len(jobs) == 0 { // черга порожня — почекати з розкидом
            idle := 500 + rand.Intn(500)
            select {
            case <-ctx.Done():
                return nil
            case <-time.After(time.Duration(idle) * time.Millisecond):
            }
            continue
        }
        for _, j := range jobs {
            runOne(ctx, db, me, h, j)
        }
    }
    return nil
}

func claim(ctx context.Context, db *sql.DB, n int, me string) ([]Job, error) {
    rows, err := db.QueryContext(ctx, claimSQL, n, lease.Seconds(), me)
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    var out []Job
    for rows.Next() {
        var j Job
        if err := rows.Scan(&j.ID, &j.Kind, &j.Payload, &j.Attempts, &j.MaxAttempts); err != nil {
            return nil, err
        }
        out = append(out, j)
    }
    return out, rows.Err()
}

func runOne(ctx context.Context, db *sql.DB, me string, h Handler, j Job) {
    // дедлайн задачі коротший за оренду — щоб не працювати після її кінця;
    // зупинка процесу не рве вже початої задачі, тому WithoutCancel
    jctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), lease-5*time.Second)
    defer cancel()

    // якщо закрити рядок не вдалося — задачу поверне оренда, тож просто пишемо в журнал
    closeRow := func(q string, args ...any) {
        if _, err := db.Exec(q, args...); err != nil {
            log.Printf("задача %d: рядок не закрито: %v", j.ID, err)
        }
    }

    switch err := h(jctx, j); {
    case err == nil:
        closeRow(`DELETE FROM jobs WHERE id = $1 AND locked_by = $2`, j.ID, me)
    case j.Attempts >= j.MaxAttempts:
        closeRow(`UPDATE jobs SET status = 'dead', last_error = $2, run_at = now()
                   WHERE id = $1 AND locked_by = $3`, j.ID, err.Error(), me)
    default:
        closeRow(`UPDATE jobs SET run_at = now() + make_interval(secs => $2), last_error = $3
                   WHERE id = $1 AND locked_by = $4`, j.ID, backoff(j.Attempts), err.Error(), me)
    }
}

// backoff повертає затримку в секундах: база·2^(спроба−1), зі стелею й розкидом.
func backoff(attempt int) float64 {
    const base, ceil = 5.0, 3600.0
    d := math.Min(ceil, base*math.Pow(2, float64(attempt-1)))
    return d/2 + rand.Float64()*d/2 // розкид: [d/2 .. d]
}
