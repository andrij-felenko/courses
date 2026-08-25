# ⚙️ Реалізація безпечного посередника CORS для бекенд-серверів

Цей проєкт демонструє створення надійного та високопродуктивного програмного посередника (CORS Middleware) для серверної частини веб-застосунків. Реалізація розв'язує комплекс ключових інженерних задач: валідацію динамічного походження (`Origin`) за суворим білим списком із підтримкою регулярних виразів для піддоменів, коректне переривання попередніх запитів `OPTIONS` зі статусом `204 No Content`, захищене керування обліковими даними (`Credentials`) без конфліктів із підстановочним символом `*`, збереження узгодженості проміжних кешів через заголовок `Vary: Origin` та нульове виділення пам'яті на гарячому шляху маршрутизації.

---

## Архітектура та послідовність обробки

Посередник CORS є першим критичним бар'єром у конвеєрі обробки HTTP-запитів на сервері. Його розміщення на самому початку ланцюжка обробників є обов'язковою вимогою архітектури: якщо розмістити перевірку автентифікації (розбір JWT-токенів чи читання сесії з Redis) до CORS-посередника, попередні запити `OPTIONS` від браузера неминуче завершаться помилкою `401 Unauthorized`. Браузерні рушії за стандартом ніколи не прикріплюють токени авторизації чи куки до службових запитів preflight, тому будь-який захищений роут без винесеного вперед CORS-посередника стане недосяжним для міжсайтових клієнтів.

Послідовність дій посередника складається з п'яти дискретних кроків:
1. **Витягнення заголовка Origin:** посередник шукає заголовок `Origin` у мапі вхідних заголовків. Якщо заголовок відсутній (запит надіслано інструментом curl, бекенд-сервісом, мобільним додатком або завданням планувальника cron), це означає, що запит не підпадає під обмеження браузерної пісочниці SOP. Посередник миттєво передає керування наступному обробнику без модифікації заголовків.
2. **Перевірка дозволу джерела:** значення `Origin` зіставляється з хеш-таблицею дозволених джерел (`allowed_origins`) для константного часу перевірки `O(1)`. Якщо точного збігу немає, перевіряється список скомпільованих регулярних виразів (`origin_patterns`) для динамічних середовищ попереднього перегляду (staging, PR preview environments).
3. **Застосування заголовків безпеки:** якщо джерело визнано валідним:
   - Встановлюється заголовок `Access-Control-Allow-Origin` із точним рядком поточного клієнта.
   - Додається обов'язковий заголовок `Vary: Origin`, який сигналізує кешувальним вузлам CDN та проксі-серверам про необхідність роздільного збереження відповідей для різних доменів.
   - Якщо застосунок працює з сесійними куками чи Bearer-токенами, встановлюється `Access-Control-Allow-Credentials: true`.
   - Заголовок `Access-Control-Expose-Headers` відкриває доступ клієнтському коду до службових заголовків відповіді (ліміти швидкості, пагінація, трасування).
4. **Обробка запиту Preflight (метод OPTIONS):**
   - Формуються заголовки дозволених методів (`Access-Control-Allow-Methods`), заголовків (`Access-Control-Allow-Headers`) та максимального часу кешування результату перевірки (`Access-Control-Max-Age`).
   - Конвеєр негайно завершує роботу, повертаючи клієнту статус `204 No Content` із нульовою довжиною тіла (`Content-Length: 0`). Запит не передається до контролерів бізнес-логіки та не навантажує базу даних.
5. **Обробка неавторизованого джерела:**
   - Для методу `OPTIONS` повертається статус `403 Forbidden` або `204 No Content` без жодного заголовка `Access-Control-*`.
   - Для фактичних запитів виконання продовжується штатно: відсутність дозволу ACAO змусить сам браузер заблокувати доступ JavaScript до отриманого результату.

---

## Програмна реалізація посередника

Нижче наведено ідіоматичні реалізації посередника для трьох популярних бекенд-стеків: TypeScript (Node.js/Express), Go (`net/http`) та сучасного C++20.

