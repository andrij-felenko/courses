namespace std::execution {
    // Створює сендер, що негайно надсилає значення
    template <typename... Ts>
    sender auto just(Ts&&... values);

    // Створює сендер, що надсилає об'єкт помилки
    template <typename E>
    sender auto just_error(E&& error);

    // Створює сендер, що сигналізує про зупинку конвеєра
    sender auto just_stopped();

    // Створює сендер перенесення виконання на планувальник
    template <scheduler Sch>
    sender auto schedule(Sch&& sch);

    // Зчитує параметри оточення (токен зупинки, алокатор)
    template <typename Query>
    sender auto read_env(Query query);
}
