// Скільки знахідок роблять рев'ю НЕзавершеним:
// відкритий ризик, за яким ніхто не стоїть або який ще не зрушив з місця.
// Рахуємо лише Risk: неризик за визначенням не треба нікому «знімати»,
// а чутливість/компроміс без обраної жертви — теж борг, тож ловимо і їх,
// коли вони ще Open. Але СИГНАЛ провалу — саме безхазяйний або незрушений ризик.
static std::size_t review_open_liabilities(const ArchReviewSession &s) {
    std::size_t bad = 0;
    for (const ArchFinding &f : s.findings) {

        // Неризик закривати нікому не треба — пропускаємо.
        if (f.kind == FindingKind::NonRisk)
            continue;

        // Ризик/чутливість/компроміс вважаємо боргом, якщо:
        //   немає власника  АБО  дедлайн не призначено  АБО  ще не зрушив.
        bool no_owner    = f.owner.empty();
        bool no_deadline = (f.due_day == 0 && f.state != FindingState::Closed);
        bool not_started = (f.state == FindingState::Open);

        if (no_owner || no_deadline || not_started)
            ++bad;
    }
    return bad;
}

// Рев'ю завершене лише коли боргів нуль.
static bool review_is_complete(const ArchReviewSession &s) {
    return review_open_liabilities(s) == 0;
}
