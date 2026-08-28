// Радар як дані: кожен блип — назва, кільце, квадрант.
// Найпростіша форма — таблиця, яку легко тримати поряд із кодом.
package radar

type Ring int

const (
	ADOPT Ring = iota
	TRIAL
	ASSESS
	HOLD
)

// напр. ідентифікатор бібліотеки/пакета -> кільце, куди команда його поклала
var RADAR = map[string]Ring{
	"grpc":         ADOPT,
	"kafka":        ADOPT,
	"postgres":     ADOPT,
	"rabbitmq":     TRIAL,
	"mongo":        ASSESS,
	"soap-legacy":  HOLD, // від цього відходимо
	"custom-queue": HOLD, // самописна черга — більше нового не заводимо
}

// Знайти кільце технології за назвою; (_, false), якщо її на радарі нема взагалі.
func ringOf(dep string) (Ring, bool) {
	r, ok := RADAR[dep] // не на радарі — окремий випадок, теж вартий уваги
	return r, ok
}
