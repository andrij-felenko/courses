import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';

export interface AssetManifest {
  [originalPath: string]: {
    hashedPath: string;
    integrity: string; // SRI (Subresource Integrity)
    size: number;
  };
}

export class AssetPipeline {
  private readonly sourceDir: string;
  private readonly distDir: string;
  private readonly manifest: AssetManifest = {};

  constructor(sourceDir: string, distDir: string) {
    this.sourceDir = path.resolve(sourceDir);
    this.distDir = path.resolve(distDir);
    fs.mkdirSync(this.distDir, { recursive: true });
  }

  // Обчислення SRI-хешу за стандартом W3C (SHA-384 base64)
  private computeSri(content: Buffer): string {
    const hash = crypto.createHash('sha384').update(content).digest('base64');
    return `sha384-${hash}`;
  }

  // Генерація короткого хешу для назви файлу (перші 8 байтів / 16 символів hex)
  private computeFingerprint(content: Buffer): string {
    return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
  }

  // Обробка одного файлу: збереження у dist з відбитком у назві
  public processAsset(relPath: string, content: Buffer | string): string {
    const buffer = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf-8');
    const fingerprint = this.computeFingerprint(buffer);
    const parsed = path.parse(relPath);

    const hashedFilename = `${parsed.name}.${fingerprint}${parsed.ext}`;
    const hashedRelPath = path.join(parsed.dir, hashedFilename).replace(/\\/g, '/');
    const targetPath = path.join(this.distDir, hashedRelPath);

    fs.mkdirSync(path.dirname(targetPath), { recursive: true });
    fs.writeFileSync(targetPath, buffer);

    this.manifest[relPath.replace(/\\/g, '/')] = {
      hashedPath: `/${hashedRelPath}`,
      integrity: this.computeSri(buffer),
      size: buffer.length,
    };

    return `/${hashedRelPath}`;
  }

  // Конвеєр обробки графа: Листки (Fonts/Images) -> Стилі (CSS) -> Точка входу (HTML)
  public build(files: { [relPath: string]: string | Buffer }): AssetManifest {
    const paths = Object.keys(files);

    // 1. Обробка статичних листків (зображення, шрифти, WASM)
    const leafExtensions = new Set(['.png', '.jpg', '.svg', '.woff2', '.ttf', '.wasm']);
    for (const p of paths) {
      if (leafExtensions.has(path.extname(p))) {
        this.processAsset(p, files[p]);
      }
    }

    // 2. Обробка CSS з підстановкою оновлених адрес зображень і шрифтів
    for (const p of paths) {
      if (path.extname(p) === '.css') {
        let cssContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          cssContent = cssContent.replaceAll(orig, entry.hashedPath);
          cssContent = cssContent.replaceAll(`/${orig}`, entry.hashedPath);
        }
        this.processAsset(p, cssContent);
      }
    }

    // 3. Обробка JS модулів
    for (const p of paths) {
      if (path.extname(p) === '.js') {
        let jsContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          jsContent = jsContent.replaceAll(`"${orig}"`, `"${entry.hashedPath}"`);
          jsContent = jsContent.replaceAll(`'${orig}'`, `'${entry.hashedPath}'`);
        }
        this.processAsset(p, jsContent);
      }
    }

    // 4. Обробка HTML (вхідна точка: Cache-Control: no-cache)
    for (const p of paths) {
      if (path.extname(p) === '.html') {
        let htmlContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          const regexScript = new RegExp(`<script([^>]*)src=["']/?${orig}["']([^>]*)>`, 'g');
          htmlContent = htmlContent.replace(regexScript, `<script$1src="${entry.hashedPath}" integrity="${entry.integrity}" crossorigin="anonymous"$2>`);

          const regexLink = new RegExp(`<link([^>]*)href=["']/?${orig}["']([^>]*)>`, 'g');
          htmlContent = htmlContent.replace(regexLink, `<link$1href="${entry.hashedPath}" integrity="${entry.integrity}" crossorigin="anonymous"$2>`);
        }
        // HTML зберігається БЕЗ хешу в імені (мутабельна точка входу)
        fs.writeFileSync(path.join(this.distDir, p), htmlContent, 'utf-8');
      }
    }

    // 5. Запис маніфесту
    fs.writeFileSync(
      path.join(this.distDir, 'manifest.json'),
      JSON.stringify(this.manifest, null, 2),
      'utf-8'
    );

    return this.manifest;
  }
}
