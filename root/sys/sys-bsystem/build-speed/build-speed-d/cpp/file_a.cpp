// Проблема: конфлікт анонімних просторів імен та локальних макросів у C++

// file_a.cpp
#define LOG_TAG "Physics"
namespace {
    struct State { float mass; };
    void reset(State& s) { s.mass = 0.0f; }
}

void update_physics() {
    State st{1.0f};
    reset(st);
}

// file_b.cpp
#define LOG_TAG "Renderer" // Попередження/помилка препроцесора: LOG_TAG вже існує
namespace {
    struct State { int texture_id; }; // Помилка: переозначення структури State
    void reset(State& s) { s.texture_id = -1; } // Помилка: переозначення функції
}

// Рішення для C++: іменовані внутрішні простори імен, RAII та прибирання макросів
// file_a.cpp (виправлено)
namespace engine::physics::detail {
    struct State { float mass; };
    inline void reset(State& s) noexcept { s.mass = 0.0f; }
}

void update_physics() {
    using namespace engine::physics::detail;
    State st{1.0f};
    reset(st);
}
