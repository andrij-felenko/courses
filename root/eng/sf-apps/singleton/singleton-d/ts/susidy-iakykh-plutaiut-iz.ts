class Settings {
  private static shared = { theme: "light" };  // один об'єкт-стан на весь клас
  get theme() { return Settings.shared.theme; }
  set theme(v: string) { Settings.shared.theme = v; }
}

const a = new Settings(), b = new Settings();
a.theme = "dark";
console.log(b.theme);   // "dark" — стан спільний
console.log(a === b);   // false — об'єкти різні
