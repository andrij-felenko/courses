#include "order_domain.hpp"
#include "in_memory_order_adapter.hpp"
#include "sql_order_adapter.hpp"
#include "leaky_storage_port.hpp"

#include <cassert>
#include <iomanip>
#include <iostream>
#include <string>

namespace {

void testInMemoryFulfillmentScenario() {
    std::cout << "\n============================================================\n";
    std::cout << "[ТЕСТ 1] Сценарій комплектації з InMemoryOrderFulfillmentAdapter\n";
    std::cout << "============================================================\n";

    // 1. Створюємо ізольований in-memory адаптер (двійник)
    InMemoryOrderFulfillmentAdapter in_memory_port;

    // 2. Наповнюємо початковими тестовими сутностями
    in_memory_port.addOrder(Order(
        OrderId("ORD-101"),
        "Олексій Бондаренко",
        1550.00,
        {"Механічна клавіатура", "Килимок для миші"}
    ));
    in_memory_port.addOrder(Order(
        OrderId("ORD-102"),
        "Марина Дмитренко",
        720.50,
        {"USB-концентратор"}
    ));
    // Замовлення, яке вже має статус Fulfilled — сервіс повинен його пропустити
    in_memory_port.addOrder(Order(
        OrderId("ORD-103"),
        "Сергій Ткач",
        300.00,
        {"Кабель HDMI"},
        OrderStatus::Fulfilled
    ));

    assert(in_memory_port.countByStatus(OrderStatus::Pending) == 2);
    assert(in_memory_port.countByStatus(OrderStatus::Fulfilled) == 1);
    std::cout << "Початковий стан двійника: 2 Pending, 1 Fulfilled.\n";

    // 3. Композиція системи: інжектуємо двійник у сервіс
    OrderFulfillmentService fulfillment_service(in_memory_port);

    // 4. Обробка першого замовлення
    auto processed_1 = fulfillment_service.processNextOrder();
    assert(processed_1.has_value());
    assert(processed_1->value() == "ORD-101");
    std::cout << "-> Оброблено замовлення: " << processed_1->value() << "\n";

    // Перевіряємо, що ORD-101 тепер Fulfilled
    auto order_101 = in_memory_port.findById(OrderId("ORD-101"));
    assert(order_101.has_value());
    assert(order_101->isFulfilled());

    // 5. Обробка другого замовлення
    auto processed_2 = fulfillment_service.processNextOrder();
    assert(processed_2.has_value());
    assert(processed_2->value() == "ORD-102");
    std::cout << "-> Оброблено замовлення: " << processed_2->value() << "\n";

    // 6. Спроба обробки наступного: більше немає доступних Pending замовлень
    auto processed_3 = fulfillment_service.processNextOrder();
    assert(!processed_3.has_value());
    std::cout << "-> Спроба вибірки за порожньої черги: успішно повернуто std::nullopt.\n";

    // Перевіряємо фінальний баланс статусів
    assert(in_memory_port.countByStatus(OrderStatus::Pending) == 0);
    assert(in_memory_port.countByStatus(OrderStatus::Fulfilled) == 3);

    std::cout << "[УСПІХ] Модульний тест виконано детерміновано без звернень до бази даних!\n";
}

void testSqlPersistenceAdapterScenario() {
    std::cout << "\n============================================================\n";
    std::cout << "[ТЕСТ 2] Паритет поведінки з реляційним SqlOrderFulfillmentAdapter\n";
    std::cout << "============================================================\n";

    // 1. Створюємо вторинний реляційний адаптер із розміром партії вибірки = 2
    const size_t batch_size = 2;
    SqlOrderFulfillmentAdapter sql_port(batch_size);

    // 2. Наповнюємо реляційну базу табличними даними з SQL-колонками
    sql_port.insertDirectRow({
        1001, "ORD-201", "Наталія Кравченко", 249900, "PENDING", 1, "Монітор 27 IPS"
    });
    sql_port.insertDirectRow({
        1002, "ORD-202", "Володимир Лисенко", 85000, "PENDING", 1, "Вебкамера 4K,Штатив"
    });
    sql_port.insertDirectRow({
        1003, "ORD-203", "Ярослав Мудрий", 12900, "PENDING", 1, "Підставка для навушників"
    });
    sql_port.insertDirectRow({
        1004, "ORD-204", "Анна Ярославна", 54000, "FULFILLED", 1, "Бездротова миша"
    });

    std::cout << "Реляційна таблиця ініціалізована 4 записами (3 PENDING, 1 FULFILLED).\n";

    // 3. Композиція: той самий сервіс OrderFulfillmentService працює з SQL-адаптером!
    OrderFulfillmentService fulfillment_service(sql_port);

    // 4. Виконуємо обробку всіх доступних замовлень
    size_t processed_count = fulfillment_service.processAllPendingOrders();
    assert(processed_count == 3);
    std::cout << "-> Сервіс успішно скомплектував " << processed_count << " замовлень.\n";

    // 5. Перевіряємо роботу пакетної вибірки (Batch Fetching)
    // 3 замовлення при batch_size = 2 потребують:
    // Партія 1 (2 замовлення) + Партія 2 (1 замовлення) + Партія 3 (порожня черга) = 3 звернення
    std::cout << "-> Кількість виконаних пакетних SQL-запитів: "
              << sql_port.batchFetchExecutionCount() << "\n";
    assert(sql_port.batchFetchExecutionCount() >= 2);

    // 6. Перевіряємо персистентний стан реляційних рядків після збереження
    auto row_201 = sql_port.queryDirectRow("ORD-201");
    assert(row_201.has_value());
    assert(row_201->status_code == "FULFILLED");
    assert(row_201->row_version == 2); // Версія зросла завдяки захисту від колізій
    assert(row_201->total_cents == 249900);

    auto row_202 = sql_port.queryDirectRow("ORD-202");
    assert(row_202.has_value());
    assert(row_202->status_code == "FULFILLED");
    assert(row_202->row_version == 2);

    auto row_203 = sql_port.queryDirectRow("ORD-203");
    assert(row_203.has_value());
    assert(row_203->status_code == "FULFILLED");
    assert(row_203->row_version == 2);

    auto row_204 = sql_port.queryDirectRow("ORD-204");
    assert(row_204.has_value());
    assert(row_204->status_code == "FULFILLED");
    assert(row_204->row_version == 1); // Не оброблявся сервісом — версія залишилась 1

    std::cout << "[УСПІХ] Повний функціональний паритет між in-memory двійником та SQL-адаптером!\n";
}

void testCollisionProtection() {
    std::cout << "\n============================================================\n";
    std::cout << "[ТЕСТ 3] Захист від колізій паралельного оновлення в SQL-адаптері\n";
    std::cout << "============================================================\n";

    SqlOrderFulfillmentAdapter sql_port(1);
    sql_port.insertDirectRow({
        3001, "ORD-301", "Конфліктний Клієнт", 50000, "PENDING", 1, "Тестовий товар"
    });

    // Отримуємо замовлення для обробки
    auto order_opt = sql_port.fetchNextPendingOrder();
    assert(order_opt.has_value());
    Order order = std::move(*order_opt);

    // Симулюємо зміну рядка паралельною транзакцією безпосередньо в базі
    sql_port.insertDirectRow({
        3001, "ORD-301", "Конфліктний Клієнт", 50000, "PROCESSING", 99, "Тестовий товар"
    });

    order.startProcessing();
    order.completeFulfillment();

    // Спроба збереження застарілої версії повинна викликати виняток колізії
    bool collision_detected = false;
    try {
        sql_port.save(order);
    } catch (const std::runtime_error& ex) {
        collision_detected = true;
        std::cout << "-> Очікувано зафіксовано SQL-колізію: " << ex.what() << "\n";
    }

    assert(collision_detected);
    std::cout << "[УСПІХ] Захист від колізій (Optimistic Locking) спрацював коректно!\n";
}

void printArchitecturalComparison() {
    std::cout << "\n============================================================\n";
    std::cout << "АРХІТЕКТУРНИЙ ВИСНОВОК: УСУНЕННЯ «ЗАПАХУ СХОВИЩА»\n";
    std::cout << "============================================================\n";
    std::cout << "1. Антипатерн (ILeakyOrderStoragePort):\n";
    std::cout << "   - Запити вимагали пагінації бази (limit, offset) у доменному шарі.\n";
    std::cout << "   - Сигнатури містили SqlErrorCode, вимагаючи обробки SQL-помилок у ядрі.\n";
    std::cout << "   - Транзакційні прапорці та локування рядків витікали в бізнес-логіку.\n\n";
    std::cout << "2. Чистий рольовий порт (IOrderFulfillmentPort):\n";
    std::cout << "   - Сформульований під потреби сценарію: fetchNextPendingOrder() / save().\n";
    std::cout << "   - Відсутність результату виражається чистим std::optional<Order>.\n";
    std::cout << "   - Доменне ядро не змінило жодного рядка коду при підміні адаптерів:\n";
    std::cout << "     InMemoryOrderFulfillmentAdapter <-> SqlOrderFulfillmentAdapter.\n";
    std::cout << "============================================================\n";
}

} // namespace

int main() {
    std::cout << "=== ДЕМОНСТРАЦІЯ РЕФАКТОРИНГУ: ПОРТ, ЩО ПАХНЕ СХОВИЩЕМ ===\n";

    testInMemoryFulfillmentScenario();
    testSqlPersistenceAdapterScenario();
    testCollisionProtection();
    printArchitecturalComparison();

    std::cout << "\nУсі перевірки завершено успішно!\n";
    return 0;
}
