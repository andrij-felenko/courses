int main(void) {
    InvalidationEngine* eng = engine_create();

    const char* tags_laptop[] = {"item:42", "brand:apple", "cat:laptops"};
    const char* tags_phone[]  = {"item:99", "brand:apple", "cat:phones"};
    const char* tags_catalog[] = {"cat:laptops", "page:1"};

    // Заповнюємо кеш записами з перехресними тегами
    engine_set(eng, "/product/42", "MacBook Pro M3", 300, tags_laptop, 3);
    engine_set(eng, "/product/99", "iPhone 15", 300, tags_phone, 3);
    engine_set(eng, "/catalog/laptops", "List of 20 Laptops", 300, tags_catalog, 2);

    printf("1. Інвалідація товару #42 за тегом 'item:42'...\n");
    int purged = engine_purge_tag(eng, "item:42");
    printf("   Очищено ключів: %d (очікується 1: /product/42)\n", purged);

    printf("2. Інвалідація всієї категорії за тегом 'cat:laptops'...\n");
    purged = engine_purge_tag(eng, "cat:laptops");
    printf("   Очищено ключів: %d (очікується 1: /catalog/laptops)\n", purged);

    printf("3. Тестування Generation Bumping для тенанта 'tenant_10'...\n");
    uint64_t gen1 = engine_get_generation(eng, "tenant_10");
    printf("   Початкова епоха: v%" PRIu64 "\n", gen1);
    uint64_t gen2 = engine_bump_generation(eng, "tenant_10");
    printf("   Нова епоха після O(1) скидання: v%" PRIu64 "\n", gen2);

    engine_free(eng);
    return 0;
}
