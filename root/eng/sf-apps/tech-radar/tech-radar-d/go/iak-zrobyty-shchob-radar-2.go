import (
	"fmt"
	"os"
)

// Фітнес-функція радара: новий код не сміє залежати від блипа в HOLD.
// Повертає кількість порушень (0 — складання проходить).
func checkNoHoldDeps(module string, deps []string) int {
	violations := 0
	for _, dep := range deps {
		r, ok := ringOf(dep)
		if ok && r == HOLD {
			fmt.Fprintf(os.Stderr,
				"[радар] %s тягне '%s' — це кільце HOLD, нового на цьому не заводимо\n",
				module, dep)
			violations++
		} else if !ok {
			// не заборона, а сигнал: технологія взагалі поза радаром —
			// її не оцінювали, тож варто винести на найближчий перегляд
			fmt.Fprintf(os.Stderr,
				"[радар] увага: %s тягне '%s', якого нема на радарі\n",
				module, dep)
		}
	}
	return violations
}
