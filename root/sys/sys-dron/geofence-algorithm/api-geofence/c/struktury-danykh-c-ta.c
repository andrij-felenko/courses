#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define GEOFENCE_MAX_POLYGON_VERTICES 32
#define GEOFENCE_MAX_POLYGONS         16
#define GEOFENCE_MAX_CYLINDERS        16

// Коди результатів виконання функцій бібліотеки
typedef enum {
    GEOFENCE_OK                     = 0,
    GEOFENCE_ERR_NULL_PTR           = -1,
    GEOFENCE_ERR_INVALID_PARAM      = -2,
    GEOFENCE_ERR_CAPACITY_EXCEEDED  = -3,
    GEOFENCE_ERR_DEGENERATE_POLYGON = -4,
    GEOFENCE_ERR_ALTITUDE_INVERTED  = -5
} GeofenceResult;

// Функціональний тип просторової зони
typedef enum {
    GEOFENCE_ZONE_KEEP_IN  = 0, // Зона дозволеного польоту (впускна)
    GEOFENCE_ZONE_KEEP_OUT = 1  // Зона заборони польоту (виключна)
} GeofenceZoneType;

// Топологічний стан системи просторового нагляду
typedef enum {
    GEOFENCE_STATE_SAFE    = 0, // Апарат у дозволеній зоні, загрози відсутні
    GEOFENCE_STATE_WARNING = 1, // Наближення до межі (смуга запасу / низький TTB)
    GEOFENCE_STATE_BREACH  = 2  // Межу порушено або вихід неминучий
} GeofenceState;

// Рекомендована дія для підсистеми захисту від відмов (Failsafe)
typedef enum {
    GEOFENCE_ACTION_NONE       = 0, // Дія не потрібна (нормальний політ)
    GEOFENCE_ACTION_WARN       = 1, // Сповістити оператора через телеметрію
    GEOFENCE_ACTION_BRAKE_HOLD = 2, // Екстрена зупинка та перехід у зависання
    GEOFENCE_ACTION_RTL        = 3, // Повернення на точку старту (Home)
    GEOFENCE_ACTION_SMART_RTL  = 4, // Повернення безпечним пройденим треком
    GEOFENCE_ACTION_LAND       = 5, // Негайна вертикальна посадка на місці
    GEOFENCE_ACTION_TERMINATE  = 6  // Аварійна відсічка тяги / викид парашута
} GeofenceAction;

// Геодезична точка у форматі WGS84 1e7
typedef struct {
    int32_t lat_e7; // Широта, помножена на 1e7
    int32_t lon_e7; // Довгота, помножена на 1e7
    float   alt_m;  // Висота над рівнем моря або точкою старту (метри)
} GeofencePointGeo;

// Вектор швидкості у системі NED (метри на секунду)
typedef struct {
    float vx; // Швидкість на північ (North)
    float vy; // Швидкість на схід (East)
    float vz; // Вертикальна швидкість (Down, додатна вниз)
} GeofenceVelocityNed;

// Габаритний контейнер AABB (Axis-Aligned Bounding Box)
typedef struct {
    int32_t min_lat;
    int32_t max_lat;
    int32_t min_lon;
    int32_t max_lon;
} GeofenceAABB;

// Полігональна зона
typedef struct {
    GeofencePointGeo vertices[GEOFENCE_MAX_POLYGON_VERTICES];
    uint8_t          vertex_count;
    GeofenceZoneType zone_type;
    float            alt_min_m;
    float            alt_max_m;
    GeofenceAABB     aabb;
    bool             enabled;
} GeofencePolygon;

// Циліндрична зона
typedef struct {
    GeofencePointGeo center;
    float            radius_m;
    float            alt_min_m;
    float            alt_max_m;
    GeofenceZoneType zone_type;
    bool             enabled;
} GeofenceCylinder;

// Налаштування кінематичного аналізу
typedef struct {
    float max_braking_accel_mps2; // Граничне безпечне уповільнення (м/с²)
    float system_latency_s;       // Затримка фільтрації та контуру стабілізації (с)
    float static_margin_m;        // Статична буферна смуга (метри)
    float warning_time_s;         // Часовий поріг попередження TTB (секунди)
} GeofenceConfig;

// Звіт за підсумками навігаційного циклу
typedef struct {
    GeofenceState  state;
    GeofenceAction recommended_action;
    float          distance_to_boundary_m;
    float          time_to_breach_s;
    int16_t        critical_zone_index;
    bool           is_keep_in_breach;
    bool           is_keep_out_breach;
    bool           is_altitude_breach;
} GeofenceReport;

// Основна структура стану бібліотеки геозонування
typedef struct {
    GeofencePolygon  polygons[GEOFENCE_MAX_POLYGONS];
    GeofenceCylinder cylinders[GEOFENCE_MAX_CYLINDERS];
    uint8_t          polygon_count;
    uint8_t          cylinder_count;
    GeofenceConfig   config;
    GeofenceReport   last_report;
} GeofenceEngine;
