// Крок 1: викинуто гілки фільтра й калібрування (вони робили тотожність)
int sensor_read_by_name(const char *name, float *celsius) {
    sensor_driver_t *d = find(name);
    if (!d) return -1;

    int32_t raw;
    if (d->read_raw(d->ctx, &raw) != 0) return -2;

    *celsius = (float)raw * 0.01f;   // сирі сотні °C → градуси
    return 0;
}
