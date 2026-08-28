// custom/src/CustomPlugin.cc
#include "CustomPlugin.h"

#include <QtCore/QApplicationStatic>
#include <QtCore/QFile>
#include <QtQml/QQmlApplicationEngine>

// ── Прапорці ─────────────────────────────────────────────────────────────

CustomOptions::CustomOptions(CustomPlugin *plugin, QObject *parent)
    : QGCOptions(parent)
    , _plugin(plugin)
{
}

bool CustomOptions::showFirmwareUpgrade() const
{
    return _plugin->showAdvancedUI();
}

// ── Перехоплювач адрес ───────────────────────────────────────────────────

QUrl CustomOverrideInterceptor::intercept(const QUrl &url,
                                          QQmlAbstractUrlInterceptor::DataType type)
{
    Q_UNUSED(type)

    if (url.scheme() != QStringLiteral("qrc")) {
        return url;                       // файли з диска нас не обходять
    }

    const QString overridePath = QStringLiteral("/Custom") + url.path();
    if (!QFile::exists(QStringLiteral(":") + overridePath)) {
        return url;                       // копії немає — хай іде стандартний
    }

    QUrl overridden(url);
    overridden.setPath(overridePath);
    return overridden;
}

// ── Саме розширення ──────────────────────────────────────────────────────

Q_APPLICATION_STATIC(CustomPlugin, _customPluginInstance);

CustomPlugin *CustomPlugin::instance()
{
    return _customPluginInstance();
}

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
{
    // Порожньо навмисно: див. нижче про момент виклику.
}

CustomPlugin::~CustomPlugin()
{
    delete _interceptor;                  // власника в нього немає
}

void CustomPlugin::init()
{
    QGCCorePlugin::init();
    // Тут — усе, що потребує піднятих підсистем застосунку.
}

QGCOptions *CustomPlugin::options()
{
    if (!_options) {
        _options = new CustomOptions(this, this);
    }
    return _options;
}

void CustomPlugin::paletteOverride(const QString &colorName,
                                   QGCPalette::PaletteColorInfo_t &colorInfo)
{
    if (colorName == QStringLiteral("window")) {
        colorInfo[QGCPalette::Dark][QGCPalette::ColorGroupEnabled]   = QColor("#12161f");
        colorInfo[QGCPalette::Dark][QGCPalette::ColorGroupDisabled]  = QColor("#12161f");
        colorInfo[QGCPalette::Light][QGCPalette::ColorGroupEnabled]  = QColor("#f4f6fa");
        colorInfo[QGCPalette::Light][QGCPalette::ColorGroupDisabled] = QColor("#f4f6fa");
    } else if (colorName == QStringLiteral("primaryButton")) {
        colorInfo[QGCPalette::Dark][QGCPalette::ColorGroupEnabled]   = QColor("#2f7d5b");
        colorInfo[QGCPalette::Dark][QGCPalette::ColorGroupDisabled]  = QColor("#41514a");
        colorInfo[QGCPalette::Light][QGCPalette::ColorGroupEnabled]  = QColor("#2f7d5b");
        colorInfo[QGCPalette::Light][QGCPalette::ColorGroupDisabled] = QColor("#9fb3aa");
    }
    // Решта кольорів лишається типовою — метод просто нічого не пише.
}

QQmlApplicationEngine *CustomPlugin::createQmlApplicationEngine(QObject *parent)
{
    QQmlApplicationEngine *const engine =
        QGCCorePlugin::createQmlApplicationEngine(parent);

    _interceptor = new CustomOverrideInterceptor();
    engine->addUrlInterceptor(_interceptor);   // до завантаження першого екрана
    return engine;
}
