#include <memory>
#include <libxml/parser.h>

struct XmlParserDeleter {
    void operator()(xmlParserCtxtPtr ptr) const noexcept {
        if (ptr) xmlFreeParserCtxt(ptr);
    }
};

using UniqueXmlCtxt = std::unique_ptr<xmlParserCtxt, XmlParserDeleter>;

[[nodiscard]] UniqueXmlCtxt create_secure_xml_parser() noexcept {
    UniqueXmlCtxt ctxt(xmlNewParserCtxt());
    if (ctxt) {
        constexpr int options = XML_PARSE_NONET | XML_PARSE_NODICT | XML_PARSE_NOENT;
        xmlCtxtUseOptions(ctxt.get(), options);
    }
    return ctxt;
}
