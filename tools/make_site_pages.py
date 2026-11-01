"""lagoonworks.app 첫 화면 + 앱 소개 쪽 다섯 개를 만듦 (2026-10-31 현우 '앱 소개 창을 만들어서 꾸미고 싶다').
틀·색은 노치 설정 창 그대로 (assets/site.css): 왼쪽 목록 · 점 띠 · 카드.
OVERMIND 쪽 띠 = 노치 점 눈 오비(assets/band.js), 다른 앱 = 대표색 작은 앱 봇(assets/appband.js — 봇 위계, FAMILY.md 5).
쓰는 법:  python tools/make_site_pages.py .   (releases 저장소 맨 위에서. family/apps.json 이 바뀌면 GitHub Actions site.yml 이 혼자 돌림)   (legal/ 은 건드리지 않음 — 그건 legal/make_site.py)
글은 해요체·누구에게나 맞는 말(학생 쏠림 금지)·이모지 없음. 사실이 아닌 것(맥 판·내려받기)은 '준비 중'으로."""
import hashlib, html, json, os, sys

# 파일 내용이 바뀌면 주소 꼬리(?v=)가 바뀌어 브라우저가 옛 파일을 안 씀
V = {}
OUT = "."
HIST = {}
# 언어 (2026-10-31 사용자 'Download 옆에 Eng/Kor'): 한국어 쪽은 맨 위, 영어 쪽은 en/ 아래 같은 모양. 한 번에 한 언어씩 만듦
L = "ko"
def T(ko, en): return en if L == "en" else ko
def R(base): return base + ("../" if L == "en" else "")      # 그림·글꼴·약관은 늘 맨 위 하나만

E = html.escape
MINI = ('<svg viewBox="0 0 10 10" aria-hidden="true"><rect x="0.8" y="1.4" width="8.4" height="7.4" rx="2.3" fill="{c}"/>'
        '<rect x="2.2" y="2.8" width="5.6" height="4.6" rx="1.3" fill="#1a1033"/>'
        '<rect x="3.3" y="4.1" width="1.1" height="2" rx="0.55" fill="#a5f3fc"/><rect x="5.6" y="4.1" width="1.1" height="2" rx="0.55" fill="#a5f3fc"/></svg>')
ICON = {
    "home": '<svg viewBox="0 0 24 24"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/></svg>',
    "legal": '<svg viewBox="0 0 24 24"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/></svg>',
    "download": '<svg viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
    "notes": '<svg viewBox="0 0 24 24"><path d="M5 4h14v16H5z"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/></svg>',
}

