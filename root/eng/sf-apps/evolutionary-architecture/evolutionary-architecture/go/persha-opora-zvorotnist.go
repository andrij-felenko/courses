// БЕЗ ШВА: конкретна черга протекла в бізнес-логіку
package orders

import (
	"context"

	"github.com/segmentio/kafka-go" // тип Kafka просочився сюди
)

func PublishOrder(ctx context.Context, w *kafka.Writer, o Order) error {
	payload := serialize(o)
	// прибито до Kafka: конкретний Writer у сигнатурі, kafka.Message у тілі
	return w.WriteMessages(ctx, kafka.Message{Value: payload})
}
