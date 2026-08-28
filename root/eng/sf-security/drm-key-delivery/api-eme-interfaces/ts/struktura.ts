interface MediaKeySystemConfiguration {
  label?: string;
  initDataTypes?: string[];              // ['cenc', 'keyids', 'webm']
  audioCapabilities?: MediaKeySystemMediaCapability[];
  videoCapabilities?: MediaKeySystemMediaCapability[];
  distinctiveIdentifier?: "required" | "optional" | "not-allowed";
  persistentState?: "required" | "optional" | "not-allowed";
  sessionTypes?: string[];               // ['temporary', 'persistent-license']
}

interface MediaKeySystemMediaCapability {
  contentType: string;                   // MIME-тип із кодеками: 'video/mp4; codecs="avc1.640028"'
  robustness?: string;                   // Рівень стійкості: 'SW_SECURE_CRYPTO', 'HW_SECURE_ALL' тощо
  encryptionScheme?: "cenc" | "cbcs" | "cbcs-1-9" | null;
}
