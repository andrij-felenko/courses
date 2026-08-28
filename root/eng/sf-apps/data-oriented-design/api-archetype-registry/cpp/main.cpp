#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <memory>
#include <typeindex>

struct Entity {
    std::uint32_t id{0};
    std::uint32_t generation{0};

    [[nodiscard]] bool operator==(const Entity& other) const noexcept = default;
};

using ComponentTypeID = std::uint32_t;

inline constexpr std::size_t kChunkSize = 16384;
inline constexpr std::size_t kMaxComponentsPerArchetype = 32;

struct ComponentInfo {
    ComponentTypeID id{0};
    std::uint32_t   size{0};
    std::uint32_t   alignment{0};
};

struct alignas(64) ChunkHeader {
    struct Archetype* archetype{nullptr};
    std::uint32_t     count{0};
    std::uint32_t     capacity{0};
    ChunkHeader*      next{nullptr};
    ChunkHeader*      prev{nullptr};
    std::uint8_t      reserved[32]{};
};

class ArchetypeRegistry {
public:
    ArchetypeRegistry() = default;
    ~ArchetypeRegistry() = default;

    ArchetypeRegistry(const ArchetypeRegistry&) = delete;
    ArchetypeRegistry& operator=(const ArchetypeRegistry&) = delete;

    template <typename T>
    ComponentTypeID register_component() {
        return register_component_raw(sizeof(T), alignof(T));
    }

    Entity create_entity(std::span<const ComponentTypeID> types);
    bool   destroy_entity(Entity e);

    template <typename T>
    bool add_component(Entity e, const T& data) {
        return add_component_raw(e, get_type_id<T>(), &data);
    }

    template <typename T>
    bool remove_component(Entity e) {
        return remove_component_raw(e, get_type_id<T>());
    }

    // Отримання неперервного стовпця для пакетної векторизованої ітерації
    template <typename T>
    std::span<T> get_chunk_column(ChunkHeader* chunk, std::uint32_t component_idx) noexcept {
        auto* ptr = static_cast<std::uint8_t*>(static_cast<void*>(chunk));
        std::size_t offset = get_component_offset(chunk, component_idx);
        return { reinterpret_cast<T*>(ptr + offset), chunk->count };
    }

private:
    ComponentTypeID register_component_raw(std::uint32_t size, std::uint32_t align);
    bool add_component_raw(Entity e, ComponentTypeID id, const void* data);
    bool remove_component_raw(Entity e, ComponentTypeID id);
    std::size_t get_component_offset(ChunkHeader* chunk, std::uint32_t component_idx) const noexcept;
    
    template <typename T>
    static ComponentTypeID get_type_id() noexcept;
};
