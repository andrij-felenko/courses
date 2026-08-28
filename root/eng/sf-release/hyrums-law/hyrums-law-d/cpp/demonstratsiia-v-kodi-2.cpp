/* Стійкий клієнтський обробник на C++ */
#include <algorithm>
#include <iostream>

void client_process_endpoints(EndpointRegistry& registry) {
    std::vector<ServiceEndpoint> list = registry.fetch_endpoints();

    /* СТІЙКИЙ КЛІЄНТ: явно виражає вимогу до порядку через std::sort,
       замість очікування недекларованого детермінізму від сервера */
    std::sort(list.begin(), list.end(), [](const auto& a, const auto& b) {
        if (a.priority != b.priority) {
            return a.priority > b.priority;
        }
        return a.name < b.name;
    });

    if (!list.empty()) {
        // Гарантована детермінована робота за будь-яких перестановок у бекенді
    }
}
