int rawDry = 730;                 // сире число «зовсім сухо» (щуп у повітрі)
int rawWet = 300;                 // сире число «зовсім волого» (щуп у воді)

int toPercent(int raw) {
    // захист від ділення на нуль, якщо краї злиплися (щуп не під'єднано)
    if (rawDry <= rawWet) return -1;                 // -1 = «калібрування зіпсоване»
    long pct = (long)(rawDry - raw) * 100 / (rawDry - rawWet);
    if (pct < 0)   pct = 0;                            // нижче сухого краю → 0
    if (pct > 100) pct = 100;                          // вище мокрого → 100
    return (int)pct;
}
