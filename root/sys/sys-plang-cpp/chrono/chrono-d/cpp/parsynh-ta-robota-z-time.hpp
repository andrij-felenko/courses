using namespace std::chrono;

// Отримання вказівника на часовий пояс Києва
const time_zone* zone = locate_zone("Europe/Kyiv");

// Створення об'єкта zoned_time для зв'язування точки часу UTC із часовим поясом
zoned_time kyiv_time{zone, system_clock::now()};

// Вивід форматованого часу з урахуванням зсуву EEST (+03:00)
std::cout << std::format("Поточний місцевий час: {:%F %T %Z}\n", kyiv_time);
