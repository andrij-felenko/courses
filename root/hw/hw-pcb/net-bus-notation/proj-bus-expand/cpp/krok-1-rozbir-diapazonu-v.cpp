#include <string>
#include <vector>
#include <cstdio>

// Розібрана шина: префікс, нижня й верхня межі ЯК НАПИСАНО, і чи це вектор.
// Увага: lo/hi тут — це ліве/праве число запису, НЕ «менше/більше».
struct BusName {
    std::string prefix;   // "D" для "D[7..0]"
    int left, right;      // ліва й права межі: 7 і 0 для "D[7..0]"
    bool is_vector;       // false для скаляра "CLK"
};
