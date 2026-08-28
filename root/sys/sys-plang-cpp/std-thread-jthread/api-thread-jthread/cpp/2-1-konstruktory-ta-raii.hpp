// 1. Default-конструктор
jthread() noexcept;

// 2. Шаблонний конструктор із підтримкою stop_token
template <class Function, class... Args>
explicit jthread(Function&& f, Args&&... args);

// 3. Конструктор переміщення
jthread(jthread&& other) noexcept;

// 4. Оператор переміщувального присвоєння
jthread& operator=(jthread&& other) noexcept;

// 5. RAII-деструктор з авто-приєднанням
~jthread();
