// Додавання власного підписаного атрибута через RAII-обгортки
CMS_SignerInfo* si = CMS_add1_signer(cms.get(), cert.get(), pkey.get(), EVP_sha256(), flags);
if (!si) return std::unexpected("Помилка додавання підписувача");

SslPtr<ASN1_OCTET_STRING> hw_rev{ASN1_OCTET_STRING_new()};
constexpr std::string_view rev_str = "HW_REV_3.2";
ASN1_OCTET_STRING_set(hw_rev.get(), reinterpret_cast<const unsigned char*>(rev_str.data()), static_cast<int>(rev_str.size()));

SslPtr<ASN1_OBJECT> custom_oid{OBJ_txt2obj("1.3.6.1.4.1.99999.1.1", 1)};
CMS_signed_add1_attr_by_OBJ(si, custom_oid.get(), V_ASN1_OCTET_STRING, hw_rev.get(), -1);
