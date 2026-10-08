#include <stdint.h>
#include <math.h>

typedef struct {
    uint32_t single_turn_bits;
    uint32_t multi_turn_bits;
    float gear_ratio;
} encoder_config_t;

typedef struct {
    int64_t total_counts;
    float raw_angle_rad;
    float output_angle_rad;
    int32_t turn_count;
} encoder_state_t;

encoder_state_t decode_multiturn_frame(uint64_t raw_frame, const encoder_config_t *config) {
    encoder_state_t state;
    uint64_t st_mask = (1ULL << config->single_turn_bits) - 1ULL;
    
    uint32_t single_turn = (uint32_t)(raw_frame & st_mask);
    uint32_t multi_turn = (uint32_t)(raw_frame >> config->single_turn_bits);
    
    uint32_t total_bits = config->single_turn_bits + config->multi_turn_bits;
    uint64_t total_counts = ((uint64_t)multi_turn << config->single_turn_bits) | single_turn;
    
    state.total_counts = (int64_t)total_counts;
    state.turn_count = (int32_t)multi_turn;
    state.raw_angle_rad = (float)(2.0 * M_PI * total_counts / (double)(1ULL << total_bits));
    state.output_angle_rad = state.raw_angle_rad / config->gear_ratio;
    
    return state;
}
