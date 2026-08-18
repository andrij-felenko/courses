# ⚙️ Маршрутизатор гео-запитів та гарантія Read-After-Write

Реалізація міжрегіонального маршрутизатора запитів (Geo-Aware Request Router) розв'язує фундаментальну проблему забезпечення причинної узгодженості (Causal Consistency) та гарантії «прочитай власний запис» (Read-After-Write, RAW) у географічно рознесених системах.

У топології Global Read / Single Write база даних джерела правди (Primary Master) розташована в одному центральному регіоні (наприклад, Франкфурт `eu-central-1`), тоді як Read-репліки розгорнуті у проміжних регіонах поруч із користувачами (наприклад, Токіо `ap-northeast-1` та Вірджинія `us-east-1`). Коли мобільний застосунок мешканця у Токіо змінює стан розумного будинку (вмикає світло або змінює цільову температуру термостата), команда запису `PUT` відправляється через міжконтинентальний канал зв'язку на Primary-базу у Франкфурт. Після успішного запису Primary-база повертає відповідь із заголовоком токена узгодженості `X-LSN`, який містить поточний номер послідовності реплікаційного журналу (Log Sequence Number, LSN).

Якщо одразу після цього користувач оновлює екран застосунку, мобільний клієнт надсилає запит читання `GET /devices` до найближчого Edge-вузла у Токіо, додаючи отриманий токен `X-LSN: 4201`. Оскільки асинхронна реплікація між Франкфуртом та Токіо займає певний час (асинхронний лаг реплікації `Δt_lag`), локальна Read-репліка у Токіо на момент надходження запиту читання може мати старий LSN `4150` (< `4201`).

Без спеціального механізму маршрутизації користувач побачить на екрані застарілий стан пристрою (світло вимкнено), що сприймається як втрата даних або збій системи. Маршрутизатор гео-запитів запобігає цьому аномальному ефекту: він перехоплює токен `X-LSN`, порівнює його з поточним зміщенням локальної репліки і, у разі виявлення лагу, приймає рішення про фолбек або блокування очікування.

## Анатомія та життєвий цикл запиту в гео-маршрутизаторі

Процес обробки кожного вхідного HTTP-запиту в міжрегіональному роутері проходить крізь п'ять послідовних етапів:

1. **Ідентифікація гео-контексту та методів (Geo-Ingress Identification):**
   На вхідному Edge-вузлі (Cloudflare Worker або Envoy Proxy) роутер аналізує IP-адресу клієнта, витягує географічний регіон (`Client Region`) та класифікує метод запиту. Усі модифікуючі методи (`POST`, `PUT`, `PATCH`, `DELETE`) маркуються як записи та відправляються прямо на Primary DB.
2. **Витягування токена причинності (Causal Token Extraction):**
   Для методів читання (`GET`, `HEAD`) роутер шукає заголовок `X-LSN` або куку `raw_token`. Якщо заголовок відсутній або термін його придатності минув (Token Expiration > 30s), запит відправляється на швидке локальне читання з репліки без додаткових перевірок.
3. **Оцінка лагу реплікації (Replica Lag Evaluation):**
   Роутер запитує поточне значення LSN з інспектора стану локальної репліки (Replication Monitor). Якщо `Replica_LSN ≥ Required_LSN`, репліка догнала стан запису, і запит виконується локально із затримкою `< 15 мс`.
4. **Прийняття рішення про фолбек (Fallback Decision Engine):**
   Якщо виявлено лаг (`Replica_LSN < Required_LSN`), роутер оцінює величина відставання та стан запобіжника (Circuit Breaker). При незначному лагу (1-2 операції) роутер виконує короткий спін-лок або `sleep(5ms)` в очікуванні надходження WAL-пакета. Якщо лаг великий, роутер перенаправляє запит на Primary DB у Франкфурт.
5. **Оновлення токена та відправка відповіді (Token Mutation & Response):**
   Після виконання запиту роутер повертає відповідь клієнту, додаючи оновлений заголовок `X-LSN` та заголовок спостережливості `X-Served-By-Region` для відстеження точок виконання.

## Стратегії захисту Primary-бази від лавинного фолбеку (Thundering Herd)

