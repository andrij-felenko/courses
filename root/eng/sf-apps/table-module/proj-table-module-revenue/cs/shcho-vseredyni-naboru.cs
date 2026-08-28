using System;
using System.Data;

// У .NET набір рядків уже написаний. Типи колонок, індекс за первинним ключем
// і стан рядка вбудовані; вторинний індекс доводиться заводити руками.
public static DataSet MakeSalesData()
{
    var data = new DataSet("sales");

    DataTable products = data.Tables.Add("products");
    products.Columns.Add("id", typeof(long));
    products.Columns.Add("kind", typeof(string));
    products.PrimaryKey = new[] { products.Columns["id"] };

    DataTable contracts = data.Tables.Add("contracts");
    contracts.Columns.Add("id", typeof(long));
    contracts.Columns.Add("product_id", typeof(long));
    contracts.Columns.Add("revenue", typeof(decimal));       // гроші — decimal, не double
    contracts.Columns.Add("signed_on", typeof(DateTime));
    contracts.PrimaryKey = new[] { contracts.Columns["id"] }; // ← індекс, яким живе Rows.Find

    DataTable recognitions = data.Tables.Add("recognitions");
    DataColumn rid = recognitions.Columns.Add("id", typeof(long));
    rid.AutoIncrement = true;
    rid.AutoIncrementSeed = -1;      // тимчасові ключі від'ємні: справжні роздасть база
    rid.AutoIncrementStep = -1;
    recognitions.Columns.Add("contract_id", typeof(long));
    recognitions.Columns.Add("amount", typeof(decimal));
    recognitions.Columns.Add("recognized_on", typeof(DateTime));
    recognitions.PrimaryKey = new[] { recognitions.Columns["id"] };

    return data;
}

// Мітка стану вже є на кожному рядку: row.RowState ∈ { Unchanged, Added, Modified, Deleted },
// а row["revenue", DataRowVersion.Original] віддасть значення, яке було до правки.
// Вторинний індекс за чужим ключем — це DataView із заданим Sort:
//     var byContract = new DataView(recognitions) { Sort = "contract_id" };
// Такий DataView будує індекс за колонкою, і FindRows шукає ним, а не перебором.
