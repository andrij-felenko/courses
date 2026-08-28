export interface BackupCodeEntry {
  hash: string;
  used: boolean;
  createdAt: Date;
}

export function generateBackupCodes(count: number = 8): string[] {
  const codes: string[] = [];
  for (let i = 0; i < count; i++) {
    const raw = crypto.randomBytes(5).toString("hex");
    const formatted = `${raw.slice(0, 5)}-${raw.slice(5)}`;
    codes.push(formatted);
  }
  return codes;
}

export function hashBackupCode(plainCode: string): string {
  const clean = plainCode.replace(/[\s-]/g, "").toLowerCase();
  return crypto.createHash("sha256").update(clean).digest("hex");
}

export function verifyAndConsumeBackupCode(
  userInput: string,
  storedCodes: BackupCodeEntry[]
): { success: boolean; updatedCodes: BackupCodeEntry[] } {
  const inputHash = hashBackupCode(userInput);
  let found = false;

  const updatedCodes = storedCodes.map((entry) => {
    if (!entry.used && entry.hash === inputHash && !found) {
      found = true;
      return { ...entry, used: true };
    }
    return entry;
  });

  return { success: found, updatedCodes };
}
