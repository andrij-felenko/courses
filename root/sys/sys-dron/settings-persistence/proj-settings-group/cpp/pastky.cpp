void PayloadPlanner::saveProfiles(const QList<PayloadProfile> &profiles)
{
    QSettings settings;

    settings.remove(kProfilesRoot);          // без цього лишиться хвіст
    settings.beginGroup(kProfilesRoot);
    settings.setValue("count", profiles.count());

    for (int i = 0; i < profiles.count(); i++) {
        settings.beginGroup(QStringLiteral("Profile%1").arg(i));
        settings.setValue("name",     profiles[i].name);
        settings.setValue("interval", profiles[i].interval);
        settings.endGroup();
    }

    settings.endGroup();
}
