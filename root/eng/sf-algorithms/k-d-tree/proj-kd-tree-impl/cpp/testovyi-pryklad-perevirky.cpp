int main() {
    std::vector<Point<2>> pts = {
        {{{50.0, 45.0}}, 1},
        {{{25.0, 65.0}}, 2},
        {{{75.0, 25.0}}, 3},
        {{{12.0, 30.0}}, 4},
        {{{38.0, 85.0}}, 5},
        {{{62.0, 75.0}}, 6},
        {{{88.0, 12.0}}, 7}
    };

    KDTree<2> tree(std::move(pts));

    // 1. Пошук найближчого сусіда для Q(48, 42)
    Point<2> query{{{48.0, 42.0}}, 0};
    auto [nn, dist_sq] = tree.nearest_neighbor(query);

    if (nn != nullptr) {
        std::cout << "Найближчий сусід: ID=" << nn->id
                  << " (" << nn->coords[0] << ", " << nn->coords[1] << ")"
                  << ", dist_sq=" << dist_sq << '\n';
    }

    // 2. Діапазонний пошук у вікні [20, 70] x [20, 70]
    Point<2> min_box{{{20.0, 20.0}}, 0};
    Point<2> max_box{{{70.0, 70.0}}, 0};
    auto range_results = tree.range_query(min_box, max_box);

    std::cout << "Знайдено точок у діапазоні: " << range_results.size() << '\n';
    for (const auto& pt : range_results) {
        std::cout << "  - ID=" << pt.id << " (" << pt.coords[0] << ", " << pt.coords[1] << ")\n";
    }

    return 0;
}
