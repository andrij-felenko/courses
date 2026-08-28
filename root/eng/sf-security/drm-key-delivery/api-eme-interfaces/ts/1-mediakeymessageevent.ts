interface MediaKeyMessageEvent extends Event {
  readonly messageType: MediaKeyMessageType;
  readonly message: ArrayBuffer;        // Бінарний челендж ліцензії (Challenge)
}

type MediaKeyMessageType = 
  | "license-request"                   // Первинний запит ліцензії
  | "license-renewal"                   // Запит на оновлення ліцензії, термін якої збігає
  | "license-release"                   // Повідомлення про звільнення офлайн-ліцензії
  | "individualization-request";        // Запит на персоналізацію/сертифікацію CDM