Найнебезпечнішим крайовим випадком гео-маршрутизації є **масовий фолбек (Thundering Herd Fallback)** під час мережевих збоїв між регіонами.

Якщо асинхронна реплікація між Франкфуртом та Токіо зупиняється на кілька хвилин (наприклад, через розрив оптичного кабелю або перевантаження WAL-десеріалізатора), LSN локальної репліки Токіо застрягає на рівні `4000`. Усі мільйони мобільних застосунків у Азії, які виконують записи та отримують нові токени `LSN > 4000`, при кожному наступному читанні бачать невиконання умов RAW.

Якщо гео-маршрутизатор сліпо перенаправлятиме 100% цих читань на Primary DB у Франкфурт, навантаження на Primary DB зросте у 100 разів за лічені секунди. Це спричиняє вичерпання пулу з'єднань, спалювання CPU та повний колапс джерела правди.

Для захисту від цієї катастрофи в роутер вбудовуються наступні механізми захисту:

- **Обмеження відсотка фолбеку (Fallback Rate Limiting):** Роутер дозволяє перенаправляти на Primary не більше ніж 5% від загального обсягу читань регіону. Усі інші запити отримують відповідь з застарілої локальної репліки із заголовком `X-Degraded-Read: true`.
- **Запобіжник за тривалістю лагу (Lag-Threshold Circuit Breaker):** Якщо часовий лаг реплікації перевищує критичну межу (наприклад, `Δt_lag > 10 секунд`), роутер вважає репліку відключеною, тимчасово деактивує перевірку RAW-токена та переходить у режим кінцевої узгодженості (Eventual Consistency Mode), зберігаючи працездатність Primary DB.

## Міграція тенентів без зупинки сервісу (Zero-Downtime Tenant Relocation)

У топології Active-Active з географічним партиціюванням (Home-Region Affinity) виникає задача перенесення будинку (`Home Tenant`) з одного регіону в інший (наприклад, коли власник будинку переносить реєстрацію з Франкфурта до Токіо).

Гео-маршрутизатор реалізує трифазний протокол перенесення тенента:

1. **Фаза подвійного запису (Dual-Write Phase):** Роутер направляє записи у старий регіон, а старий регіон синхронно дублює записи у новий регіон.
2. **Фаза блокування записів (Write Freeze Window):** Роутер переводить будинок у режим «лише читання» на 500 мілісекунд, чекаючи остаточного зрівняння LSN обох баз даних.
3. **Переключення affinity (Affinity Switch):** Роутер змінює у гео-реєстрі `Home Region` на Токіо та знімає блокування запису. Усі наступні записи починають оброблятися локально у Токіо.

## Метрики та спостережність гео-маршрутизації

Для моніторингу роботи гео-маршрутизатора у Prometheus/OpenTelemetry виводяться наступні обов'язкові метрики:

- `geo_router_requests_total{region, method, target_region}` — лічильник розповсюдження запитів за регіонами призначення.
- `geo_router_raw_fallback_total{client_region, reason}` — кількість виконаних фолбеків на Primary через лаг реплікації.
- `geo_router_replica_lag_seconds{region}` — поточний часовий лаг локальних реплік.
- `geo_router_circuit_breaker_state{region}` — стан запобіжника (0 — Closed/Normal, 1 — Open/Degraded).

Нижче наведено повністю робочу, ідіоматичну реалізацію гео-маршрутизатора мовами C++ та Go з підтримкою перевірки LSN-токена, вимірюванням лагу реплікацій та автоматичним вибором вузла виконання.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <cstdint>

// Послідовна позначка журналу транзакцій (LSN)
using Lsn = uint64_t;

// Перелік доступних глобальних регіонів
enum class Region {
    Frankfurt_Primary,
    Virginia_Replica,
    Tokyo_Replica
};

// Перетворення регіону у рядок для логування
constexpr std::string_view region_to_string(Region r) noexcept {
    switch (r) {
        case Region::Frankfurt_Primary: return "eu-central-1 (Primary)";
        case Region::Virginia_Replica:  return "us-east-1 (Replica)";
        case Region::Tokyo_Replica:     return "ap-northeast-1 (Replica)";
    }
    return "unknown";
}

