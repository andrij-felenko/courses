/* Клієнтська функція порівняння для явного впорядкування */
int compare_by_priority(const void *a, const void *b) {
    const ServiceEndpoint *ea = (const ServiceEndpoint *)a;
    const ServiceEndpoint *eb = (const ServiceEndpoint *)b;
    if (ea->priority > eb->priority) return -1;
    if (ea->priority < eb->priority) return 1;
    return strcmp(ea->name, eb->name);
}

void client_process_endpoints(EndpointRegistry *reg) {
    ServiceEndpoint list[MAX_ITEMS];
    size_t count = endpoint_registry_fetch(reg, list, MAX_ITEMS);

    /* СТІЙКИЙ КЛІЄНТ: не покладається на випадковий порядок із API,
       а явно сортує масив за пріоритетом перед вибором лідера */
    qsort(list, count, sizeof(ServiceEndpoint), compare_by_priority);

    if (count > 0) {
        /* Найвищий за пріоритетом ендпоінт гарантовано буде на позиції 0 */
    }
}
