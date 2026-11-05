public class AtomicEventCounter {
    private final AtomicLong counter = new AtomicLong(0);

    public void increment() {
        long current;
        long next;
        do {
            current = counter.get();
            next = current + 1;
        } while (!counter.compareAndSet(current, next));
    }

    public long getValue() {
        return counter.get();
    }
}
