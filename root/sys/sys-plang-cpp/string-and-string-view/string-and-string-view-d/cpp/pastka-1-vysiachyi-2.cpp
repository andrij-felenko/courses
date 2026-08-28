// C++: Пастка часу життя та висячого погляду
#include <iostream>
#include <string>
#include <string_view>

std::string_view create_dangling_view() {
    std::string local_str = "Тимчасові дані в локальній змінній";
    return local_str; // Небезпека: local_str знищиться при виході з функції!
}

void dangling_demo() {
    std::string_view bad_sv = create_dangling_view();
    // bad_sv.data() тепер вказує на сміття у стековому кадрі
}
