ffmpeg -i input_source.mov \
  -filter_complex \
  "[0:v]split=4[v1][v2][v3][v4]; \
   [v1]scale=1920:1080[v1out]; \
   [v2]scale=1280:720[v2out]; \
   [v3]scale=854:480[v3out]; \
   [v4]scale=640:360[v4out]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 6000k -maxrate:v:0 6600k -bufsize:v:0 12000k \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 3000k -maxrate:v:1 3300k -bufsize:v:1 6000k \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 1200k -maxrate:v:2 1320k -bufsize:v:2 2400k \
  -map "[v4out]" -c:v:3 libx264 -b:v:3 600k  -maxrate:v:3 660k  -bufsize:v:3 1200k \
  -map 0:a -c:a aac -b:a 128k -ac 2 \
  -preset fast -profile:v main \
  -g 48 -keyint_min 48 -sc_threshold 0 -no-scenecut 1 \
  -hls_time 2 -hls_playlist_type vod -hls_segment_type fmp4 \
  -hls_flags independent_segments+split_by_time \
  -master_pl_name master.m3u8 \
  -f hls output_%v.m3u8
