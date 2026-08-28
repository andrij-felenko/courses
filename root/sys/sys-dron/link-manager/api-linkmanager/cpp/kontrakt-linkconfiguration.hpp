bool isForwarding() const;             void setForwarding(bool forwarding = true);
bool suppressAutoReconnect() const;    void setSuppressAutoReconnect(bool suppress);
bool autoConnectStarted() const;       void setAutoConnectStarted(bool started);

bool reconnectReady() const;           // чи минула витримка після невдалої спроби
void noteReconnectAttempt();           // зафіксувати невдачу — витримка подвоїться
void resetReconnectBackoff();          // явне під'єднання скидає лічильник
void noteConnected();                  void noteDisconnected();

virtual void copyFrom(const LinkConfiguration *source);
virtual LinkType type() const = 0;
virtual void loadSettings(QSettings &settings, const QString &root) = 0;
virtual void saveSettings(QSettings &settings, const QString &root) const = 0;

static LinkConfiguration *createSettings(int type, const QString &name);
static LinkConfiguration *duplicateSettings(const LinkConfiguration *source);
