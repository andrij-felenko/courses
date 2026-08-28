// ── Диспетчер тестування та емулятор середовища ─────────────────────────
int main() {
    std::cout << "=== СТАРТ НОВОГО РОБОЧОГО ПРОЦЕСУ ===" << std::endl;
    std::vector<WorkflowEvent> history;
    history.push_back(WorkflowStartedEvent{"order-101", "user=Andrii"});

    // ── Ітерація 1: Перший запуск на новому вузлі ────────────────────────
    std::cout << "\n[Вузол 1] Запуск виконання workflow..." << std::endl;
    {
        WorkflowContext ctx(history);
        try {
            order_fulfillment_workflow(ctx, "order-101");
        } catch (const ExecutionYieldedException&) {
            std::cout << "[Вузол 1] Процес призупинено. Заплановано нові події:" << std::endl;
            for (const auto& ev : ctx.get_new_events()) {
                if (auto sched = std::get_if<ActivityScheduledEvent>(&ev)) {
                    std::cout << "  -> Scheduled Activity: " << sched->activity_name 
                              << " (Input: " << sched->input << ")" << std::endl;
                    // В реальності диспетчер відправляє задачу у чергу
                    history.push_back(ev);
                }
            }
        }
    }

    // ── Емуляція виконання Activity воркером та збереження результату ──────
    std::cout << "\n[Activity Worker] Виконано ProcessPayment -> повернено 'PAYMENT_OK_#9981'" << std::endl;
    history.push_back(ActivityCompletedEvent{"ProcessPayment", "PAYMENT_OK_#9981"});

    // ── АВАРІЯ СЕРВЕРА: Вузол 1 згорів, пам'ять стерто! ──────────────────
    std::cout << "\n!!! АВАРІЯ: Сервер Вузол 1 впав. Локальний стан знищено. Перезапуск на Вузлі 2..." << std::endl;

    // ── Ітерація 2: Відновлення на Вузлі 2 через Replay ───────────────────
    std::cout << "\n[Вузол 2] Підхоплення задачі з історії (Replay). Розмір історії: " 
              << history.size() << " подій." << std::endl;
    {
        WorkflowContext ctx(history);
        try {
            order_fulfillment_workflow(ctx, "order-101");
        } catch (const ExecutionYieldedException&) {
            std::cout << "[Вузол 2] Replay успішно відновив крок 1 без повторного виклику платежу!" << std::endl;
            std::cout << "[Вузол 2] Заплановано наступний крок:" << std::endl;
            for (const auto& ev : ctx.get_new_events()) {
                if (auto sched = std::get_if<ActivityScheduledEvent>(&ev)) {
                    std::cout << "  -> Scheduled Activity: " << sched->activity_name 
                              << " (Input: " << sched->input << ")" << std::endl;
                    history.push_back(ev);
                }
            }
        }
    }

    // ── Завершення решти кроків ──────────────────────────────────────────
    history.push_back(ActivityCompletedEvent{"ReserveInventory", "INVENTORY_RESERVED"});
    history.push_back(ActivityCompletedEvent{"CreateShippingLabel", "TRACKING_UA_12345"});

    std::cout << "\n[Вузол 2] Фінальний запуск (всі кроки виконано)..." << std::endl;
    {
        WorkflowContext ctx(history);
        std::string final_result = order_fulfillment_workflow(ctx, "order-101");
        std::cout << "[Вузол 2] Результат завершення: " << final_result << std::endl;
    }

    return 0;
}
