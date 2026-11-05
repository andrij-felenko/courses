import java.util.concurrent.atomic.LongAdder;

public class MetricsBuffer {
    private final LongAdder requestCounter = new LongAdder();

    public void recordRequest() {
        // Оновлення відбувається локально в комірці потоку без загального CAS-замка
        requestCounter.increment();
    }

    public long getTotalRequests() {
        // Підсумовування значень усіх комірок
        return requestCounter.sum();
    }
}
