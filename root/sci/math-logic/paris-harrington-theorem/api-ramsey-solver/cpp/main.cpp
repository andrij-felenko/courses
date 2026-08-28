PhConfig config;
config.target_m = 3;
config.num_colors = 2;

PhResult result = compute_bound(config);
if (result.status == PhStatus::Success) {
    std::cout << "Обчислено поріг PH: " << result.computed_N
              << " за " << result.execution_time_sec << " сек.\n";
} else if (result.status == PhStatus::ErrorTimeout) {
    std::cerr << "Обчислення перервано за тайм-аутом.\n";
}