APPS = [
  dict(id="overmind", name="OVERMIND", color="#a78bfa", on="#1a1033",
       ko="화면 맨 위의 작은 섬", en="A little island at the top of your screen",
       short="화면 위 작은 섬 — 알림·일정·할 일·음악·AI 를 한곳에", short_en="A little island at the top of your screen",
       intro="평소엔 화면 맨 위에 작은 섬으로 조용히 있다가, 마우스를 올리면 열려요. 다른 가족 앱의 소식이 알약으로 모이고, 일정·할 일·음악·AI 를 한곳에서 써요. 섬에는 캐릭터 오비가 살아요.",
       feats=[("한눈에 보는 섬", "날씨·시각·와이파이·배터리를 작은 섬에서 바로 봐요. 쉬는 동안은 거의 힘을 쓰지 않아요."),
              ("알림 알약", "Parser·Optic·Glen 이 보낸 소식이 알약으로 떠요. 눌러서 바로 열거나 답해요."),
              ("일정·D-day·할 일", "다가오는 일정과 D-day 를 세고, 할 일과 메모를 섬에 적어 둬요."),
              ("집중 타이머", "정한 시간 동안 집중하고, 쉬는 시간을 알려 줘요."),
              ("음악", "지금 재생 중인 곡을 섬에서 멈추고 넘겨요."),
              ("클립보드 기록", "복사했던 글을 다시 찾아 붙여요."),
              ("녹음·받아쓰기", "녹음하고 글로 받아 적어요."),
              ("노치 AI", "내 AI 키로 섬에서 바로 물어봐요. 키는 OS 보안 저장소에만 둬요."),
              ("가족 앱의 키를 한곳에서", "AI 키를 노치에 한 번 넣으면 Parser·Optic 도 같이 써요.")]),
  dict(id="ovi-family", name="Ovi Family", color="#a78bfa", on="#1a1033",
       ko="가족 앱을 한곳에서", en="Install and update the family apps",
       short="가족 앱을 한 번에 설치하고 새 버전으로", short_en="Installs and updates the family apps",
       intro="OVERMIND·Parser·Optic·Glen 을 여기서 설치하고, 새 버전이 나오면 바로 바꿔요. 무엇이 바뀌었는지도 함께 보여 줘요.",
       feats=[("한 번에 설치", "필요한 앱만 골라 설치해요."),
              ("새 버전 알림", "새 버전이 나오면 알려 주고, 누르면 바꿔요."),
              ("바뀐 것 보기", "버전마다 무엇이 바뀌었는지 짧게 보여 줘요."),
              ("문제 알리기", "앱에 문제가 생기면 기록을 모아 문의에 붙일 수 있어요.")]),
  dict(id="parser", name="Parser", color="#d6262f", on="#ffffff",
       ko="PDF 를 읽고, 적고, 고치는 곳", en="Read, annotate and fix your PDFs",
       short="PDF 읽기·필기·글자 인식", short_en="Read, annotate and OCR your PDFs",
       intro="PDF 를 탭으로 열어 읽고, 그 위에 필기하고, 스캔한 PDF 의 글자를 살려요. 사진 속 글자까지 고칠 수 있어요.",
       feats=[("읽기", "탭으로 여러 PDF 를 열고, 미리보기·목차·찾기로 원하는 쪽을 바로 찾아요."),
              ("필기", "형광펜·밑줄·펜·도형·글상자·메모·사진·서명을 넣고, 다른 PDF 앱에서도 그대로 보여요."),
              ("글자 인식", "스캔한 PDF 를 복사·검색되는 PDF 로 바꿔요. 한글·영어·한자·표를 읽어요."),
              ("글자 고치기", "PDF 의 글자를 눌러 바로 고쳐요. 스캔 속 글자와 문단도 고치고 옮겨요."),
              ("그림 편집", "PDF 속 그림에 번호·화살표를 넣고, 가리고, 자르고, 밝기를 바꿔요."),
              ("쪽 편집", "쪽을 옮기고 돌리고, 합치고 나누고, 워터마크를 넣어요."),
              ("내보내기", "한글·워드·txt 로 내보내고, 인쇄해요."),
              ("Ask Parser", "보고 있는 PDF 에 대해 AI 에게 물어봐요.")]),
  dict(id="optic", name="Optic", color="#2dd4bf", on="#04211d",
       ko="화면을 찍으면 글자로", en="Turn a screen capture into text",
       short="화면을 캡처하면 글자로", short_en="Turns a screen capture into text",
       intro="단축키를 누르고 화면에서 네모를 끌면, AI 가 그 안의 글자를 읽어 바로 클립보드에 넣어 줘요. 붙여 넣기만 하면 돼요.",
       feats=[("단축키 한 번", "Ctrl+Alt+Z 로 화면을 멈추고 읽을 곳을 골라요. 단축키는 바꿀 수 있어요."),
              ("원문 그대로", "한글·영어 약어·한자·표를 원문 그대로 살려요."),
              ("여러 장 이어서", "같은 크기로 여러 장을 찍고, 모두 한 번에 복사하거나 txt 로 저장해요."),
              ("사진 읽기", "사진 여러 장을 넣으면 차례로 글자로 옮겨요."),
              ("고르는 AI", "Gemini·Claude·GPT 중에서 골라 쓰고, 붐비면 다른 모델로 넘겨요."),
              ("섬에서 결과", "OVERMIND 섬에 결과가 떠서, 다시 복사도 섬에서 해요.")]),
  dict(id="glen", name="Glen", color="#b9855a", on="#24160a",
       ko="흩어진 파일을 한곳에", en="Bring your scattered files together",
       short="흩어진 파일을 한 곳에", short_en="Brings your scattered files together",
       intro="다운로드·바탕화면에 쌓이는 파일을 한곳에서 보여 줘요. 파일은 제자리에 두고, 목록만 정리해요.",
       feats=[("새로 온 파일", "새 파일이 생기면 바로 알려 주고, 어디서 받았는지도 보여 줘요."),
              ("파일은 제자리", "Glen 은 파일을 몰래 옮기거나 지우지 않아요. 옮기기는 누를 때만, 지우기는 휴지통으로만 해요."),
              ("별과 이름표", "중요한 파일에 별을 달고, 일 이름으로 이름표를 붙여 찾아요."),
              ("파일 찾기", "이름·이름표·받은 곳으로 찾아요. 섬에서도 찾을 수 있어요."),
              ("버린 파일 찾기", "휴지통에 버린 파일이 어디 있었는지 알려 줘요."),
              ("한 곳 폴더", "Optic·Parser 가 만든 파일이 Glen 폴더에 모여요.")]),
]

PRIVACY = {
    "ai": "AI 키는 OS 보안 저장소(Windows 자격 증명 관리자·macOS 키체인)에만 둬요. AI 에는 내가 고른 것만 보내요.",
    "ovi-family": "내려받은 설치 파일이 원본과 같은지(SHA-256) 확인한 뒤에만 설치해요. 앱 기록은 내 PC 에 남고, 문의할 때 직접 붙여요.",
    "glen": "파일을 훑을 때 내용은 열지 않고 이름·크기·날짜만 봐요. 파일은 옮기거나 지우지 않아요.",
}

