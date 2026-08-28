// content_negotiator.ts — Промисловий рушій узгодження вмісту за RFC 9110
export interface MediaRange {
  type: string;
  subtype: string;
  params: Record<string, string>;
  q: number;
  specificity: number;
  clientIndex: number;
}

export interface LanguageRange {
  tag: string;
  primary: string;
  region?: string;
  q: number;
  clientIndex: number;
}

export interface MatchResult {
  selectedType: string;
  q: number;
  vary: string[];
}

export interface LanguageMatchResult {
  selectedLanguage: string;
  q: number;
  vary: string[];
}

export class ContentNegotiator {
  private readonly availableTypes: string[];
  private readonly availableLanguages: string[];

  constructor(availableTypes: string[], availableLanguages: string[] = []) {
    if (!availableTypes || availableTypes.length === 0) {
      throw new Error("ContentNegotiator вимагає щонайменше одного доступного типу сервера");
    }
    this.availableTypes = availableTypes.map((t) => t.toLowerCase().trim());
    this.availableLanguages = availableLanguages.map((l) => l.toLowerCase().trim());
  }

  /**
   * Розбір заголовка Accept у структурований та впорядкований список діапазонів
   */
  public parseAccept(header?: string | null): MediaRange[] {
    if (!header || !header.trim()) {
      return [{
        type: "*",
        subtype: "*",
        params: {},
        q: 1.0,
        specificity: 0,
        clientIndex: 0,
      }];
    }

    const ranges: MediaRange[] = [];
    const entries = this.splitHeaderEntries(header);

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i].trim();
      if (!entry) continue;

      const segments = entry.split(";").map((s) => s.trim());
      const mimePart = segments[0].toLowerCase();
      const slashIndex = mimePart.indexOf("/");

      if (slashIndex === -1) continue;

      const type = mimePart.slice(0, slashIndex).trim();
      const subtype = mimePart.slice(slashIndex + 1).trim();

      if (!type || !subtype) continue;

      let q = 1.0;
      const params: Record<string, string> = {};

      for (let j = 1; j < segments.length; j++) {
        const paramPart = segments[j];
        const eqIndex = paramPart.indexOf("=");
        if (eqIndex === -1) continue;

        const key = paramPart.slice(0, eqIndex).trim().toLowerCase();
        let val = paramPart.slice(eqIndex + 1).trim();

        if (val.length >= 2 && val.startsWith('"') && val.endsWith('"')) {
          val = val.slice(1, -1);
        }

        if (key === "q") {
          const parsed = parseFloat(val);
          q = isNaN(parsed) ? 1.0 : Math.max(0, Math.min(1, parsed));
        } else {
          params[key] = val;
        }
      }

      let specificity = 0;
      if (type !== "*") {
        if (subtype !== "*") {
          specificity = Object.keys(params).length > 0 ? 3 : 2;
        } else {
          specificity = 1;
        }
      }

      ranges.push({
        type,
        subtype,
        params,
        q,
        specificity,
        clientIndex: i,
      });
    }

    ranges.sort((a, b) => {
      if (b.q !== a.q) return b.q - a.q;
      if (b.specificity !== a.specificity) return b.specificity - a.specificity;
      return a.clientIndex - b.clientIndex;
    });

    return ranges;
  }

  /**
   * Розбір заголовка Accept-Language за стандартом BCP 47
   */
  public parseAcceptLanguage(header?: string | null): LanguageRange[] {
    if (!header || !header.trim()) {
      return [{
        tag: "*",
        primary: "*",
        q: 1.0,
        clientIndex: 0,
      }];
    }

    const ranges: LanguageRange[] = [];
    const entries = this.splitHeaderEntries(header);

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i].trim();
      if (!entry) continue;

      const segments = entry.split(";").map((s) => s.trim());
      const rawTag = segments[0].toLowerCase();
      if (!rawTag) continue;

      let q = 1.0;
      for (let j = 1; j < segments.length; j++) {
        const param = segments[j];
        const eqIdx = param.indexOf("=");
        if (eqIdx !== -1 && param.slice(0, eqIdx).trim().toLowerCase() === "q") {
          const parsed = parseFloat(param.slice(eqIdx + 1).trim());
          q = isNaN(parsed) ? 1.0 : Math.max(0, Math.min(1, parsed));
        }
      }

      const dashIdx = rawTag.indexOf("-");
      const primary = dashIdx === -1 ? rawTag : rawTag.slice(0, dashIdx);
      const region = dashIdx === -1 ? undefined : rawTag.slice(dashIdx + 1);

      ranges.push({
        tag: rawTag,
        primary,
        region,
        q,
        clientIndex: i,
      });
    }

    ranges.sort((a, b) => {
      if (b.q !== a.q) return b.q - a.q;
      return a.clientIndex - b.clientIndex;
    });

    return ranges;
  }

  /**
   * Селекція типу носія
   */
  public negotiate(acceptHeader?: string | null): MatchResult | null {
    const ranges = this.parseAccept(acceptHeader);

    for (const range of ranges) {
      if (range.q === 0) continue;

      for (const serverType of this.availableTypes) {
        const slashIdx = serverType.indexOf("/");
        const sType = serverType.slice(0, slashIdx);
        const sSubtype = serverType.slice(slashIdx + 1);

        const typeMatches = range.type === "*" || range.type === sType;
        const subtypeMatches = range.subtype === "*" || range.subtype === sSubtype;

        if (typeMatches && subtypeMatches) {
          return {
            selectedType: serverType,
            q: range.q,
            vary: ["Accept"],
          };
        }
      }
    }

    return null;
  }

  /**
   * Селекція мовної локалі за алгоритмом префіксного пошуку
   */
  public negotiateLanguage(acceptLanguageHeader?: string | null): LanguageMatchResult | null {
    if (this.availableLanguages.length === 0) return null;

    const ranges = this.parseAcceptLanguage(acceptLanguageHeader);

    for (const range of ranges) {
      if (range.q === 0) continue;

      // 1. Точний збіг повного мовного тегу (наприклад, uk-ua)
      for (const lang of this.availableLanguages) {
        if (range.tag === "*" || lang === range.tag) {
          return { selectedLanguage: lang, q: range.q, vary: ["Accept-Language"] };
        }
      }

      // 2. Префіксний збіг (наприклад, uk-ua зіставляється з uk)
      for (const lang of this.availableLanguages) {
        const sDash = lang.indexOf("-");
        const sPrimary = sDash === -1 ? lang : lang.slice(0, sDash);
        if (range.primary === sPrimary) {
          return { selectedLanguage: lang, q: range.q, vary: ["Accept-Language"] };
        }
      }
    }

    // За замовчуванням повертаємо першу мову сервера
    return {
      selectedLanguage: this.availableLanguages[0],
      q: 1.0,
      vary: ["Accept-Language"],
    };
  }

  private splitHeaderEntries(header: string): string[] {
    const results: string[] = [];
    let start = 0;
    let inQuotes = false;

    for (let i = 0; i < header.length; i++) {
      const char = header[i];
      if (char === '"' && (i === 0 || header[i - 1] !== "\\")) {
        inQuotes = !inQuotes;
      } else if (char === "," && !inQuotes) {
        results.push(header.slice(start, i));
        start = i + 1;
      }
    }

    if (start < header.length) {
      results.push(header.slice(start));
    }

    return results;
  }
}
