#include <cstdint>
#include <string>
#include <vector>

struct Vertex {                       // одна вершина сітки
    float px, py, pz;                 // позиція     12 Б
    float nx, ny, nz;                 // нормаль      12 Б
    float u,  v;                      // текстурні    8 Б  → 32 Б на вершину
};

// Внутрішній стан: важкий, СПІЛЬНИЙ, НЕЗМІННИЙ.
class TreeKind {
public:
    TreeKind(std::string name, std::vector<Vertex> mesh,
             uint32_t texture, uint32_t color)
        : name_(std::move(name)), mesh_(std::move(mesh)),
          texture_(texture), color_(color) {}

    const std::string&          name()    const { return name_; }
    const std::vector<Vertex>&  mesh()     const { return mesh_; }
    uint32_t                    texture() const { return texture_; }
    uint32_t                    color()   const { return color_; }

private:
    const std::string           name_;    // "дуб", "сосна", "береза"
    const std::vector<Vertex>   mesh_;     // десятки тисяч вершин ≈ 1 МБ
    const uint32_t              texture_;  // хендл текстури
    const uint32_t              color_;    // RGBA
};
