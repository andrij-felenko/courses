void take(const std::string&);   // 1
void take(std::string&&);        // 2

std::string name = "Ада";
const std::string frozen = "Грейс";

take(name);                  // 1 — 2 не бере lvalue
take(frozen);                // 1 — 2 не бере lvalue
take(std::string("тимч"));   // 2 — обидві підходять, rvalue краще лягає на T&&
take(std::move(name));       // 2
