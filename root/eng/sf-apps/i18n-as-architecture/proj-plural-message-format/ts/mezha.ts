const BASE = "en";                               // мова-основа проєкту
const catalog: Record<string, Record<string, string>> = {
  uk: {
    "files.added":
      "{gender, select, female {{actor} додала} other {{actor} додав}} " +
      "{count, plural, one {# файл} few {# файли} many {# файлів} other {# файлу}} " +
      "до теки «{folder}»",
  },
  en: {
    "files.added":
      "{actor} added {count, plural, one {# file} other {# files}} to “{folder}”",
  },
  ja: {
    "files.added": "{actor}が「{folder}」に{count}件のファイルを追加しました",
  },
};

const trees = new Map<string, Node[]>();

function t(loc: string, key: string,
           args: Record<string, unknown> = {}, o: NumOpts = {}): string {
  const chain = [loc, loc.split("-")[0], BASE];          // uk-UA → uk → en
  const lang = chain.find(l => catalog[l]?.[key]);
  if (!lang) return key;                                 // перекладу нема — видно ключ
  const tree = memo(trees, lang + " " + key, () => parse(catalog[lang][key]));
  const fmt = loc.startsWith(lang) ? loc : lang;         // числа — у мові шаблону
  return run(tree, args, fmt, o, null);
}