// Конверт запиту з гео-метаданими
struct HttpRequest {
    std::string path;
    bool is_write_method{false};
    Region client_region{Region::Tokyo_Replica};
    std::optional<Lsn> required_lsn; // Токен Read-After-Write (X-LSN Header)
};

// Структура відповіді сервера
struct HttpResponse {
    int status_code{200};
    std::string body;
    Region served_by_region{Region::Frankfurt_Primary};
    std::optional<Lsn> new_lsn; // Повертається при записі
};

// Інтерфейс вузла бази даних
class IDatabaseNode {
public:
    virtual ~IDatabaseNode() = default;
    [[nodiscard]] virtual Region get_region() const noexcept = 0;
    [[nodiscard]] virtual Lsn get_current_lsn() const noexcept = 0;
    [[nodiscard]] virtual HttpResponse execute_read(const HttpRequest& req) = 0;
    [[nodiscard]] virtual HttpResponse execute_write(const HttpRequest& req) = 0;
};

// Реалізація Primary-вузла бази даних у Франкфурті
class PrimaryDatabase final : public IDatabaseNode {
private:
    Lsn current_lsn_{4000};

public:
    Region get_region() const noexcept override {
        return Region::Frankfurt_Primary;
    }

    Lsn get_current_lsn() const noexcept override {
        return current_lsn_;
    }

    HttpResponse execute_read(const HttpRequest& req) override {
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"ok\", \"data\": \"fresh_primary_state\"}",
            .served_by_region = Region::Frankfurt_Primary,
            .new_lsn = current_lsn_
        };
    }

    HttpResponse execute_write(const HttpRequest& req) override {
        ++current_lsn_; // Монотонний приріст LSN при кожному записі
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"written\", \"lsn\": " + std::to_string(current_lsn_) + "}",
            .served_by_region = Region::Frankfurt_Primary,
            .new_lsn = current_lsn_
        };
    }
};

// Реалізація Read-репліки у віддаленому регіоні
class ReadReplica final : public IDatabaseNode {
private:
    Region region_;
    Lsn replicated_lsn_{3950}; // Репліка відстає від Primary

public:
    explicit ReadReplica(Region region, Lsn initial_lsn)
        : region_(region), replicated_lsn_(initial_lsn) {}

    Region get_region() const noexcept override {
        return region_;
    }

    Lsn get_current_lsn() const noexcept override {
        return replicated_lsn_;
    }

    void update_replication_lsn(Lsn new_lsn) noexcept {
        replicated_lsn_ = new_lsn;
    }

    HttpResponse execute_read(const HttpRequest& req) override {
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"ok\", \"data\": \"local_replica_state\"}",
            .served_by_region = region_,
            .new_lsn = replicated_lsn_
        };
    }

    HttpResponse execute_write(const HttpRequest& req) override {
        // Read Replica не приймає записи
        return HttpResponse{
            .status_code = 405,
            .body = "{\"error\": \"Method Not Allowed on Replica\"}",
            .served_by_region = region_,
            .new_lsn = std::nullopt
        };
    }
};

// Розумний міжрегіональний маршрутизатор
class GeoAwareRouter {
private:
    std::shared_ptr<PrimaryDatabase> primary_db_;
    std::unordered_map<Region, std::shared_ptr<ReadReplica>> replicas_;

public:
    explicit GeoAwareRouter(std::shared_ptr<PrimaryDatabase> primary)
        : primary_db_(std::move(primary)) {}

    void register_replica(Region region, std::shared_ptr<ReadReplica> replica) {
        replicas_[region] = std::move(replica);
    }

