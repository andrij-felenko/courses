// Підйом типів даних
constexpr std::meta::info int_ref   = ^^int;
constexpr std::meta::info str_ref   = ^^std::string;

// Підйом членів класу
struct Account {
    std::string login;
    int balance;
};
constexpr std::meta::info field_ref = ^^Account::login;

// Підйом просторів назв, шаблонів та констант
constexpr std::meta::info ns_ref    = ^^std;
constexpr std::meta::info tmpl_ref  = ^^std::vector;
