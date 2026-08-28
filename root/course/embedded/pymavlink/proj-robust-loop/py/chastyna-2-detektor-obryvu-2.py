def check_link(m, state, prev_alive):
    """Повертає поточний стан лінії; на ФРОНТІ втрати — діє один раз."""
    alive = state.link_alive()

    if prev_alive and not alive:
        # ФРОНТ: щойно було живо, стало мертво — реагуємо РІВНО ТУТ
        print("[LINK] обрив зв'язку — переходимо в безпечний режим")
        enter_safe_mode(m, state)

    elif not prev_alive and alive:
        # ФРОНТ у зворотний бік: лінія ожила
        print("[LINK] зв'язок відновлено")

    return alive