    // Головний метод маршрутизації запиту
    [[nodiscard]] HttpResponse route_request(const HttpRequest& req) {
        // 1. Усі записи безвинятково йдуть на Primary у Франкфурт
        if (req.is_write_method) {
            std::cout << "[Router] Write request -> Routing to Primary in "
                      << region_to_string(primary_db_->get_region()) << "\n";
            return primary_db_->execute_write(req);
        }

        // 2. Якщо це читання, шукаємо найближчу локальну репліку
        auto it = replicas_.find(req.client_region);
        if (it == replicas_.end()) {
            // Немає репліки у регіоні -> йдемо на Primary
            std::cout << "[Router] No local replica -> Fallback to Primary\n";
            return primary_db_->execute_read(req);
        }

        const auto& local_replica = it->second;

        // 3. Перевірка Read-After-Write узгодженості (LSN Token Check)
        if (req.required_lsn.has_value()) {
            Lsn target_lsn = req.required_lsn.value();
            Lsn replica_lsn = local_replica->get_current_lsn();

            if (replica_lsn < target_lsn) {
                // Виявлено лаг реплікації! Локальні дані застаріли.
                std::cout << "[Router] RAW Check Failed! Client LSN: " << target_lsn
                          << ", Replica LSN: " << replica_lsn
                          << " (Lag: " << (target_lsn - replica_lsn) << " ops)"
                          << " -> Fallback to Primary in Frankfurt!\n";
                return primary_db_->execute_read(req);
            }
        }

        // 4. Локальна репліка свіжа -> віддаємо локальне швидке читання
        std::cout << "[Router] Local Replica LSN is fresh -> Serving locally in "
                  << region_to_string(local_replica->get_region()) << "\n";
        return local_replica->execute_read(req);
    }
};

int main() {
    // Ініціалізація кластера
    auto primary = std::make_shared<PrimaryDatabase>();
    auto tokyo_replica = std::make_shared<ReadReplica>(Region::Tokyo_Replica, 4000);

    GeoAwareRouter router(primary);
    router.register_replica(Region::Tokyo_Replica, tokyo_replica);

    std::cout << "=== Крок 1: Користувач у Токіо робить запис (PUT) ===\n";
    HttpRequest write_req{
        .path = "/api/v1/homes/h-101/devices/lamp",
        .is_write_method = true,
        .client_region = Region::Tokyo_Replica,
        .required_lsn = std::nullopt
    };

    HttpResponse write_resp = router.route_request(write_req);
    Lsn issued_token = write_resp.new_lsn.value_or(0);
    std::cout << "Відповідь запису: " << write_resp.body
              << " | Отримано токен X-LSN=" << issued_token << "\n\n";

    std::cout << "=== Крок 2: Негайне читання (GET) з токеном LSN=" << issued_token << " ===\n";
    HttpRequest read_req1{
        .path = "/api/v1/homes/h-101/devices",
        .is_write_method = false,
        .client_region = Region::Tokyo_Replica,
        .required_lsn = issued_token
    };

    // Оскільки tokyo_replica ще має LSN=4000, а токен=401, буде виконано фолбек на Primary
    HttpResponse read_resp1 = router.route_request(read_req1);
    std::cout << "Результат читання 1: " << read_resp1.body
              << " | Оброблено регіоном: " << region_to_string(read_resp1.served_by_region) << "\n\n";

    std::cout << "=== Крок 3: Синхронізація репліки Токіо до LSN=" << issued_token << " ===\n";
    tokyo_replica->update_replication_lsn(issued_token);

    std::cout << "=== Крок 4: Повторне читання (GET) з тим самим токеном ===\n";
    HttpResponse read_resp2 = router.route_request(read_req1);
    std::cout << "Результат читання 2: " << read_resp2.body
              << " | Оброблено регіоном: " << region_to_string(read_resp2.served_by_region) << "\n";

    return 0;
}
```
```go
package main

import (
	"fmt"
	"sync"
)

type Region string

const (
	RegionFrankfurtPrimary Region = "eu-central-1 (Primary)"
	RegionVirginiaReplica  Region = "us-east-1 (Replica)"
	RegionTokyoReplica     Region = "ap-northeast-1 (Replica)"
)

type Lsn uint64

type HttpRequest struct {
	Path         string
	IsWrite      bool
	ClientRegion Region
	RequiredLSN  Lsn // RAW token
}

type HttpResponse struct {
	StatusCode int
	Body       string
	ServedBy   Region
	NewLSN     Lsn
}

type PrimaryDB struct {
	mu  sync.Mutex
	lsn Lsn
}

func NewPrimaryDB(initialLSN Lsn) *PrimaryDB {
	return &PrimaryDB{lsn: initialLSN}
}

