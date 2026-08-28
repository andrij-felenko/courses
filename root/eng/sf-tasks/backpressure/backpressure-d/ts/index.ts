// Node-потік: write() повертає false, коли буфер переповнено.
// false — це сигнал протитиску: припини писати, чекай на 'drain'.
import { once } from 'node:events';

async function pump(source: Iterable<Chunk>, dest: NodeJS.WritableStream) {
  for (const chunk of source) {
    if (!dest.write(chunk)) {        // буфер повний → false
      await once(dest, 'drain');     // пауза, доки споживач не спорожнить його
    }
  }
  dest.end();
}
