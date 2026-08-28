interface Deprecation {
  field: string;         // "tempC"
  replacedBy: string;    // "temperature"
  deprecatedAt: number;  // epoch-СЕКУНДИ — для заголовка Deprecation (RFC 9745)
  sunsetAt: number;      // epoch-СЕКУНДИ — для заголовка Sunset  (RFC 8594)
  docs: string;
}

const DEPRECATED: Deprecation[] = [
  { field: "tempC", replacedBy: "temperature",
    deprecatedAt: Date.UTC(2026, 0, 15) / 1000,   // 2026-01-15
    sunsetAt:     Date.UTC(2026, 6, 15) / 1000,   // 2026-07-15
    docs: "https://developer.digitalhomes.io/deprecations/tempC" },
  { field: "at", replacedBy: "atMs",
    deprecatedAt: Date.UTC(2026, 0, 15) / 1000,
    sunsetAt:     Date.UTC(2026, 6, 15) / 1000,
    docs: "https://developer.digitalhomes.io/deprecations/at-ms" },
];
