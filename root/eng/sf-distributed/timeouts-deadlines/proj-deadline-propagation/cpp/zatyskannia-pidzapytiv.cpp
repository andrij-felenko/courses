/* Створення дочірнього контексту з динамічним затисканням */
std::optional<DeadlineContext> derive_subcall_context(
    const DeadlineContext& parent,
    std::chrono::milliseconds configured_limit,
    std::chrono::milliseconds min_viable_rtt = std::chrono::milliseconds(10)) {

    const auto parent_rem = parent.remaining();
    const auto available = parent_rem - parent.margin();

    /* Якщо часу не вистачить навіть на мережевий раунд-тріп — відмовляємося */
    if (available < min_viable_rtt) {
        return std::nullopt;
    }

    const auto subcall_limit = std::min(configured_limit, available);
    return DeadlineContext(subcall_limit, parent.margin());
}
