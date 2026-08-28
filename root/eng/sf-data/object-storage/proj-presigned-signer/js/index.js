function uploadDirect(presignedUrl, file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('PUT', presignedUrl, true);
        xhr.setRequestHeader('Content-Type', file.type);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const etag = xhr.getResponseHeader('ETag');
                resolve({ etag: etag ? etag.replace(/"/g, '') : null });
            } else {
                reject(new Error(`Upload failed with status ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.send(file);
    });
}
