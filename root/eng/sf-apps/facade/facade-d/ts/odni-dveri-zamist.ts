// Фасад: один простий метод ховає весь порядок роботи підсистеми
class VideoConverter {
  convert(filename: string, targetFormat: string): File {
    const file = new VideoFile(filename);
    const sourceCodec = new CodecFactory().extract(file);
    const targetCodec = targetFormat === "mp4"
      ? new MPEG4Codec() : new OggCodec();

    const buffer = BitrateReader.read(file, sourceCodec);
    let result = BitrateReader.convert(buffer, targetCodec);
    result = new AudioMixer().fix(result);

    return new File(result);   // клієнт про все це не знає
  }
}

// Уся робота клієнта тепер — один рядок:
const mp4 = new VideoConverter().convert("holiday.ogg", "mp4");
