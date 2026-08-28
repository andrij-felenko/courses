abstract class Importer {
  // ШАБЛОННИЙ МЕТОД: каркас, який нащадок не чіпає
  importFile(path: string): void {
    const text = this.readFile(path);                     // спільний крок
    const rows = this.parse(text).filter(r => this.isValid(r));  // дірка + гачок
    this.saveAll(rows);                                   // спільний крок
    this.log(rows.length);                                // спільний крок
  }

  protected abstract parse(text: string): Record[];       // мусить дати нащадок
  protected isValid(r: Record): boolean { return true; }  // гачок із типовим «так»

  private readFile(path: string): string { /* однакове */ return ""; }
  private saveAll(rows: Record[]): void  { /* однакове */ }
  private log(n: number): void           { /* однакове */ }
}

class CsvImporter extends Importer {
  protected parse(text: string): Record[] { /* комами */ return []; }
}
class JsonImporter extends Importer {
  protected parse(text: string): Record[] { return JSON.parse(text); }
  protected isValid(r: Record): boolean { return r.id > 0; }  // суворіше
}
