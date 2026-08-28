using System;
using System.Collections.Generic;
using System.Data;

public sealed class ProductModule
{
    private readonly DataSet _data;
    public ProductModule(DataSet data) => _data = data;

    public string KindOf(long productId)
    {
        DataRow row = _data.Tables["products"].Rows.Find(productId)
                      ?? throw new InvalidOperationException($"немає товару {productId}");
        return (string)row["kind"];
    }
}

public sealed class ContractModule
{
    // Розклад визнання: правило таблицею. Ключ — тип товару,
    // значення — зсуви часток у днях від дати підписання.
    private static readonly Dictionary<string, int[]> Schedules = new()
    {
        ["word-processor"] = new[] { 0 },
        ["database"]       = new[] { 0 },
        ["spreadsheet"]    = new[] { 0, 60, 90 },
    };

    private readonly DataSet _data;
    private readonly DataView _byContract;      // вторинний індекс за чужим ключем

    public ContractModule(DataSet data)
    {
        _data = data;
        _byContract = new DataView(data.Tables["recognitions"]) { Sort = "contract_id" };
    }

    public void CalculateRecognitions(long contractId)
    {
        DataRow contract = _data.Tables["contracts"].Rows.Find(contractId)   // індексом за PK
                           ?? throw new InvalidOperationException($"немає контракту {contractId}");
        decimal revenue = (decimal)contract["revenue"];
        DateTime signed = (DateTime)contract["signed_on"];
        string kind = new ProductModule(_data).KindOf((long)contract["product_id"]);

        if (!Schedules.TryGetValue(kind, out int[] offsets))
            throw new InvalidOperationException($"немає розкладу: {kind}");

        DropRecognitions(contractId);           // повторний виклик не подвоює рядки
        decimal[] parts = SplitEvenly(revenue, offsets.Length);
        DataTable table = _data.Tables["recognitions"];
        for (int i = 0; i < offsets.Length; i++)
        {
            DataRow row = table.NewRow();
            row["contract_id"] = contractId;
            row["amount"] = parts[i];
            row["recognized_on"] = signed.AddDays(offsets[i]);
            table.Rows.Add(row);                // рядок одразу стає Added
        }
    }

    public decimal RecognizedAsOf(long contractId, DateTime asOf)
    {
        decimal sum = 0m;
        foreach (DataRowView v in _byContract.FindRows(contractId))   // індексом, не перебором
            if ((DateTime)v["recognized_on"] <= asOf) sum += (decimal)v["amount"];
        return sum;
    }

    // Підсумок за НАБОРОМ: один прохід по визнаннях, решта — доступи за ключем.
    public IDictionary<string, decimal> RecognizedByKind(DateTime asOf)
    {
        var total = new SortedDictionary<string, decimal>();
        var products = new ProductModule(_data);
        DataTable contracts = _data.Tables["contracts"];
        foreach (DataRow r in _data.Tables["recognitions"].Rows)
        {
            if (r.RowState == DataRowState.Deleted) continue;   // до вилученого не дотягнешся
            if ((DateTime)r["recognized_on"] > asOf) continue;
            DataRow c = contracts.Rows.Find((long)r["contract_id"]);
            if (c == null) continue;                        // осиротіле визнання
            string kind = products.KindOf((long)c["product_id"]);
            total.TryGetValue(kind, out decimal had);
            total[kind] = had + (decimal)r["amount"];
        }
        return total;
    }

    // Ділимо так, щоб сума часток ТОЧНО дорівнювала цілому:
    // кожну — вниз до копійки, залишок — в останні частки.
    private static decimal[] SplitEvenly(decimal total, int n)
    {
        const decimal cent = 0.01m;
        decimal each = decimal.Floor(total / n / cent) * cent;
        int rest = (int)((total - each * n) / cent);            // 0 ≤ rest < n
        decimal[] parts = new decimal[n];
        for (int i = 0; i < n; i++) parts[i] = each;
        for (int i = n; rest > 0; rest--) parts[--i] += cent;
        return parts;
    }

    private void DropRecognitions(long contractId)
    {
        foreach (DataRowView v in _byContract.FindRows(contractId))
            v.Row.Delete();      // рядок лишається в наборі з міткою Deleted
    }
}
