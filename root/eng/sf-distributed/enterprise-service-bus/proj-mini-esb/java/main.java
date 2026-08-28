// Приклад декларативного опису маршруту в Apache Camel
from("kafka:incoming_orders")
    .routeId("order-mediation-pipeline")
    .process(new AuthTokenValidator())
    .idempotentConsumer(header("Message-ID"), redisIdempotentRepository)
    .choice()
        .when(header("X-Message-Type").isEqualTo("ORDER_PAYMENT"))
            .process(new JsonOrderTransformer())
            .to("http://billing-service.internal/v1/charge")
        .when(header("X-Message-Type").isEqualTo("INVENTORY_SYNC"))
            .to("amqp:queue:warehouse_updates")
        .otherwise()
            .to("jms:queue:dead_letter_queue");
