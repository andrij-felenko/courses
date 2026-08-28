// БУЛО: фабрика повертала локальну реалізацію
public final class WarehouseFactory {
    public static Warehouse local(StockTable stock) {
        return new WarehouseServiceImpl(stock);
    }
}

// СТАЛО: та сама фабрика повертає клієнт до сервісу.
// Тип Warehouse не змінився — виклики orders лишаються дослівно ті самі.
public final class WarehouseHttpClient implements Warehouse {
    private final HttpClient http;
    private final URI base;

    public WarehouseHttpClient(HttpClient http, URI base) {
        this.http = http; this.base = base;
    }

    @Override public Reservation reserve(OrderId id, int qty) {
        HttpRequest req = HttpRequest.newBuilder()
            .uri(base.resolve("/reserve"))
            .POST(bodyOf(id, qty))
            .build();
        try {
            HttpResponse<String> res = http.send(req, ofString());
            if (res.statusCode() != 200)                   // ← НОВЕ: мережа падає
                throw new WarehouseUnavailable(res.statusCode());
            return parse(res.body());
        } catch (IOException | InterruptedException e) {
            throw new WarehouseUnavailable(e);             // таймаут, обрив
        }
    }
}
