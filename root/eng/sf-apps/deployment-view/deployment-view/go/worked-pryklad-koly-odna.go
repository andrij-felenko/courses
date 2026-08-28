package deploy

// Container — логічний контейнер зі статичної моделі, те, що на статиці одна «коробка».
type Container struct {
	Name string // "api" або "db" — назва з логічної моделі
}

// Deployment — вузол розгортання, місце, де крутяться копії (сервер / VM / контейнер).
type Deployment struct {
	Node     string     // напр. "eu-node-1"
	Of       *Container // ЯКИЙ логічний контейнер тут живе
	Replicas uint8      // СКІЛЬКИ копій — ось чого немає на статиці
}

// TotalReplicas — скільки всього копій цього контейнера піднято в цьому середовищі.
func TotalReplicas(deps []Deployment, name string) uint16 {
	var sum uint16
	for _, d := range deps {
		if d.Of.Name == name { // той самий логічний контейнер...
			sum += uint16(d.Replicas) // ...сумуємо копії по всіх вузлах
		}
	}
	return sum
}
