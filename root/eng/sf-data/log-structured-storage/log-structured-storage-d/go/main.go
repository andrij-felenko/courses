package store

// Один запис журналу: короткий ключ + значення. У кінець дописуємо ТІЛЬКИ такі.
type Record struct {
	Key   string // ім'я налаштування, напр. "volume"
	Value int32  // його значення
}

const CAP = 256

var log []Record // сам журнал (тут — зріз; насправді був би Flash)

// ЗАПИС = завжди в кінець. Старі записи про той самий ключ НЕ чіпаємо.
func LogPut(key string, value int32) int {
	if len(log) >= CAP { // журнал повний → час ущільнювати
		return -1
	}
	if len(key) > 8 {
		key = key[:8]
	}
	log = append(log, Record{Key: key, Value: value}) // фронт зсунувся вперед
	return 0
}

// ЧИТАННЯ = знайти НАЙНОВІШИЙ запис із цим ключем: скануємо з КІНЦЯ назад.
func LogGet(key string) (int32, bool) {
	if len(key) > 8 {
		key = key[:8]
	}
	for i := len(log) - 1; i >= 0; i-- { // від останнього до першого
		if log[i].Key == key {
			return log[i].Value, true // перший знайдений з кінця — чинний
		}
	}
	return 0, false // ключа взагалі немає
}
