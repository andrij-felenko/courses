void report(const fpv_system *s, float speed_kmh) {
    span_ms g = glass_to_glass(s);
    float period = frame_period_ms(s->fps);
    float load   = compute_load_ms(s);
    bool  fits   = fits_frame_deadline(s);
    float margin = reaction_margin_ms(g);

    printf("== %s (%d к/с) ==\n", s->name, s->fps);
    if (g.lo == g.hi)
        printf("  Скло-скло:     %.1f мс (стала)\n", g.lo);
    else
        printf("  Скло-скло:     %.1f-%.1f мс (змінна)\n", g.lo, g.hi);

    printf("  Наосліп @%.0f км/год: %.2f-%.2f м\n",
           speed_kmh,
           blind_distance_m(g.lo, speed_kmh),
           blind_distance_m(g.hi, speed_kmh));

    printf("  Кадровий період: %.2f мс, обробка: %.1f мс -> %s\n",
           period, load, fits ? "ВЛАЗИТЬ" : "НЕ ВЛАЗИТЬ");

    printf("  Запас реакції:   %.0f мс %s\n\n",
           margin, margin > 0 ? "" : "(!) з'їдено весь бюджет");
}
