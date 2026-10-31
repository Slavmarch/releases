// Glen ui/band.js 그대로 (하위 앱 점 띠 — 작은 앱 봇 + 대표색). 고치려면 그쪽과 같이.
// 점 띠 컴포넌트 (FAMILY.md 5 '큰 창 쪽 머리 띠') — OVERMIND src/band.ts 를 옮김, 하위 앱 변형만:
// Parser ui/band.py 처럼 오른쪽에 노치 섬의 작은 앱 봇(OVERMIND ovi/mini.ts, viewBox 10)을 크게, 둘레는 대표색 빛.
// 검은 점 화면, 점은 왼쪽 흰색 → 오른쪽 대표색으로 물결. 마우스 둘레 점은 밝아지며 비켜나고, 누르면 빛 고리,
// 봇을 누르면 웃으며 폴짝 (빨리 다섯 번이면 X 눈). 가끔 별, 아주 가끔 별똥별.
// 초당 20번(마우스가 놀 때 30번) — 창이 보일 때만 (숨기면 멈춤, 쉴 때 CPU 0).

const STEP = 6; // 점 사이 (CSS px)
const BOT_SCREEN = "#12101a"; // OVERMIND --bot-screen
const GLOW_R = 72;
const PUSH = 3;
const RIPPLE_S = 0.9;
const RIPPLE_SPEED = 320;
const RIPPLE_W = 16;
const TWINKLE_S = 1.1;
const GRAVITY = 90;
const TAIL = 14;
const out = (k) => 1 - (1 - k) ** 3;

/** 다음에 볼 곳 (OVERMIND wander.ts nextLook 그대로). */
function nextLook(prev, rand = Math.random) {
  const hold = (lo, hi) => Math.round(lo + rand() * (hi - lo));
  if (Math.hypot(prev.x, prev.y) >= 0.5 && rand() < 0.3) return { x: 0, y: 0, holdMs: hold(1800, 3800) };
  for (let i = 0; i < 6; i++) {
    const x = Math.round((rand() * 2 - 1) * 4) / 4;
    const y = Math.round((rand() * 1.25 - 0.75) * 4) / 4;
    if (Math.hypot(x - prev.x, y - prev.y) >= 0.5) return { x, y, holdMs: rand() < 0.2 ? hold(500, 900) : hold(1400, 3200) };
  }
  return { x: -Math.sign(prev.x || 1), y: 0, holdMs: hold(1400, 3200) };
}

export class Band {
  constructor(root, sky, tint) {
    this.root = root;
    this.sky = sky;
    this.ctx = sky.getContext("2d");
    const n = parseInt(tint.slice(1), 16);
    this.tintHex = tint;
    this.tint = [n >> 16, (n >> 8) & 255, n & 255];
    this.frame = null;
    this.visible = false;
    this.size = { w: 0, h: 0 };
    this.lastDraw = 0;
    this.look = { x: 0, y: 0 };
    this.eyes = { x: 0, y: 0 };
    this.lookTimer = null;
    this.nextBlink = 0;
    this.blinkAt = -1;
    this.smileAt = -10;
    this.nextSmile = 0;
    this.pointer = { x: 0, y: 0, over: false };
    this.glow = 0;
    this.followUntil = 0;
    this.ripples = [];
    this.hopAt = -10;
    this.dizzyAt = -10;
    this.pats = [];
    this.twinkles = [];
    this.nextTwinkle = 0;
    this.meteor = null;
    this.nextMeteor = 0;
    this.bot = { x: 0, y: 0, s: 0 };
    new ResizeObserver(() => this.fit()).observe(root);
    root.addEventListener("pointermove", (e) => this.hover(e, true));
    root.addEventListener("pointerleave", (e) => this.hover(e, false));
    root.addEventListener("pointerdown", (e) => this.press(e));
    window.addEventListener("pointermove", (e) => this.follow(e.clientX, e.clientY));
    this.loop = this.loop.bind(this);
  }

