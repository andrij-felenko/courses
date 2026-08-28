// Один експортер на ВСІ запити: він не знає ні таблиць, ні предметних класів —
// усе, що йому треба, набір розповідає про себе сам.
static void ExportCsv(DataTable table, TextWriter output)
{
    var columns = table.Columns.Cast<DataColumn>().ToList();

    // заголовок — зі схеми набору
    output.WriteLine(string.Join(",", columns.Select(c => Quote(c.ColumnName))));

    foreach (DataRow row in table.Rows)
    {
        // порожня комірка й порожній рядок — різні речі, тому питаємо явно
        var cells = columns.Select(c =>
            row.IsNull(c) ? "" : Quote(Convert.ToString(row[c], CultureInfo.InvariantCulture)));
        output.WriteLine(string.Join(",", cells));
    }
}

static string Quote(string s) =>
    s.IndexOfAny(new[] { ',', '"', '\n' }) >= 0
        ? "\"" + s.Replace("\"", "\"\"") + "\""
        : s;
