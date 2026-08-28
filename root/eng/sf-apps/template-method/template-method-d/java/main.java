abstract class Importer {
    // ШАБЛОННИЙ МЕТОД: незмінний каркас. final — нащадок його не підмінить.
    public final void importFile(String path) {
        String text   = readFile(path);           // спільний крок
        List<Record> rows = parse(text);           // ← дірка: дає нащадок
        rows.removeIf(r -> !isValid(r));           // гачок із типовою поведінкою
        saveAll(rows);                             // спільний крок
        log(rows.size());                          // спільний крок
    }

    protected abstract List<Record> parse(String text);   // МУСИТЬ дати нащадок

    protected boolean isValid(Record r) { return true; }  // гачок: МОЖЕ підмінити

    private String readFile(String path) { /* однакове для всіх */ return ""; }
    private void   saveAll(List<Record> rows) { /* однакове для всіх */ }
    private void   log(int n) { /* однакове для всіх */ }
}

class CsvImporter extends Importer {
    protected List<Record> parse(String text) { /* рядки, розбиті комами */ return List.of(); }
}

class JsonImporter extends Importer {
    protected List<Record> parse(String text) { /* JSON → записи */ return List.of(); }
    protected boolean isValid(Record r) { return r.id() > 0; }  // цей формат хоче суворіше
}
