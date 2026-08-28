void CustomPlugin::init()
{
    QGCCorePlugin::init();

    // Ті самі шляхи, під які підроблені псевдоніми в custom.qrc
    static constexpr const char *kOverridden[] = {
        "/qmlimages/PaperPlane.svg",
        "/qml/QGroundControl/FlyView/FlyViewCustomLayer.qml",
    };

    for (const char *path : kOverridden) {
        if (!QFile::exists(QStringLiteral(":") + QLatin1String(path))) {
            qWarning() << "Підміна мертва: апстрим більше не має" << path;
        }
    }
}
