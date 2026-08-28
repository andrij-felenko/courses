struct Solvable {
    Id name;           // Id імені пакунка (string pool index)
    Id evr;            // Id версії (string pool index)
    Id arch;           // Id архітектури (string pool index)
    Repo* repo;        // Покажчик на репозиторій-власник

    Id provides;       // Індекс масиву наданих можливостей у Pool
    Id requires;       // Індекс масиву необхідних залежностей у Pool
    Id conflicts;      // Індекс масиву конфліктних вимог у Pool
    Id obsoletes;      // Індекс масиву замінюваних пакунків у Pool
    Id recommends;     // Індекс масиву рекомендованих залежностей
    Id suggests;       // Індекс масиву пропонованих залежностей
    Id enhances;       // Індекс початку масиву розширень
    Id supplements;    // Індекс початку масиву зворотних рекомендацій
};
