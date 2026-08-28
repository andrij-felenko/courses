#include "ReachabilityEngine.hpp"
#include <iostream>

void checkRbacPermissionCpp() {
    using namespace graph::analytics;

    EngineConfig cfg{
        .vertices = 1000,
        .mode = AlgorithmMode::BitsetVectorized,
        .auto_reflexive = true
    };

    ReachabilityEngine engine(cfg);

    // Додаємо зв'язки ролей: User 5 -> Role 12 -> Permission 105
    engine.addEdge(5, 12);
    engine.addEdge(12, 105);

    engine.compute();

    if (engine.isReachable(5, 105)) {
        std::cout << "Access GRANTED for user 5 to permission 105\n";
    }
}
