type Variant = { url: URL; bandwidth: number; resolution?: string };
type Segment = { url: URL; duration: number; seq: number };
type MediaPlaylist = { targetDuration: number; mediaSequence: number;
                       segments: Segment[]; ended: boolean };

function attrs(s: string): Record<string, string> {
  const out: Record<string, string> = {};
  // NAME=VALUE через кому; значення у лапках саме може містити кому (CODECS)
  for (const m of s.matchAll(/([A-Z0-9-]+)=("[^"]*"|[^,]*)/g))
    out[m[1]] = m[2].replace(/^"|"$/g, '');
  return out;
}

function parseMultivariant(text: string, base: URL): Variant[] {
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const out: Variant[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (!lines[i].startsWith('#EXT-X-STREAM-INF:')) continue;
    const a = attrs(lines[i].slice('#EXT-X-STREAM-INF:'.length));
    const uri = lines[i + 1];                       // адреса — ЗАВЖДИ наступний рядок
    if (!uri || uri.startsWith('#')) continue;
    out.push({ url: new URL(uri, base), bandwidth: Number(a.BANDWIDTH),
               resolution: a.RESOLUTION });
  }
  return out.sort((x, y) => x.bandwidth - y.bandwidth);   // від найдешевшої вгору
}

function parseMedia(text: string, base: URL): MediaPlaylist {
  const pl: MediaPlaylist = { targetDuration: 6, mediaSequence: 0,
                              segments: [], ended: false };
  let dur = 0;
  for (const l of text.split(/\r?\n/).map(s => s.trim()).filter(Boolean)) {
    if (l.startsWith('#EXT-X-TARGETDURATION:')) pl.targetDuration = Number(l.split(':')[1]);
    else if (l.startsWith('#EXT-X-MEDIA-SEQUENCE:')) pl.mediaSequence = Number(l.split(':')[1]);
    else if (l.startsWith('#EXTINF:')) dur = parseFloat(l.slice(8));
    else if (l === '#EXT-X-ENDLIST') pl.ended = true;
    else if (!l.startsWith('#'))
      pl.segments.push({ url: new URL(l, base), duration: dur,
                         seq: pl.mediaSequence + pl.segments.length });
  }
  return pl;
}
