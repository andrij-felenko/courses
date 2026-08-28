package main

import (
	"crypto"
	"crypto/ecdsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"os"
)

// InTotoEnvelope описує універсальну структуру підписаного контейнера
type InTotoEnvelope struct {
	PayloadType string          `json:"payloadType"`
	Payload     string          `json:"payload"`
	Signatures  []SignatureMeta `json:"signatures"`
}

type SignatureMeta struct {
	KeyID string `json:"keyid"`
	Sig   string `json:"sig"`
}

// SLSAStatement описує структуру корисного навантаження SLSA Provenance v1.0
type SLSAStatement struct {
	Type          string          `json:"_type"`
	Subject       []SubjectMeta   `json:"subject"`
	PredicateType string          `json:"predicateType"`
	Predicate     SLSAPredicateV1 `json:"predicate"`
}

type SubjectMeta struct {
	Name   string            `json:"name"`
	Digest map[string]string `json:"digest"`
}

type SLSAPredicateV1 struct {
	BuildDefinition struct {
		BuildType          string `json:"buildType"`
		ExternalParameters struct {
			Source struct {
				URI    string `json:"uri"`
				Digest struct {
					GitCommit string `json:"gitCommit"`
				} `json:"digest"`
			} `json:"source"`
		} `json:"externalParameters"`
	} `json:"buildDefinition"`
	RunDetails struct {
		Builder struct {
			ID string `json:"id"`
		} `json:"builder"`
	} `json:"runDetails"`
}

// 1. Обчислення SHA-256 артефакту
func calculateSHA256(filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

// 2. Перевірка підпису ECDSA над декодованим корисним навантаженням
func verifySignature(payload []byte, sigBase64 string, pubKeyPEM []byte) error {
	block, _ := pem.Decode(pubKeyPEM)
	if block == nil {
		return errors.New("помилка парсингу PEM блоку публічного ключа")
	}

	pub, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return err
	}

	ecdsaPub, ok := pub.(*ecdsa.PublicKey)
	if !ok {
		return errors.New("ключ не є валідним ECDSA публічним ключем")
	}

	sigBytes, err := base64.StdEncoding.DecodeString(sigBase64)
	if err != nil {
		return err
	}

	h := sha256.Sum256(payload)
	if !ecdsa.VerifyASN1(ecdsaPub, h[:], sigBytes) {
		return errors.New("криптографічний підпис не відповідає даним")
	}
	return nil
}

// Головна функція верифікації
func VerifyArtifactPipeline(artifactPath string, envelopeBytes []byte, pubKeyPEM []byte) error {
	// Крок 1: Обчислення гешу цільового бінарника
	actualDigest, err := calculateSHA256(artifactPath)
	if err != nil {
		return fmt.Errorf("помилка читання артефакту: %w", err)
	}

	// Крок 2: Розбір конверта in-toto
	var env InTotoEnvelope
	if err := json.Unmarshal(envelopeBytes, &env); err != nil {
		return fmt.Errorf("невалідний JSON конверта in-toto: %w", err)
	}

	rawPayload, err := base64.StdEncoding.DecodeString(env.Payload)
	if err != nil {
		return fmt.Errorf("помилка декодування Base64 payload: %w", err)
	}

	// Крок 3: Перевірка підпису
	if len(env.Signatures) == 0 {
		return errors.New("відсутні цифрові підписи в конверті")
	}
	if err := verifySignature(rawPayload, env.Signatures[0].Sig, pubKeyPEM); err != nil {
		return fmt.Errorf("помилка перевірки підпису: %w", err)
	}

	// Крок 4: Розбір та зіставлення предикату SLSA
	var stmt SLSAStatement
	if err := json.Unmarshal(rawPayload, &stmt); err != nil {
		return fmt.Errorf("помилка парсингу SLSA Statement: %w", err)
	}

	if len(stmt.Subject) == 0 || stmt.Subject[0].Digest["sha256"] != actualDigest {
		return fmt.Errorf("геш артефакту (%s) не збігається з гешем атестації (%s)",
			actualDigest, stmt.Subject[0].Digest["sha256"])
	}

	// Крок 5: Перевірка відповідності правилам безпеки
	const expectedBuilder = "https://github.com/actions/runner/slsa-builder-generic@v2"
	const expectedSource = "git+https://github.com/enterprise/payment-gateway"

	if stmt.Predicate.RunDetails.Builder.ID != expectedBuilder {
		return fmt.Errorf("недовірений збирач: %s", stmt.Predicate.RunDetails.Builder.ID)
	}
	if stmt.Predicate.BuildDefinition.ExternalParameters.Source.URI != expectedSource {
		return fmt.Errorf("недозволене джерело: %s", stmt.Predicate.BuildDefinition.ExternalParameters.Source.URI)
	}

	fmt.Println("[УСПІХ] Артефакт успішно верифіковано. SLSA гарантії підтверджено.")
	return nil
}
