// 첫 화면 들어올 때 (2026-10-31): 앱마다 봇 카드를 둥근 고리에 두고 돌려 넘김 — 끌기·화살표 키·점·옆 카드 누르기, 가만두면 3.5초마다 다음.
// [들어가기]·Enter 면 사이트로. 탭마다 한 번 (sessionStorage).
import { Band as Ovi } from "./band.js";
import { Band as AppBot } from "./appband.js";

export function start() {
  const intro = document.getElementById("intro");
  if (!intro || !document.documentElement.classList.contains("intro-on")) { intro?.remove(); return; }
  const ring = document.getElementById("ring");
  const cards = [...ring.querySelectorAll(".ring-card")];
  const dots = [...intro.querySelectorAll(".ring-dot")];
  const n = cards.length;
  const bots = cards.map((c) => {
    const screen = c.querySelector(".ring-screen"), sky = c.querySelector("canvas");
    if (c.dataset.id === "overmind") { const b = new Ovi(screen, sky); b.setTheme({ tint: c.dataset.tint }); return b; }
    return new AppBot(screen, sky, c.dataset.tint);
  });
  let cur = 0, drag = null, timer = null;
  const wide = () => (innerWidth <= 760 ? 150 : 210);
  const off = (i, at) => { let d = (((i - at) % n) + n) % n; if (d > n / 2) d -= n; return d; };

  function place(at) {
    cards.forEach((c, i) => {
      const d = off(i, at), a = Math.abs(d);
      c.style.transform = `translateX(${d * wide()}px) translateZ(${-a * 150}px) rotateY(${-d * 24}deg)`;
      c.style.opacity = a > 2.2 ? 0 : String(1 - a * 0.32);
      c.style.filter = a > 0.5 ? `brightness(${1 - Math.min(a, 2) * 0.22})` : "none";
      c.style.zIndex = String(10 - Math.round(a * 2));
      c.style.pointerEvents = a > 2.2 ? "none" : "";
    });
  }
  function go(i) {
    cur = ((i % n) + n) % n;
    place(cur);
    cards.forEach((c, k) => c.classList.toggle("on", k === cur));
    dots.forEach((d, k) => { d.classList.toggle("on", k === cur); d.style.setProperty("--dot", cards[k].dataset.tint); });
    bots.forEach((b, k) => b.setVisible(Math.abs(off(k, cur)) <= 1));   // 보이는 셋만 움직임
  }
  const auto = () => { clearInterval(timer); timer = setInterval(() => go(cur + 1), 3500); };
  const stop = () => { clearInterval(timer); timer = null; };

  ring.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    drag = { x: e.clientX, moved: false, card: e.target.closest(".ring-card") };
    ring.setPointerCapture(e.pointerId); stop();
  });
  ring.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x;
    if (Math.abs(dx) > 6 && !drag.moved) { drag.moved = true; ring.classList.add("drag"); }
    if (drag.moved) place(cur - dx / wide());
  });
  const up = (e) => {
    if (!drag) return;
    ring.classList.remove("drag");
    if (drag.moved) go(Math.round(cur - (e.clientX - drag.x) / wide()));
    else if (drag.card) go(cards.indexOf(drag.card));
    drag = null; auto();
  };
  ring.addEventListener("pointerup", up);
  ring.addEventListener("pointercancel", up);
  dots.forEach((d, k) => d.addEventListener("click", () => { go(k); auto(); }));

  function enter() {
    try { sessionStorage.setItem("intro", "1"); } catch (e) {}
    stop(); removeEventListener("keydown", key);
    intro.classList.add("gone");
    setTimeout(() => { bots.forEach((b) => b.setVisible(false)); intro.remove(); document.documentElement.classList.remove("intro-on"); }, 450);
  }
  function key(e) {
    if (e.key === "ArrowRight") { go(cur + 1); auto(); }
    else if (e.key === "ArrowLeft") { go(cur - 1); auto(); }
    else if (e.key === "Enter" && document.activeElement?.tagName !== "BUTTON" || e.key === "Escape") enter();
  }
  document.getElementById("intro-enter").addEventListener("click", enter);
  addEventListener("keydown", key);
  addEventListener("resize", () => place(cur));
  go(0); auto();
}
