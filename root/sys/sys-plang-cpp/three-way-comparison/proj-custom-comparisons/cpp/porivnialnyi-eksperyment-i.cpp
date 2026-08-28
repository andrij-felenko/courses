void run_floating_point_experiment() {
    double nan1 = std::numeric_limits<double>::quiet_NaN();
    double nan2 = std::numeric_limits<double>::quiet_NaN();

    Point3D raw_p1{nan1, 0.0, 0.0};
    Point3D raw_p2{nan2, 0.0, 0.0};

    // 1. Поведінка звичайного часткового порядку
    auto partial_cmp = (raw_p1 <=> raw_p2);
    std::cout << "Raw points equal: " << (raw_p1 == raw_p2) << "\n"; // false (NaN != NaN)
    std::cout << "Is unordered: "
              << (partial_cmp == std::partial_ordering::unordered) << "\n"; // true

    // 2. Поведінка адаптера тотального порядку
    TotalOrderPoint3D safe_p1{raw_p1};
    TotalOrderPoint3D safe_p2{raw_p2};

    auto total_cmp = (safe_p1 <=> safe_p2);
    std::cout << "Safe points equal: " << (safe_p1 == safe_p2) << "\n"; // true!
    std::cout << "Is strong equal: "
              << (total_cmp == std::strong_ordering::equal) << "\n"; // true

    // 3. Безпечна робота з std::set: дедуплікація та відсутність невизначеної поведінки
    std::set<TotalOrderPoint3D, std::less<>> safe_set;
    safe_set.insert(safe_p1);
    safe_set.insert(safe_p2);

    std::cout << "Set size with NaN duplicates: " << safe_set.size() << "\n"; // Рівно 1!
}