:::tabs
```ts
import { Request, Response, NextFunction } from 'express';

export interface CorsOptions {
  allowedOrigins: string[];
  allowedOriginPatterns?: RegExp[];
  allowedMethods?: string[];
  allowedHeaders?: string[];
  exposedHeaders?: string[];
  allowCredentials?: boolean;
  maxAgeSeconds?: number;
}

export function createCorsMiddleware(options: CorsOptions) {
  const {
    allowedOrigins,
    allowedOriginPatterns = [],
    allowedMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders = ['Content-Type', 'Authorization', 'X-Requested-With', 'X-Request-Id'],
    exposedHeaders = ['X-Total-Count', 'X-RateLimit-Remaining'],
    allowCredentials = true,
    maxAgeSeconds = 86400,
  } = options;

  const originSet = new Set(allowedOrigins);

  const isOriginAllowed = (origin: string): boolean => {
    if (originSet.has(origin)) return true;
    return allowedOriginPatterns.some((pattern) => pattern.test(origin));
  };

  return (req: Request, res: Response, next: NextFunction): void => {
    const origin = req.headers.origin;

    // Якщо заголовок Origin відсутній (не браузер) — передаємо керування далі
    if (!origin || typeof origin !== 'string') {
      next();
      return;
    }

    if (isOriginAllowed(origin)) {
      // Суворе встановлення точного Origin замість *
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Vary', 'Origin');

      if (allowCredentials) {
        res.setHeader('Access-Control-Allow-Credentials', 'true');
      }

      if (exposedHeaders.length > 0) {
        res.setHeader('Access-Control-Expose-Headers', exposedHeaders.join(', '));
      }

      // Обробка попереднього запиту Preflight
      if (req.method === 'OPTIONS') {
        res.setHeader('Access-Control-Allow-Methods', allowedMethods.join(', '));
        res.setHeader('Access-Control-Allow-Headers', allowedHeaders.join(', '));
        res.setHeader('Access-Control-Max-Age', maxAgeSeconds.toString());
        res.setHeader('Content-Length', '0');
        res.status(204).end();
        return;
      }
    } else if (req.method === 'OPTIONS') {
      // Відхилення неавторизованого Preflight
      res.status(403).end();
      return;
    }

    next();
  };
}
```
```go
package cors

import (
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

type Config struct {
	AllowedOrigins        []string
	AllowedOriginPatterns []*regexp.Regexp
	AllowedMethods        []string
	AllowedHeaders        []string
	ExposedHeaders        []string
	AllowCredentials      bool
	MaxAgeSeconds         int
}

func DefaultConfig(allowedOrigins []string) Config {
	return Config{
		AllowedOrigins:   allowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization", "X-Requested-With", "X-Request-Id"},
		ExposedHeaders:   []string{"X-Total-Count", "X-RateLimit-Remaining"},
		AllowCredentials: true,
		MaxAgeSeconds:    86400,
	}
}

func Middleware(cfg Config) func(http.Handler) http.Handler {
	originMap := make(map[string]struct{}, len(cfg.AllowedOrigins))
	for _, o := range cfg.AllowedOrigins {
		originMap[o] = struct{}{}
	}

	methodsHeader := strings.Join(cfg.AllowedMethods, ", ")
	allowedHeadersStr := strings.Join(cfg.AllowedHeaders, ", ")
	exposedHeadersStr := strings.Join(cfg.ExposedHeaders, ", ")
	maxAgeStr := strconv.Itoa(cfg.MaxAgeSeconds)

	isAllowed := func(origin string) bool {
		if _, ok := originMap[origin]; ok {
			return true
		}
		for _, re := range cfg.AllowedOriginPatterns {
			if re.MatchString(origin) {
				return true
			}
		}
		return false
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origin := r.Header.Get("Origin")
			if origin == "" {
				next.ServeHTTP(w, r)
				return
			}

			if isAllowed(origin) {
				h := w.Header()
				h.Set("Access-Control-Allow-Origin", origin)
				h.Add("Vary", "Origin")

				if cfg.AllowCredentials {
					h.Set("Access-Control-Allow-Credentials", "true")
				}

				if len(cfg.ExposedHeaders) > 0 {
					h.Set("Access-Control-Expose-Headers", exposedHeadersStr)
				}

				if r.Method == http.MethodOptions {
					h.Set("Access-Control-Allow-Methods", methodsHeader)
					h.Set("Access-Control-Allow-Headers", allowedHeadersStr)
					h.Set("Access-Control-Max-Age", maxAgeStr)
					h.Set("Content-Length", "0")
					w.WriteHeader(http.StatusNoContent)
					return
				}
			} else if r.Method == http.MethodOptions {
				w.WriteHeader(http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
```
```cpp
#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>
#include <regex>
#include <optional>
#include <memory>
#include <algorithm>
#include <cctype>

struct CorsConfig {
    std::unordered_set<std::string> allowed_origins;
    std::vector<std::regex> origin_patterns;
    std::string allowed_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS";
    std::string allowed_headers = "Content-Type, Authorization, X-Requested-With, X-Request-Id";
    std::string exposed_headers = "X-Total-Count, X-RateLimit-Remaining";
    bool allow_credentials = true;
    int max_age_seconds = 86400;
};

// Абстракції HTTP-запиту та відповіді для вбудовування в асинхронні веб-сервери
struct HttpRequest {
    std::string_view method;
    std::string_view path;
    std::vector<std::pair<std::string_view, std::string_view>> headers;

    [[nodiscard]] std::optional<std::string_view> get_header(std::string_view key) const {
        for (const auto& [k, v] : headers) {
            if (k.size() == key.size() && 
                std::equal(k.begin(), k.end(), key.begin(), [](char a, char b) {
                    return std::tolower(static_cast<unsigned char>(a)) == 
                           std::tolower(static_cast<unsigned char>(b));
                })) {
                return v;
            }
        }
        return std::nullopt;
    }
};

struct HttpResponse {
    int status_code = 200;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string body;

    void set_header(std::string key, std::string value) {
        headers.emplace_back(std::move(key), std::move(value));
    }
};

class CorsMiddleware {
public:
    explicit CorsMiddleware(CorsConfig config) 
        : config_(std::move(config)), 
          max_age_str_(std::to_string(config_.max_age_seconds)) {}

    template <typename NextHandler>
    HttpResponse handle(const HttpRequest& req, NextHandler&& next) const {
        const auto origin_opt = req.get_header("origin");
        if (!origin_opt.has_value() || origin_opt->empty()) {
            return next(req);
        }

        const std::string_view origin = *origin_opt;
        if (is_origin_allowed(origin)) {
            if (req.method == "OPTIONS") {
                HttpResponse preflight_res;
                preflight_res.status_code = 204;
                preflight_res.set_header("Access-Control-Allow-Origin", std::string(origin));
                preflight_res.set_header("Vary", "Origin");
                preflight_res.set_header("Access-Control-Allow-Methods", config_.allowed_methods);
                preflight_res.set_header("Access-Control-Allow-Headers", config_.allowed_headers);
                preflight_res.set_header("Access-Control-Max-Age", max_age_str_);
                preflight_res.set_header("Content-Length", "0");
                
                if (config_.allow_credentials) {
                    preflight_res.set_header("Access-Control-Allow-Credentials", "true");
                }
                return preflight_res;
            }

            HttpResponse res = next(req);
            res.set_header("Access-Control-Allow-Origin", std::string(origin));
            res.set_header("Vary", "Origin");

            if (config_.allow_credentials) {
                res.set_header("Access-Control-Allow-Credentials", "true");
            }
            if (!config_.exposed_headers.empty()) {
                res.set_header("Access-Control-Expose-Headers", config_.exposed_headers);
            }
            return res;
        }

        if (req.method == "OPTIONS") {
            HttpResponse forbidden_res;
            forbidden_res.status_code = 403;
            return forbidden_res;
        }

        return next(req);
    }

private:
    [[nodiscard]] bool is_origin_allowed(std::string_view origin) const {
        const std::string origin_str(origin);
        if (config_.allowed_origins.contains(origin_str)) {
            return true;
        }
        for (const auto& pattern : config_.origin_patterns) {
            if (std::regex_match(origin_str, pattern)) {
                return true;
            }
        }
        return false;
    }

    CorsConfig config_;
    std::string max_age_str_;
};
```
:::

