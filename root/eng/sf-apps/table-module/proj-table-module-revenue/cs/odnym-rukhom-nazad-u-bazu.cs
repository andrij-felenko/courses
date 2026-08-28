using System.Data;
using Microsoft.Data.SqlClient;

public static void Save(DataSet data, SqlConnection cn,
                        SqlDataAdapter contracts, SqlDataAdapter recognitions)
{
    using SqlTransaction tx = cn.BeginTransaction();   // Dispose без Commit = відкат
    Enlist(contracts, tx);
    Enlist(recognitions, tx);

    // Update за замовчуванням сам кличе AcceptChanges на кожному вдалому рядку.
    // Тоді відкат транзакції прибере зміни в базі — але не в наборі, і той збреше.
    contracts.AcceptChangesDuringUpdate = false;
    recognitions.AcceptChangesDuringUpdate = false;

    contracts.Update(data, "contracts");               // поїдуть лише помічені рядки
    recognitions.Update(data, "recognitions");

    tx.Commit();
    data.AcceptChanges();                              // мітки скидаємо ЛИШЕ після commit
}

private static void Enlist(SqlDataAdapter a, SqlTransaction tx)
{
    foreach (SqlCommand cmd in new[] { a.InsertCommand, a.UpdateCommand, a.DeleteCommand })
        if (cmd != null) cmd.Transaction = tx;
}
