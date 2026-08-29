import { ControlLink } from "./link.js";
import { ValveWidget } from "./widget.js";

/*
 * Розмітка віджета (частина сторінки панелі):
 *
 * <section id="valve-widget" data-device-id="zone1" data-token="…">
 *   <input data-role="target" type="range" min="0" max="100" value="0">
 *   <button data-role="send">Виконати</button>
 *   <div class="bar"><i data-role="bar"></i></div>
 *   <p data-role="status"></p>
 * </section>
 */

const root = document.querySelector<HTMLElement>("#valve-widget");
if (root === null) {
    throw new Error("на сторінці немає #valve-widget");
}

const deviceId = root.dataset.deviceId;
const token = root.dataset.token;
if (!deviceId || !token) {
    throw new Error("віджету потрібні data-device-id і data-token");
}

const apiBase = root.dataset.api ?? window.location.origin;

let widget!: ValveWidget;
const link = new ControlLink(
    apiBase,
    token,
    (event) => widget.applyEvent(event),
    (online) => widget.setOnline(online),
);

widget = new ValveWidget(root, link, deviceId);
link.connect();

window.addEventListener("beforeunload", () => link.close());
