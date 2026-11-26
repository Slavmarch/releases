// Dial Pop — web bridge for the browser build (lagoonworks.app/dialpop/play/).
// Loaded before the game script instead of native.js. It only sets window.* hooks the game already reads.
//
// Ads: Google H5 Games Ads (AdSense "Ad Placement API", adBreak). build.py --web fills WEB_AD_CLIENT
// from DIALPOP_WEB_ADS=ca-pub-…; empty = no ads at all. Either way the game's 3-second placeholder
// "ad" never shows on the public web:
//   revive  → 'ok' after a watched ad, 'skipped' if the player closed it early, 'nofill' otherwise
//             (no ad / blocked / capped). The game grants the revive on 'ok' and 'nofill' (억까 없음).
//   between runs ('inter') → Google decides whether an ad fits (frequency is theirs), then the run starts.
// Platform leaderboards / achievements / reminders stay app-only (no DIALPOP_GS / DIALPOP_PUSH here);
// the web gets its own Firestore board instead (DIALPOP_LB_LIVE).
(function () {
  if (window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()) return;
  const WEB_AD_CLIENT = 'ca-pub-3455429014217845';      // set by build.py --web (DIALPOP_WEB_ADS)
  const WEB_AD_TEST = false;      // data-adbreak-test="on" until the site is approved for H5 games ads
  // Ranking: the web board lives in Firestore (lb/…, rules in firestore-lb.rules). false = hide the chip.
  const WEB_RANKING = true;
  window.DIALPOP_LB_LIVE = WEB_RANKING;
  // short screens (landscape tablet, browser bars): when the HUD + board don't fit, keep the top
  // (score, pause) on screen instead of centring the overflow off both edges
  const fit = document.createElement('style');
  // PC / tablet: bigger board, sitting a bit lower than the phone layout (game.html layout() reads DIALPOP_BIG)
  const BIG_Q = '(min-width: 700px) and (min-height: 600px)';
  window.DIALPOP_BIG = () => matchMedia(BIG_Q).matches;
  fit.textContent = '#app{justify-content:safe center}@media ' + BIG_Q + '{#app{padding-bottom:min(60px,6vh)}}';
  document.head.appendChild(fit);
  if (!WEB_RANKING) {
    const st = document.createElement('style');
    st.textContent = '#intro .lbAdd{display:none!important}';
    document.head.appendChild(st);
  }

  // PWA: offline play after the first visit (sw.js caches the page, fonts and icons)
  // Google sign-in for the web board (Google Identity Services). Client ID = the Firebase project's
  // "Web client (auto created by Google Service)"; build.py fills it from DIALPOP_GOOGLE_CLIENT_ID.
  // Empty = no sign-in button, so nobody can join the board.
  const GOOGLE_CLIENT_ID = '127787460637-n7vq94otv5pt6mbpa1um01jj50hbdoha.apps.googleusercontent.com';   // public, not a secret
  if (GOOGLE_CLIENT_ID) {
    let gsi = null;
    const load = () => gsi || (gsi = new Promise((ok, no) => {
      const g = document.createElement('script');
      g.src = 'https://accounts.google.com/gsi/client'; g.async = true;
      g.onload = () => ok(window.google.accounts.id); g.onerror = no;
      document.head.appendChild(g);
    }));
    let onCred = null;
    window.DIALPOP_GOOGLE = {
      // draws Google's own button into el; cb(idToken) after the player picks an account
      render(el, cb) {
        onCred = cb;
        load().then(id => {
          if (!window.__gsiInit) {
            id.initialize({ client_id: GOOGLE_CLIENT_ID, callback: r => onCred && onCred(r.credential),
              auto_select: false, cancel_on_tap_outside: true, use_fedcm_for_prompt: true });
            window.__gsiInit = true;
          }
          id.renderButton(el, { type: 'standard', theme: 'filled_black', size: 'large', shape: 'pill',
            text: 'signin_with', logo_alignment: 'left' });
        }).catch(() => { el.textContent = 'Google sign-in could not load.'; });
      }
    };
  }

  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
  }

  if (!WEB_AD_CLIENT) {
    window.DIALPOP_ADS = { show: kind => Promise.resolve(kind === 'reward' ? 'nofill' : 'skipped') };
    return;
  }

  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + WEB_AD_CLIENT;
  s.crossOrigin = 'anonymous';
  s.setAttribute('data-ad-client', WEB_AD_CLIENT);
  s.setAttribute('data-ad-frequency-hint', '90s');
  if (WEB_AD_TEST) s.setAttribute('data-adbreak-test', 'on');
  let blocked = false;                                    // ad blocker / offline: don't make the player wait
  s.onerror = () => { blocked = true; };
  document.head.appendChild(s);
  window.adsbygoogle = window.adsbygoogle || [];
  const adBreak = o => window.adsbygoogle.push(o);
  adBreak({ preloadAdBreaks: 'on', sound: 'on' });       // adConfig

  // the game's sounds go quiet while an ad plays
  let ac = null;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (AC) {
    const Orig = AC;
    const Wrapped = function (...a) { const c = new Orig(...a); ac = c; return c; };
    Wrapped.prototype = Orig.prototype;
    if (window.AudioContext) window.AudioContext = Wrapped; else window.webkitAudioContext = Wrapped;
  }
  const mute = on => { try { ac && (on ? ac.suspend() : ac.resume()); } catch (e) {} };

  window.DIALPOP_ADS = {
    show(kind) {
      if (blocked) return Promise.resolve(kind === 'reward' ? 'nofill' : 'skipped');
      return new Promise(done => {
        let result = kind === 'reward' ? 'nofill' : 'skipped', fin = false;
        const end = () => { if (fin) return; fin = true; mute(false); done(result); };
        // adBreakDone is Google's "always called last"; the timer covers the script being blocked.
        const guard = setTimeout(end, 4000);
        const o = {
          name: kind === 'reward' ? 'revive' : 'between_runs',
          beforeAd: () => { clearTimeout(guard); mute(true); },   // 'next' ads only start here
          afterAd: () => mute(false),
          adBreakDone: () => { clearTimeout(guard); end(); }
        };
        if (kind === 'reward') {
          o.type = 'reward';
          o.beforeReward = showAdFn => { clearTimeout(guard); if (!fin) showAdFn(); };
          o.adViewed = () => { result = 'ok'; };
          o.adDismissed = () => { result = 'skipped'; };
        } else {
          o.type = 'next';
        }
        try { adBreak(o); } catch (e) { clearTimeout(guard); end(); }
      });
    }
  };
})();
