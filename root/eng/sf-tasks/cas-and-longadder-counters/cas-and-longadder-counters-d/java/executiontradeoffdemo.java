import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class ExecutionTradeoffDemo {

    // AtomicLong: точний лімітер ресурсів (забігання наперед заборонено)
    public static class StrictRateLimiter {
        private final long maxCapacity;
        private final AtomicLong currentTokens;

        public StrictRateLimiter(long maxCapacity) {
            this.maxCapacity = maxCapacity;
            this.currentTokens = new AtomicLong(maxCapacity);
        }

        public boolean tryAcquire() {
            long current;
            do {
                current = currentTokens.get();
                if (current <= 0) {
                    return false; // Квоту вичерпано
                }
            } while (!currentTokens.compareAndSet(current, current - 1));
            return true;
        }
    }

    // LongAdder: високонавантажений лічильник оброблених запитів
    public static class HighThroughputMetric {
        private final LongAdder totalRequests = new LongAdder();

        public void markSuccess() {
            totalRequests.increment(); // O(1) запис без конкуренції
        }

        public long getSnapshot() {
            return totalRequests.sum(); // Підсумкова узгодженість для моніторингу
        }
    }
}