# 영어 쪽 글 (APPS 의 ko·short 는 en·short_en 이 이미 있음)
EN = {
  "overmind": dict(
    intro="It rests quietly as a little island at the top of your screen and opens when you move the mouse over it. News from the other family apps gathers there as pills, and your schedule, to-dos, music and AI live in one place. A character called Ovi lives on the island.",
    feats=[("The island at a glance", "See the weather, time, Wi-Fi and battery right on the little island. While it rests, it uses almost no power."),
           ("Notification pills", "News from Parser, Optic and Glen shows up as pills. Click to open or reply right away."),
           ("Schedule, D-day and to-dos", "Count down to upcoming events and D-days, and keep to-dos and notes on the island."),
           ("Focus timer", "Stay focused for a set time, and get told when to take a break."),
           ("Music", "Pause and skip the song that is playing, right from the island."),
           ("Clipboard history", "Find text you copied earlier and paste it again."),
           ("Recording and dictation", "Record and turn speech into text."),
           ("Notch AI", "Ask questions on the island with your own AI key. Keys stay only in your OS secure storage."),
           ("One place for AI keys", "Add an AI key to the notch once, and Parser and Optic use it too.")]),
  "ovi-family": dict(
    intro="Install OVERMIND, Parser, Optic and Glen from here, and switch to a new version as soon as it is out. It also shows what changed.",
    feats=[("Install in one go", "Pick only the apps you need and install them."),
           ("New version alerts", "Get told when a new version is out, and update with one click."),
           ("See what changed", "A short list of what changed in each version."),
           ("Report a problem", "If an app has a problem, gather its logs and attach them to your message.")]),
  "parser": dict(
    intro="Open PDFs in tabs to read them, write on top of them, and bring the text in scanned PDFs back to life. You can even fix the text inside photos.",
    feats=[("Read", "Open many PDFs in tabs and jump to the page you want with thumbnails, the outline and search."),
           ("Annotate", "Add highlights, underlines, pen, shapes, text boxes, notes, pictures and signatures. They show the same in other PDF apps."),
           ("Text recognition", "Turn a scanned PDF into one you can copy and search. Reads Korean, English, Hanja and tables."),
           ("Fix text", "Click any text in a PDF to fix it. Text and paragraphs inside scans can be fixed and moved too."),
           ("Picture editing", "Add numbers and arrows to pictures in a PDF, hide parts, crop them and change the brightness."),
           ("Page editing", "Move and rotate pages, merge and split files, and add watermarks."),
           ("Export", "Export to Hangul, Word or txt, and print."),
           ("Ask Parser", "Ask AI about the PDF you are reading.")]),
  "optic": dict(
    intro="Press the shortcut and drag a box on your screen. AI reads the text inside and puts it straight into your clipboard, ready to paste.",
    feats=[("One shortcut", "Ctrl+Alt+Z freezes the screen so you can pick what to read. You can change the shortcut."),
           ("True to the source", "Keeps Korean, English abbreviations, Hanja and tables exactly as they are."),
           ("Many captures in a row", "Capture several areas of the same size, then copy them all at once or save them as txt."),
           ("Read photos", "Drop in several photos and turn them into text one by one."),
           ("Choose your AI", "Pick Gemini, Claude or GPT, and switch to another model when one is busy."),
           ("Results on the island", "Results appear on the OVERMIND island, and you can copy them again from there.")]),
  "glen": dict(
    intro="See the files piling up in Downloads and on your desktop in one place. Your files stay where they are; Glen only organises the list.",
    feats=[("Newly arrived files", "Get told the moment a new file appears, and see where it came from."),
           ("Files stay put", "Glen never moves or deletes files behind your back. It moves only when you click, and deletes only to the Recycle Bin."),
           ("Stars and labels", "Star important files and label them by task to find them later."),
           ("Find files", "Search by name, label or where a file came from. You can search from the island too."),
           ("Find thrown-away files", "See where a file in the Recycle Bin used to be."),
           ("One home folder", "Files made by Optic and Parser gather in the Glen folder.")]),
}
PRIVACY_EN = {
    "ai": "AI keys stay only in your OS secure storage (Windows Credential Manager, macOS Keychain). Only what you choose is sent to AI.",
    "ovi-family": "Installers are installed only after checking that they match the original (SHA-256). App logs stay on your PC, and you attach them yourself when you contact us.",
    "glen": "When Glen scans, it never opens file contents; it looks only at names, sizes and dates. It does not move or delete files.",
}

# 다른 사람이 만든 앱 소개 칸 (2026-11-01 현우 '동기가 만든 앱도 광고하고 싶다'): 첫 화면 앱 카드 아래에 '광고' 표시를 달고 보여 줌.
# 비어 있으면 칸이 안 생김. 광고 회사 스크립트·추적 없음 — 그림은 assets/picks/<id>.png 로 사이트에 직접 넣음(없으면 첫 글자).
# 고칠 것: id(영문, 바꾸지 않음) · name · url(https 만) · ko·en(소개 한두 줄) · color(대표색, 없으면 회색)
# 세로 배너 위 큰 그림 = assets/picks/<id>_cover.jpg (+ _cover2.jpg 면 번갈아) (그 사이트 대표 그림을 잘라 넣음, 2026-11-01 현우 — 없으면 대표색 바탕)
# paid=True(돈을 받고 싣는 광고)면 표시는 '광고'·rel sponsored — 법(표시광고법·추천보증 심사지침)상 꼭. 돈 안 받는 소개는 '추천' (2026-11-01 현우 'DUK 는 아직 돈 받는 거래 아님').
# 안쪽 이름표·그림 폴더는 ad- 말고 pick- (광고 차단 프로그램이 ad- 이름을 보고 지웠음). 보이는 표시는 늘 그대로.
LABEL = lambda ad: T("광고", "Ad") if ad.get("paid") else T("추천", "Pick")
REL = lambda ad: "sponsored noopener noreferrer" if ad.get("paid") else "noopener noreferrer"
ADS = [
  dict(id="duk", name="DUK", url="https://duk-hello.pages.dev/", color="#e07b5e",
       ko="멀리 있어도, 같은 층 옆자리.",
       en="Far apart, still at the next desk."),
]

def _ad_items(base=""):
    for ad in ADS:
        if not str(ad.get("url", "")).startswith("https://"): continue
        icon = (f'<img class="pick-icon" src="{R(base)}assets/picks/{ad["id"]}.png" alt="" width="44" height="44">' if os.path.exists(os.path.join(OUT, "assets", "picks", ad["id"] + ".png"))
                else f'<span class="pick-icon pick-letter" aria-hidden="true">{E(ad["name"][:1])}</span>')
        yield ad, icon

AD_NOTE = lambda: T("라군웍스가 만든 앱이 아니에요. 누르면 그 앱의 사이트로 가요.", "Not made by Lagoonworks. Opens the app's own site.")

def ads_card():
    """좁은 화면: 첫 화면 앱 카드 아래 칸 (넓은 화면에선 숨기고 오른쪽 세로 배너 ads_rail 이 대신)."""
    rows = [f'<a class="pick-row" style="--app:{ad.get("color", "#9399a1")}" href="{E(ad["url"])}" target="_blank" rel="{REL(ad)}">{icon}'
            f'<span class="pick-text"><span class="pick-name">{E(ad["name"])}<span class="pick-tag">{LABEL(ad)}</span></span>'
            f'<span class="pick-desc">{E(T(ad["ko"], ad["en"]))}</span></span><span class="pick-go" aria-hidden="true">↗</span></a>' for ad, icon in _ad_items()]
    if not rows: return ""
    return (f'<section class="card pick-card" aria-label="{T("다른 앱 소개", "Other apps")}"><h2>{T("이런 앱도 있어요", "You might also like")}</h2>{"".join(rows)}'
            f'<p class="note">{AD_NOTE()}</p></section>')

