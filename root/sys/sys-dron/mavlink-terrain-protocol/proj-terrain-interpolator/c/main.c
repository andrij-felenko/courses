#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define TERRAIN_GRID_SPACING 100
#define TERRAIN_BLOCK_NODES  4
#define TERRAIN_CLUSTER_SIZE 8
#define TERRAIN_CACHE_CAPACITY 32
#define TERRAIN_NO_DATA_VALUE (-32768)

// Структура одного блоку 4x4 у пам'яті
typedef struct {
    int32_t  lat_sw;        // SW широта (град * 1e7)
    int32_t  lon_sw;        // SW довгота (град * 1e7)
    uint32_t last_access;   // Лічильник звернень для LRU витіснення
    int16_t  data[16];      // Матриця 4x4 висот AMSL у метрах
    bool     valid;         // Прапорець завантаженості блоку
} terrain_block_t;

// Структура менеджера кешу рельєфу
typedef struct {
    terrain_block_t pool[TERRAIN_CACHE_CAPACITY];
    uint32_t access_counter;
    uint16_t loaded_count;
} terrain_cache_t;

// Ініціалізація кешу
void terrain_cache_init(terrain_cache_t *cache) {
    memset(cache, 0, sizeof(terrain_cache_t));
}

// Допоміжний розрахунок кутового кроку (масштаб 1e7)
static int32_t get_lat_step_1e7(uint16_t spacing) {
    return (int32_t)((((double)spacing) / 111319.5) * 1e7);
}

static int32_t get_lon_step_1e7(uint16_t spacing, int32_t lat_1e7) {
    double lat_rad = (lat_1e7 * 1e-7) * (M_PI / 180.0);
    double cos_lat = cos(lat_rad);
    if (cos_lat < 0.01) cos_lat = 0.01; // Захист від ділення на нуль біля полюсів
    return (int32_t)((((double)spacing) / (111319.5 * cos_lat)) * 1e7);
}

// Пошук блоку в кеші за координатами SW кута
static terrain_block_t* find_block(terrain_cache_t *cache, int32_t lat_sw, int32_t lon_sw) {
    for (int i = 0; i < TERRAIN_CACHE_CAPACITY; ++i) {
        if (cache->pool[i].valid &&
            cache->pool[i].lat_sw == lat_sw &&
            cache->pool[i].lon_sw == lon_sw) {
            cache->pool[i].last_access = ++cache->access_counter;
            return &cache->pool[i];
        }
    }
    return NULL;
}

// Збереження отриманого блоку TERRAIN_DATA у кеш (з LRU витісненням)
void terrain_cache_insert(terrain_cache_t *cache, int32_t lat_sw, int32_t lon_sw, const int16_t heights[16]) {
    terrain_block_t *target = find_block(cache, lat_sw, lon_sw);
    
    // Якщо блок ще не в кеші, шукаємо вільний або найстаріший слот
    if (!target) {
        int lru_index = 0;
        uint32_t min_access = UINT32_MAX;
        
        for (int i = 0; i < TERRAIN_CACHE_CAPACITY; ++i) {
            if (!cache->pool[i].valid) {
                lru_index = i;
                break;
            }
            if (cache->pool[i].last_access < min_access) {
                min_access = cache->pool[i].last_access;
                lru_index = i;
            }
        }
        
        target = &cache->pool[lru_index];
        if (!target->valid) {
            cache->loaded_count++;
        }
        target->lat_sw = lat_sw;
        target->lon_sw = lon_sw;
        target->valid = true;
    }
    
    memcpy(target->data, heights, sizeof(int16_t) * 16);
    target->last_access = ++cache->access_counter;
}

// Розрахунок 64-бітної маски відсутніх блоків навколо центру кластера
uint64_t terrain_build_request_mask(terrain_cache_t *cache, int32_t center_lat, int32_t center_lon, uint16_t spacing) {
    int32_t d_lat = get_lat_step_1e7(spacing);
    int32_t d_lon = get_lon_step_1e7(spacing, center_lat);
    
    int32_t block_span_lat = (TERRAIN_BLOCK_NODES - 1) * d_lat;
    int32_t block_span_lon = (TERRAIN_BLOCK_NODES - 1) * d_lon;
    
    int32_t cluster_sw_lat = center_lat - 4 * block_span_lat;
    int32_t cluster_sw_lon = center_lon - 4 * block_span_lon;
    
    uint64_t mask = 0;
    
    for (int r = 0; r < TERRAIN_CLUSTER_SIZE; ++r) {
        for (int c = 0; c < TERRAIN_CLUSTER_SIZE; ++c) {
            int32_t b_lat = cluster_sw_lat + r * block_span_lat;
            int32_t b_lon = cluster_sw_lon + c * block_span_lon;
            
            int bit_idx = r * 8 + c;
            if (find_block(cache, b_lat, b_lon) == NULL) {
                mask |= ((uint64_t)1 << bit_idx);
            }
        }
    }
    return mask;
}

// Двовимірна білінійна інтерполяція висоти поверхні в точці (lat, lon)
bool terrain_interpolate_height(terrain_cache_t *cache, int32_t lat, int32_t lon, uint16_t spacing, float *out_height) {
    int32_t d_lat = get_lat_step_1e7(spacing);
    int32_t d_lon = get_lon_step_1e7(spacing, lat);
    int32_t block_span_lat = (TERRAIN_BLOCK_NODES - 1) * d_lat;
    int32_t block_span_lon = (TERRAIN_BLOCK_NODES - 1) * d_lon;
    
    // Квантування координат до південно-західного кута блоку
    int32_t lat_sw = lat - (lat % block_span_lat);
    int32_t lon_sw = lon - (lon % block_span_lon);
    if (lat < 0 && (lat % block_span_lat != 0)) lat_sw -= block_span_lat;
    if (lon < 0 && (lon % block_span_lon != 0)) lon_sw -= block_span_lon;
    
    terrain_block_t *block = find_block(cache, lat_sw, lon_sw);
    if (!block) {
        return false; // Дані відсутні у кеші
    }
    
    // Позиція всередині 4x4 матриці
    int32_t rel_lat = lat - lat_sw;
    int32_t rel_lon = lon - lon_sw;
    
    int cell_row = rel_lat / d_lat;
    int cell_col = rel_lon / d_lon;
    if (cell_row > 2) cell_row = 2;
    if (cell_col > 2) cell_col = 2;
    
    // Чотири кутові висоти комірки
    int16_t h00 = block->data[cell_row * 4 + cell_col];
    int16_t h10 = block->data[cell_row * 4 + (cell_col + 1)];
    int16_t h01 = block->data[(cell_row + 1) * 4 + cell_col];
    int16_t h11 = block->data[(cell_row + 1) * 4 + (cell_col + 1)];
    
    if (h00 == TERRAIN_NO_DATA_VALUE || h10 == TERRAIN_NO_DATA_VALUE ||
        h01 == TERRAIN_NO_DATA_VALUE || h11 == TERRAIN_NO_DATA_VALUE) {
        return false;
    }
    
    // Нормалізовані координати всередині комірки [0.0 .. 1.0]
    float u = (float)(rel_lon - cell_col * d_lon) / (float)d_lon;
    float v = (float)(rel_lat - cell_row * d_lat) / (float)d_lat;
    
    // Білінійна інтерполяція
    *out_height = (1.0f - u) * (1.0f - v) * (float)h00 +
                  u * (1.0f - v) * (float)h10 +
                  (1.0f - u) * v * (float)h01 +
                  u * v * (float)h11;
    return true;
}
