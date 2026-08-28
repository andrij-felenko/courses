function generateTraceparent(): string {
  const version = '00';
  const traceId = Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map(b => b.toString(16).padStart(2, '0')).join('');
  const parentId = Array.from(crypto.getRandomValues(new Uint8Array(8)))
    .map(b => b.toString(16).padStart(2, '0')).join('');
  const flags = '01'; // Записано прапорець sampled

  return `${version}-${traceId}-${parentId}-${flags}`;
}
