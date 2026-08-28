#include <iostream>
#include "IntervalTree.hpp"

int main() {
    geo::IntervalTree tree;
    tree.insert({15.0, 20.0});
    tree.insert({10.0, 30.0});

    if (auto match = tree.find_any_overlap({21.0, 25.0}); match) {
        std::cout << "Знайдено перетин: [" << match->low << ", " << match->high << "]\n";
    }
    return 0;
}
