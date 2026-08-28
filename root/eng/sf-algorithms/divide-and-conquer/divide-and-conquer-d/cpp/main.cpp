#include <vector>

std::vector<int> merge(const std::vector<int>& x, const std::vector<int>& y) {
    std::vector<int> out;
    out.reserve(x.size() + y.size());
    size_t i = 0, j = 0;
    while (i < x.size() && j < y.size())          // менша з двох верхівок
        out.push_back(x[i] <= y[j] ? x[i++] : y[j++]);
    while (i < x.size()) out.push_back(x[i++]);   // долити рештку
    while (j < y.size()) out.push_back(y[j++]);
    return out;
}

std::vector<int> merge_sort(const std::vector<int>& a) {
    if (a.size() <= 1) return a;                  // базовий випадок
    size_t mid = a.size() / 2;
    std::vector<int> left (a.begin(), a.begin() + mid);
    std::vector<int> right(a.begin() + mid, a.end());
    return merge(merge_sort(left), merge_sort(right));   // підкорити + поєднати
}
