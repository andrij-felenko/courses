package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"net/url"
	"time"
)

type S3Presigner struct {
	AccessKey string
	SecretKey string
	Region    string
	Service   string
}

func hmacSHA256(key []byte, data string) []byte {
	h := hmac.New(sha256.New, key)
	h.Write([]byte(data))
	return h.Sum(nil)
}

func sha256Hex(data string) string {
	h := sha256.Sum256([]byte(data))
	return hex.EncodeToString(h[:])
}

func (p *S3Presigner) deriveSigningKey(dateStamp string) []byte {
	kDate := hmacSHA256([]byte("AWS4"+p.SecretKey), dateStamp)
	kRegion := hmacSHA256(kDate, p.Region)
	kService := hmacSHA256(kRegion, p.Service)
	return hmacSHA256(kService, "aws4_request")
}

func (p *S3Presigner) GeneratePresignedURL(method, host, uri string, expiresSec int, now time.Time) string {
	dateStamp := now.UTC().Format("20060102")
	amzDate := now.UTC().Format("20060102T150405Z")
	credScope := fmt.Sprintf("%s/%s/%s/aws4_request", dateStamp, p.Region, p.Service)

	v := url.Values{}
	v.Set("X-Amz-Algorithm", "AWS4-HMAC-SHA256")
	v.Set("X-Amz-Credential", fmt.Sprintf("%s/%s", p.AccessKey, credScope))
	v.Set("X-Amz-Date", amzDate)
	v.Set("X-Amz-Expires", fmt.Sprintf("%d", expiresSec))
	v.Set("X-Amz-SignedHeaders", "host")

	canonicalQS := v.Encode()
	canonicalReq := fmt.Sprintf("%s\n%s\n%s\nhost:%s\n\nhost\nUNSIGNED-PAYLOAD",
		method, uri, canonicalQS, host)

	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%s",
		amzDate, credScope, sha256Hex(canonicalReq))

	signingKey := p.deriveSigningKey(dateStamp)
	signature := hex.EncodeToString(hmacSHA256(signingKey, stringToSign))

	return fmt.Sprintf("https://%s%s?%s&X-Amz-Signature=%s", host, uri, canonicalQS, signature)
}

func (p *S3Presigner) Validate(method, host, uri, canonicalQSNoSig, providedSig, amzDate, dateStamp string, reqTime time.Time, expiresSec int) error {
	now := time.Now().UTC()
	if now.Before(reqTime) || now.After(reqTime.Add(time.Duration(expiresSec)*time.Second)) {
		return fmt.Errorf("URL expired")
	}

	credScope := fmt.Sprintf("%s/%s/%s/aws4_request", dateStamp, p.Region, p.Service)
	canonicalReq := fmt.Sprintf("%s\n%s\n%s\nhost:%s\n\nhost\nUNSIGNED-PAYLOAD",
		method, uri, canonicalQSNoSig, host)

	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%s",
		amzDate, credScope, sha256Hex(canonicalReq))

	signingKey := p.deriveSigningKey(dateStamp)
	expectedSig := hex.EncodeToString(hmacSHA256(signingKey, stringToSign))

	if subtle.ConstantTimeCompare([]byte(providedSig), []byte(expectedSig)) != 1 {
		return fmt.Errorf("signature mismatch")
	}
	return nil
}
