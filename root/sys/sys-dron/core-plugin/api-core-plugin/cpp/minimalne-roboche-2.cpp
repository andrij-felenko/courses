QQmlApplicationEngine *CustomPlugin::createQmlApplicationEngine(QObject *parent)
{
    _qmlEngine = QGCCorePlugin::createQmlApplicationEngine(parent);   // спершу базовий!
    _qmlEngine->addImportPath("qrc:/qml/Custom/Widgets");
    _selector = new CustomOverrideInterceptor();
    _qmlEngine->addUrlInterceptor(_selector);
    return _qmlEngine;
}

void CustomPlugin::cleanup()
{
    if (_qmlEngine) { _qmlEngine->removeUrlInterceptor(_selector); }
    delete _selector;
}