def ads_rail(base):
    """넓은 화면(1700 이상): 창 오른쪽 빈자리에 길쭉한 세로 배너 (2026-11-01 현우 '옆의 공간에', '좀 길게, 대표 이미지 잘라서'). 모든 쪽에."""
    cards = []
    for ad, icon in _ad_items(base):
        covers = [n for n in (ad["id"] + "_cover.jpg", ad["id"] + "_cover2.jpg") if os.path.exists(os.path.join(OUT, "assets", "picks", n))]
        # 그림이 둘이면 천천히 번갈아 (2026-11-01 현우 '이 이미지도 같이') — 움직임 줄이기 설정이면 첫 그림만
        art = (f'<span class="rail-art{" two" if len(covers) > 1 else ""}">' + "".join(
                   f'<img class="rail-cover" src="{R(base)}assets/picks/{n}" alt="" width="220" loading="lazy">' for n in covers) + '</span>'
               if covers else '<span class="rail-cover rail-blank" aria-hidden="true"></span>')
        cards.append(f'<a class="rail-pick" style="--app:{ad.get("color", "#9399a1")}" href="{E(ad["url"])}" target="_blank" rel="{REL(ad)}">'
                     f'{art}<span class="pick-tag">{LABEL(ad)}</span><span class="rail-body">{icon}<span class="pick-name">{E(ad["name"])}</span>'
                     f'<span class="pick-desc">{E(T(ad["ko"], ad["en"]))}</span><span class="rail-go">{T("보러 가기", "Visit")} <span aria-hidden="true">↗</span></span></span></a>')
    if not cards: return ""
    return f'<aside class="pick-rail" aria-label="{T("다른 앱 소개", "Other apps")}">{"".join(cards)}<p class="rail-note">{AD_NOTE()}</p></aside>'

def path_of(current):
    """이 쪽의 언어 없는 자리 (한국어 = 맨 위, 영어 = en/ 아래)."""
    return {"home": "", "download": "download/", "notes": "notes/"}.get(current, f"apps/{current}/")

def lang_switch(base, current, cls):
    """Eng | Kor — 지금 쪽과 같은 쪽의 다른 언어로 (2026-10-31 사용자)."""
    p = path_of(current)
    ko = (base + "../" if L == "en" else base) + p
    en = (base if L == "en" else base + "en/") + p
    one = lambda href, label, me, lang: f'<a href="{href or "./"}" hreflang="{lang}" lang="{lang}"{" aria-current=\"true\"" if me else ""}>{label}</a>'
    return f'<nav class="{cls}" aria-label="Language">{one(en, "Eng", L == "en", "en")}{one(ko, "Kor", L == "ko", "ko")}</nav>'

def footer(base):
    """사이트 맨 아래 (2026-10-31 사용자 — 약관·문의 카드를 빼고 꼭 필요한 것만 여기에 모음)."""
    r = R(base)
    apps = "".join(f'<li><a href="{base}apps/{a["id"]}/">{E(a["name"])}</a></li>' for a in APPS)
    return (f'<footer class="site-foot" id="contact"><div class="foot-cols">'
            f'<div class="foot-brand"><p class="foot-name"><img src="{r}assets/icons/overmind.png?v={V["icons"]}" alt="" width="24" height="24">Lagoonworks</p>'
            '<p class="foot-motto">Calm tools, close at hand</p>'
            '<a class="foot-mail" href="mailto:support@lagoonworks.app">support@lagoonworks.app</a></div>'
            f'<div><p class="foot-h">{T("앱", "Apps")}</p><ul>{apps}</ul></div>'
            f'<div><p class="foot-h">{T("내려받기", "Download")}</p><ul><li><a href="{base}download/">{T("모든 앱", "All apps")}</a></li><li><span>Windows 10·11</span></li><li><span>macOS · {T("준비 중", "coming soon")}</span></li></ul></div>'
            f'<div><p class="foot-h">{T("약관", "Legal")}</p><ul><li><a href="{r}legal/terms-{L}.html">{T("이용약관", "Terms of Service")}</a></li><li><a href="{r}legal/privacy-{L}.html">{T("개인정보 처리방침", "Privacy Policy")}</a></li></ul></div>'
            f'<div><p class="foot-h">{T("문의", "Contact")}</p><ul><li><a href="mailto:support@lagoonworks.app">{T("메일 보내기", "Send an email")}</a></li><li><span>{T("앱 문제·약관·개인정보", "App problems, terms, privacy")}</span></li></ul></div>'
            f'</div><div class="foot-bottom"><span>© 2026 Lagoonworks</span><span>{T("지금은 Windows 판을 시험하는 중이에요.", "The Windows versions are in testing.")}</span></div></footer>')

def side(base, current):
    r = R(base)
    cur = lambda c: ' aria-current="page"' if current == c else ""
    nav = [f'<a class="nav-item" href="{base or "./"}"{cur("home")}>{ICON["home"]}{T("처음", "Home")}</a>',
           f'<a class="nav-item" href="{base}download/"{cur("download")}>{ICON["download"]}{T("내려받기", "Download")}</a>',
           f'<div class="nav-label">{T("앱", "Apps")}</div>']
    for a in APPS:
        nav.append(f'<a class="nav-item app" style="--app:{a["color"]}" href="{base}apps/{a["id"]}/"{cur(a["id"])}><span class="app-dot"></span>{E(a["name"])}</a>')
    nav.append(f'<div class="nav-label">{T("정보", "Info")}</div>')
    nav.append(f'<a class="nav-item" href="{base}notes/"{cur("notes")}>{ICON["notes"]}{T("변경점", "Release notes")}</a>')
    nav.append(f'<div class="nav-label">{T("도움", "Help")}</div>')
    nav.append(f'<a class="nav-item" href="{r}legal/{T("", "index-en.html")}">{ICON["legal"]}{T("약관", "Legal")}</a>')
    nav.append(f'<a class="nav-item" href="#contact">{ICON["mail"]}{T("문의", "Contact")}</a>')
    return (f'<aside class="side"><a class="brand" href="{base or "./"}" aria-label="Lagoonworks"><img src="{r}assets/icons/overmind.png?v={V["icons"]}" alt="" width="30" height="30">'
            f'<span class="brand-name">LAGOONWORKS</span></a>{lang_switch(base, current, "lang side-lang")}<nav class="nav">{"".join(nav)}</nav>'
            '<div class="side-foot">© 2026 Lagoonworks</div></aside>')

