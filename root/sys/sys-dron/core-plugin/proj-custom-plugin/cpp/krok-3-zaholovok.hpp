// custom/src/CustomPlugin.h
#pragma once

#include <QtQml/QQmlAbstractUrlInterceptor>

#include "QGCCorePlugin.h"
#include "QGCOptions.h"
#include "QGCPalette.h"

class CustomPlugin;

/// Прапорці: що показувати й що дозволяти саме в нашому продукті.
class CustomOptions : public QGCOptions
{
    Q_OBJECT
public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);

    // Прошивку оновлює лише той, хто свідомо ввімкнув розширений режим.
    bool showFirmwareUpgrade() const final;

    // Апарат приїжджає відкаліброваним — майстри покупцеві ні до чого.
    bool showSensorCalibrationCompass() const final { return false; }
    bool showSensorCalibrationLevel()   const final { return false; }

private:
    CustomPlugin *_plugin = nullptr;
};

/// Перехоплювач адрес: підмінює файл ресурсу, не чіпаючи місць виклику.
class CustomOverrideInterceptor : public QQmlAbstractUrlInterceptor
{
public:
    QUrl intercept(const QUrl &url,
                   QQmlAbstractUrlInterceptor::DataType type) final;
};

class CustomPlugin : public QGCCorePlugin
{
    Q_OBJECT
public:
    explicit CustomPlugin(QObject *parent = nullptr);
    ~CustomPlugin() override;

    /// ⚠️ Обов'язковий: саме сюди веде CUSTOMCLASS::instance() в апстримі.
    static CustomPlugin *instance();

    void init() final;

    QGCOptions *options() final;
    void paletteOverride(const QString &colorName,
                         QGCPalette::PaletteColorInfo_t &colorInfo) final;
    QQmlApplicationEngine *createQmlApplicationEngine(QObject *parent) final;

private:
    CustomOptions *_options = nullptr;
    CustomOverrideInterceptor *_interceptor = nullptr;
};
