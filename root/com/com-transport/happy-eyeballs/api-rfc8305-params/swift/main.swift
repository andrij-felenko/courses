import Network

let parameters = NWParameters.tcp
// Дозволити автоматичне змагання інтерфейсів та родин адрес
parameters.multipathServiceType = .handover

let endpoint = NWEndpoint.hostPort(host: "example.com", port: 443)
let connection = NWConnection(to: endpoint, using: parameters)

connection.stateUpdateHandler = { state in
    switch state {
    case .ready:
        print("З'єднання встановлено через найшвидший доступний шлях")
    case .failed(let error):
        print("Помилка підключення: \(error)")
    case .waiting(let error):
        print("Очікування відновлення зв'язку: \(error)")
    default:
        break
    }
}

connection.start(queue: .global())