# 첫 화면 들어올 때 (2026-10-31 사용자): 모토 + 앱마다 봇 카드(둥글게 돌려 넘김) + [들어가기]. 탭마다 한 번.
# JS 가 없으면 html 에 intro-on 이 안 붙어 안 보임 → 사이트가 바로 보임. 움직임 줄이기 설정이면 안 띄움
INTRO_HEAD = """<script>try{if(sessionStorage.getItem("intro")!=="1"&&!matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("intro-on")}catch(e){}</script>"""

def intro():
    cards = "".join(
        f'<div class="ring-card" style="--app:{a["color"]}" data-id="{a["id"]}" data-tint="{a["color"]}"><div class="ring-screen"><canvas></canvas></div>'
        f'<p class="ring-name">{E(a["name"])}</p><p class="ring-desc">{E(T(a["short"], a["short_en"]))}</p></div>' for a in APPS)
    dots = "".join(f'<button class="ring-dot" type="button" aria-label="{E(a["name"])}"></button>' for a in APPS)
    return (f'<div class="intro" id="intro"><p class="intro-brand">Lagoonworks</p><p class="intro-motto">Calm tools, close at hand</p>'
            f'<div class="ring" id="ring" tabindex="0" aria-label="{T("앱 둘러보기", "Browse the apps")}">{cards}</div><div class="ring-dots">{dots}</div>'
            f'<button class="intro-enter" id="intro-enter" type="button">{T("들어가기", "Enter")}</button></div>'
            f'<script type="module">import {{ start }} from "{R("./")}assets/intro.js?v={V["intro.js"]}"; start();</script>')

def shell(base, current, title, desc, tint, on, head, band_html, body, script):
    return f'''<!doctype html>
<html lang="{L}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#1b1c20">
<link rel="preload" href="{R(base)}assets/PretendardVariable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="/favicon.png" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" hreflang="ko" href="https://lagoonworks.app/{path_of(current)}"><link rel="alternate" hreflang="en" href="https://lagoonworks.app/en/{path_of(current)}">
<link rel="stylesheet" href="{R(base)}assets/site.css?v={V["site.css"]}">{INTRO_HEAD if current == "home" else ""}
</head><body style="--accent:{tint};--on-accent:{on}">{intro() if current == "home" else ""}
<div class="window">
{side(base, current)}
<main class="scroll"><div class="page">
<header class="head"><div class="head-act">{lang_switch(base, current, "lang head-lang")}<a class="head-dl" href="{base}download/"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>Download</a></div>{f'<p class="hello">{E(head[0])}</p>' if head[0] else ""}<p class="title">{E(head[1])}{f'<span class="title-en">{E(head[2])}</span>' if len(head) > 2 else ""}</p></header>
<section class="band">{band_html}<div class="screen" id="band"><canvas class="band-sky" id="band-sky" aria-hidden="true"></canvas></div></section>
{body}
{footer(base)}
</div></main>
</div>
{ads_rail(base)}
<script type="module">
{script}
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
band.setVisible(true);
if (still) setTimeout(() => band.setVisible(false), 200);
else document.addEventListener("visibilitychange", () => band.setVisible(!document.hidden));
</script>
</body></html>
'''

def H2(ko, en):
    """카드 제목: 한국어 쪽은 영어를 작게 곁들이고, 영어 쪽은 영어만."""
    return f'<h2>{T(ko, en)}</h2>'

def DESC(a):
    return E(T(a["short"], a["short_en"]))

def BAND_EN(ko_line, en_line):
    """띠의 둘째 줄: 한국어 쪽은 영어 한 줄을 곁들임."""
    return ""      # 한국어 쪽도 영어 줄을 뺌 (2026-10-31 사용자 — 영어는 Eng 쪽에)

def home():
    rows = "".join(
        f'<a class="app-card{' hub' if a["id"] == "overmind" else ''}" style="--app:{a["color"]}" href="apps/{a["id"]}/">{f'<span class="hub-tag">{T("모두를 잇는 섬", "The hub")}</span>' if a["id"] == "overmind" else ''}<img class="app-icon" src="{R("")}assets/icons/{a["id"]}.png?v={V["icons"]}" alt="" width="52" height="52">'
        f'<span class="app-name">{E(a["name"])}</span><span class="app-desc">{DESC(a)}</span>'
        f'<span class="app-more">{T("자세히 보기", "Learn more")}<span aria-hidden="true"> →</span></span></a>' for a in APPS)
    body = f'''<section class="card" id="apps">{H2("앱", "Apps")}<div class="app-grid">{rows}</div></section>{ads_card()}'''
    band = (f'<div class="band-text"><h1>Lagoonworks</h1><p class="band-sub">{T("화면 위 작은 섬과 함께 쓰는 데스크톱 앱들", "Desktop apps that live around a little island on your screen")}</p>'
            + BAND_EN("", "Desktop apps that live around a little island on your screen.") +
            f'<a class="band-btn" href="#apps">{T("앱 둘러보기", "Browse the apps")}</a></div>')
    script = ('import { Band } from "' + R("./") + 'assets/band.js?v=' + V["band.js"] + '";\nconst band = new Band(document.getElementById("band"), document.getElementById("band-sky"));\n'
              'band.setTheme({ tint: "#a78bfa" });')
    return shell("./", "home", "Lagoonworks", T("라군웍스 — OVERMIND · Ovi Family · Parser · Optic · Glen 을 만드는 곳", "Lagoonworks makes OVERMIND, Ovi Family, Parser, Optic and Glen"), "#a78bfa", "#1a1033",
                 ("", "Calm tools, close at hand"), band, body, script)

