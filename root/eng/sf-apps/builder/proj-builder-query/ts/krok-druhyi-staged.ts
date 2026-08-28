type Method = "GET" | "POST" | "PUT" | "DELETE";

// ── Стадії як ОКРЕМІ інтерфейси. У кожній — лише дозволене тут. ──
interface NeedMethod {
  method(m: Method): NeedUrl;          // єдине, що можна зробити першим — задати метод
}
interface NeedUrl {
  url(u: string): Ready;               // єдине, що можна другим — задати url
}
interface Ready {
  header(name: string, value: string): Ready;   // необов'язкові — вертають ТУ Ж стадію
  body(text: string): Ready;
  timeout(ms: number): Ready;
  build(): HttpRequest;                // ← build() існує ЛИШЕ тут, у фінальній стадії
}

// ── Один клас реалізує всі стадії; кожен обов'язковий крок «підіймає» стадію. ──
class HttpRequestSteps implements NeedMethod, NeedUrl, Ready {
  private _method!: Method;
  private _url!: string;
  private _headers = new Map<string, string>();
  private _body: string | null = null;
  private _timeoutMs = 30_000;

  method(m: Method): NeedUrl {         // повертаємо СЕБЕ, але під типом наступної стадії
    this._method = m;
    return this;                       // рантайм — той самий об'єкт; ТИП звузив дозволене
  }
  url(u: string): Ready {
    this._url = u;
    return this;
  }
  header(name: string, value: string): Ready { this._headers.set(name, value); return this; }
  body(text: string): Ready { this._body = text; return this; }
  timeout(ms: number): Ready { this._timeoutMs = ms; return this; }

  build(): HttpRequest {
    // Обов'язкові тут ГАРАНТОВАНО задані — інакше ми б сюди не дісталися за типами.
    // Лишається перевірити те, що типами не виразиш: комбінації.
    if (this._body !== null && (this._method === "GET" || this._method === "DELETE")) {
      throw new Error(`HttpRequest: метод ${this._method} не несе тіла`);
    }
    // Складання й КОПІЯ мапи — так само, як у простому будівельнику вище
    // (тут для стислості показано об'єктом-продуктом; у реальному коді —
    //  той самий приватний вхід у створення HttpRequest).
    return HttpRequest.of({
      method: this._method,
      url: this._url,
      headers: new Map(this._headers),   // копія — продукт не ділить мапу зі стадіями
      body: this._body,
      timeoutMs: this._timeoutMs,
      retries: 0,
    });
  }
}

// Вхід у складання віддає ПЕРШУ стадію — і більш нічого звідти не досяжно.
function httpRequest(): NeedMethod {
  return new HttpRequestSteps();
}
