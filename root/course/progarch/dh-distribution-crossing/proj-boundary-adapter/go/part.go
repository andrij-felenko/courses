// пакет boundary; import: context, errors, fmt, sync, sync/atomic, time,
//                          "math/rand/v2" (як rand), testing.
type Command struct {
	Key, Kind, Dev, Arg string // Key = ключ ідемпотентності, СТАЛИЙ крізь усі повтори
}
type Result struct{ OK bool; Note string }
type Report struct {
	Dev, Field, Value string
	TS                int64 // ВЛАСНА мітка часу відліку; строго зростає per (Dev,Field)
}

// Порт, що бачить логіка хаба (та сама форма, що в статті).
type CloudLink interface {
	Send(ctx context.Context, cmd Command) (Result, error) // команда: синхронно, «фактично раз»
	Emit(rep Report)                                        // звіт: у буфер, не чекаючи мережі
}

// Те, що фізично лягає в мережу. НЕнадійне: таймаут, обрив, тиша.
type Wire interface {
	PostCmd(ctx context.Context, cmd Command) (Result, error)
	PostReport(ctx context.Context, rep Report) error
	GetState(ctx context.Context, dev string) (string, error)
}

var ErrUnreachable = errors.New("хмара недосяжна") // єдине, що вільно повторювати
