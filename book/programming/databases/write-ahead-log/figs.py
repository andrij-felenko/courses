import os
os.makedirs("book/programming/databases/write-ahead-log/img", exist_ok=True)

svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 280" width="100%" height="100%">
<style>
  .box { fill: #1e293b; stroke: #3b82f6; stroke-width: 2; rx: 8px; }
  .box-disk { fill: #0f172a; stroke: #10b981; stroke-width: 2; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
  .arrow { stroke: #38bdf8; stroke-width: 2; fill: none; marker-end: url(#ah); }
</style>
<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#38bdf8" /></marker></defs>
<rect width="800" height="280" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Життєвий цикл журналу попереднього запису (WAL Pipeline)</text>
<text x="30" y="55" class="txt-muted">Інваріант WAL: Запис у журнал на диск ПЕРЕД скиданням брудної сторінки даних</text>
<g transform="translate(40, 85)"><rect width="210" height="150" class="box" /><text x="15" y="25" class="txt-bold" fill="#60a5fa">1. Оперативна пам'ять</text><text x="15" y="55" class="txt">WAL Buffers: запис LSN</text><text x="15" y="80" class="txt">Buffer Pool: Dirty Page</text><text x="15" y="115" class="txt-muted">PageLSN = 10450</text></g>
<path d="M 250 160 L 290 160" class="arrow" />
<g transform="translate(295, 85)"><rect width="210" height="150" class="box-disk" /><text x="15" y="25" class="txt-bold" fill="#34d399">2. Послідовний WAL</text><text x="15" y="55" class="txt">Синхронний fsync()</text><text x="15" y="80" class="txt">Append-Only на диск</text><text x="15" y="115" class="txt-bold" fill="#38bdf8">FlushedLSN = 10500</text></g>
<path d="M 505 160 L 545 160" class="arrow" />
<g transform="translate(550, 85)"><rect width="210" height="150" class="box" stroke="#f59e0b" /><text x="15" y="25" class="txt-bold" fill="#fbbf24">3. Файли даних (Heap)</text><text x="15" y="55" class="txt">Асинхронний Checkpoint</text><text x="15" y="80" class="txt">Випадковий I/O запис</text><text x="15" y="115" class="txt-muted">FlushedLSN ≥ PageLSN</text></g>
</svg>"""

svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 280" width="100%" height="100%">
<style>
  .phase { fill: #1e293b; stroke: #64748b; stroke-width: 1.5; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
</style>
<rect width="800" height="280" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Три фази відновлення за алгоритмом ARIES</text>
<g transform="translate(40, 75)"><rect width="225" height="165" class="phase" stroke="#3b82f6" stroke-width="2" /><text x="15" y="30" class="txt-bold" fill="#60a5fa">Фаза 1: Analysis</text><text x="15" y="60" class="txt">Сканування вперед від чекпойнта</text><text x="15" y="85" class="txt">Відновлення Dirty Page Table</text><text x="15" y="110" class="txt">Виявлення активних транзакцій</text><text x="15" y="140" class="txt-muted">Визначає точку старту RedoLSN</text></g>
<g transform="translate(285, 75)"><rect width="225" height="165" class="phase" stroke="#10b981" stroke-width="2" /><text x="15" y="30" class="txt-bold" fill="#34d399">Фаза 2: Redo</text><text x="15" y="60" class="txt">Повторення всієї історії</text><text x="15" y="85" class="txt">Відтворення committed + aborted</text><text x="15" y="110" class="txt">Ідемпотентне накатування змін</text><text x="15" y="140" class="txt-muted">Повертає стан на момент краху</text></g>
<g transform="translate(530, 75)"><rect width="230" height="165" class="phase" stroke="#ef4444" stroke-width="2" /><text x="15" y="30" class="txt-bold" fill="#f87171">Фаза 3: Undo</text><text x="15" y="60" class="txt">Зворотне сканування журналу</text><text x="15" y="85" class="txt">Відкат незавершених транзакцій</text><text x="15" y="110" class="txt">Запис CLR (Compensation Logs)</text><text x="15" y="140" class="txt-muted">Гарантує завершення відкату</text></g>
</svg>"""

svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 260" width="100%" height="100%">
<style>
  .card { fill: #1e293b; stroke: #334155; stroke-width: 1.5; rx: 8px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
</style>
<rect width="800" height="260" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Ієрархія номерів LSN (Log Sequence Number)</text>
<g transform="translate(40, 70)"><rect width="340" height="150" class="card" stroke="#3b82f6" stroke-width="2" /><text x="20" y="30" class="txt-bold" fill="#60a5fa">PageLSN (у заголовку сторінки)</text><text x="20" y="60" class="txt">Останній LSN, що змінив цю сторінку</text><text x="20" y="85" class="txt">Дозволяє уникати повторного Redo</text><text x="20" y="115" class="txt-bold" fill="#38bdf8">Якщо RecordLSN ≤ PageLSN → Пропуск</text></g>
<g transform="translate(420, 70)"><rect width="340" height="150" class="card" stroke="#10b981" stroke-width="2" /><text x="20" y="30" class="txt-bold" fill="#34d399">FlushedLSN (на дисковому накопичувачі)</text><text x="20" y="60" class="txt">Максимальний LSN, синхронізований на диск</text><text x="20" y="85" class="txt">Контролює скидання брудних сторінок</text><text x="20" y="115" class="txt-bold" fill="#34d399">Сторінка скидається лише якщо PageLSN ≤ FlushedLSN</text></g>
</svg>"""

svg4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 260" width="100%" height="100%">
<style>
  .bar { fill: #1e293b; stroke: #475569; stroke-width: 1.5; rx: 6px; }
  .txt { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-bold { fill: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-muted { fill: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; }
</style>
<rect width="800" height="260" fill="#0b0f19" rx="12" />
<text x="30" y="35" class="txt-bold" font-size="16">Пакетна синхронізація транзакцій (Group Commit Pipeline)</text>
<g transform="translate(40, 70)"><rect width="340" height="150" class="bar" stroke="#ef4444" stroke-width="2" /><text x="20" y="30" class="txt-bold" fill="#f87171">Без Group Commit</text><text x="20" y="60" class="txt">Кожен COMMIT викликає окремий fsync()</text><text x="20" y="85" class="txt">1000 tx/sec = 1000 операцій вводу/виводу</text><text x="20" y="115" class="txt-muted">Жорстке дискове обмеження IOPS</text></g>
<g transform="translate(420, 70)"><rect width="340" height="150" class="bar" stroke="#10b981" stroke-width="2" /><text x="20" y="30" class="txt-bold" fill="#34d399">З Group Commit</text><text x="20" y="60" class="txt">Групування 50 транзакцій в один пакет</text><text x="20" y="85" class="txt">1 єдиний системний виклик fsync() на пачку</text><text x="20" y="115" class="txt-bold" fill="#38bdf8">Зростання пропускної здатності в десятки разів</text></g>
</svg>"""

with open("book/programming/databases/write-ahead-log/img/wal-lifecycle.svg", "w", encoding="utf-8") as f: f.write(svg1)
with open("book/programming/databases/write-ahead-log/img/aries-recovery-phases.svg", "w", encoding="utf-8") as f: f.write(svg2)
with open("book/programming/databases/write-ahead-log/img/lsn-page-relationship.svg", "w", encoding="utf-8") as f: f.write(svg3)
with open("book/programming/databases/write-ahead-log/img/group-commit-pipeline.svg", "w", encoding="utf-8") as f: f.write(svg4)
print("Generated WAL SVGs")
