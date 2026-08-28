/* c */
bpp_status_t bpp_init(bpp_config_t* config);

bpp_status_t bpp_execute(const bpp_config_t* config, 
                         const uint8_t* data, 
                         size_t len, 
                         bpp_execution_stats_t* stats);

uint32_t bpp_calculate_required_rounds(double max_eps, double delta_gap);

void bpp_cleanup(bpp_config_t* config);
