#include <iostream>
#include <string_view>
#include <vector>
#include <charconv>
#include <cstdint>
#include <algorithm>
#include <cctype>

enum class HttpMethod {
    GET, POST, PUT, DELETE_, HEAD, OPTIONS, PATCH, UNKNOWN
};

enum class ParseResult {
    NEED_MORE_DATA,
    COMPLETE,
    ERROR_INVALID_METHOD,
    ERROR_INVALID_URI,
    ERROR_INVALID_VERSION,
    ERROR_INVALID_HEADER,
    ERROR_INVALID_CHUNK,
    ERROR_SMUGGLING_CONFLICT
};

struct HttpHeaderView {
    std::string_view name;
    std::string_view value;
};

struct HttpRequestView {
    HttpMethod method = HttpMethod::UNKNOWN;
    std::string_view uri;
    int version_major = 1;
    int version_minor = 1;
    std::vector<HttpHeaderView> headers;
    std::string_view body;
    bool is_chunked = false;
    size_t content_length = 0;
};

class HttpStreamingParser {
public:
    enum class State {
        METHOD,
        URI,
        VERSION,
        HEADER_NAME,
        HEADER_VALUE,
        BODY_IDENTITY,
        CHUNK_SIZE,
        CHUNK_DATA,
        CHUNK_CRLF,
        COMPLETE
    };

    HttpStreamingParser() = default;

