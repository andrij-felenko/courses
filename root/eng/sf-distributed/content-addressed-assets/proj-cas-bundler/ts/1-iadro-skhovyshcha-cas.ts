import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';

export class ContentAddressableStore {
  private readonly rootDir: string;
  private readonly tmpDir: string;

  constructor(rootDir: string) {
    this.rootDir = path.resolve(rootDir);
    this.tmpDir = path.join(this.rootDir, 'tmp');
    fs.mkdirSync(this.tmpDir, { recursive: true });
  }

  // Обчислення криптографічного дайджесту SHA-256
  public computeHash(content: Buffer | string): string {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  // Шлях до об'єкта зі структурою каталогів 2/62 символи
  public getBlobPath(digest: string): string {
    const prefix = digest.slice(0, 2);
    const remainder = digest.slice(2);
    return path.join(this.rootDir, prefix, remainder);
  }

  // Атомарний запис блобу
  public put(content: Buffer | string): string {
    const buffer = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf-8');
    const digest = this.computeHash(buffer);
    const targetPath = this.getBlobPath(digest);

    if (fs.existsSync(targetPath)) {
      return digest; // Повна дедуплікація
    }

    fs.mkdirSync(path.dirname(targetPath), { recursive: true });

    // Тимчасовий файл у межах того ж монтування для атомарного rename
    const tempFile = path.join(this.tmpDir, `${digest}.${Date.now()}.${Math.random().toString(36).slice(2)}.tmp`);
    fs.writeFileSync(tempFile, buffer);
    fs.renameSync(tempFile, targetPath);

    return digest;
  }

  // Читання з миттєвою верифікацією
  public get(digest: string): Buffer | null {
    const targetPath = this.getBlobPath(digest);
    if (!fs.existsSync(targetPath)) {
      return null;
    }

    const data = fs.readFileSync(targetPath);
    const actualHash = this.computeHash(data);

    if (actualHash !== digest) {
      throw new Error(`[Помилка цілісності CAS] Невідповідність хешу: очікувався ${digest}, отримано ${actualHash}`);
    }

    return data;
  }
}
