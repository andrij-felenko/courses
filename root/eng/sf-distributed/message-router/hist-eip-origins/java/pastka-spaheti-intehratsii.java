// Жорстке зчеплення всередині відправника (антипатерн)
queueSession.createProducer("QUEUE_FRAUD_INSPECT").send(msg);
queueSession.createProducer("QUEUE_LEDGER_ACCOUNTING").send(msg);

if (customer.getCountry().equals("DE")) {
    queueSession.createProducer("QUEUE_SEPA_FRANKFURT").send(msg);
} else if (customer.getCountry().equals("US")) {
    queueSession.createProducer("QUEUE_FEDWIRE_NEWYORK").send(msg);
}

if (order.getTotalAmount() > 50000) {
    queueSession.createProducer("QUEUE_EXECUTIVE_AUDIT").send(msg);
}
