// stl_list_example.cpp — Демонстрація ефективного використання std::list та splice
#include <iostream>
#include <list>
#include <string>
#include <algorithm>

int main() {
    std::list<std::string> main_queue = {"Task1", "Task2", "Task5"};
    std::list<std::string> priority_queue = {"UrgentTaskA", "UrgentTaskB"};

    // Знайдемо позицію перед Task5
    auto it = std::find(main_queue.begin(), main_queue.end(), "Task5");

    // splice() переміщує вузли з priority_queue у main_queue за O(1) без копіювання рядків!
    if (it != main_queue.end()) {
        main_queue.splice(it, priority_queue);
    }

    std::cout << "Головна черга після сплайсингу:\n";
    for (const auto& task : main_queue) {
        std::cout << " - " << task << "\n";
    }

    std::cout << "Розмір пріоритетної черги: " << priority_queue.size() << " (порожня)\n";

    return 0;
}
