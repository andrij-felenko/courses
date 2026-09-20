typedef struct {
    device_repository_t repo;
    void* ctx;
    void (*cleanup)(void* ctx);
} test_fixture_t;

typedef test_fixture_t (*fixture_factory_t)(void);

void verify_device_repository_contract(fixture_factory_t create_fixture) {
    test_fixture_t f = create_fixture();

    // Збереження та зчитування стану
    device_t dev = { .id = "dev-1", .name = "Клапан", .is_on = true };
    assert(f.repo.save(f.ctx, &dev) == 0);
    device_t* found = f.repo.find_by_id(f.ctx, "dev-1");
    assert(found != NULL && found->is_on == true);
    free(found);

    // Пошук неіснуючого запису
    assert(f.repo.find_by_id(f.ctx, "absent") == NULL);

    if (f.cleanup) {
        f.cleanup(f.ctx);
    }
}
