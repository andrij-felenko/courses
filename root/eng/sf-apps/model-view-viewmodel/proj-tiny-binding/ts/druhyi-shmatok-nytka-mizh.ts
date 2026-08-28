// ── 2а. Перетворювачі: у полі завжди рядок ──
interface Convert<V> {
  toView(v: V): string;      // властивість → текст поля
  toModel(s: string): V;     // текст поля → властивість
}

const asText: Convert<string> = {
  toView: v => v ?? '',
  toModel: s => s,
};

const asNumber: Convert<number> = {
  toView: v => Number.isFinite(v) ? String(v) : '',
  toModel: s => {
    const t = s.trim();
    return t === '' ? NaN : Number(t.replace(',', '.'));  // порожнє — НЕ нуль
  },
};
