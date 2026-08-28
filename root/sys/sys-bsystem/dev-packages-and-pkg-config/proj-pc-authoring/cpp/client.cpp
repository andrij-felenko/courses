// client.cpp
#include <geomcalc.hpp>
#include <iostream>
#include <vector>

int main() {
    geom::Point p1{0.0, 0.0};
    geom::Point p2{4.0, 0.0};
    geom::Point p3{0.0, 3.0};

    double area = geom::triangle_area(p1, p2, p3);
    std::cout << "Обчислена площа трикутника: " << area << " (очікується 6.00)\n";

    std::vector<geom::Point> pts{p1, p2, p3};
    auto report = geom::export_compressed_report(pts);

    if (report.has_value()) {
        std::cout << "Звіт успішно стиснуто через zlib до " 
                  << report->size() << " байтів.\n";
    } else {
        std::cerr << "Помилка стиснення звіту.\n";
        return 1;
    }

    return 0;
}