func (p *PrimaryDB) ExecuteRead(req HttpRequest) HttpResponse {
	p.mu.Lock()
	defer p.mu.Unlock()
	return HttpResponse{
		StatusCode: 200,
		Body:       `{"status": "ok", "data": "fresh_primary_state"}`,
		ServedBy:   RegionFrankfurtPrimary,
		NewLSN:     p.lsn,
	}
}

func (p *PrimaryDB) ExecuteWrite(req HttpRequest) HttpResponse {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.lsn++
	return HttpResponse{
		StatusCode: 200,
		Body:       fmt.Sprintf(`{"status": "written", "lsn": %d}`, p.lsn),
		ServedBy:   RegionFrankfurtPrimary,
		NewLSN:     p.lsn,
	}
}

type ReadReplica struct {
	mu     sync.RWMutex
	region Region
	lsn    Lsn
}

func NewReadReplica(region Region, initialLSN Lsn) *ReadReplica {
	return &ReadReplica{region: region, lsn: initialLSN}
}

func (r *ReadReplica) UpdateLSN(newLSN Lsn) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.lsn = newLSN
}

func (r *ReadReplica) GetLSN() Lsn {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.lsn
}

func (r *ReadReplica) ExecuteRead(req HttpRequest) HttpResponse {
	return HttpResponse{
		StatusCode: 200,
		Body:       `{"status": "ok", "data": "local_replica_state"}`,
		ServedBy:   r.region,
		NewLSN:     r.GetLSN(),
	}
}

type GeoRouter struct {
	primary  *PrimaryDB
	replicas map[Region]*ReadReplica
}

func NewGeoRouter(primary *PrimaryDB) *GeoRouter {
	return &GeoRouter{
		primary:  primary,
		replicas: make(map[Region]*ReadReplica),
	}
}

func (g *GeoRouter) RegisterReplica(region Region, replica *ReadReplica) {
	g.replicas[region] = replica
}

func (g *GeoRouter) RouteRequest(req HttpRequest) HttpResponse {
	if req.IsWrite {
		fmt.Printf("[Router] Write request -> Routing to Primary in %s\n", RegionFrankfurtPrimary)
		return g.primary.ExecuteWrite(req)
	}

	replica, exists := g.replicas[req.ClientRegion]
	if !exists {
		fmt.Printf("[Router] No local replica -> Fallback to Primary\n")
		return g.primary.ExecuteRead(req)
	}

	if req.RequiredLSN > 0 {
		replicaLSN := replica.GetLSN()
		if replicaLSN < req.RequiredLSN {
			fmt.Printf("[Router] RAW Check Failed! Client LSN: %d, Replica LSN: %d (Lag: %d ops) -> Fallback to Primary!\n",
				req.RequiredLSN, replicaLSN, req.RequiredLSN-replicaLSN)
			return g.primary.ExecuteRead(req)
		}
	}

	fmt.Printf("[Router] Local Replica LSN is fresh -> Serving locally in %s\n", req.ClientRegion)
	return replica.ExecuteRead(req)
}

func main() {
	primary := NewPrimaryDB(4000)
	tokyoReplica := NewReadReplica(RegionTokyoReplica, 4000)

	router := NewGeoRouter(primary)
	router.RegisterReplica(RegionTokyoReplica, tokyoReplica)

	fmt.Println("=== Крок 1: Запис у Токіо ===")
	wResp := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices/lamp",
		IsWrite:      true,
		ClientRegion: RegionTokyoReplica,
	})
	token := wResp.NewLSN
	fmt.Printf("Отримано токен X-LSN=%d\n\n", token)

	fmt.Println("=== Крок 2: Читання з відстаючої репліки ===")
	rResp1 := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices",
		IsWrite:      false,
		ClientRegion: RegionTokyoReplica,
		RequiredLSN:  token,
	})
	fmt.Printf("Відповідь оброблено: %s\n\n", rResp1.ServedBy)

	fmt.Println("=== Крок 3: Оновлення репліки ===")
	tokyoReplica.UpdateLSN(token)

	fmt.Println("=== Крок 4: Читання після синхронізації ===")
	rResp2 := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices",
		IsWrite:      false,
		ClientRegion: RegionTokyoReplica,
		RequiredLSN:  token,
	})
	fmt.Printf("Відповідь оброблено: %s\n", rResp2.ServedBy)
}
```
:::
