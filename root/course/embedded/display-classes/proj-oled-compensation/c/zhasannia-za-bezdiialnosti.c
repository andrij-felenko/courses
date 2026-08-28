// оновити ЦІЛЬ яскравості за часом бездіяльності (не саму яскравість — її веде slew)
void idle_update_target(disp_guard_t *g, uint32_t now_ms) {
    uint32_t idle = now_ms - g->last_activity_ms;
    if      (idle >= g->off_ms)  g->bright_target = 0;                 // згасити зовсім
    else if (idle >= g->dim_ms)  g->bright_target = g->bright_full / 4; // притемнити до ~25 %
    else                         g->bright_target = g->bright_full;    // повна яскравість
}

// будь-яка взаємодія (кнопка, дотик, подія) — прокидаємось миттєво
void activity_ping(disp_guard_t *g, uint32_t now_ms) {
    g->last_activity_ms = now_ms;
    g->bright_target = g->bright_full;
    // важливо: НЕ ставимо bright_now = full стрибком — хай slew підніме плавно,
    // інакше пробудження «клацне». Виняток — вихід з повного нуля (див. пастки).
}
