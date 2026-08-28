interface ProfileParser { parse(raw: string): Profile; }

class JsonProfileParser implements ProfileParser { parse(raw: string): Profile { /* ... */ return {} as Profile; } }
class CsvProfileParser  implements ProfileParser { parse(raw: string): Profile { /* ... */ return {} as Profile; } }
class XmlProfileParser  implements ProfileParser { parse(raw: string): Profile { /* ... */ return {} as Profile; } }

// параметризований фабричний метод: за КЛЮЧЕМ (розширення) обирає клас
function parserForFile(path: string): ProfileParser {
  const ext = path.slice(path.lastIndexOf(".") + 1).toLowerCase();
  switch (ext) {
    case "json": return new JsonProfileParser();
    case "csv":  return new CsvProfileParser();
    case "xml":  return new XmlProfileParser();
    default:
      throw new Error(`Немає парсера для формату .${ext}`);
  }
}
