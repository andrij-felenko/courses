package boundarybench

// DirectValidator реалізує прямий виклик функції в межах поточного стеку.
// Компілятор Go за наявності можливості оптимізує цей виклик через inlining.
type DirectValidator struct{}

func (DirectValidator) Validate(order *Order) (ValidationResponse, error) {
	return ValidateOrder(order)
}

// InterfaceValidator огортає виклик через інтерфейсний тип OrderValidator.
// Це змушує компілятор застосовувати динамічну диспетчеризацію (itable lookup),
// що вимикає пряме вбудовування тіла функції.
type InterfaceValidator struct {
	inner OrderValidator
}

// NewInterfaceValidator створює екземпляр з інтерфейсним посиланням.
func NewInterfaceValidator(inner OrderValidator) *InterfaceValidator {
	return &InterfaceValidator{inner: inner}
}

func (iv *InterfaceValidator) Validate(order *Order) (ValidationResponse, error) {
	return iv.inner.Validate(order)
}

// channelJob інкапсулює замовлення та канал для передачі результату з горутини-воркера.
type channelJob struct {
	order *Order
	reply chan ValidationResponse
}

// ChannelValidator демонструє межу конкурентності: синхронізацію між горутинами
// через Go-канал із перемиканням контексту планувальника (Go scheduler overhead).
type ChannelValidator struct {
	jobs chan channelJob
	quit chan struct{}
}

// NewChannelValidator ініціалізує чергу та запускає окрему горутину-обробник.
func NewChannelValidator(bufferSize int) *ChannelValidator {
	cv := &ChannelValidator{
		jobs: make(chan channelJob, bufferSize),
		quit: make(chan struct{}),
	}

	go func() {
		for {
			select {
			case job := <-cv.jobs:
				resp, _ := ValidateOrder(job.order)
				job.reply <- resp
			case <-cv.quit:
				return
			}
		}
	}()

	return cv
}

// Validate надсилає повідомлення у чергу каналу та блокується до повернення відповіді.
func (cv *ChannelValidator) Validate(order *Order) (ValidationResponse, error) {
	reply := make(chan ValidationResponse, 1)
	cv.jobs <- channelJob{order: order, reply: reply}
	return <-reply, nil
}

// Close коректно завершує роботу горутини-воркера.
func (cv *ChannelValidator) Close() {
	close(cv.quit)
}
