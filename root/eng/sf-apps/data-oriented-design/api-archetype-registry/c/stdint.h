#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CHUNK_SIZE 16384
#define MAX_COMPONENTS_PER_ARCHETYPE 32

typedef uint32_t EntityID;

/* Структура ідентифікатора сутності з поколінням для усунення проблеми ABA */
typedef struct {
    uint32_t id;
    uint32_t generation;
} Entity;

typedef uint32_t ComponentTypeID;

/* Опис метаданих типу компонента */
typedef struct {
    ComponentTypeID id;
    uint32_t        size;
    uint32_t        alignment;
} ComponentInfo;

/* Заголовок чанка */
typedef struct Chunk {
    struct Archetype* archetype;
    uint32_t          count;
    uint32_t          capacity;
    struct Chunk*     next;
    struct Chunk*     prev;
    uint8_t           padding[32];
} Chunk;

/* Дескриптор унікальної комбінації компонентів */
typedef struct Archetype {
    uint32_t      component_count;
    ComponentInfo components[MAX_COMPONENTS_PER_ARCHETYPE];
    uint32_t      component_offsets[MAX_COMPONENTS_PER_ARCHETYPE];
    uint32_t      chunk_capacity;
    
    Chunk*        first_chunk;
    Chunk*        last_chunk;
    uint32_t      total_entities;
} Archetype;

/* Реєстр сутностей та граф архетипів */
typedef struct ArchetypeRegistry ArchetypeRegistry;

/* Створення та знищення реєстру */
ArchetypeRegistry* arch_registry_create(void);
void               arch_registry_destroy(ArchetypeRegistry* reg);

/* Реєстрація компонентів */
ComponentTypeID    arch_register_component(ArchetypeRegistry* reg, uint32_t size, uint32_t align);

/* Створення та видалення сутності */
Entity             arch_entity_create(ArchetypeRegistry* reg, const ComponentTypeID* types, uint32_t type_count);
bool               arch_entity_destroy(ArchetypeRegistry* reg, Entity e);

/* Динамічна мутація складу компонентів (перехід між архетипами) */
bool               arch_entity_add_component(ArchetypeRegistry* reg, Entity e, ComponentTypeID comp_id, const void* initial_data);
bool               arch_entity_remove_component(ArchetypeRegistry* reg, Entity e, ComponentTypeID comp_id);

/* Отримання прямого доступу до стовпця даних усередині чанка */
void*              arch_chunk_get_column(Chunk* chunk, uint32_t component_index);
