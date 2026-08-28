#include <iostream>
#include <span>
#include <type_traits>
#include <utility>
#include <vector>

static_assert( std::is_const_v<const int>);
static_assert(!std::is_const_v<const int&>);      // посилання ніколи не const-кваліфіковане
static_assert(!std::is_const_v<const int*>);      // const на мішені, не на стрілці
static_assert( std::is_const_v<int* const>);      // а тут — на стрілці
static_assert(std::is_same_v<std::add_const_t<int&>,          int&>);
static_assert(std::is_same_v<std::remove_const_t<const int*>, const int*>);
static_assert(std::is_same_v<std::remove_cvref_t<const int&>, int>);

class Table {
    std::vector<int> rows_{1, 2, 3};
    mutable std::size_t reads_ = 0;          // лічильник звернень — назовні невидимий

public:
    int&       at(std::size_t i)       { return rows_[i]; }
    const int& at(std::size_t i) const { ++reads_; return rows_[i]; }

    std::span<const int> view()  const { return rows_; }   // vector → span<const int>
    std::size_t          reads() const { return reads_; }
};

int main() {
    Table t;
    t.at(0) = 10;                            // об'єкт мінливий → неконстантне перевантаження
    int x = std::as_const(t).at(0);          // той самий t, але добір іде на const-версію

    std::span<const int> s = t.view();       // дивимось, не чіпаючи
    std::cout << x << ' ' << s.size() << ' ' << t.reads() << '\n';   // 10 3 1
}
