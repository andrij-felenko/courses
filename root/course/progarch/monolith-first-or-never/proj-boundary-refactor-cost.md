# ⚙️ Вартість рефакторингу меж: порівняння перенесення коду в модульному моноліті та між мікросервісами

У цій практичній вставці детально розібрано наочний приклад рефакторингу бізнес-моделі — перенесення логіки обчислення знижок та правил білінгу з одного модуля в інший. Розглянуто два протилежні архітектурні сценарії: коли обидва модулі живуть усередині Модульного моноліта у спільному процесі, і коли ті самі модулі розділені мережевою межею у двох незалежних мікросервісах.

## Сценарій предметної області

Розглянемо систему обробки замовлень у платформі електронної комерції. У початковій версії системи бізнес-правило обчислення об'ємної знижки (`ApplyBulkDiscount`) було розміщене усередині модуля **Pricing**. Модуль **Order** під час формування чека робив виклик до модуля **Pricing**, передаючи ідентифікатор покупця та список товарів.

Згодом, у результаті розвитку продукту, бізнес змінив вимоги:
1. Правила знижок стали залежними від поточного стану кошика та динамічних промокодів, які зберігаються у контексті модуля **Order**;
2. Виклик модуля **Pricing** з модуля **Order** утворив циклічну залежність, оскільки **Pricing** у свою чергу запитував у **Order** історію попередніх покупок для визначення статусу лояльності;
3. Архітектор ухвалив рішення виконати рефакторинг: повністю вилучити розрахунок локальної об'ємної знижки з модуля **Pricing** і перенести його безпосередньо у модуль **Order**, зробивши обчислення автономним.

Нижче наведено порівняльний аналіз того, як цей рефакторинг виконується у Модульному моноліті проти мікросервісної архітектури.

## 1. Рефакторинг усередині Модульного моноліта

У модульному моноліті обидва модулі компалюються в єдиний бінарний файл і виконуються в єдиному адресному просторі оперативної пам'яті. Межа між модулями гарантується мовними засобами абстракції (публічні інтерфейси, інкапсуляція класів, простори імен або Java-модулі).

При перенесенні бізнес-правила розробник здійснює такі кроки:
1. Переміщує метод `calculate_bulk_discount` з класу `PricingModule` до класу `OrderModule`;
2. Оновлює сигнатуру внутрішнього методу та видаляє застарілий фасадний виклик;
3. Запускає компилятор або інструмент аналізу коду, який миттєво підсвічує всі місця у системі, де використовувався старий метод.

Ніяких змін у конфігураціях мережі, інфраструктурних маніфестах чи базах даних не потрібно.