  local(e) {
    const r = this.root.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  hover(e, over) {
    this.pointer = { ...this.local(e), over };
    this.wake();
  }

  /** 눈은 창 안 어디든 마우스 쪽으로. */
  follow(cx, cy) {
    const r = this.root.getBoundingClientRect();
    if (r.width === 0) return;
    const dx = cx - r.left - (this.bot.x + this.bot.s / 2);
    const dy = cy - r.top - (this.bot.y + this.bot.s / 2);
    this.look = { x: Math.max(-1, Math.min(1, dx / 260)), y: Math.max(-1, Math.min(1, dy / 90)) };
    this.followUntil = performance.now() + 4000;
  }

  press(e) {
    if (e.button !== 0) return;
    const p = this.local(e);
    const t = performance.now() / 1000;
    this.ripples.push({ ...p, at: t });
    if (this.ripples.length > 4) this.ripples.shift();
    const b = this.bot;
    if (p.x >= b.x && p.x <= b.x + b.s && p.y >= b.y && p.y <= b.y + b.s) {
      this.pats = this.pats.filter((at) => t - at < 1.5).concat(t);
      if (this.pats.length >= 5) {
        this.pats = [];
        this.dizzyAt = t;
      } else if (t - this.dizzyAt > 1.6) {
        this.smileAt = t;
        this.hopAt = t;
      }
    }
    this.wake();
  }

  wake() {
    if (this.visible && this.frame == null) this.frame = requestAnimationFrame(this.loop);
  }

  setVisible(on) {
    if (this.visible === on) return;
    this.visible = on;
    if (on) {
      this.fit();
      const t = performance.now() / 1000;
      this.nextBlink = t + 2 + Math.random() * 3;
      this.nextSmile = t + 6 + Math.random() * 8;
      this.nextTwinkle = t + 1 + Math.random() * 2;
      this.nextMeteor = t + 6 + Math.random() * 10;
      const glance = () => {
        const l = nextLook(this.look);
        if (performance.now() > this.followUntil) this.look = { x: l.x, y: l.y };
        this.lookTimer = window.setTimeout(glance, l.holdMs);
      };
      this.lookTimer = window.setTimeout(glance, 800);
      this.frame = requestAnimationFrame(this.loop);
    } else {
      if (this.lookTimer != null) window.clearTimeout(this.lookTimer);
      this.lookTimer = null;
      if (this.frame != null) cancelAnimationFrame(this.frame);
      this.frame = null;
    }
  }

  fit() {
    const width = this.root.offsetWidth, height = this.root.offsetHeight;  // 돌리거나 줄인 카드에서도 원래 크기로 (getBoundingClientRect 는 줄어든 크기라 흐려졌음)
    if (width === 0 || height === 0) return;
    const dpr = window.devicePixelRatio || 1;
    this.sky.width = Math.round(width * dpr);
    this.sky.height = Math.round(height * dpr);
    this.size = { w: width, h: height };
    this.draw(performance.now() / 1000);
  }

  loop(now) {
    this.frame = null;
    if (!this.visible) return;
    const busy = this.glow > 0.01 || this.pointer.over || this.ripples.length > 0 || this.meteor != null;
    if (now - this.lastDraw > (busy ? 33 : 50)) {
      this.lastDraw = now;
      const t = now / 1000;
      if (t > this.nextBlink && this.blinkAt < 0) this.blinkAt = t;
      if (this.blinkAt >= 0 && t - this.blinkAt > 0.18) {
        this.blinkAt = -1;
        this.nextBlink = t + 2.5 + Math.random() * 4;
      }
      if (t > this.nextSmile) {
        this.smileAt = t;
        this.nextSmile = t + 10 + Math.random() * 10;
      }
      this.glow += ((this.pointer.over ? 1 : 0) - this.glow) * 0.3;
      this.ripples = this.ripples.filter((r) => t - r.at < RIPPLE_S);
      this.stars(t);
      this.eyes.x += (this.look.x - this.eyes.x) * 0.25;
      this.eyes.y += (this.look.y - this.eyes.y) * 0.25;
      this.draw(t);
    }
    this.frame = requestAnimationFrame(this.loop);
  }

  stars(t) {
    const { w, h } = this.size;
    this.twinkles = this.twinkles.filter((s) => t - s.at < TWINKLE_S);
    if (t > this.nextTwinkle && w > 0) {
      const cols = Math.floor((w * 0.66) / STEP);
      this.twinkles.push({ col: Math.floor(Math.random() * cols), row: Math.floor(Math.random() * (h / STEP)), at: t });
      this.nextTwinkle = t + 1.5 + Math.random() * 3;
    }
    if (this.meteor && (t - this.meteor.at > 2.5 || this.meteorAt(t).y > h + 20)) this.meteor = null;
    if (!this.meteor && t > this.nextMeteor && w > 0) {
      this.meteor = { x: w * (0.05 + Math.random() * 0.45), y: -8, vx: 130 + Math.random() * 60, vy: 10 + Math.random() * 20, at: t };
      this.nextMeteor = t + 14 + Math.random() * 16;
    }
  }

  meteorAt(t) {
    const m = this.meteor;
    const dt = t - m.at;
    return { x: m.x + m.vx * dt, y: m.y + m.vy * dt + 0.5 * GRAVITY * dt * dt };
  }

  draw(t) {
    const { ctx } = this;
    const { w, h } = this.size;
    if (w === 0) return;
    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const [r, g, b] = this.tint;
    // 봇 자리: 오른쪽, 높이의 78% (104 까지) — Parser band.py 와 같음
    const cols = Math.floor(w / STEP);
    const mid = Math.round(cols / 2);  // 사이트: 따로 떠 있는 화면이라 가운데 (앱 창 띠는 오른쪽)
    const s = Math.min(104, h * 0.78);
    this.bot = { x: mid * STEP - s / 2, y: h / 2 - s / 2, s };
    // 봇 둘레가 대표색으로 은은하게 (하위 앱)
    const cx = this.bot.x + s / 2;
    const cy = this.bot.y + s / 2;
    const halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, s * 1.3);
    halo.addColorStop(0, `rgba(${r},${g},${b},${80 / 255})`);
    halo.addColorStop(1, `rgba(${r},${g},${b},0)`);
    ctx.fillStyle = halo;
    ctx.fillRect(0, 0, w, h);

    const px = this.pointer.x;
    const py = this.pointer.y;
    const glow = this.glow;
    const sparks = new Map();
    for (const st of this.twinkles) {
      const k = Math.sin((Math.PI * (t - st.at)) / TWINKLE_S);
      sparks.set(st.col * 1000 + st.row, 0.9 * k);
      for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) sparks.set((st.col + dc) * 1000 + st.row + dr, 0.3 * k);
    }
    if (this.meteor) {
      for (let i = 0; i < TAIL; i++) {
        const at = t - i * 0.03;
        if (at < this.meteor.at) break;
        const p = this.meteorAt(at);
        const key = Math.round((p.x - STEP / 2) / STEP) * 1000 + Math.round((p.y - STEP / 2) / STEP);
        sparks.set(key, Math.max(sparks.get(key) ?? 0, 0.95 * (1 - i / TAIL)));
      }
    }
    const rings = this.ripples.map((rp) => ({ x: rp.x, y: rp.y, rad: RIPPLE_SPEED * out((t - rp.at) / RIPPLE_S) * RIPPLE_S, fade: 1 - (t - rp.at) / RIPPLE_S }));
    for (let row = 0, y0 = STEP / 2; y0 < h; row++, y0 += STEP) {
      for (let col = 0, x0 = STEP / 2; x0 < w; col++, x0 += STEP) {
        let boost = 0;
        let x = x0;
        let y = y0;
        const spark = sparks.get(col * 1000 + row) ?? 0;
        boost += spark;
        if (glow > 0.01) {
          const dx = x0 - px;
          const dy = y0 - py;
          const d = Math.hypot(dx, dy);
          if (d < GLOW_R) {
            const k = (1 - d / GLOW_R) ** 2 * glow;
            boost += 0.8 * k;
            if (d > 0.5) {
              x += (dx / d) * PUSH * k;
              y += (dy / d) * PUSH * k;
            }
          }
        }
        for (const ring of rings) {
          const off = Math.abs(Math.hypot(x0 - ring.x, y0 - ring.y) - ring.rad);
          if (off < RIPPLE_W) boost += 0.45 * (1 - off / RIPPLE_W) * ring.fade;
        }
        if (boost > 0.02) {
          ctx.fillStyle = spark > 0.15 ? "#fff" : `rgb(${r},${g},${b})`;
          ctx.globalAlpha = Math.min(0.9, 0.12 + boost);
        } else {
          const edge = 0.07 * Math.sin(y * 0.045 + x * 0.006 + t * 0.25) + 0.04 * Math.sin(y * 0.12 - t * 0.4);
          const u = Math.min(1, Math.max(0, (x / w - 0.18 + edge) / 0.8));
          const k = u * u * (3 - 2 * u);
          const wave = 0.5 + 0.5 * Math.sin(x * 0.018 - y * 0.03 - t * 0.9);
          const m = Math.min(1, k * 2.5);
          ctx.fillStyle = `rgb(${255 + (r - 255) * m},${255 + (g - 255) * m},${255 + (b - 255) * m})`;
          ctx.globalAlpha = 0.06 + (0.04 + 0.01 * k) * wave + k * (0.1 + 0.12 * wave);
        }
        ctx.beginPath();
        ctx.arc(x, y, 1.5 + Math.min(0.6, boost), 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
    this.paintBot(t);
  }

  /** 작은 앱 봇을 크게: 대표색 몸 · 어두운 화면 · 흰 네모 눈 둘 (Parser band.py _paint_bot 과 같음). */
  paintBot(t) {
    const { ctx } = this;
    const { x: bx, y: by, s } = this.bot;
    const u = s / 10;
    const hop = t - this.hopAt < 0.32 ? 0.6 * Math.sin((Math.PI * (t - this.hopAt)) / 0.32) : 0;
    const ox = bx;
    const oy = by - hop * u;
    const rect = (x, y, w, h, rad) => {
      ctx.beginPath();
      ctx.roundRect(ox + x * u, oy + y * u, w * u, h * u, rad * u);
    };
    const gx = this.eyes.x;
    const gy = this.eyes.y;
    ctx.fillStyle = this.tintHex;
    rect(0.8, 1.4, 8.4, 7.4, 2.3);
    ctx.fill();
    ctx.fillStyle = BOT_SCREEN;
    rect(2.2 + gx * 0.45, 2.8 + gy * 0.4, 5.6, 4.6, 1.3);
    ctx.fill();
    const ex = gx * 0.9;
    const ey = gy * 0.8;
    ctx.strokeStyle = "#fff";
    ctx.fillStyle = "#fff";
    ctx.lineWidth = 0.45 * u;
    ctx.lineCap = "round";
    if (t - this.dizzyAt < 1.6) {
      const wob = 0.15 * Math.sin((t - this.dizzyAt) * 14);
      for (const c of [3.85 + wob, 6.15 - wob]) {
        ctx.beginPath();
        ctx.moveTo(ox + (c - 0.55) * u, oy + 4.5 * u);
        ctx.lineTo(ox + (c + 0.55) * u, oy + 5.7 * u);
        ctx.moveTo(ox + (c + 0.55) * u, oy + 4.5 * u);
        ctx.lineTo(ox + (c - 0.55) * u, oy + 5.7 * u);
        ctx.stroke();
      }
      return;
    }
    if (t - this.smileAt < 1.4) {
      for (const c of [3.85 + ex, 6.15 + ex]) {
        ctx.beginPath();
        ctx.arc(ox + c * u, oy + (5.2 + ey) * u, 0.6 * u, Math.PI, 0);
        ctx.stroke();
      }
      return;
    }
    let tall = 2.0;
    if (this.blinkAt >= 0) {
      const k = (t - this.blinkAt) / 0.18;
      tall = k > 0.33 && k < 0.66 ? 0.35 : 1.0;
    }
    for (const x of [3.3, 5.6]) {
      rect(x + ex, 4.1 + ey + (2.0 - tall) / 2, 1.1, tall, Math.min(0.55, tall / 2));
      ctx.fill();
    }
  }
}
