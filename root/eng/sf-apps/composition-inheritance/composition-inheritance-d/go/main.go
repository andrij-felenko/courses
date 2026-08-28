type Engine struct{}
func (Engine) Start() { fmt.Println("двигун заведено") }

type Car struct {
    Engine          // вбудовано — метод Start() підіймається в Car
    plate string
}

func main() {
    c := Car{plate: "AA1234"}
    c.Start()       // працює, хоч Start оголошено на Engine
}
