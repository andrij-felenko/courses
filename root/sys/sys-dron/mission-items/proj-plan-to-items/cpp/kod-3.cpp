// Ціле поле int32 не має NaN і не має «майже нуля» — або число, або відмова.
static bool packInt32(double value, const char* field, qint32& out, QString& err)
{
    if (qIsNaN(value)) {
        err = QStringLiteral("поле %1 не може бути NaN: воно ціле, а нулем підміняти не можна")
                  .arg(QLatin1String(field));
        return false;
    }
    // Межі перевіряємо ДО округлення: qRound64 від нескінченності або від числа
    // поза діапазоном дає невизначену поведінку, а не «велике число».
    if (!(value >= -2147483648.0 && value <= 2147483647.0)) {
        err = QStringLiteral("поле %1 (%2) не влазить у int32")
                  .arg(QLatin1String(field)).arg(value);
        return false;
    }
    out = static_cast<qint32>(qRound64(value));
    return true;
}

// Прохід 5: градуси → десятимільйонні частки градуса, крім MAV_FRAME_MISSION.
static bool toMissionItemInt(const Record& rec, mavlink_mission_item_int_t& out, QString& err)
{
    out = {};
    out.seq          = rec.seq;
    out.frame        = rec.frame;
    out.command      = rec.command;
    out.current      = rec.current;
    out.autocontinue = rec.autocontinue;
    out.mission_type = MAV_MISSION_TYPE_MISSION;
    // target_system і target_component проставляє той, хто відправлятиме.

    // Ці п'ять полів — float: NaN тут легальний і значущий («лиши як є»).
    out.param1 = static_cast<float>(rec.params[0]);
    out.param2 = static_cast<float>(rec.params[1]);
    out.param3 = static_cast<float>(rec.params[2]);
    out.param4 = static_cast<float>(rec.params[3]);
    out.z      = static_cast<float>(rec.params[6]);

    const bool spatial = (rec.frame != MAV_FRAME_MISSION);
    return packInt32(spatial ? rec.params[4] * 1e7 : rec.params[4], "x", out.x, err)
        && packInt32(spatial ? rec.params[5] * 1e7 : rec.params[5], "y", out.y, err);
}

// Увесь конвеєр в одному місці.
bool missionFromPlanFile(const QString& path, bool homeAsItemZero,
                         QVector<mavlink_mission_item_int_t>& mission, QString& err)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        err = QStringLiteral("не відкривається %1: %2").arg(path, file.errorString());
        return false;
    }

    QJsonParseError parseError {};
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &parseError);
    if (parseError.error != QJsonParseError::NoError) {
        err = QStringLiteral("зіпсований JSON: %1").arg(parseError.errorString());
        return false;
    }

    const QJsonObject plan = doc.object();
    if (plan.value(QStringLiteral("fileType")).toString() != QLatin1String("Plan")) {
        err = QStringLiteral("це не файл плану: ключ fileType не «Plan»");
        return false;
    }

    QVector<Record> records;
    if (!recordsFromPlan(plan, homeAsItemZero, records, err)) {   // проходи 1 і 2
        return false;
    }
    renumber(records);                                            // прохід 3
    if (!retargetJumps(records, err)) {                           // прохід 4
        return false;
    }

    mission.clear();
    mission.reserve(records.count());
    for (const Record& rec : records) {                           // прохід 5
        mavlink_mission_item_int_t item {};
        if (!toMissionItemInt(rec, item, err)) {
            return false;
        }
        mission.append(item);
    }
    return true;
}
