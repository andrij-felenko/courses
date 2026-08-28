// Приклад 1: Матеріалізація типу для оголошення змінної
constexpr std::meta::info target_type = ^^double;
typename [: target_type :] precise_measurement = 3.1415926535;

// Приклад 2: Звернення до поля об'єкта за його метадескриптором
NetworkEndpoint server{.hostname = "127.0.0.1", .port = 8080, .use_tls = true};
constexpr auto members = std::meta::nonstatic_data_members_of(^^NetworkEndpoint);

// Отримуємо прямий доступ до другого поля (port) без знання його імені у вихідному коді
server.[: members[1] :] = 9090;

// Приклад 3: Інстанціювання шаблону за рефлексивним дескриптором
constexpr std::meta::info vector_template = ^^std::vector;
template [: vector_template :]<int> dynamic_buffer;
