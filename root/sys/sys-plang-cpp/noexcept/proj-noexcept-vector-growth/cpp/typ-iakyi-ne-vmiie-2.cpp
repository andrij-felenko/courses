static_assert(std::is_same_v<
    decltype(std::move_if_noexcept(std::declval<Payload<true>&>())),
    Payload<true>&&>);                       // обіцянка є → переміщуємо

static_assert(std::is_same_v<
    decltype(std::move_if_noexcept(std::declval<Payload<false>&>())),
    const Payload<false>&>);                 // обіцянки немає, копія є → копіюємо

static_assert(std::is_same_v<
    decltype(std::move_if_noexcept(std::declval<MoveOnly&>())),
    MoveOnly&&>);                            // копії немає → переміщуємо попри все
