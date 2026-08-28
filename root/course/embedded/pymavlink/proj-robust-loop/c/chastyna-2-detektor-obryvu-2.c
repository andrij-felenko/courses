static void enter_safe_mode(int fd, LinkState *st);   // оголошення наперед

// Повертає поточний стан лінії; на ФРОНТІ втрати — діє один раз.
static bool check_link(int fd, LinkState *st, bool prev_alive) {
    bool alive = link_alive(st);

    if (prev_alive && !alive) {
        // ФРОНТ: щойно було живо, стало мертво — реагуємо РІВНО ТУТ
        printf("[LINK] обрив зв'язку — переходимо в безпечний режим\n");
        enter_safe_mode(fd, st);
    } else if (!prev_alive && alive) {
        printf("[LINK] зв'язок відновлено\n");   // ФРОНТ у зворотний бік
    }

    return alive;
}