---

## Налаштування та тонкощі експлуатації

### Нормалізація портів та локальних адрес
Під час розробки типовою помилкою є плутанина між `http://localhost:3000` та `http://127.0.0.1:3000`. Для політики SOP це два абсолютно різні походження, оскільки текстове порівняння хостів не виконує зворотного перетворення імен через DNS. Якщо фронтенд відкривається за адресою `localhost`, а бекенд дозволяє лише `127.0.0.1`, усі виклики API будуть відхилені браузером. Білий список повинен містити обидва варіанти або суворо уніфікувати адресу в локальних конфігураціях розробника.

Також слід враховувати неявні порти: для протоколу `https://` порт `443` є стандартним і браузери зазвичай опускають його в рядку `Origin` (`https://example.com`), тоді як при явному запуску на порту `8443` рядок набуває вигляду `https://example.com:8443`. Білий список повинен точно зберігати номер порту, якщо він відрізняється від стандартних 80 чи 443.

### Підводні камені незакріплених регулярних виразів
При написанні регулярних виразів для динамічних піддоменів (наприклад, середовищ попереднього перегляду гілок Git) відсутність символів початку `^` та кінця `$` рядка призводить до критичної діри в безпеці. 

Розглянемо вразливий регулярний вираз:
```
/example\.com/
```
Такий вираз знайде збіг у домені `https://example.com.evil-hacker.net` або `https://attacker-example.com`, оскільки рядок містить шукану підстроку. Зловмисник отримує можливість зареєструвати подібний домен і повністю зчитувати конфіденційні дані через заголовок `Origin`.