# 바뀐 것 (2026-10-31 사용자 '패치노트 우리 웹에 게시'): 노치 업데이트 관리와 같은 재료 — 공개 releases 의 family/apps.json 앱마다 history
# (최근 3버전, 새것 먼저, {version, date, summary, lines}). history 가 아직 없으면 가장 최근 노트 폴더(/mnt/project-files/release-notes/노트_*/앱 이름.txt —
# 첫 줄 요약, 아래 바뀐 것)를 그 앱의 지금 버전으로
FEED_ID = {"overmind": "overmind", "ovi-family": "ovi_family", "parser": "parser", "optic": "header_ocr", "glen": "glen"}
NOTE_NAME = {"overmind": "Overmind", "ovi-family": "Ovi Family", "parser": "Parser", "optic": "Optic", "glen": "Glen"}
NOTES_DIR = "/mnt/project-files/release-notes"

def history(out, site_id):
    try:
        with open(os.path.join(out, "family", "apps.json"), encoding="utf-8") as f: feed = json.load(f)
    except (OSError, ValueError):
        return []
    app = next((x for x in feed.get("apps", []) if x.get("id") == FEED_ID[site_id]), None)
    if not app: return []
    if app.get("history"): return app["history"][:3]
    try:
        last = sorted((d for d in os.listdir(NOTES_DIR) if d.startswith("노트_") and d[3:4].isdigit()),
                      key=lambda d: [int(x) if x.isdigit() else 0 for x in d[3:].split(".")])[-1]
        with open(os.path.join(NOTES_DIR, last, NOTE_NAME[site_id] + ".txt"), encoding="utf-8") as f:
            rows = [r.strip() for r in f.read().splitlines() if r.strip()]
    except (OSError, IndexError):
        return []
    return [{"version": app["version"], "date": feed.get("made", "")[:10], "summary": rows[0], "lines": rows[1:]}] if rows else []

# 다음 버전 미리 보기 (2026-10-31 사용자 '변경된 게 많아서 지금 페이지에도') — 노트_다음/<앱 이름>.txt (첫 줄 요약, 아래 바뀐 것).
# 배포하는 날 이 폴더의 글을 노트_<버전> 으로 옮기면 '준비 중' 칸은 사라지고 최신 판이 됨
UPCOMING = {}

def upcoming(site_id):
    try:
        with open(os.path.join(NOTES_DIR, "노트_다음", NOTE_NAME[site_id] + ".txt"), encoding="utf-8") as f:
            rows = [r.strip() for r in f.read().splitlines() if r.strip()]
    except OSError:
        return None
    return {"summary": rows[0], "lines": rows[1:]} if rows else None

def notes_html(hist, up=None):
    """최신 판은 펼쳐 보이고, 그 아래 '이전 패치 노트'는 버전마다 눌러 펼침 (2026-10-31 사용자)."""
    if not hist and not up: return ""
    def body(h):
        return f'<p class="note-sum">{E(h.get("summary", ""))}</p><ul>{"".join(f"<li>{E(l)}</li>" for l in h.get("lines", []))}</ul>'
    soon = (f'<div class="note-ver soon"><p class="note-head"><span class="note-v">{T("다음 버전", "Next version")}</span>'
            f'<span class="note-new soon">{T("준비 중", "Coming soon")}</span></p>{body(up)}</div>') if up else ""
    if not hist:
        return (f'<section class="card" id="notes">{H2("바뀐 것", "What&#39;s new")}<div class="notes">{soon}</div></section>')
    top = hist[0]
    now = (f'<div class="note-ver now"><p class="note-head"><span class="note-v">{E(top.get("version", ""))}</span><span class="note-d">{E(top.get("date", ""))}</span>'
           f'<span class="note-new">{T("최신", "Latest")}</span></p>{body(top)}</div>')
    old = "".join(f'<details class="note-old"><summary><span class="note-v">{E(h.get("version", ""))}</span><span class="note-d">{E(h.get("date", ""))}</span>'
                  f'<span class="note-peek">{E(h.get("summary", ""))}</span></summary>{body(h)}</details>' for h in hist[1:])
    old = old or f'<p class="note-none">{T("아직 이전 버전이 없어요.", "No earlier versions yet.")}</p>'
    ko_only = "" if L == "ko" else '<p class="note-lang">Release notes are written in Korean for now.</p>'
    return (f'<section class="card" id="notes">{H2("바뀐 것", "What&#39;s new")}<div class="notes">{ko_only}{soon}{now}'
            f'<p class="note-old-h">{T("이전 패치 노트", "Earlier versions")}</p>{old}</div></section>')

