/* Додавання власного підписаного атрибута перед фіналізацією підпису */
CMS_SignerInfo *si = CMS_add1_signer(cms, sign_cert, sign_key, EVP_sha256(), flags);
if (!si) goto cleanup;

/* Створення ASN.1 рядка з версією апаратної плати */
ASN1_OCTET_STRING *hw_rev = ASN1_OCTET_STRING_new();
ASN1_OCTET_STRING_set(hw_rev, (const unsigned char*)"HW_REV_3.2", 10);

/* Додавання атрибута за числовим OID підприємства */
ASN1_OBJECT *custom_oid = OBJ_txt2obj("1.3.6.1.4.1.99999.1.1", 1);
CMS_signed_add1_attr_by_OBJ(si, custom_oid, V_ASN1_OCTET_STRING, hw_rev, -1);

ASN1_OBJECT_free(custom_oid);
ASN1_OCTET_STRING_free(hw_rev);
