// Свій порт: рівно потреба системи, у власних поняттях.
// Жодного типу постачальника тут немає — саме тому це шов, а не
// переодягнений SDK.
type ObjectStore interface {
	// Покласти байти під ключем. Повертає *StoreError при збої (див. нижче).
	Put(key string, bytes []byte) error

	// Дістати байти. found == false означає «такого ключа немає»
	// (це НЕ помилка); ненульовий err — саме збій доступу.
	Get(key string) (bytes []byte, found bool, err error)

	// Перелічити ключі, що починаються з префікса.
	List(prefix string) ([]string, error)
}
