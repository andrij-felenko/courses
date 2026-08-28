# Скільки знахідок роблять рев'ю НЕзавершеним:
# відкритий ризик, за яким ніхто не стоїть або який ще не зрушив з місця.
# Рахуємо лише RISK: неризик за визначенням не треба нікому «знімати»,
# а чутливість/компроміс без обраної жертви — теж борг, тож ловимо і їх,
# коли вони ще OPEN. Але СИГНАЛ провалу — саме безхазяйний або незрушений ризик.
def review_open_liabilities(s: ArchReviewSession) -> int:
    bad = 0
    for f in s.findings:

        # Неризик закривати нікому не треба — пропускаємо.
        if f.kind is FindingKind.NON_RISK:
            continue

        # Ризик/чутливість/компроміс вважаємо боргом, якщо:
        #   немає власника  АБО  дедлайн не призначено  АБО  ще не зрушив.
        no_owner = not f.owner
        no_deadline = f.due_day == 0 and f.state is not FindingState.CLOSED
        not_started = f.state is FindingState.OPEN

        if no_owner or no_deadline or not_started:
            bad += 1
    return bad


# Рев'ю завершене лише коли боргів нуль.
def review_is_complete(s: ArchReviewSession) -> bool:
    return review_open_liabilities(s) == 0
