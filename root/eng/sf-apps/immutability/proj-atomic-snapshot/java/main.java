import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.atomic.AtomicReference;

public final class RoutingTable {
    // ЄДИНА мінлива комірка: посилання на НЕЗМІННИЙ знімок
    private final AtomicReference<Map<String, String>> ref =
        new AtomicReference<>(Map.of());          // Map.of() — незмінна порожня мапа

    // ЧИТАЧ: миттєвий незмінний знімок, без замка
    public String route(String prefix) {
        return ref.get().get(prefix);             // get() — один атомарний load, далі читаємо застиглу мапу
    }

    // ПИСАР: копіюй-зміни-CAS; при збігу — повтор із новим знімком
    public void put(String prefix, String nextHop) {
        Map<String, String> prev, next;
        do {
            prev = ref.get();                     // знімок, з якого будуємо
            var draft = new HashMap<>(prev);      // мутабельна копія-чернетка
            draft.put(prefix, nextHop);
            next = Map.copyOf(draft);             // заморозити → новий незмінний знімок
        } while (!ref.compareAndSet(prev, next)); // збіг (хтось устиг) → ще коло
    }
}
