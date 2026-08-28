/**
 * @file acoustics_api.h
 * @brief Low-level C API for high-precision acoustic calculations
 */

#ifndef ACOUSTICS_API_H
#define ACOUSTICS_API_H

#include <stdint.h>
#include <stddef.h>

#define ACOUSTICS_AIR_DRY_0C_SPEED 331.45
#define ACOUSTICS_WATER_FRESH_20C_SPEED 1482.3

typedef int32_t acoustics_status_t;

#define ACOUSTICS_SUCCESS            0
#define ACOUSTICS_ERR_NULL_POINTER -101
#define ACOUSTICS_ERR_RANGE        -102
#define ACOUSTICS_ERR_MATH_DOMAIN  -103

typedef struct {
    double temp_k;      /**< Absolute temperature in Kelvin (> 0) */
    double pressure_pa; /**< Static pressure in Pascals (> 0) */
    double humidity_rh; /**< Relative humidity in percent [0..100] */
    double co2_ppm;     /**< Carbon dioxide concentration in ppm (default 400.0) */
} acoustics_air_config_t;

typedef struct {
    double speed_m_s;         /**< Calculated speed of sound in m/s */
    double specific_imp_rayl; /**< Specific acoustic impedance in Pa*s/m */
    double density_kg_m3;     /**< Medium density in kg/m^3 */
} acoustics_prop_result_t;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Calculate acoustic properties of humid air per ISO 9613-1
 * @param[in]  cfg Pointer to air configuration structure
 * @param[out] res Pointer to output properties structure
 * @return ACOUSTICS_SUCCESS on success, negative error code on failure
 */
acoustics_status_t acoustics_calc_air_props(
    const acoustics_air_config_t* cfg,
    acoustics_prop_result_t* res
);

/**
 * @brief Calculate speed of sound in seawater using UNESCO 1981 equation
 * @param[in]  temp_c Temperature in degrees Celsius [-2.0 .. 40.0]
 * @param[in]  salinity_ppt Salinity in parts per thousand [0.0 .. 42.0]
 * @param[in]  depth_m Depth in meters [0.0 .. 10000.0]
 * @param[out] out_speed_m_s Output pointer for speed of sound in m/s
 * @return ACOUSTICS_SUCCESS on success, negative error code on failure
 */
acoustics_status_t acoustics_calc_seawater_speed(
    double temp_c,
    double salinity_ppt,
    double depth_m,
    double* out_speed_m_s
);

#ifdef __cplusplus
}
#endif

#endif /* ACOUSTICS_API_H */
