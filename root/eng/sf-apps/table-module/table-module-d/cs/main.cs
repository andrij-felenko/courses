// Набір рядків: contracts(id, product_id, revenue, signed_on)
//               recognitions(contract_id, amount, recognized_on)
// У contracts заданий PrimaryKey = id — саме тому працює дешевий Rows.Find.
public class ContractModule
{
    private readonly DataSet _data;              // стан — у наборі рядків, а не в полях модуля
    public ContractModule(DataSet data) { _data = data; }

    // тотожності немає: рядок називають ключем у виклику
    public void CalculateRecognitions(long contractId)
    {
        DataRow contract = _data.Tables["contracts"].Rows.Find(contractId);
        decimal revenue = (decimal)contract["revenue"];
        DateTime signed = (DateTime)contract["signed_on"];

        // про товар питаємо модуль товарів — і знову ключем
        string type = new ProductModule(_data).TypeOf((long)contract["product_id"]);

        if (type == "spreadsheet")                // вибір за ЗНАЧЕННЯМ у рядку, не за типом об'єкта
        {
            decimal third = Math.Round(revenue / 3, 2);
            AddRecognition(contractId, third, signed);
            AddRecognition(contractId, third, signed.AddDays(60));
            AddRecognition(contractId, revenue - 2 * third, signed.AddDays(90));  // залишок — щоб сума зійшлася
        }
        else
        {
            AddRecognition(contractId, revenue, signed);
        }
    }

    // питання «скільки визнано на дату» — підсумок по набору, а не обхід об'єктів
    public decimal RecognizedRevenue(long contractId, DateTime asOf)
    {
        object sum = _data.Tables["recognitions"].Compute(
            "sum(amount)",
            $"contract_id = {contractId} and recognized_on <= #{asOf:MM/dd/yyyy}#");
        return sum is DBNull ? 0m : (decimal)sum;
    }

    private void AddRecognition(long contractId, decimal amount, DateTime on)
    {
        DataTable t = _data.Tables["recognitions"];
        DataRow r = t.NewRow();
        r["contract_id"] = contractId;
        r["amount"] = amount;
        r["recognized_on"] = on;
        t.Rows.Add(r);                            // зміна лягає в набір; до бази вона поїде потім, разом з іншими
    }
}
