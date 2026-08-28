#include <tbb/flow_graph.h>
#include <iostream>

void build_dataflow_dag() {
    tbb::flow::graph g;

    // Вузол джерела даних
    tbb::flow::broadcast_node<int> start_node(g);

    // Паралельні вузли обробки
    tbb::flow::function_node<int, int> node_a(g, tbb::flow::unlimited, [](int v) {
        return v * 2;
    });

    tbb::flow::function_node<int, int> node_b(g, tbb::flow::unlimited, [](int v) {
        return v + 10;
    });

    // Вузол об'єднання результатів
    tbb::flow::join_node<std::tuple<int, int>, tbb::flow::queueing> join(g);

    tbb::flow::function_node<std::tuple<int, int>, int> final_node(g, tbb::flow::serial, [](const std::tuple<int, int> &t) {
        return std::get<0>(t) + std::get<1>(t);
    });

    // Побудова ребер графа
    tbb::flow::make_edge(start_node, node_a);
    tbb::flow::make_edge(start_node, node_b);
    tbb::flow::make_edge(node_a, tbb::flow::input_port<0>(join));
    tbb::flow::make_edge(node_b, tbb::flow::input_port<1>(join));
    tbb::flow::make_edge(join, final_node);

    start_node.try_put(5);
    g.wait_for_all();
}
