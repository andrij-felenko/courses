#include <string>
#include <format>
#include <string_view>

class S3RangeRequestBuilder {
public:
    static std::string buildRequest(
        std::string_view bucket,
        std::string_view key,
        const ByteRange& range)
    {
        return std::format(
            "GET /{}/{} HTTP/1.1\r\n"
            "Host: {}.s3.amazonaws.com\r\n"
            "Range: bytes={}-{}\r\n"
            "Connection: close\r\n\r\n",
            bucket, key, bucket, range.start, range.end);
    }
};
