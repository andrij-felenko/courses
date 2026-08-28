# Фасад: один простий метод ховає весь порядок роботи підсистеми
class VideoConverter:
    def convert(self, filename: str, target_format: str) -> "File":
        file = VideoFile(filename)
        source_codec = CodecFactory().extract(file)
        target_codec = MPEG4Codec() if target_format == "mp4" else OggCodec()

        buffer = BitrateReader.read(file, source_codec)
        result = BitrateReader.convert(buffer, target_codec)
        result = AudioMixer().fix(result)

        return File(result)      # клієнт про все це не знає


# Уся робота клієнта тепер — один рядок:
mp4 = VideoConverter().convert("holiday.ogg", "mp4")
