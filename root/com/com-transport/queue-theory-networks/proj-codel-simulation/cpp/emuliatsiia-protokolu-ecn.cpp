// Псевдокод ECN у методі dequeue:
if (ok_to_drop) {
    if (candidate.is_ecn_capable()) {
        candidate.set_ce_mark(); // виставляємо біти Congestion Experienced
        total_ecn_marked_++;
        // пакет НЕ скидається, а передається отримувачу
        return candidate;
    } else {
        total_dropped_++;
        continue; // фізичне скидання для звичайного трафіку
    }
}
