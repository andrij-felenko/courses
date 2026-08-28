// Одне джерело правди для обох методів — і назва живе в одному місці
static constexpr char kPerimeterScan[] = "PerimeterScan";

QVariantList CustomPlugin::complexMissionItemNames(Vehicle *vehicle)
{
    QVariantList names = QGCCorePlugin::complexMissionItemNames(vehicle);
    names.append(QString::fromLatin1(kPerimeterScan));
    return names;
}

ComplexMissionItem *CustomPlugin::createComplexMissionItem(
        const QString &complexItemType, PlanMasterController *masterController,
        bool flyView, const QString &kmlOrShpFile)
{
    if (complexItemType == QLatin1String(kPerimeterScan)) {
        return new PerimeterScanItem(masterController, flyView, kmlOrShpFile);
    }
    // ⚠️ Без цього рядка зникнуть ВСІ штатні патерни зйомки
    return QGCCorePlugin::createComplexMissionItem(
        complexItemType, masterController, flyView, kmlOrShpFile);
}
