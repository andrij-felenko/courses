interface ProfileParser { parse(raw: string): Profile; }

// реєстр: ключ → конструктор. Відповідність стала ДАНИМИ, а не гілками коду
const PARSERS = new Map<string, new () => ProfileParser>([
  ["json", JsonProfileParser],
  ["csv",  CsvProfileParser],
  ["xml",  XmlProfileParser],
]);

function parserForFile(path: string): ProfileParser {
  const ext = path.slice(path.lastIndexOf(".") + 1).toLowerCase();
  const Ctor = PARSERS.get(ext);
  if (!Ctor) throw new Error(`Немає парсера для формату .${ext}`);
  return new Ctor();
}

// новий формат — БЕЗ дотику до parserForFile: лише запис у таблицю
export function registerParser(ext: string, ctor: new () => ProfileParser): void {
  PARSERS.set(ext, ctor);
}
