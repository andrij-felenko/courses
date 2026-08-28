// пошук найближчого й другого праворуч + проба відношення.
// повертає індекс прийнятого збігу або −1, якщо неоднозначно.
int match_ratio(const float *query, const float train[][128], int m, float ratio) {
    float best = 1e30f, second = 1e30f;
    int best_j = -1;
    for (int j = 0; j < m; ++j) {
        float d = l2_sq(query, train[j], 128);        // працюємо у квадраті
        if (d < best)      { second = best; best = d; best_j = j; }
        else if (d < second) { second = d; }
    }
    // порівнюємо у КВАДРАТІ: (d₁/d₂ < r) ⇔ (d₁² < r²·d₂²)
    if (second > 0.0f && best < ratio * ratio * second)
        return best_j;      // відрив достатній — прийняти
    return -1;              // майже нічия — відкинути
}
