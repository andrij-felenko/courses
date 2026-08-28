QString applicationName;
if (_runningUnitTests || _simpleBootTest) {
    // …ім'я з міткою тесту, щоб прогони не заважали один одному
} else {
#ifdef QGC_DAILY_BUILD
    applicationName = QStringLiteral("%1 Daily").arg(QGC_APP_NAME);
#else
    applicationName = QGC_APP_NAME;
#endif
}

setApplicationName(applicationName);
setDesktopFileName(QGC_PACKAGE_NAME);
setOrganizationName(QGC_ORG_NAME);
setOrganizationDomain(QGC_ORG_DOMAIN);
setApplicationVersion(QString(QGC_APP_VERSION_STR));
