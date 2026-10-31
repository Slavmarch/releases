// OVERMIND src/band.ts (+ wander.ts) 를 묶은 것 — 노치 설정 창의 점 띠와 같은 그림. 고치려면 노치 쪽을 고치고 다시 묶음 (npx esbuild src/band.ts --bundle --format=esm).
var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);

// src/wander.ts
var FRONT = 0.3;
var QUICK = 0.2;
function nextLook(prev, rand = Math.random) {
  const hold = (lo, hi) => Math.round(lo + rand() * (hi - lo));
  if (Math.hypot(prev.x, prev.y) >= 0.5 && rand() < FRONT) return { x: 0, y: 0, holdMs: hold(1800, 3800) };
  for (let i = 0; i < 6; i++) {
    const x = Math.round((rand() * 2 - 1) * 4) / 4;
    const y = Math.round((rand() * 1.25 - 0.75) * 4) / 4;
    if (Math.hypot(x - prev.x, y - prev.y) >= 0.5) {
      return { x, y, holdMs: rand() < QUICK ? hold(500, 900) : hold(1400, 3200) };
    }
  }
  return { x: -Math.sign(prev.x || 1), y: 0, holdMs: hold(1400, 3200) };
}

// src/band.ts
var STEP = 6;
var EYE = "#A5F3FC";
var CHEEK = "#F9A8D4";
var EYE_OPEN = [".##.", "####", "####", "####", "####", "####", "####", "####", ".##."];
var EYE_HALF = [".##.", "####", "####", "####", ".##."];
var EYE_SHUT = ["####"];
var EYE_SMILE = [".####.", "##..##", "#....#"];
var EYE_DIZZY = ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"];
var CHEEK_DOTS = [".###.", "#####", ".###."];
var EYE_GAP = 7;
var GLOW_R = 72;
var PUSH = 3;
var RIPPLE_S = 0.9;
var RIPPLE_SPEED = 320;
var RIPPLE_W = 16;
var out = (k) => 1 - (1 - k) ** 3;
var TWINKLE_S = 1.1;
var GRAVITY = 90;
var TAIL = 14;
var Band = class {
  constructor(root, sky) {
    this.root = root;
    this.sky = sky;
    __publicField(this, "ctx");
    __publicField(this, "frame", null);
    __publicField(this, "visible", false);
    __publicField(this, "tint", [167, 139, 250]);
    __publicField(this, "size", { w: 0, h: 0 });
    __publicField(this, "lastDraw", 0);
    /** Where the eyes look (−1…1) and where they are drawn now (eased toward it). */
    __publicField(this, "look", { x: 0, y: 0 });
    __publicField(this, "eyes", { x: 0, y: 0 });
    __publicField(this, "lookTimer", null);
    __publicField(this, "nextBlink", 0);
    __publicField(this, "blinkAt", -1);
    __publicField(this, "smileAt", -10);
    __publicField(this, "nextSmile", 0);
    /** The pointer over the band (CSS px), how strongly it lights the dots (eased 0…1). */
    __publicField(this, "pointer", { x: 0, y: 0, over: false });
    __publicField(this, "glow", 0);
    /** While the pointer moves in the window, the eyes follow it instead of wandering. */
    __publicField(this, "followUntil", 0);
    __publicField(this, "ripples", []);
    __publicField(this, "hopAt", -10);
    __publicField(this, "dizzyAt", -10);
    __publicField(this, "pats", []);
    __publicField(this, "twinkles", []);
    __publicField(this, "nextTwinkle", 0);
    __publicField(this, "meteor", null);
    __publicField(this, "nextMeteor", 0);
    /** Where the face is drawn now, in CSS px (for clicks and for following the pointer). */
    __publicField(this, "faceBox", { x0: 0, y0: 0, x1: 0, y1: 0 });
    __publicField(this, "loop", (now) => {
      this.frame = null;
      if (!this.visible) return;
      const busy = this.glow > 0.01 || this.pointer.over || this.ripples.length > 0 || this.meteor != null;
      if (now - this.lastDraw > (busy ? 33 : 50)) {
        this.lastDraw = now;
        const t = now / 1e3;
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
    });
    this.ctx = sky.getContext("2d");
    new ResizeObserver(() => this.fit()).observe(root);
    root.addEventListener("pointermove", (e) => this.hover(e, true));
    root.addEventListener("pointerleave", (e) => this.hover(e, false));
    root.addEventListener("pointerdown", (e) => this.press(e));
    window.addEventListener("pointermove", (e) => this.follow(e.clientX, e.clientY));
  }
  local(e) {
    const r = this.root.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }
  hover(e, over) {
    this.pointer = { ...this.local(e), over };
    this.wake();
  }
  /** The eyes turn toward the pointer, wherever it is in the window. */
  follow(cx, cy) {
    const r = this.root.getBoundingClientRect();
    if (r.width === 0) return;
    const f = this.faceBox;
    const dx = cx - r.left - (f.x0 + f.x1) / 2;
    const dy = cy - r.top - (f.y0 + f.y1) / 2;
    this.look = { x: Math.max(-1, Math.min(1, dx / 260)), y: Math.max(-1, Math.min(1, dy / 90)) };
    this.followUntil = performance.now() + 4e3;
  }
  press(e) {
    if (e.button !== 0) return;
    const p = this.local(e);
    const t = performance.now() / 1e3;
    this.ripples.push({ ...p, at: t });
    if (this.ripples.length > 4) this.ripples.shift();
    const f = this.faceBox;
    if (p.x >= f.x0 && p.x <= f.x1 && p.y >= f.y0 && p.y <= f.y1) {
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
  /** Start drawing again at once (a pointer event while the loop idles between frames). */
  wake() {
    if (this.visible && this.frame == null) this.frame = requestAnimationFrame(this.loop);
  }
  setTheme(theme) {
    const n = parseInt(theme.tint.slice(1), 16);
    this.tint = [n >> 16, n >> 8 & 255, n & 255];
    this.root.style.setProperty("--band-tint", theme.tint);
    this.draw(performance.now() / 1e3);
  }
  setVisible(on) {
    if (this.visible === on) return;
    this.visible = on;
    if (on) {
      this.fit();
      const t = performance.now() / 1e3;
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
    const { width, height } = this.root.getBoundingClientRect();
    if (width === 0 || height === 0) return;
    const dpr = window.devicePixelRatio || 1;
    this.sky.width = Math.round(width * dpr);
    this.sky.height = Math.round(height * dpr);
    this.size = { w: width, h: height };
    this.draw(performance.now() / 1e3);
  }
  /** Stars and meteors: start one when its time comes, drop the ones that are over. */
  stars(t) {
    const { w, h } = this.size;
    this.twinkles = this.twinkles.filter((s) => t - s.at < TWINKLE_S);
    if (t > this.nextTwinkle && w > 0) {
      const cols = Math.floor(w * 0.66 / STEP);
      this.twinkles.push({ col: Math.floor(Math.random() * cols), row: Math.floor(Math.random() * (h / STEP)), at: t });
      this.nextTwinkle = t + 1.5 + Math.random() * 3;
    }
    if (this.meteor && (t - this.meteor.at > 2.5 || this.meteorAt(t).y > h + 20)) this.meteor = null;
    if (!this.meteor && t > this.nextMeteor && w > 0) {
      this.meteor = { x: w * (0.05 + Math.random() * 0.45), y: -8, vx: 130 + Math.random() * 60, vy: 10 + Math.random() * 20, at: t };
      this.nextMeteor = t + 14 + Math.random() * 16;
    }
  }
  /** Where the meteor is `dt` seconds after it started. */
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
    const lit = this.face(t, w, h);
    const px = this.pointer.x;
    const py = this.pointer.y;
    const glow = this.glow;
    const sparks = /* @__PURE__ */ new Map();
    for (const st of this.twinkles) {
      const k = Math.sin(Math.PI * (t - st.at) / TWINKLE_S);
      sparks.set(st.col * 1e3 + st.row, 0.9 * k);
      for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) sparks.set((st.col + dc) * 1e3 + st.row + dr, 0.3 * k);
    }
    if (this.meteor) {
      for (let i = 0; i < TAIL; i++) {
        const at = t - i * 0.03;
        if (at < this.meteor.at) break;
        const p = this.meteorAt(at);
        const col = Math.round((p.x - STEP / 2) / STEP);
        const row = Math.round((p.y - STEP / 2) / STEP);
        const k = 1 - i / TAIL;
        const key = col * 1e3 + row;
        sparks.set(key, Math.max(sparks.get(key) ?? 0, 0.95 * k));
      }
    }
    const rings = this.ripples.map((r2) => ({ x: r2.x, y: r2.y, rad: RIPPLE_SPEED * out((t - r2.at) / RIPPLE_S) * RIPPLE_S, fade: 1 - (t - r2.at) / RIPPLE_S }));
    for (let row = 0, y0 = STEP / 2; y0 < h; row++, y0 += STEP) {
      for (let col = 0, x0 = STEP / 2; x0 < w; col++, x0 += STEP) {
        const color = lit.get(col * 1e3 + row);
        let boost = 0;
        let spark = 0;
        let x = x0;
        let y = y0;
        if (!color) {
          spark = sparks.get(col * 1e3 + row) ?? 0;
          boost += spark;
          if (glow > 0.01) {
            const dx = x0 - px;
            const dy = y0 - py;
            const d = Math.hypot(dx, dy);
            if (d < GLOW_R) {
              const k = (1 - d / GLOW_R) ** 2 * glow;
              boost += 0.8 * k;
              if (d > 0.5) {
                x += dx / d * PUSH * k;
                y += dy / d * PUSH * k;
              }
            }
          }
          for (const ring of rings) {
            const off = Math.abs(Math.hypot(x0 - ring.x, y0 - ring.y) - ring.rad);
            if (off < RIPPLE_W) boost += 0.45 * (1 - off / RIPPLE_W) * ring.fade;
          }
        }
        if (color) {
          ctx.fillStyle = color;
          ctx.globalAlpha = color === CHEEK ? 0.6 : 0.95;
        } else if (boost > 0.02) {
          ctx.fillStyle = spark > 0.15 ? "#fff" : `rgb(${r},${g},${b})`;
          ctx.globalAlpha = Math.min(0.9, 0.12 + boost);
        } else {
          const edge = 0.07 * Math.sin(y * 0.045 + x * 6e-3 + t * 0.25) + 0.04 * Math.sin(y * 0.12 - t * 0.4);
          const u = Math.min(1, Math.max(0, (x / w - 0.18 + edge) / 0.8));
          const k = u * u * (3 - 2 * u);
          const wave = 0.5 + 0.5 * Math.sin(x * 0.018 - y * 0.03 - t * 0.9);
          const m = Math.min(1, k * 2.5);
          ctx.fillStyle = `rgb(${255 + (r - 255) * m},${255 + (g - 255) * m},${255 + (b - 255) * m})`;
          ctx.globalAlpha = 0.06 + (0.04 + 0.01 * k) * wave + k * (0.1 + 0.12 * wave);
        }
        ctx.beginPath();
        ctx.arc(x, y, color ? 2 : 1.5 + Math.min(0.6, boost), 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
  }
  /** The lit dots of the face now, by col * 1000 + row. */
  face(t, w, h) {
    const lit = /* @__PURE__ */ new Map();
    const put = (art, col0, row0, color) => {
      art.forEach((line, dr) => {
        for (let dc = 0; dc < line.length; dc++) if (line[dc] === "#") lit.set((col0 + dc) * 1e3 + row0 + dr, color);
      });
    };
    const cols = Math.floor(w / STEP);
    const rows = Math.floor(h / STEP);
    const mid = Math.round(cols / 2);  // 사이트: 띠 안 따로 떠 있는 화면이라 가운데 (노치 설정 창은 오른쪽)
    const top = Math.round(rows / 2) - 6;
    const gx = Math.round(this.eyes.x * 2);
    const hop = t - this.hopAt < 0.32 ? Math.round(2 * Math.sin(Math.PI * (t - this.hopAt) / 0.32)) : 0;
    const gy = Math.round(this.eyes.y * 2) - hop;
    const left = mid - Math.floor(EYE_GAP / 2) - 4;
    const right = left + 4 + EYE_GAP;
    this.faceBox = { x0: (left - 7) * STEP, y0: (top - 2) * STEP, x1: (right + 11) * STEP, y1: (top + 14) * STEP };
    if (t - this.dizzyAt < 1.6) {
      const wob = Math.round(Math.sin((t - this.dizzyAt) * 14));
      put(EYE_DIZZY, left + wob, top + 2, EYE);
      put(EYE_DIZZY, right - wob, top + 2, EYE);
    } else if (t - this.smileAt < 1.4) {
      put(EYE_SMILE, left - 1 + gx, top + 3 + gy, EYE);
      put(EYE_SMILE, right - 1 + gx, top + 3 + gy, EYE);
    } else {
      let eye = EYE_OPEN;
      if (this.blinkAt >= 0) {
        const p = (t - this.blinkAt) / 0.18;
        eye = p > 0.33 && p < 0.66 ? EYE_SHUT : EYE_HALF;
      }
      const dy = Math.floor((EYE_OPEN.length - eye.length) / 2);
      put(eye, left + gx, top + dy + gy, EYE);
      put(eye, right + gx, top + dy + gy, EYE);
    }
    put(CHEEK_DOTS, left - 6, top + 10, CHEEK);
    put(CHEEK_DOTS, right + 5, top + 10, CHEEK);
    return lit;
  }
};
export {
  Band
};
