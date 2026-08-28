import * as fs from "fs";
import * as path from "path";

// ── Табличний розрахунок CRC32 (IEEE 802.3) ──────────────────────────────────
class Crc32 {
  private static table: Uint32Array = (() => {
    const tbl = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
      let c = i;
      for (let k = 0; k < 8; k++) {
        c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      }
      tbl[i] = c >>> 0;
    }
    return tbl;
  })();

  static calculate(buf: Buffer): number {
    let crc = 0xffffffff;
    for (let i = 0; i < buf.length; i++) {
      crc = (crc >>> 8) ^ Crc32.table[(crc ^ buf[i]) & 0xff];
    }
    return (crc ^ 0xffffffff) >>> 0;
  }
}

const WAL_MAGIC = 0x57414c31; // "WAL1"
const HEADER_SIZE = 24; // Magic(4) + Seq(8) + Timestamp(8) + Len(4)

// ── Документ у пам'яті ──────────────────────────────────────────────────────
export class DocumentModel {
  private lines: string[] = [];

  applyOperation(op: string): void {
    if (op.startsWith("INSERT:")) {
      this.lines.push(op.slice(7));
    } else if (op === "CLEAR") {
      this.lines = [];
    }
  }

  serialize(): string {
    return this.lines.join("\n") + "\n";
  }

  deserialize(content: string): void {
    this.lines = content.split("\n").filter((l) => l.length > 0);
  }

  getLines(): string[] {
    return [...this.lines];
  }
}

// ── Менеджер аварійної стійкості (Write-Ahead Log + Snapshotting) ────────────
export class CrashResilientStore {
  private snapPath: string;
  private walPath: string;
  private lockPath: string;
  private seqNum = 0n;
  private lockFd: number | null = null;

  constructor(basePath: string) {
    this.snapPath = `${basePath}.snap`;
    this.walPath = `${basePath}.wal`;
    this.lockPath = `${basePath}.lock`;
  }

  // Ексклюзивне блокування через відкриття з прапорцем O_EXCL
  acquireLock(): boolean {
    try {
      this.lockFd = fs.openSync(this.lockPath, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_RDWR);
      return true;
    } catch {
      return false; // Файл уже заблоковано іншим процесом
    }
  }

  releaseLock(): void {
    if (this.lockFd !== null) {
      fs.closeSync(this.lockFd);
      try { fs.unlinkSync(this.lockPath); } catch {}
      this.lockFd = null;
    }
  }

  // Відновлення після аварії
  recover(model: DocumentModel): void {
    // 1. Читання базового знімка
    if (fs.existsSync(this.snapPath)) {
      const snapContent = fs.readFileSync(this.snapPath, "utf-8");
      model.deserialize(snapContent);
    }

    // 2. Читання та валідація журналу WAL
    if (!fs.existsSync(this.walPath)) return;

    const walBuffer = fs.readFileSync(this.walPath);
    let offset = 0;
    let validOps = 0;

    while (offset + HEADER_SIZE + 4 <= walBuffer.length) {
      const magic = walBuffer.readUInt32LE(offset);
      if (magic !== WAL_MAGIC) break;

      const seq = walBuffer.readBigUInt64LE(offset + 4);
      const payloadLen = walBuffer.readUInt32LE(offset + 20);

      const totalSize = HEADER_SIZE + payloadLen + 4;
      if (offset + totalSize > walBuffer.length) {
        // Розірваний запис на хвості файлу — крах перервав запис
        break;
      }

      const payloadBuf = walBuffer.subarray(offset + HEADER_SIZE, offset + HEADER_SIZE + payloadLen);
      const storedCrc = walBuffer.readUInt32LE(offset + HEADER_SIZE + payloadLen);

      // Перевірка цілісності корисного навантаження
      if (Crc32.calculate(payloadBuf) !== storedCrc) {
        // Спотворені байти — зупинка відновлення
        break;
      }

      const op = payloadBuf.toString("utf-8");
      model.applyOperation(op);

      if (seq > this.seqNum) this.seqNum = seq;
      offset += totalSize;
      validOps++;
    }

    // 3. Автоматичний знімок після відновлення для очищення обробленого WAL
    if (validOps > 0) {
      this.checkpoint(model);
    }
  }

  // Дописування операції в кінець WAL
  appendOperation(op: string): void {
    this.seqNum++;
    const payloadBuf = Buffer.from(op, "utf-8");
    const crc = Crc32.calculate(payloadBuf);

    const record = Buffer.alloc(HEADER_SIZE + payloadBuf.length + 4);
    record.writeUInt32LE(WAL_MAGIC, 0);
    record.writeBigUInt64LE(this.seqNum, 4);
    record.writeBigInt64LE(BigInt(Date.now()), 12);
    record.writeUInt32LE(payloadBuf.length, 20);

    payloadBuf.copy(record, HEADER_SIZE);
    record.writeUInt32LE(crc, HEADER_SIZE + payloadBuf.length);

    fs.appendFileSync(this.walPath, record);
  }

  // Контрольна точка: атомарний знімок + truncate WAL
  checkpoint(model: DocumentModel): void {
    const tmpSnap = `${this.snapPath}.tmp`;
    fs.writeFileSync(tmpSnap, model.serialize(), "utf-8");

    // Атомарна підміна
    fs.renameSync(tmpSnap, this.snapPath);

    // Очищення файлу журналу
    fs.writeFileSync(this.walPath, Buffer.alloc(0));
  }
}
