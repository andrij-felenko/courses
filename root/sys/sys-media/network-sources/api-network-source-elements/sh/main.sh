# 1. Одноадресний UDP, живий лінк: маленьке вікно, облік втрат, тиша замість зелених квадратів
gst-launch-1.0 -v \
  udpsrc port=5600 buffer-size=524288 \
    caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" \
  ! rtpjitterbuffer latency=100 do-lost=true drop-on-latency=true \
  ! rtph264depay wait-for-keyframe=true ! h264parse ! avdec_h264 ! autovideosink sync=false

# 2. Багатоадресна група на машині з кількома мережами
gst-launch-1.0 -v \
  udpsrc address=239.1.2.3 port=5600 multicast-iface=eth1 auto-multicast=true \
    caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" \
  ! rtpjitterbuffer latency=200 ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink

# 3. RTSP із камери, налаштований на свіжість, а не на плавність
gst-launch-1.0 -v \
  rtspsrc location=rtsp://user:pass@192.168.1.64:554/Streaming/Channels/101 \
          latency=100 protocols=udp timeout=2000000 \
  ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false

# 4. Той самий потік крізь NAT: транспорт зафіксовано, UDP не пробують узагалі
gst-launch-1.0 -v \
  rtspsrc location=rtsp://192.168.1.64:554/Streaming/Channels/101 \
          latency=300 protocols=tcp \
  ! decodebin ! autovideosink
