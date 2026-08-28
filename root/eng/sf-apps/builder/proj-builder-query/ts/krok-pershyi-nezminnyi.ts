type Method = "GET" | "POST" | "PUT" | "DELETE";

// ── ПРОДУКТ: незмінний. Поля readonly, конструктор приватний. ──
class HttpRequest {
  private constructor(
    readonly method: Method,
    readonly url: string,
    readonly headers: ReadonlyMap<string, string>,
    readonly body: string | null,
    readonly timeoutMs: number,
    readonly retries: number,
  ) {}

  // Єдиний вхід у створення — статична фабрика, що віддає будівельник.
  static builder(method: Method, url: string): HttpRequestBuilder {
    return new HttpRequestBuilder(method, url);
  }

  // Внутрішній «конструктор для будівельника»: він у тому самому модулі,
  // тож бачить приватний constructor, а зовнішній світ — ні.
  static _assemble(b: HttpRequestBuilder): HttpRequest {
    return new HttpRequest(
      b._method, b._url,
      new Map(b._headers),        // копія — щоб продукт не ділив мапу з будівельником
      b._body, b._timeoutMs, b._retries,
    );
  }
}

// ── БУДІВЕЛЬНИК: змінний і тимчасовий. Копить рішення, нічого не віддає. ──
class HttpRequestBuilder {
  _method: Method;
  _url: string;
  _headers = new Map<string, string>();
  _body: string | null = null;
  _timeoutMs = 30_000;
  _retries = 0;

  constructor(method: Method, url: string) {   // обов'язкове — одразу
    this._method = method;
    this._url = url;
  }

  header(name: string, value: string): this {  // крок повертає САМ будівельник...
    this._headers.set(name, value);
    return this;                               // ...тому виклики й чіпляються в ланцюжок
  }
  body(text: string): this {
    this._body = text;
    return this;
  }
  timeout(ms: number): this {
    this._timeoutMs = ms;
    return this;
  }
  retries(n: number): this {
    this._retries = n;
    return this;
  }

  build(): HttpRequest {
    // ── ЄДИНА точка перевірки: маємо перед собою ВСІ рішення разом ──
    if (this._url.trim() === "") {
      throw new Error("HttpRequest: url порожній");
    }
    if (this._body !== null && (this._method === "GET" || this._method === "DELETE")) {
      throw new Error(
        `HttpRequest: метод ${this._method} не несе тіла, але body задано — ` +
        `прибери body або зміни метод на POST/PUT`,
      );
    }
    if (this._timeoutMs <= 0) {
      throw new Error(`HttpRequest: timeout має бути > 0, а не ${this._timeoutMs}`);
    }
    if (this._retries < 0) {
      throw new Error(`HttpRequest: retries не може бути від'ємним (${this._retries})`);
    }
    return HttpRequest._assemble(this);
  }
}

// ── Виклик читається сам ──
const req = HttpRequest.builder("POST", "https://api.example.com/orders")
  .header("Content-Type", "application/json")
  .body('{"item":"кава","qty":2}')
  .timeout(5_000)
  .retries(3)
  .build();

console.log(req.method, req.url, req.retries);   // POST  https://…/orders  3
