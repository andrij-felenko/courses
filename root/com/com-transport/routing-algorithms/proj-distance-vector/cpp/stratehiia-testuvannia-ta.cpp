void test_two_node_loop_prevention() {
    NetworkSimulator net(3);
    net.add_link(0, 1, 1);
    net.add_link(1, 2, 1);
    net.run_until_convergence();

    // Симулюємо обрив лінка (1, 2)
    net.remove_link(1, 2);
    net.run_until_convergence();

    // Завдяки Poison Reverse вузли повинні за 1-2 ітерації встановити INF
    // замість нескінченного відліку 3, 4, 5...
}
