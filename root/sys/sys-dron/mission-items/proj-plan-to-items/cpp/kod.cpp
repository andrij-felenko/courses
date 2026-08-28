#include <QFile>
#include <QHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>
#include <QString>
#include <QVector>
#include <QtGlobal>
#include <QtMath>

#include <mavlink/common/mavlink.h>

// Один запис місії: рівно ті поля, що є в MISSION_ITEM_INT, плюс ім'я з файлу.
struct Record {
    quint16 command      = 0;
    quint8  frame        = 0;
    quint8  autocontinue = 1;
    double  params[7]    {};    // param1..4, x, y, z — координати в ГРАДУСАХ
    int     doJumpId     = -1;  // ім'я з файлу; -1 = імені немає
    quint16 seq          = 0;   // проставить перенумерація
    quint8  current      = 0;
};

// NaN у файлі записано як null: JSON не має способу зобразити NaN числом, тому
// застосунок пише null і на завантаженні чекає саме null.
static double numberOrNaN(const QJsonValue& value)
{
    return (value.isNull() || value.isUndefined()) ? qQNaN() : value.toDouble();
}

// Старіша форма елемента клала в params лише param1..param4, а координату —
// окремим ключем "coordinate": [широта, довгота, висота]. Зводимо до теперішньої
// форми, інакше спіткнемося на першому ж елементі старого файлу.
static QJsonArray sevenParams(const QJsonObject& obj, QString& err)
{
    QJsonArray params = obj.value(QStringLiteral("params")).toArray();

    if (params.count() == 4 && obj.contains(QStringLiteral("coordinate"))) {
        const QJsonArray coordinate = obj.value(QStringLiteral("coordinate")).toArray();
        if (coordinate.count() != 3) {
            err = QStringLiteral("ключ coordinate має бути [широта, довгота, висота]");
            return {};
        }
        for (const QJsonValue& value : coordinate) {
            params.append(value);
        }
    }

    if (params.count() != 7) {
        err = QStringLiteral("очікується рівно 7 параметрів, знайдено %1").arg(params.count());
        return {};
    }
    return params;
}

static bool recordFromSimpleItem(const QJsonObject& obj, Record& rec, QString& err)
{
    const QJsonArray params = sevenParams(obj, err);
    if (params.isEmpty()) {
        return false;
    }

    rec.command      = static_cast<quint16>(obj.value(QStringLiteral("command")).toInt());
    rec.frame        = static_cast<quint8>(obj.value(QStringLiteral("frame")).toInt());
    rec.autocontinue = obj.value(QStringLiteral("autoContinue")).toBool(true) ? 1 : 0;
    rec.doJumpId     = obj.value(QStringLiteral("doJumpId")).toInt(-1);

    for (int i = 0; i < 7; i++) {
        rec.params[i] = numberOrNaN(params.at(i));
    }
    return true;
}

// Проходи 1 і 2: читання масиву items і — за потреби — дім нульовим записом.
static bool recordsFromPlan(const QJsonObject& plan, bool homeAsItemZero,
                            QVector<Record>& records, QString& err)
{
    const QJsonObject mission = plan.value(QStringLiteral("mission")).toObject();
    const QJsonArray  items   = mission.value(QStringLiteral("items")).toArray();

    if (items.isEmpty()) {
        err = QStringLiteral("масив items порожній: порожня місія і відсутня місія — різні речі");
        return false;
    }

    if (homeAsItemZero) {
        const QJsonArray home = mission.value(QStringLiteral("plannedHomePosition")).toArray();
        if (home.count() != 3) {
            err = QStringLiteral("plannedHomePosition має бути [широта, довгота, висота AMSL]");
            return false;
        }
        Record rec;
        rec.command   = MAV_CMD_NAV_WAYPOINT;
        rec.frame     = MAV_FRAME_GLOBAL;        // дім завжди в абсолютній висоті
        rec.params[4] = home.at(0).toDouble();
        rec.params[5] = home.at(1).toDouble();
        rec.params[6] = home.at(2).toDouble();
        records.append(rec);
    }

    for (int i = 0; i < items.count(); i++) {
        const QJsonObject obj  = items.at(i).toObject();
        const QString     kind = obj.value(QStringLiteral("type")).toString();

        if (kind == QLatin1String("SimpleItem")) {
            Record rec;
            if (!recordFromSimpleItem(obj, rec, err)) {
                err = QStringLiteral("items[%1]: %2").arg(i).arg(err);
                return false;
            }
            records.append(rec);
        } else if (kind == QLatin1String("ComplexItem")) {
            err = QStringLiteral("items[%1]: складений елемент «%2» зберігається параметрами "
                                 "й розгортається не тут")
                      .arg(i)
                      .arg(obj.value(QStringLiteral("complexItemType")).toString());
            return false;
        } else {
            err = QStringLiteral("items[%1]: невідомий тип елемента «%2»").arg(i).arg(kind);
            return false;
        }
    }
    return true;
}
