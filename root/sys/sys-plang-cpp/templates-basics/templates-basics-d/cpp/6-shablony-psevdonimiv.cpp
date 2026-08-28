// До C++11: громіздкий обхідний шлях
template <typename T>
struct StringMapLegacy {
    typedef std::map<std::string, T> type;
};
// Використання: typename StringMapLegacy<int>::type my_map;

// Починаючи з C++11: чистий шаблон псевдоніма
template <typename T>
using StringMap = std::map<std::string, T>;
// Використання: StringMap<int> my_map;
