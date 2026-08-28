// Лаконічний DSL Apache Camel, що повторює EIP
from("kafka:orders.incoming")
    .routeId("OrderDispatchPipeline")
    .wireTap("direct:auditLog")
    .choice()
        .when(header("region").isEqualTo("EU"))
            .to("kafka:orders.eu.processing")
        .when(header("region").isEqualTo("US"))
            .to("kafka:orders.us.processing")
        .otherwise()
            .to("kafka:orders.unrouted.dlq")
    .end();
