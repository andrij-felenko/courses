// e2e_smoke_test.go — жене справжнє значення від HTTP-краю крізь усі вузли й СТВЕРДЖУЄ вихід.
// `go test` ПРОТИ вже розгорнутої нитки (SMOKE_URL); торкається лише двох країв.
package smoke

import (
	"io"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"
)

func base() string {
	if u := os.Getenv("SMOKE_URL"); u != "" {
		return u
	}
	return "http://localhost:8080"
}

func TestThreadWalksEndToEnd(t *testing.T) {
	// (1) Унікальне значення на прогін: читаємо СВІЙ запис, не леглий з минулого разу.
	sent := strconv.Itoa(1000 + rand.Intn(9000))

	// (2) справжній вхід у перший вузол — HTTP-край
	resp, err := http.Post(base()+"/temp", "text/plain", strings.NewReader(sent))
	if err != nil {
		t.Fatalf("POST не пройшов: %v", err)
	}
	resp.Body.Close()
	if resp.StatusCode != 200 {
		t.Fatalf("POST дав код %d", resp.StatusCode)
	}

	// (3) опитуємо останній край з дедлайном (не фіксований сон), поки значення
	// пройде API → брокер → воркер → сховище й виявиться на іншому краї.
	deadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		if got, err := http.Get(base() + "/temp"); err == nil {
			b, _ := io.ReadAll(got.Body)
			got.Body.Close()
			if strings.TrimSpace(string(b)) == sent {
				return // СТВЕРДЖЕННЯ: повернулось саме наше значення — нитка пройшла
			}
		}
		time.Sleep(200 * time.Millisecond)
	}
	t.Fatalf("нитка не пройшла: %s не з'явилось на іншому краї", sent)
}
