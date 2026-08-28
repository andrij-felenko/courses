const stats = await peerConnection.getStats();
stats.forEach(report => {
  if (report.type === 'inbound-rtp' && report.kind === 'audio') {
    console.log(`Мережевий джитер (RFC 3550): ${report.jitter * 1000} мс`);
    console.log(`Середня затримка буфера джитеру: ${
      (report.jitterBufferDelay / report.jitterBufferEmittedCount) * 1000
    } мс`);
    console.log(`Кількість викинутих запізнілих пакетів: ${report.packetsDiscarded}`);
  }
});
