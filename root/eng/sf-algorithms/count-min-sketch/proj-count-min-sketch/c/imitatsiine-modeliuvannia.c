int main(void) {
    /* Ініціалізація ескізу з параметрами epsilon = 0.001, delta = 0.01 */
    cm_sketch_t *sketch = cm_create(0.001, 0.01);
    if (!sketch) {
        fprintf(stderr, "Помилка виділення пам'яті для ескізу\n");
        return 1;
    }
    
    printf("Розмір матриці Count-Min Sketch: %u стовпців x %u рядків (пам'ять: %.2f КБ)\n",
           sketch->width, sketch->depth,
           (sketch->width * sketch->depth * sizeof(uint32_t)) / 1024.0);
    
    /* Імітація потоку з відомими точними частотами */
    const char *heavy_ip = "192.168.1.100";
    const char *medium_ip = "10.0.0.5";
    const char *rare_ip = "172.16.0.1";
    
    cm_update_conservative(sketch, heavy_ip, strlen(heavy_ip), 50000);
    cm_update_conservative(sketch, medium_ip, strlen(medium_ip), 5000);
    cm_update_conservative(sketch, rare_ip, strlen(rare_ip), 10);
    
    /* Додавання фонового шуму (944 990 випадкових подій) */
    char noise_ip[32];
    for (int i = 0; i < 944990; ++i) {
        snprintf(noise_ip, sizeof(noise_ip), "10.1.%d.%d", (i / 256) % 256, i % 256);
        cm_update_conservative(sketch, noise_ip, strlen(noise_ip), 1);
    }
    
    printf("\nРезультати оцінки частот:\n");
    printf("IP %-15s | Істинна частота: %6d | Оцінка ескізу: %6u\n",
           heavy_ip, 50000, cm_estimate(sketch, heavy_ip, strlen(heavy_ip)));
    printf("IP %-15s | Істинна частота: %6d | Оцінка ескізу: %6u\n",
           medium_ip, 5000, cm_estimate(sketch, medium_ip, strlen(medium_ip)));
    printf("IP %-15s | Істинна частота: %6d | Оцінка ескізу: %6u\n",
           rare_ip, 10, cm_estimate(sketch, rare_ip, strlen(rare_ip)));
    
    cm_destroy(sketch);
    return 0;
}
