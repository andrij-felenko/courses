interface SubtleCrypto {
  digest(algorithm: AlgorithmIdentifier, data: BufferSource): Promise<ArrayBuffer>;
  importKey(
    format: 'raw' | 'pkcs8' | 'spki' | 'jwk',
    keyData: BufferSource | JsonWebKey,
    algorithm: AlgorithmIdentifier | RsaHashedImportParams | HmacImportParams,
    extractable: boolean,
    keyUsages: KeyUsage[]
  ): Promise<CryptoKey>;
  sign(algorithm: AlgorithmIdentifier | HmacParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
  verify(algorithm: AlgorithmIdentifier | HmacParams, key: CryptoKey, signature: BufferSource, data: BufferSource): Promise<boolean>;
  encrypt(algorithm: AlgorithmIdentifier | AesGcmParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
  decrypt(algorithm: AlgorithmIdentifier | AesGcmParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
}
