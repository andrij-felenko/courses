long t0 = System.nanoTime();                     // довільний нуль
// ... робота ...
long elapsedNs = System.nanoTime() - t0;

long timeoutNs = TimeUnit.SECONDS.toNanos(30);
if (System.nanoTime() - t0 >= timeoutNs) {       // різниця, НЕ сума
    // вийшов час
}

Instant stamp = Instant.now();                   // момент за календарем
