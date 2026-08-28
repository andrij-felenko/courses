// ПОМИЛКА: некоректне розуміння блоку requires
template<typename T>
concept BrokenLogic = requires(T a, T b) {
    (a + b) && (a - b); // Це ПРОСТА вимога синтаксису оператора && між результатами!
                         // Якщо a + b повертає void, вираз викличе помилку,
                         // навіть якщо оператор + існує!
};

// ПРАВИЛЬНО: роздільні вимоги або логічний оператор між концептами
template<typename T>
concept CorrectLogic = requires(T a, T b) {
    a + b;
    a - b;
};
