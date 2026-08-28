#include <stdio.h>
#include <string.h>

/* Формування висхідного заголовка для S3 REST API */
int format_upstream_s3_range_request(char *out_buf, size_t buf_size, const char *s3_bucket, const char *s3_key, uint64_t start, uint64_t end) {
    return snprintf(out_buf, buf_size,
        "GET /%s/%s HTTP/1.1\r\n"
        "Host: %s.s3.amazonaws.com\r\n"
        "Range: bytes=%llu-%llu\r\n"
        "Connection: close\r\n\r\n",
        s3_bucket, s3_key, s3_bucket,
        (unsigned long long)start,
        (unsigned long long)end);
}
