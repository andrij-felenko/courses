// ? extends T — коваріантно: з такого можна лише ЧИТАТИ T (продюсер)
void printAll(List<? extends Number> src) {
    for (Number n : src) System.out.println(n);   // читати — можна
    // src.add(...) — заборонено компілятором: писати не можна
}

// ? super T — контраваріантно: у такий можна лише ПИСАТИ T (консюмер)
void fillWithInts(List<? super Integer> dst) {
    dst.add(42);          // писати Integer — можна
    // Number n = dst.get(0); — прийде лише Object: читати конкретне не можна
}
