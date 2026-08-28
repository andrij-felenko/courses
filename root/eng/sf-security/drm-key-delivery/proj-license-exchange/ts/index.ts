/**
 * DrmLicenseManager: Універсальний контролер W3C EME для браузерного медіаплеєра.
 */
export interface DrmConfiguration {
  keySystem: string;            // наприклад, 'com.widevine.alpha' або 'com.microsoft.playready'
  licenseServerUrl: string;     // URL проксі-сервера видачі ліцензій
  authToken: string;            // JWT або сесійний токен користувача
  serverCertificate?: Uint8Array; // Публічний сертифікат сервера ліцензій
}

export class DrmLicenseManager {
  private videoElement: HTMLVideoElement;
  private config: DrmConfiguration;
  private mediaKeys: MediaKeys | null = null;
  private activeSession: MediaKeySession | null = null;
  private isInitializing: boolean = false;

  constructor(video: HTMLVideoElement, config: DrmConfiguration) {
    this.videoElement = video;
    this.config = config;
    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    this.videoElement.addEventListener('encrypted', (event: MediaEncryptedEvent) => {
      this.handleEncryptedEvent(event).catch((err) => {
        console.error('[DRM] Критична помилка обробки події encrypted:', err);
      });
    });
  }

  private async handleEncryptedEvent(event: MediaEncryptedEvent): Promise<void> {
    if (!event.initData) {
      console.warn('[DRM] Подія encrypted не містить initData');
      return;
    }

    if (this.isInitializing || this.activeSession) {
      // Сесія вже створена або ініціалізується
      return;
    }

    this.isInitializing = true;

    try {
      if (!this.mediaKeys) {
        await this.setupMediaKeys();
      }

      // Створення тимчасової сесії дешифрування
      const session = this.mediaKeys!.createSession('temporary');
      this.activeSession = session;

      // Підписка на повідомлення від CDM
      session.addEventListener('message', (msgEvent: MediaKeyMessageEvent) => {
        this.handleSessionMessage(session, msgEvent).catch((err) => {
          console.error('[DRM] Помилка доставки ліцензійного челенджу:', err);
        });
      });

      // Підписка на зміну статусу ключів
      session.addEventListener('keystatuseschange', () => {
        this.handleKeyStatusesChange(session);
      });

      const initDataType = event.initDataType || 'cenc';
      console.log(`[DRM] Генерація License Request для initDataType: ${initDataType}`);
      
      // Передаємо PSSH-бокс у CDM для створення Challenge
      await session.generateRequest(initDataType, event.initData);
    } finally {
      this.isInitializing = false;
    }
  }

  private async setupMediaKeys(): Promise<void> {
    const keySystemConfigs: MediaKeySystemConfiguration[] = [
      {
        initDataTypes: ['cenc'],
        audioCapabilities: [
          {
            contentType: 'audio/mp4; codecs="mp4a.40.2"',
            robustness: 'SW_SECURE_CRYPTO'
          }
        ],
        videoCapabilities: [
          {
            contentType: 'video/mp4; codecs="avc1.640028"',
            robustness: 'SW_SECURE_CRYPTO'
          },
          {
            contentType: 'video/mp4; codecs="hvc1.1.6.L153.B0"',
            robustness: 'HW_SECURE_ALL'
          }
        ],
        distinctiveIdentifier: 'optional',
        persistentState: 'optional',
        sessionTypes: ['temporary']
      }
    ];

    console.log(`[DRM] Запит доступу до системи: ${this.config.keySystem}`);
    const keySystemAccess = await navigator.requestMediaKeySystemAccess(
      this.config.keySystem,
      keySystemConfigs
    );

    const mediaKeys = await keySystemAccess.createMediaKeys();

    // Якщо надано сертифікат сервера, завантажуємо його перед запитом ліцензії
    if (this.config.serverCertificate) {
      console.log('[DRM] Встановлення публічного сертифіката сервера ліцензій...');
      await mediaKeys.setServerCertificate(this.config.serverCertificate as unknown as BufferSource);
    }

    // Прив'язка криптографічного контексту до HTML5 Video Element
    await this.videoElement.setMediaKeys(mediaKeys);
    this.mediaKeys = mediaKeys;
    console.log('[DRM] MediaKeys успішно прив\'язано до медіаелемента');
  }

  private async handleSessionMessage(
    session: MediaKeySession,
    event: MediaKeyMessageEvent
  ): Promise<void> {
    const challenge = event.message;
    console.log(`[DRM] Отримано ${challenge.byteLength} байтів челенджу (${event.messageType}). Відправка на сервер...`);

    // Мережевий запит на License Proxy з авторизаційним заголовком
    const response = await fetch(this.config.licenseServerUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': `Bearer ${this.config.authToken}`,
        'X-DRM-Message-Type': event.messageType
      },
      body: challenge
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Сервер ліцензій відхилив запит (${response.statusText})`);
    }

    const licenseData = await response.arrayBuffer();
    console.log(`[DRM] Отримано ліцензійну відповідь: ${licenseData.byteLength} байтів. Оновлення сесії CDM...`);

    // Завантаження зашифрованої ліцензії в CDM
    await session.update(licenseData);
    console.log('[DRM] Сесію CDM успішно оновлено (License Response застосовано)');
  }

  private handleKeyStatusesChange(session: MediaKeySession): void {
    console.log(`[DRM] Зміна статусу ключів (всього ключів у сесії: ${session.keyStatuses.size}):`);
    
    session.keyStatuses.forEach((status: MediaKeyStatus, keyIdBuffer: ArrayBuffer) => {
      const kidHex = Array.from(new Uint8Array(keyIdBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
      
      console.log(`  - KID [${kidHex}]: статус = ${status}`);

      if (status === 'output-restricted') {
        console.warn(`[DRM] Попередження: Ключ ${kidHex} обмежено політикою HDCP. Відео може бути заблоковано.`);
      } else if (status === 'internal-error') {
        console.error(`[DRM] Апаратна помилка TEE під час розгортання ключа ${kidHex}`);
      }
    });
  }

  public async destroy(): Promise<void> {
    if (this.activeSession) {
      await this.activeSession.close();
      this.activeSession = null;
    }
    if (this.videoElement) {
      await this.videoElement.setMediaKeys(null);
    }
    this.mediaKeys = null;
  }
}
