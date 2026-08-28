package webhook

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"time"
)

type SignedDelivery struct {
	Body    string            // ті САМІ байти, що підуть по дроту
	Headers map[string]string
}

func Sign(payload any, secret string) (SignedDelivery, error) {
	body, err := json.Marshal(payload) // серіалізуємо РАЗ
	if err != nil {
		return SignedDelivery{}, err
	}
	ts := time.Now().Unix()
	signedString := fmt.Sprintf("%d.%s", ts, body) // час . тіло

	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(signedString)) // підписуємо саме цей рядок
	sig := hex.EncodeToString(mac.Sum(nil))

	return SignedDelivery{
		Body: string(body), // і надсилаємо ЙОГО, не пере-серіалізуємо
		Headers: map[string]string{
			"Content-Type":        "application/json",
			"X-Webhook-Timestamp": fmt.Sprint(ts),
			"X-Webhook-Signature": "v1=" + sig, // версіонуємо схему підпису
		},
	}, nil
}

// Бік ОДЕРЖУВАЧА: hmac.Equal — стале-в-часі порівняння.
func Verify(body, headerTs, headerSig, secret string, toleranceSec float64) bool {
	var ts int64
	fmt.Sscan(headerTs, &ts)
	if math.Abs(float64(time.Now().Unix()-ts)) > toleranceSec {
		return false // задавнена звістка — геть
	}
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(headerTs + "." + body))
	expected := hex.EncodeToString(mac.Sum(nil))
	got := headerSig[len("v1="):]
	return hmac.Equal([]byte(expected), []byte(got))
}
