export class CasGarbageCollector {
  private readonly storeDir: string;

  constructor(storeDir: string) {
    this.storeDir = path.resolve(storeDir);
  }

  public runGc(activeManifests: AssetManifest[], dryRun = false): { deleted: number; retained: number } {
    // 1. Mark phase: збір усіх досяжних хешів з активних маніфестів
    const reachableHashes = new Set<string>();
    for (const manifest of activeManifests) {
      for (const entry of Object.values(manifest)) {
        const match = entry.hashedPath.match(/\.([a-f0-9]{16,64})\./);
        if (match) {
          reachableHashes.add(match[1]);
        }
      }
    }

    let deleted = 0;
    let retained = 0;

    // 2. Sweep phase: видалення недосяжних блобів
    const scanDir = (dir: string) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (entry.name !== 'tmp') scanDir(fullPath);
        } else if (entry.isFile()) {
          const match = entry.name.match(/\.([a-f0-9]{16,64})\./);
          const hash = match ? match[1] : null;

          if (hash && !reachableHashes.has(hash)) {
            if (!dryRun) fs.unlinkSync(fullPath);
            deleted++;
          } else {
            retained++;
          }
        }
      }
    };

    scanDir(this.storeDir);
    return { deleted, retained };
  }
}