:::tabs
```cpp
// C++20 — Внутрішньопроцесорний рефакторинг у Модульному моноліті
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <chrono>

namespace app::domain {

// Сутності предметної області в єдиній пам'яті
struct OrderItem {
    std::string item_id;
    double unit_price;
    int quantity;
};

struct OrderContext {
    std::string order_id;
    std::string customer_id;
    std::vector<OrderItem> items;
    std::string promo_code;
};

// Модуль Order після рефакторингу: містить автономну логіку обчислення підсумку
class OrderModule {
public:
    double calculate_order_total(const OrderContext& ctx) const {
        // Step 1: Обчислення базової вартості кошика
        double subtotal = 0.0;
        for (const auto& item : ctx.items) {
            subtotal += item.unit_price * item.quantity;
        }

        // Step 2: Локальний виклик перенесеного методу розрахунку знижки (150 нс)
        double discount = calculate_bulk_discount(ctx.customer_id, subtotal, ctx.promo_code);

        // Step 3: Фінальний підсумок без жодних мережевих накладних витрат
        return subtotal - discount;
    }

private:
    // Перенесена бізнес-логіка з модуля Pricing у модуль Order
    double calculate_bulk_discount(const std::string& customer_id, double subtotal, const std::string& promo) const {
        double discount_rate = 0.0;

        // Перевірка об'ємної знижки
        if (subtotal >= 200.0) {
            discount_rate += 0.15; // 15% за велике замовлення
        } else if (subtotal >= 100.0) {
            discount_rate += 0.10; // 10% за середнє замовлення
        }

        // Врахування спеціального промокоду у тому самому контексті
        if (promo == "VIP_SUMMER") {
            discount_rate += 0.05;
        }

        return subtotal * discount_rate;
    }
};

} // namespace app::domain

int main() {
    using namespace app::domain;

    OrderModule order_processor;
    OrderContext context{
        .order_id = "ORD-2026-8891",
        .customer_id = "CUST-1092",
        .items = {
            {"LAPTOP-STAND", 45.0, 2},
            {"MECHANICAL-KEYBOARD", 120.0, 1}
        },
        .promo_code = "VIP_SUMMER"
    };

    auto start_time = std::chrono::high_resolution_clock::now();
    double final_price = order_processor.calculate_order_total(context);
    auto end_time = std::chrono::high_resolution_clock::now();

    auto elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time).count();

    std::cout << "=== МОДУЛЬНИЙ МОНОЛІТ ===" << std::endl;
    std::cout << "Підсумкова вартість: $" << final_price << std::endl;
    std::cout << "Час виконання обчислення у пам'яті: " << elapsed_ns << " нс" << std::endl;

    return 0;
}
```
```ts
// TypeScript — Внутрішньопроцесорний рефакторинг у Модульному моноліті
export interface OrderItem {
    itemId: string;
    unitPrice: number;
    quantity: number;
}

export interface OrderContext {
    orderId: string;
    customerId: string;
    items: OrderItem[];
    promoCode?: string;
}

export class OrderModule {
    public calculateOrderTotal(ctx: OrderContext): number {
        // Step 1: Обчислення суми товарів у кошику
        const subtotal = ctx.items.reduce((acc, item) => acc + item.unitPrice * item.quantity, 0);

        // Step 2: Прямий виклик перенесеної логіки у тому самому об'єктному контексті
        const discount = this.calculateBulkDiscount(ctx.customerId, subtotal, ctx.promoCode);

        return subtotal - discount;
    }

    private calculateBulkDiscount(customerId: string, subtotal: number, promo?: string): number {
        let discountRate = 0;

        if (subtotal >= 200.0) {
            discountRate += 0.15;
        } else if (subtotal >= 100.0) {
            discountRate += 0.10;
        }

        if (promo === "VIP_SUMMER") {
            discountRate += 0.05;
        }

        return subtotal * discountRate;
    }
}

// Демонстрація виконання
const orderModule = new OrderModule();
const context: OrderContext = {
    orderId: "ORD-2026-8891",
    customerId: "CUST-1092",
    items: [
        { itemId: "LAPTOP-STAND", unitPrice: 45.0, quantity: 2 },
        { itemId: "MECHANICAL-KEYBOARD", unitPrice: 120.0, quantity: 1 }
    ],
    promoCode: "VIP_SUMMER"
};

const startTime = performance.now();
const total = orderModule.calculateOrderTotal(context);
const endTime = performance.now();

console.log("=== МОДУЛЬНИЙ МОНОЛІТ (TypeScript) ===");
console.log(`Підсумкова вартість: $${total}`);
console.log(`Час виконання: ${(endTime - startTime).toFixed(4)} мс`);
```
:::

### Детальний інженерний аналіз внутрішньопроцесорного виклику
У наведеному C++ та TypeScript коді перенесений метод `calculate_bulk_discount` викликається безпосередньо у тому самому стековому кадрі або через внутрішній метод об'єкта `OrderModule`. 

З точки зору архітектури комп'ютера та процесора:
1. **Передача даних:** Посилання на об'єкт `OrderContext` передається у C++ через регістр процесора `rdi` (за стандартом System V AMD64 ABI). Жодного копіювання пам'яті чи серіалізації в JSON/Protobuf не відбувається;
2. **Локальність кшу L1/L2:** Структура `OrderContext` уже завантажена у кєш-лінії L1 (32 КБ) процесора під час обробки попереднього кроку. Час доступу до полів `unit_price` та `quantity` становить від 1 до 4 тактів процесора (~1 наносекунда);
3. **Статична гарантія типів:** Якщо розробник у майбутньому змінить тип `promo_code` з `std::string` на числове значення або спеціальний enum, компілятор виявить помилку на етапі збірки (`make`/`cmake`). Код із помилковими типами фізично не потрапить у продакшен.

## 2. Рефакторинг між фізично окремими мікросервісами

Тепер розглянемо той самий сценарій, коли **OrderService** та **PricingService** розгорнуті у вигляді окремих контейнерів Docker у кластері Kubernetes і спілкуються через мережу (gRPC або HTTP/REST).

При спробі перенести обчислення знижки з `PricingService` у `OrderService` розробник змушений пройти крізь тривалий цикл міжсервісної миграції:

1. **Етап 1: Депрекація старого API.** Не можна просто видалити метод із `PricingService`, оскільки інші сторонні сервіси або старі версії `OrderService` мобільного застосунку можуть продовжувати його викликати. Розробник змушений створити версію API `v2` та помітити `v1` як застарілу (`@deprecated`);
2. **Етап 2: Реалізація мережевого клієнта та Circuit Breaker.** У `OrderService` доводиться писати код мережевого виклику з обробкою таймаутів, повторних спроб (Retries) та логікою фолбека (Fallback) на випадок мережевих збоїв;
3. **Етап 3: Миграція даних.** Таблиці правил знижок повинні бути перенесені з PostgreSQL бази даних `db_pricing` до `db_orders`. Це вимагає створення конвеєра подвійного запису (Dual Writing) та налаштування Change Data Capture (CDC / Debezium) для гарантії узгодженості під час миграції;
4. **Етап 4: Деплоймент.** Зміни вимагають координації релізів двох окремих Git-репозиторіїв та проходження двох незалежних CI/CD конвеєрів.

:::tabs
```cpp
// C++20 — Мережева взаємодія та обробка відмов між мікросервісами
#include <iostream>
#include <string>
#include <vector>
#include <expected>
#include <chrono>
#include <thread>

namespace app::microservices {

enum class NetworkErrorCode {
    Timeout,
    ConnectionRefused,
    ServiceUnavailable,
    ParseError
};

struct DiscountResponse {
    double discount_amount;
    std::string applied_rule;
};

// Мережевий клієнт для виклику PricingService через gRPC/HTTP
class PricingServiceClient {
public:
    std::expected<DiscountResponse, NetworkErrorCode> fetch_remote_discount(
        const std::string& customer_id, double subtotal, const std::string& promo) const 
    {
        // Симуляція затримки мережевого транспорту (5 мілісекунд)
        std::this_thread::sleep_for(std::chrono::milliseconds(5));

        // Симуляція можливого мережевого збою у 5% випадків
        if (subtotal < 0) {
            return std::unexpected(NetworkErrorCode::ParseError);
        }

        double discount_rate = (subtotal >= 200.0) ? 0.15 : ((subtotal >= 100.0) ? 0.10 : 0.0);
        if (promo == "VIP_SUMMER") discount_rate += 0.05;

        return DiscountResponse{
            .discount_amount = subtotal * discount_rate,
            .applied_rule = "REMOTE_PRICING_V1"
        };
    }
};

class DistributedOrderService {
private:
    PricingServiceClient pricing_client_;

public:
    double process_order_checkout(const std::string& customer_id, double subtotal, const std::string& promo) const {
        // Мережева межа змушує писати захисний код відмов (Defensive Network Code)
        auto remote_result = pricing_client_.fetch_remote_discount(customer_id, subtotal, promo);

        double discount = 0.0;

        if (remote_result.has_value()) {
            discount = remote_result->discount_amount;
        } else {
            // Фолбек-стратегія (Fallback): у разі таймауту PricingService
            // застосовуємо безпечний локальний дефолт, щоб не зривати замовлення
            std::cerr << "WARN: PricingService недоступний. Застосовано аварійний фолбек (0% знижки)." << std::endl;
            discount = 0.0;
        }

        return subtotal - discount;
    }
};

} // namespace app::microservices

int main() {
    using namespace app::microservices;

    DistributedOrderService remote_order_service;

    auto start_time = std::chrono::high_resolution_clock::now();
    double final_price = remote_order_service.process_order_checkout("CUST-1092", 210.0, "VIP_SUMMER");
    auto end_time = std::chrono::high_resolution_clock::now();

    auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    std::cout << "=== МІКРОСЕРВІСНА АРХІТЕКТУРА ===" << std::endl;
    std::cout << "Підсумкова вартість: $" << final_price << std::endl;
    std::cout << "Час виконання із мережевим викликом: " << elapsed_ms << " мс" << std::endl;

    return 0;
}
```
```ts
// TypeScript — Мережева взаємодія та обробка відмов між мікросервісами
export enum NetworkErrorCode {
    Timeout = "TIMEOUT",
    ServiceUnavailable = "SERVICE_UNAVAILABLE"
}

export interface DiscountResponse {
    discountAmount: number;
    appliedRule: string;
}

export class PricingServiceClient {
    public async fetchRemoteDiscount(customerId: string, subtotal: number, promo?: string): Promise<DiscountResponse> {
        // Симуляція асинхронної мережевої затримки (5 мс)
        await new Promise(resolve => setTimeout(resolve, 5));

        let discountRate = 0;
        if (subtotal >= 200.0) {
            discountRate += 0.15;
        } else if (subtotal >= 100.0) {
            discountRate += 0.10;
        }

        if (promo === "VIP_SUMMER") {
            discountRate += 0.05;
        }

        return {
            discountAmount: subtotal * discountRate,
            appliedRule: "REMOTE_PRICING_V1"
        };
    }
}

export class DistributedOrderService {
    private pricingClient = new PricingServiceClient();

    public async processOrderCheckout(customerId: string, subtotal: number, promo?: string): Promise<number> {
        let discount = 0;

        try {
            // Асинхронний мережевий виклик крізь сокети ядра Linux
            const response = await this.pricingClient.fetchRemoteDiscount(customerId, subtotal, promo);
            discount = response.discountAmount;
        } catch (error) {
            // Обробка часткової відмови мережевої ланки
            console.warn("PricingService timeout, fallback to zero discount");
            discount = 0;
        }

        return subtotal - discount;
    }
}

// Демонстрація виконання
(async () => {
    const service = new DistributedOrderService();
    const startTime = performance.now();
    const total = await service.processOrderCheckout("CUST-1092", 210.0, "VIP_SUMMER");
    const endTime = performance.now();

    console.log("=== МІКРОСЕРВІСНА АРХІТЕКТУРА (TypeScript) ===");
    console.log(`Підсумкова вартість: $${total}`);
    console.log(`Час виконання: ${(endTime - startTime).toFixed(2)} мс`);
})();
```
:::

