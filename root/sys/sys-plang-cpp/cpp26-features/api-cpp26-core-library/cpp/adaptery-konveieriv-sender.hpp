namespace std::execution {
    // Синхронне перетворення результату функцією
    template <sender S, typename F>
    sender auto then(S&& s, F&& f);

    // Асинхронне продовження: функція повертає новий сендер
    template <sender S, typename F>
    sender auto let_value(S&& s, F&& f);

    // Обробка каналу помилок із можливістю відновлення
    template <sender S, typename F>
    sender auto let_error(S&& s, F&& f);

    // Обробка каналу скасування
    template <sender S, typename F>
    sender auto let_stopped(S&& s, F&& f);

    // Запуск виконання на конкретному планувальнику
    template <sender S, scheduler Sch>
    sender auto starts_on(Sch&& sch, S&& s);

    // Перенесення продовження на інший планувальник
    template <sender S, scheduler Sch>
    sender auto continues_on(S&& s, Sch&& sch);

    // Паралельний запуск кількох сендерів (fork-join)
    template <sender... Ss>
    sender auto when_all(Ss&&... senders);

    // Розгалуження сендера для кількох споживачів
    template <sender S>
    sender auto split(S&& s);
}
