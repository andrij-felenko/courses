#include <functional>

// У C++ ми передаємо функціональні об'єкти (ручні санки)
template <typename ThenFn, typename ElseFn>
auto my_if_cpp(bool cond, ThenFn then_branch, ElseFn else_branch) {
    if (cond) {
        return then_branch();
    } else {
        return else_branch();
    }
}
