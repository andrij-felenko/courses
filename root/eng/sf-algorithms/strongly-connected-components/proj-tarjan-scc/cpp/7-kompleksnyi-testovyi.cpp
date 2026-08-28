#include <iostream>
#include <cassert>

void run_unit_tests() {
    // Тест 1: Простий граф із циклом 1->0->2->1
    TarjanSCCSolver test1(5);
    test1.add_edge(1, 0);
    test1.add_edge(0, 2);
    test1.add_edge(2, 1);
    test1.add_edge(0, 3);
    test1.add_edge(3, 4);

    auto res1 = test1.compute_scc();
    assert(res1.size() == 3);
    std::cout << "Unit test 1 (Cycle + DAG path): PASSED\n";

    // Тест 2: DAG граф (кожна вершина — окрема SCC)
    TarjanSCCSolver test2(4);
    test2.add_edge(0, 1);
    test2.add_edge(1, 2);
    test2.add_edge(2, 3);

    auto res2 = test2.compute_scc();
    assert(res2.size() == 4);
    std::cout << "Unit test 2 (DAG graph): PASSED\n";

    std::cout << "All unit tests completed successfully!\n";
}

int main() {
    run_unit_tests();
    return 0;
}
