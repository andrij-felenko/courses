// Підйом типів
constexpr std::meta::info int_info   = ^^int;
constexpr std::meta::info acc_info   = ^^Account;

// Підйом членів структури
constexpr std::meta::info field_info = ^^Account::owner;

// Підйом просторів назв та шаблонів
constexpr std::meta::info ns_info    = ^^std;
constexpr std::meta::info tmpl_info  = ^^std::vector;

// Підйом елементів переліку
enum class Status { Ok, Error };
constexpr std::meta::info enum_info  = ^^Status::Ok;