def app_page(a):
    r = R("../../")
    en = EN[a["id"]]
    feats = "".join(f'<div class="feat"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in (a["feats"] if L == "ko" else en["feats"]))
    others = "".join(f'<a class="chip" style="--app:{o["color"]}" href="../{o["id"]}/"><img class="chip-icon" src="{r}assets/icons/{o["id"]}.png?v={V["icons"]}" alt="" width="20" height="20">{E(o["name"])}</a>'
                     for o in APPS if o["id"] != a["id"])
    dl = (f'<a class="chip on" style="--app:{a["color"]}" href="{E(DOWNLOAD[a["id"]])}">{T("Windows 용 내려받기", "Download for Windows")}</a>' if DOWNLOAD.get(a["id"])
          else f'<span class="chip off" title="{T("곧 열려요", "Coming soon")}">{T("내려받기 · 준비 중", "Download · coming soon")}</span>')
    priv = T(PRIVACY.get(a["id"], PRIVACY["ai"]), PRIVACY_EN.get(a["id"], PRIVACY_EN["ai"]))
    more = T(f'자세한 것은 <a href="{r}legal/privacy-ko.html">개인정보 처리방침</a>에 있어요.', f'See the <a href="{r}legal/privacy-en.html">Privacy Policy</a> for details.')
    body = f"""<section class="card"><p class="lead">{E(T(a["intro"], en["intro"]))}</p>
<div class="chips">{dl}<span class="chip ghost">Windows 10·11{"" if DOWNLOAD.get(a["id"]) else " · " + T("시험 중", "in testing")}</span><span class="chip ghost">macOS · {T("준비 중", "coming soon")}</span></div></section>
<section class="card" id="features">{H2("할 수 있는 것", "Features")}<div class="feats">{feats}</div></section>
<section class="card">{H2("안심하고 쓰도록", "Privacy")}
<p class="note">{E(priv)} {more}</p></section>
{notes_html(HIST.get(a["id"], []), UPCOMING.get(a["id"]))}
<section class="card">{H2("다른 가족 앱", "Family")}<div class="chips">{others}</div></section>"""
    band = (f'<div class="band-text"><p class="band-kicker"><img class="kicker-icon" src="{r}assets/icons/{a["id"]}.png?v={V["icons"]}" alt="" width="28" height="28">{E(a["name"])}</p><h1>{E(T(a["ko"], a["en"]))}</h1>'
            + BAND_EN("", a["en"]) + f'<a class="band-btn" href="#features">{T("할 수 있는 것 보기", "See the features")}</a></div>')
    if a["id"] == "overmind":
        script = ('import { Band } from "' + r + 'assets/band.js?v=' + V["band.js"] + '";\nconst band = new Band(document.getElementById("band"), document.getElementById("band-sky"));\n'
                  f'band.setTheme({{ tint: "{a["color"]}" }});')
    else:
        script = ('import { Band } from "' + r + 'assets/appband.js?v=' + V["appband.js"] + '";\n'
                  f'const band = new Band(document.getElementById("band"), document.getElementById("band-sky"), "{a["color"]}");')
    return shell("../../", a["id"], f'{a["name"]} · Lagoonworks', f'{a["name"]} — {T(a["ko"], a["en"])}', a["color"], a["on"],
                 ("", a["name"]), band, body, script)

def download():
    """내려받기 쪽 (2026-10-31 사용자). 앱을 공개하기 전이라 단추는 '준비 중' — 공개할 때 DOWNLOAD 에 주소를 넣으면 단추가 켜짐."""
    r = R("../")
    def card(a, wide=False):
        url = DOWNLOAD.get(a["id"])
        btn = (f'<a class="dl-btn" href="{E(url)}">{T("Windows 용 내려받기", "Download for Windows")}</a>' if url else f'<span class="dl-btn off">{T("곧 열려요", "Coming soon")}</span>')
        tag = f'<span class="hub-tag">{T("추천", "Recommended")}</span>' if wide else ''
        return (f'<div class="dl-card{" hub" if wide else ""}" style="--app:{a["color"]}">{tag}<img class="app-icon" src="{r}assets/icons/{a["id"]}.png?v={V["icons"]}" alt="" width="52" height="52">'
                f'<p class="app-name">{E(a["name"])}</p><p class="app-desc">{DESC(a)}</p>'
                f'<div class="dl-os"><span class="chip ghost">Windows 10·11</span><span class="chip ghost">macOS · {T("준비 중", "coming soon")}</span></div>{btn}</div>')
    fam = next(a for a in APPS if a["id"] == "ovi-family")
    terms = f'{r}legal/terms-{L}.html'
    one = T('Ovi Family 하나만 설치하면 다른 앱을 골라 설치하고 새 버전도 알려 줘요.',
            'Install Ovi Family to pick the other apps and keep them up to date.')
    before = T(f'지금은 Windows 판을 시험하는 중이에요. 설치하면 <a href="{terms}">이용약관</a>에 동의하는 거예요. 앱은 무료이고, 앞으로 광고나 유료 구독이 생기면 30일 전에 알려요.',
               f'Windows builds are in testing. Installing means you accept the <a href="{terms}">Terms of Service</a>. The apps are free; any ads or paid plans will be announced 30 days ahead.')
    body = (f'<section class="card" id="all">{H2("한 번에 받기", "All apps")}<div class="dl-grid one">{card(fam, True)}</div>'
            f'<p class="note">{one}</p></section>'
            f'<section class="card">{H2("앱마다 받기", "Each app")}<div class="dl-grid">{"".join(card(a) for a in APPS if a["id"] != "ovi-family")}</div></section>'
            f'<section class="card">{H2("설치하기 전에", "Before you install")}<p class="note">{before}</p></section>')
    band = (f'<div class="band-text"><p class="band-kicker">Download</p><h1>{T("앱 내려받기", "Get the apps")}</h1>'
            + BAND_EN("", "Get the Lagoonworks apps for your computer.") + f'<a class="band-btn" href="#all">{T("Ovi Family 로 한 번에", "All at once with Ovi Family")}</a></div>')
    script = ('import { Band } from "' + r + 'assets/band.js?v=' + V["band.js"] + '";\nconst band = new Band(document.getElementById("band"), document.getElementById("band-sky"));\n'
              'band.setTheme({ tint: "#a78bfa" });')
    return shell("../", "download", T("내려받기", "Download") + " · Lagoonworks", T("라군웍스 앱 내려받기", "Download the Lagoonworks apps"), "#a78bfa", "#1a1033", ("", "Download"), band, body, script)

def notes_page():
    """정보 → 변경점 (2026-10-31 사용자 '한번에 볼 수 있게'): 모든 앱의 바뀐 것을 한 쪽에. 재료는 앱 쪽과 같음 (HIST)."""
    r = R("../")
    jump = "".join(f'<a class="chip note-tab" style="--app:{a["color"]};--on:{a["on"]}" data-app="{a["id"]}" href="#{a["id"]}"><img class="chip-icon" src="{r}assets/icons/{a["id"]}.png?v={V["icons"]}" alt="" width="20" height="20">{E(a["name"])}</a>' for a in APPS)
    blocks = "".join(
        f'<section class="card notes-app" id="{a["id"]}" style="--app:{a["color"]}"><h2 class="notes-title"><img class="chip-icon" src="{r}assets/icons/{a["id"]}.png?v={V["icons"]}" alt="" width="24" height="24">'
        f'<a href="../apps/{a["id"]}/">{E(a["name"])}</a></h2>'
        + (notes_html(HIST.get(a["id"], []), UPCOMING.get(a["id"])).split('<div class="notes">', 1)[1].rsplit("</section>", 1)[0].join(['<div class="notes">', '']) if HIST.get(a["id"]) or UPCOMING.get(a["id"]) else f'<p class="note">{T("아직 적힌 변경점이 없어요.", "No release notes yet.")}</p>')
        + '</section>' for a in APPS)
    body = f'<section class="card"><div class="chips" role="tablist">{jump}</div></section><div class="note-panels">{blocks}</div>'
    band = (f'<div class="band-text"><p class="band-kicker">Release notes</p><h1>{T("변경점", "What changed")}</h1>'
            + BAND_EN("", "What changed in each app, newest first.") + '</div>')
    script = ('import { Band } from "' + r + 'assets/band.js?v=' + V["band.js"] + '";\nconst band = new Band(document.getElementById("band"), document.getElementById("band-sky"));\n'
              'band.setTheme({ tint: "#a78bfa" });\n'
              # 앱 단추 = 탭: 누른 앱의 변경점만 보임 (2026-10-31 사용자). 주소 끝 #parser 로도. JS 가 없으면 모두 보임
              'const tabs = [...document.querySelectorAll(".note-tab")], panels = [...document.querySelectorAll(".notes-app")];\n'
              'function pick(id, push) { if (!panels.some((p) => p.id === id)) id = panels[0].id;\n'
              '  panels.forEach((p) => p.hidden = p.id !== id); tabs.forEach((t) => t.setAttribute("aria-selected", t.dataset.app === id));\n'
              '  if (push) history.replaceState(null, "", "#" + id); }\n'
              'tabs.forEach((t) => t.addEventListener("click", (e) => { e.preventDefault(); pick(t.dataset.app, true); }));\n'
              'addEventListener("hashchange", () => pick(location.hash.slice(1)));\n'
              'pick(location.hash.slice(1));')
    return shell("../", "notes", T("변경점", "Release notes") + " · Lagoonworks", T("라군웍스 앱 변경점", "Lagoonworks release notes"), "#a78bfa", "#1a1033", ("", "Release notes"), band, body, script)

# 내려받기 단추 (2026-10-31): DOWNLOAD_OPEN 을 True 로 하면 family/apps.json 의 설치 파일 주소로 단추가 켜짐 — 새 판을 올리면 저절로 새 주소.
# False 면 '곧 열려요'
DOWNLOAD_OPEN = False
DOWNLOAD = {}

def load_download(out):
    if not DOWNLOAD_OPEN: return
    try:
        with open(os.path.join(out, "family", "apps.json"), encoding="utf-8") as f: feed = json.load(f)
    except (OSError, ValueError):
        return
    for a in APPS:
        app = next((x for x in feed.get("apps", []) if x.get("id") == FEED_ID[a["id"]]), None)
        if app and str(app.get("url", "")).startswith("https://"): DOWNLOAD[a["id"]] = app["url"]

def main(out):
    global OUT
    OUT = out
    for n in ("site.css", "band.js", "appband.js", "intro.js"):
        with open(os.path.join(out, "assets", n), "rb") as f: V[n] = hashlib.sha1(f.read()).hexdigest()[:8]
    h = hashlib.sha1()
    for a in APPS:
        with open(os.path.join(out, "assets", "icons", a["id"] + ".png"), "rb") as f: h.update(f.read())
    V["icons"] = h.hexdigest()[:8]
    load_download(out)
    arch_path = os.path.join(out, "notes", "archive.json")
    try:
        with open(arch_path, encoding="utf-8") as f: arch = json.load(f)
    except (OSError, ValueError):
        arch = {}
    for a in APPS:
        UPCOMING[a["id"]] = upcoming(a["id"])
    for a in APPS:
        seen = {h["version"]: h for h in arch.get(a["id"], [])}
        for h in history(out, a["id"]): seen[h["version"]] = h        # 새 글이 이김
        HIST[a["id"]] = arch[a["id"]] = sorted(seen.values(), key=lambda h: [int(x) if x.isdigit() else 0 for x in h["version"].split(".")], reverse=True)
    os.makedirs(os.path.dirname(arch_path), exist_ok=True)
    with open(arch_path, "w", encoding="utf-8") as f: json.dump(arch, f, ensure_ascii=False, indent=1)
    global L
    for L in ("ko", "en"):
        root = out if L == "ko" else os.path.join(out, "en")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f: f.write(home())
        for a in APPS:
            d = os.path.join(root, "apps", a["id"]); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f: f.write(app_page(a))
        for name, make in (("notes", notes_page), ("download", download)):
            os.makedirs(os.path.join(root, name), exist_ok=True)
            with open(os.path.join(root, name, "index.html"), "w", encoding="utf-8") as f: f.write(make())
    L = "ko"
    print("made", 2 * (3 + len(APPS)), "pages (ko + en) in", out)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