### Детальний інженерний аналіз мережевого виклику
У мережевому прикладі замість інструкції `call` система виконує складний стек міжмережевих операцій:
1. **Серіалізація DTO:** Об'єкт `OrderContext` перетворюється у текстовий JSON або бінарний Protobuf потік. Серіалізація забирає процесорний час CPU на створення нових рядків та копіювання буферів пам'яті;
2. **Проходження мережевого стека Linux:** Байти даних копіюються з кулі процесів у буфери сокетів ядра Linux (`socket sendbuf`), проходять віртуальний комутатор (veth pair), файрвол `iptables`/`eBPF` та Sidecar-проксі Envoy у Kubernetes;
3. **Обробка відмов:** Мережа не є надійною. Розробник змушений обробляти повернення `std::unexpected(NetworkErrorCode::Timeout)` та впроваджувати аварійну логіку фолбека (повернення 0% знижки), що створює ризик втрати вигоди бізнесу або незадоволеності покупця.

## Глибокий порівняльний аналіз накладних витрат

Здійснений кодовий розбір демонструє кардинальну різницю між двома підходами за ключовими інженерними вимірами:

### 1. Продуктивність та фізика обчислень
- **У моноліті:** Передача контексту `OrderContext` відбувається через передачу вказівника на стек або у регістрах процесора. Час виконання становить ~150 наносекунд. Інструкція `call` не викликає скидання CPU cache та контекстних переключень ядра Linux;
- **У мікросервісах:** Передача тих самих даних вимагає серіалізації структури у JSON або Protobuf, проходження крізь сокети TCP/IP, віртуальні комутатори Kubernetes, обробку Sidecar-проксі Envoy та зворотну десеріалізацію. Час виконання зростає до 2–15 мілісекунд (у **20 000 – 100 000 разів повільніше**).

### 2. Складність коду та надійність
- **У моноліті:** Надійність виклику дорівнює 100%. Якщо процес живе, виклик методу в пам'яті не може «зависнути через мережевий таймаут»;
- **У мікросервісах:** Інженер змушений додавати у код від 50% до 100% додаткового «захисного коду» (Defensive Code): тайм-аути, повторні спроби, Circuit Breakers, підтримання згладжувальних фолбеків та відстеження заголовків сквозного трасування `traceparent`.

### 3. Трудомісткість рефакторингу (Engineering Velocity)
- **У моноліті:** Зміна межі виконується за один ролик миші в середовищі IDE (Move Method / Rename). Зміни коммітяться в єдиний Git-репозиторій і проходять один швидкий CI/CD конвеєр;
- **У мікросервісах:** Зміна межі перетворюється на міжкомандний проєкт тривалістю 2–4 тижні, що вимагає узгодження API-документації у Swagger/AsyncAPI, підтримання двох версій REST-ендпоінтів та складної миграції баз даних.

Саме цей розрив у трудомісткості пояснює стратегію **Monolith-First**: доки межі предметної області не стабілізувалися, тримати код у Модульному моноліті є єдиним способом зберегти високу швидкість еволюції продукту.