    ParseResult parse(std::string_view input, HttpRequestView& out_req) {
        size_t pos = 0;
        const size_t len = input.size();

        while (pos < len && state_ != State::COMPLETE) {
            switch (state_) {
                case State::METHOD: {
                    size_t space = input.find(' ', pos);
                    if (space == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    
                    std::string_view method_str = input.substr(pos, space - pos);
                    out_req.method = parse_method(method_str);
                    if (out_req.method == HttpMethod::UNKNOWN) {
                        return ParseResult::ERROR_INVALID_METHOD;
                    }
                    pos = space + 1;
                    state_ = State::URI;
                    break;
                }
                case State::URI: {
                    size_t space = input.find(' ', pos);
                    if (space == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    
                    out_req.uri = input.substr(pos, space - pos);
                    if (out_req.uri.empty() || out_req.uri[0] != '/') {
                        return ParseResult::ERROR_INVALID_URI;
                    }
                    pos = space + 1;
                    state_ = State::VERSION;
                    break;
                }
                case State::VERSION: {
                    size_t crlf = input.find("\r\n", pos);
                    if (crlf == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    
                    std::string_view ver = input.substr(pos, crlf - pos);
                    if (ver == "HTTP/1.1") {
                        out_req.version_major = 1;
                        out_req.version_minor = 1;
                    } else if (ver == "HTTP/1.0") {
                        out_req.version_major = 1;
                        out_req.version_minor = 0;
                    } else {
                        return ParseResult::ERROR_INVALID_VERSION;
                    }
                    pos = crlf + 2;
                    state_ = State::HEADER_NAME;
                    break;
                }
                case State::HEADER_NAME: {
                    // Перевірка на порожній рядок CRLF (кінець блоку заголовків)
                    if (pos + 1 < len && input[pos] == '\r' && input[pos + 1] == '\n') {
                        pos += 2;
                        return process_headers_complete(input, pos, out_req);
                    }
                    
                    size_t colon = input.find(':', pos);
                    size_t line_end = input.find("\r\n", pos);
                    if (line_end == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    if (colon == std::string_view::npos || colon > line_end) {
                        return ParseResult::ERROR_INVALID_HEADER;
                    }
                    
                    // RFC 9112: заборона пробілів перед двокрапкою
                    if (colon > pos && (input[colon - 1] == ' ' || input[colon - 1] == '\t')) {
                        return ParseResult::ERROR_INVALID_HEADER;
                    }

                    current_header_name_ = input.substr(pos, colon - pos);
                    pos = colon + 1;
                    state_ = State::HEADER_VALUE;
                    break;
                }
                case State::HEADER_VALUE: {
                    size_t line_end = input.find("\r\n", pos);
                    if (line_end == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    
                    std::string_view val = input.substr(pos, line_end - pos);
                    // Обрізання необов'язкових пробілів (OWS)
                    while (!val.empty() && (val.front() == ' ' || val.front() == '\t')) {
                        val.remove_prefix(1);
                    }
                    while (!val.empty() && (val.back() == ' ' || val.back() == '\t')) {
                        val.remove_suffix(1);
                    }
                    
                    out_req.headers.push_back({current_header_name_, val});
                    check_framing_headers(current_header_name_, val, out_req);
                    
                    pos = line_end + 2;
                    state_ = State::HEADER_NAME;
                    break;
                }
                case State::BODY_IDENTITY: {
                    size_t available = len - pos;
                    if (available < out_req.content_length) {
                        return ParseResult::NEED_MORE_DATA;
                    }
                    out_req.body = input.substr(pos, out_req.content_length);
                    pos += out_req.content_length;
                    state_ = State::COMPLETE;
                    break;
                }
                case State::CHUNK_SIZE: {
                    size_t crlf = input.find("\r\n", pos);
                    if (crlf == std::string_view::npos) return ParseResult::NEED_MORE_DATA;
                    
                    std::string_view size_str = input.substr(pos, crlf - pos);
                    size_t chunk_sz = 0;
                    auto res = std::from_chars(size_str.data(), size_str.data() + size_str.size(), chunk_sz, 16);
                    if (res.ec != std::errc{}) {
                        return ParseResult::ERROR_INVALID_CHUNK;
                    }
                    
                    current_chunk_size_ = chunk_sz;
                    pos = crlf + 2;
                    
                    if (current_chunk_size_ == 0) {
                        // Термінальний чанк 0\r\n\r\n
                        if (len - pos < 2) return ParseResult::NEED_MORE_DATA;
                        if (input.substr(pos, 2) != "\r\n") return ParseResult::ERROR_INVALID_CHUNK;
                        pos += 2;
                        state_ = State::COMPLETE;
                    } else {
                        state_ = State::CHUNK_DATA;
                    }
                    break;
                }
                case State::CHUNK_DATA: {
                    if (len - pos < current_chunk_size_) return ParseResult::NEED_MORE_DATA;
                    pos += current_chunk_size_;
                    state_ = State::CHUNK_CRLF;
                    break;
                }
                case State::CHUNK_CRLF: {
                    if (len - pos < 2) return ParseResult::NEED_MORE_DATA;
                    if (input.substr(pos, 2) != "\r\n") return ParseResult::ERROR_INVALID_CHUNK;
                    pos += 2;
                    state_ = State::CHUNK_SIZE;
                    break;
                }
                case State::COMPLETE:
                    break;
            }
        }
        
        return (state_ == State::COMPLETE) ? ParseResult::COMPLETE : ParseResult::NEED_MORE_DATA;
    }

    void reset() {
        state_ = State::METHOD;
        current_header_name_ = {};
        current_chunk_size_ = 0;
        has_cl_ = false;
        has_te_ = false;
    }

private:
    State state_ = State::METHOD;
    std::string_view current_header_name_;
    size_t current_chunk_size_ = 0;
    bool has_cl_ = false;
    bool has_te_ = false;

    static HttpMethod parse_method(std::string_view m) {
        if (m == "GET") return HttpMethod::GET;
        if (m == "POST") return HttpMethod::POST;
        if (m == "PUT") return HttpMethod::PUT;
        if (m == "DELETE") return HttpMethod::DELETE_;
        if (m == "HEAD") return HttpMethod::HEAD;
        if (m == "OPTIONS") return HttpMethod::OPTIONS;
        if (m == "PATCH") return HttpMethod::PATCH;
        return HttpMethod::UNKNOWN;
    }

    static bool iequals(std::string_view a, std::string_view b) {
        return std::equal(a.begin(), a.end(), b.begin(), b.end(),
            [](char ca, char cb) { return std::tolower(ca) == std::tolower(cb); });
    }

    void check_framing_headers(std::string_view name, std::string_view val, HttpRequestView& req) {
        if (iequals(name, "Content-Length")) {
            has_cl_ = true;
            size_t cl = 0;
            auto res = std::from_chars(val.data(), val.data() + val.size(), cl);
            if (res.ec == std::errc{}) {
                req.content_length = cl;
            }
        } else if (iequals(name, "Transfer-Encoding")) {
            has_te_ = true;
            if (val.find("chunked") != std::string_view::npos) {
                req.is_chunked = true;
            }
        }
    }

    ParseResult process_headers_complete(std::string_view input, size_t& pos, HttpRequestView& req) {
        // RFC 9112 §6.3: Захист від розсинхронізації запитів (CL.TE)
        if (has_cl_ && has_te_) {
            return ParseResult::ERROR_SMUGGLING_CONFLICT;
        }

        if (req.is_chunked) {
            state_ = State::CHUNK_SIZE;
        } else if (req.content_length > 0) {
            state_ = State::BODY_IDENTITY;
        } else {
            state_ = State::COMPLETE;
        }
        return parse(input.substr(pos), req);
    }
};
