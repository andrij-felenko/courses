#include <iostream>
#include <vector>
#include <algorithm>

// Структура для представлення інтервалу події
struct Interval {
    int id;
    int start;
    int finish;
};

// Функція розв'язання задачі інтервального планування
std::vector<Interval> scheduleIntervals(std::vector<Interval>& intervals) {
    if (intervals.empty()) {
        return {};
    }

    // Крок 1: Жадібне сортування за часом закінчення finish
    std::sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
        if (a.finish != b.finish) {
            return a.finish < b.finish;
        }
        return a.start < b.start;
    });

    std::vector<Interval> result;
    // Крок 2: Обираємо перший інтервал з найранішим фінішем
    result.push_back(intervals[0]);
    int lastFinish = intervals[0].finish;

    // Крок 3: Жадібне фільтрування решти інтервалів
    for (size_t i = 1; i < intervals.size(); ++i) {
        if (intervals[i].start >= lastFinish) {
            result.push_back(intervals[i]);
            lastFinish = intervals[i].finish;
        }
    }

    return result;
}

int main() {
    std::vector<Interval> intervals = {
        {1, 0, 3},
        {2, 1, 4},
        {3, 2, 6},
        {4, 3, 7},
        {5, 5, 8},
        {6, 7, 10}
    };

    std::vector<Interval> scheduled = scheduleIntervals(intervals);

    std::cout << "Обрано інтервалів: " << scheduled.size() << "\n";
    for (const auto& item : scheduled) {
        std::cout << "Подія " << item.id << ": [" << item.start << ", " << item.finish << "]\n";
    }

    return 0;
}
