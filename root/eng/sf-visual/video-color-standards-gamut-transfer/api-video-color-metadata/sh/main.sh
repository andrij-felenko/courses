# Приклади команд транскодування з явним вказуванням метаданих BT.709 та BT.2020 HDR
ffmpeg -i input_sd.mp4 \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -color_range tv \
  -c:v libx264 -crf 18 output_hd.mp4

# Перекодування HDR10 у SDR із тономапінгом та правильними прапорами
ffmpeg -i input_hdr.mkv \
  -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709:t=bt709:m=bt709,format=yuv420p" \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -color_range tv \
  -c:v libx264 -crf 20 output_sdr.mp4
