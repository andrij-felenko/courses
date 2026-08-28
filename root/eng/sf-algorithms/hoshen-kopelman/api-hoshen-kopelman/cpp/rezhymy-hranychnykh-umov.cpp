enum class BoundaryCondition {
    Open = 0,       // Відкриті (фіксовані) границі
    Periodic = 1    // Періодичні (тороїдальні) границі
};

enum class Connectivity {
    Four = 4,       // 2D 4-зв'язність
    Eight = 8,      // 2D 8-зв'язність
    Six = 6,        // 3D 6-зв'язність
    TwentySix = 26  // 3D 26-зв'язність
};
