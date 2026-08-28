// Перевірка підтримки колірного простору та передавальної функції через W3C Media Capabilities API
navigator.mediaCapabilities.decodingInfo({
    type: 'file',
    videoConfiguration: {
        contentType: 'video/mp4; codecs="av01.0.08M.10"',
        width: 3840,
        height: 2160,
        bitrate: 15000000,
        framerate: 60,
        colorGamut: 'rec2020',
        transferFunction: 'pq',
        hdrMetadataType: 'smpteSt2086'
    }
}).then(result => {
    console.log("HDR BT.2020 підтримка:", result.supported, result.smooth);
});