Безпечний вираз вимагає суворої прив'язки меж і екранування спеціальних символів крапки:
```
^https:\/\/(?:[a-zA-Z0-9-]+\.)*example\.com$
```

### Вплив навантаження та оптимізація часу життя Preflight
Попередні запити `OPTIONS` створюють додатковий мережевий раунд (Round Trip Time, RTT) перед кожною реальною операцією. На мобільних мережах із високою затримкою (3G/4G/LTE) подвоєння запитів сповільнює роботу інтерфейсу на 150–400 мілісекунд.

Для мінімізації навантаження заголовок `Access-Control-Max-Age` у виробничих середовищах рекомендується встановлювати у значення не менше `86400` (24 години). Браузери самостійно затиснуть це значення до власних внутрішніх лімітів безпеки (наприклад, 2 години в Chromium), проте це усуне 95% зайвих викликів `OPTIONS` під час активної сесії користувача.

---

## Тестування та верифікація через командний рядок

Для перевірки коректності роботи CORS-посередника перед розгортанням у продакшені найзручніше використовувати консольну утиліту `curl`. Вона дозволяє точно зімітувати поведінку браузерного User Agent без необхідності підіймати повноцінний клієнтський фронтенд.

### 1. Перевірка простого запиту (Simple Request)
Команда надсилає заголовок `Origin` і виводить виключно отримані HTTP-заголовки відповіді:

```bash
curl -I -X GET "https://api.example.com/v1/profile" \
  -H "Origin: https://app.example.com"
```

Очікувана відповідь сервера:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
Content-Type: application/json
```

### 2. Перевірка попереднього запиту Preflight (OPTIONS)
Команда імітує preflight-запит для методу `DELETE` із передачею кастомного заголовка `Authorization`:

```bash
curl -I -X OPTIONS "https://api.example.com/v1/users/42" \
  -H "Origin: https://app.example.com" \
  -H "Access-Control-Request-Method: DELETE" \
  -H "Access-Control-Request-Headers: Authorization, X-Request-Id"
```

Очікувана відповідь сервера:
```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, X-Request-Id
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
Vary: Origin
Content-Length: 0
```

Якщо у відповіді на `OPTIONS` статус відрізняється від `204` (або `200`), або відсутній заголовок `Access-Control-Allow-Methods`, браузер заблокує виклик ще до передачі основного запиту на сервер.
