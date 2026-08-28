import { Readable, Writable, Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import * as fs from 'node:fs';

export interface MultipartPartHeader {
  name: string;
  filename?: string;
  contentType?: string;
}

export class StreamingMultipartWriter extends Writable {
  private boundary: Buffer;
  private currentPartFile?: fs.WriteStream;
  private isCollectingHeader = false;
  private headerBuffer = '';

  constructor(boundaryStr: string, private outputDir: string) {
    super();
    this.boundary = Buffer.from(`--${boundaryStr}`);
  }

  override _write(chunk: Buffer, _encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
    // Потоковий запис безпосередньо у дескриптор цільового файлу
    // Backpressure підтримується вбудованою чергою Node.js Stream
    if (this.currentPartFile && !this.currentPartFile.write(chunk)) {
      this.currentPartFile.once('drain', callback);
    } else {
      callback();
    }
  }

  override _final(callback: (error?: Error | null) => void): void {
    if (this.currentPartFile) {
      this.currentPartFile.end(callback);
    } else {
      callback();
    }
  }
}
