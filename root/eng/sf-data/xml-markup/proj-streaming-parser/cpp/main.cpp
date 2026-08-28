#include <iostream>
#include <string_view>
#include <string>
#include <memory>
#include <stdexcept>
#include <libxml/xmlreader.h>

struct StreamSummary {
    double total_uah = 0.0;
    double total_usd = 0.0;
    std::size_t count = 0;
};

/* RAII-обгортка над покажчиком рядка libxml2 */
struct XmlCharDeleter {
    void operator()(xmlChar* ptr) const noexcept {
        if (ptr) xmlFree(ptr);
    }
};
using XmlStringPtr = std::unique_ptr<xmlChar, XmlCharDeleter>;

/* RAII-обгортка над xmlTextReader */
class SafeXmlReader {
public:
    SafeXmlReader(const std::string& filepath, int options) {
        reader_ = xmlReaderForFile(filepath.c_str(), nullptr, options);
        if (!reader_) {
            throw std::runtime_error("Не вдалося ініціалізувати SafeXmlReader: " + filepath);
        }
    }

    ~SafeXmlReader() noexcept {
        if (reader_) xmlFreeTextReader(reader_);
        xmlCleanupParser();
    }

    SafeXmlReader(const SafeXmlReader&) = delete;
    SafeXmlReader& operator=(const SafeXmlReader&) = delete;
    SafeXmlReader(SafeXmlReader&& other) noexcept : reader_(other.reader_) {
        other.reader_ = nullptr;
    }

    bool read() {
        int ret = xmlTextReaderRead(reader_);
        if (ret < 0) throw std::runtime_error("Помилка синтаксичного розбору XML-потоку");
        return ret == 1;
    }

    int node_type() const noexcept {
        return xmlTextReaderNodeType(reader_);
    }

    int depth() const noexcept {
        return xmlTextReaderDepth(reader_);
    }

    std::string_view local_name() const noexcept {
        const auto* name = xmlTextReaderConstLocalName(reader_);
        return name ? reinterpret_cast<const char*>(name) : std::string_view{};
    }

    std::string_view value() const noexcept {
        const auto* val = xmlTextReaderConstValue(reader_);
        return val ? reinterpret_cast<const char*>(val) : std::string_view{};
    }

    XmlStringPtr get_attribute(const char* name) const noexcept {
        return XmlStringPtr(xmlTextReaderGetAttribute(
            reader_, reinterpret_cast<const xmlChar*>(name)));
    }

private:
    xmlTextReaderPtr reader_ = nullptr;
};

void parse_stream_safe_cpp(const std::string& filepath, StreamSummary& summary) {
    constexpr int secure_options = XML_PARSE_NONET | XML_PARSE_NODTD | XML_PARSE_NOBLANKS;
    SafeXmlReader reader(filepath, secure_options);

    while (reader.read()) {
        if (reader.node_type() == XML_READER_TYPE_ELEMENT && reader.local_name() == "tx") {
            auto status = reader.get_attribute("status");
            if (!status || std::string_view(reinterpret_cast<char*>(status.get())) != "completed") {
                continue;
            }

            std::string currency;
            double amount = 0.0;
            int tx_depth = reader.depth();

            while (reader.read()) {
                int type = reader.node_type();
                int d = reader.depth();

                if (d <= tx_depth && type == XML_READER_TYPE_END_ELEMENT) {
                    break;
                }

                if (type == XML_READER_TYPE_ELEMENT && reader.local_name() == "amount") {
                    auto curr = reader.get_attribute("currency");
                    if (curr) {
                        currency = reinterpret_cast<char*>(curr.get());
                    }
                    if (reader.read() && reader.node_type() == XML_READER_TYPE_TEXT) {
                        amount = std::stod(std::string(reader.value()));
                    }
                }
            }

            if (currency == "UAH") summary.total_uah += amount;
            else if (currency == "USD") summary.total_usd += amount;
            summary.count++;
        }
    }
}
