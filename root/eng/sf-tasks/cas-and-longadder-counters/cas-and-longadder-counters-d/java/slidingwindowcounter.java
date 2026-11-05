import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class SlidingWindowCounter {
    private final int windowSizeSeconds;
    private final Bucket[] buckets;

    private static class Bucket {
        final AtomicLong timestamp = new AtomicLong(-1);
        final LongAdder counter = new LongAdder();
    }

    public SlidingWindowCounter(int windowSizeSeconds) {
        this.windowSizeSeconds = windowSizeSeconds;
        this.buckets = new Bucket[windowSizeSeconds];
        for (int i = 0; i < windowSizeSeconds; i++) {
            buckets[i] = new Bucket();
        }
    }

    public void increment() {
        long nowSec = System.currentTimeMillis() / 1000;
        int index = (int) (nowSec % windowSizeSeconds);
        Bucket bucket = buckets[index];

        long bucketTime = bucket.timestamp.get();
        if (bucketTime != nowSec) {
            // Спроба оновити епоху кошика при настанні нової секунди
            if (bucket.timestamp.compareAndSet(bucketTime, nowSec)) {
                bucket.counter.reset();
            }
        }
        bucket.counter.increment();
    }

    public long getSum() {
        long nowSec = System.currentTimeMillis() / 1000;
        long totalSum = 0;

        for (Bucket bucket : buckets) {
            long bucketTime = bucket.timestamp.get();
            // Враховуються лише кошики, що входять у поточне часове вікно
            if (nowSec - bucketTime < windowSizeSeconds && bucketTime > 0) {
                totalSum += bucket.counter.sum();
            }
        }
        return totalSum;
    }
}
