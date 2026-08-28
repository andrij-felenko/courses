// Прохід 3: номер — це позиція в остаточному масиві, рахуючи від нуля.
static void renumber(QVector<Record>& records)
{
    for (int i = 0; i < records.count(); i++) {
        records[i].seq     = static_cast<quint16>(i);
        records[i].current = (i == 0) ? 1 : 0;
    }
}

// Прохід 4: ім'я doJumpId → теперішній номер. Тільки після перенумерації.
static bool retargetJumps(QVector<Record>& records, QString& err)
{
    QHash<int, quint16> seqByName;
    for (const Record& rec : records) {
        if (rec.doJumpId < 0) {
            continue;
        }
        if (seqByName.contains(rec.doJumpId)) {
            err = QStringLiteral("ім'я doJumpId %1 трапляється двічі — стрибок став би двозначним")
                      .arg(rec.doJumpId);
            return false;
        }
        seqByName.insert(rec.doJumpId, rec.seq);
    }

    for (Record& rec : records) {
        if (rec.command != MAV_CMD_DO_JUMP) {
            continue;
        }
        if (qIsNaN(rec.params[0])) {
            err = QStringLiteral("DO_JUMP без цілі: у param1 лежить NaN");
            return false;
        }

        const int name = static_cast<int>(rec.params[0]);
        const auto it  = seqByName.constFind(name);
        if (it == seqByName.constEnd()) {
            err = QStringLiteral("DO_JUMP посилається на ім'я %1, якого в плані немає").arg(name);
            return false;
        }
        rec.params[0] = *it;
    }
    return true;
}
