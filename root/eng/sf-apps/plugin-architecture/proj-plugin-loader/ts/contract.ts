// contract.ts — це знають ОБИДВІ сторони: і ядро, і кожен автор плагіна.
// Номер версії контракту. Піднімаємо його ЩОРАЗУ, коли міняємо форму гнізда
// так, що старі плагіни перестають працювати (несумісна зміна).
export const HOST_API = 3;

export interface Exporter {
  readonly extension: string;               // "pdf", "html", "md"
  export(doc: Document): Uint8Array;        // документ -> байти
}

export interface Host {
  // Вузьке вікно, яке ядро дає плагінові. НІЧОГО, крім цього, плагін
  // про ядро не знає — і не може дотягтись до його нутрощів.
  registerExporter(e: Exporter): void;
}

// Умовлена форма плагіна: модуль ЗОБОВ'ЯЗАНИЙ експортувати саме це —
//   export const PLUGIN_API = 3;
//   export function register(host: Host): void { ... }
