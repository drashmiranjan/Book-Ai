"""Gyan Book AI - Streamlit front end (single file: run with `streamlit run app.py`).

Talks to a FastAPI backend:
    POST {API_URL}/chat  {"question": str, "book": str}
    ->   {"answer": str, "sources": [str | {...}]}
    GET  {API_URL}/health (optional, used for the status indicator)
"""

from __future__ import annotations

import html
import os
import time
from datetime import datetime

import requests
import streamlit as st

# ============================================================ CONFIG
# Theme is set in code so this app works as a single file (no .streamlit/config.toml).
try:
    for _key, _val in {
        "theme.base": "dark",
        "theme.primaryColor": "#E8A33D",
        "theme.backgroundColor": "#0E1322",
        "theme.secondaryBackgroundColor": "#141A2E",
        "theme.textColor": "#E9E7E0",
        "client.toolbarMode": "minimal",
    }.items():
        st._config.set_option(_key, _val)
except Exception:  # private API; CSS below still enforces the look
    pass

st.set_page_config(
    page_title="Gyan Book AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("API_TIMEOUT", "120"))

BOOKS: dict[str, str] = {
    "All books": "all",
    "Ramayan": "ramayan",
    "Srimad Bhagavad Gita": "bhagavad_gita",
}
SLUG_TO_LABEL = {slug: label for label, slug in BOOKS.items()}

BOOK_META = {
    "Ramayan": {
        "glyph": "🏹",
        "blurb": "The journey of Rama: dharma, courage, devotion and leadership.",
        "size": "About 1,960 pages",
    },
    "Srimad Bhagavad Gita": {
        "glyph": "🪷",
        "blurb": "Krishna and Arjuna on duty, action, wisdom and inner peace.",
        "size": "About 952 pages",
    },
}

SUGGESTIONS = {
    "All books": [
        "What is dharma?",
        "Explain the importance of karma",
        "How do the Gita and Ramayan treat duty?",
        "What does devotion mean in these texts?",
    ],
    "Ramayan": [
        "What can I learn from Lord Rama?",
        "Why did Rama accept exile?",
        "Describe Hanuman's role in the story",
        "What does the Ramayan say about loyalty?",
    ],
    "Srimad Bhagavad Gita": [
        "What does Krishna teach about fear?",
        "Explain karma yoga",
        "What is a person of steady wisdom?",
        "How should I act without attachment?",
    ],
}

# ============================================================ STYLE
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Noto+Serif+Devanagari:wght@400;600&display=swap');

:root {
  --bg:        #0E1322;
  --surface:   #141A2E;
  --surface-2: #1B2340;
  --line:      #2A3354;
  --text:      #E9E7E0;
  --muted:     #9AA3BD;
  --accent:    #E8A33D;
  --accent-ink:#1A1304;
  --ok:        #5FBF8F;
  --err:       #E5707E;
  --serif: 'Newsreader','Noto Serif Devanagari',Georgia,serif;
  --sans:  'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}

html, body, [data-testid="stAppViewContainer"], .stApp { font-family: var(--sans); color-scheme: dark; }
.stApp, .stApp label, .stApp p, .stApp li, .stApp span, .stApp summary,
.stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stMarkdownContainer"] { color: var(--text); }
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * { color: var(--muted); }
[data-testid="stToggle"] [role="switch"][aria-checked="true"], [data-testid="stToggle"] input:checked + div { background-color: var(--accent); }
div[data-testid="stChatInput"] textarea { color: var(--text); background: transparent; }
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"] { background: transparent; }
footer, #MainMenu { visibility: hidden; }
.block-container { max-width: 880px; padding: 2.2rem 1.5rem 7rem; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding: 1.6rem 1.1rem; }
.brand { display:flex; align-items:center; gap:.65rem; }
.brand-mark {
  width: 36px; height: 36px; border-radius: 9px; display:grid; place-items:center;
  background: var(--accent); color: var(--accent-ink); font-size: 1.15rem;
}
.brand-name { font-family: var(--serif); font-size: 1.35rem; font-weight: 600; line-height: 1.1; }
.brand-sub  { color: var(--muted); font-size: .8rem; margin-top: 2px; }
.side-title { font-size: .8rem; font-weight: 600; color: var(--muted); margin: 1.4rem 0 .4rem; letter-spacing: .01em; }

[data-testid="stSidebar"] [role="radiogroup"] { gap: .35rem; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
  padding: .6rem .8rem; border: 1px solid var(--line); border-radius: 8px;
  background: transparent; transition: border-color .15s, background .15s; width: 100%;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover { border-color: var(--muted); }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
  border-color: var(--accent); background: rgba(232,163,61,.10);
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display: none; }

.status { display:inline-flex; align-items:center; gap:.45rem; font-size:.8rem; color: var(--muted); }
.dot { width:8px; height:8px; border-radius:50%; background: var(--muted); }
.dot.ok  { background: var(--ok);  box-shadow: 0 0 0 3px rgba(95,191,143,.18); }
.dot.err { background: var(--err); box-shadow: 0 0 0 3px rgba(229,112,126,.18); }

.dev { font-size: .85rem; line-height: 1.6; color: var(--muted); }
.dev b { color: var(--text); font-weight: 600; }
.dev a { color: var(--accent); text-decoration: none; }
.dev a:hover { text-decoration: underline; }

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button {
  font-family: var(--sans); font-weight: 500; border-radius: 8px;
  border: 1px solid var(--line); background: var(--surface-2); color: var(--text);
  transition: border-color .15s, background .15s;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--accent); color: var(--text); background: #222C50;
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:focus-visible) {
  outline: 2px solid var(--accent); outline-offset: 2px;
}
.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }

/* ---------- top bar ---------- */
.scope { display:flex; align-items:center; gap:.6rem; color: var(--muted); font-size:.88rem; margin-bottom: 1.4rem; }
.scope b { color: var(--text); font-weight: 600; }
.chip {
  display:inline-flex; align-items:center; gap:.4rem; padding:.22rem .65rem;
  border:1px solid var(--line); border-radius: 999px; color: var(--text); font-size:.82rem;
}

/* ---------- empty state ---------- */
.intro h1 {
  font-family: var(--serif); font-weight: 500; font-size: clamp(2rem, 4.2vw, 2.9rem);
  line-height: 1.12; letter-spacing: -0.02em; margin: .6rem 0 .8rem; max-width: 16ch;
}
.intro p { color: var(--muted); max-width: 58ch; line-height: 1.7; font-size: 1.02rem; margin-bottom: 1.8rem; }
.lib { display:grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: 1rem; margin-bottom: 2rem; }
.lib-item { border:1px solid var(--line); border-radius: 12px; padding: 1.1rem 1.2rem; background: var(--surface); }
.lib-item .g { font-size: 1.5rem; }
.lib-item h3 { font-family: var(--serif); font-size: 1.2rem; font-weight: 600; margin: .35rem 0 .25rem; }
.lib-item p  { color: var(--muted); font-size: .88rem; line-height: 1.55; margin: 0 0 .6rem; }
.lib-item small { color: var(--muted); font-size: .78rem; }
.sec-title { font-size: .85rem; font-weight: 600; color: var(--muted); margin: 0 0 .6rem; }

/* ---------- chat ---------- */
div[data-testid="stChatMessage"] { background: transparent; border: 0; padding: .6rem 0; }
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .8rem 1rem;
  margin-top: 1.2rem;
}
div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] li {
  font-family: var(--serif); font-size: 1.08rem; line-height: 1.75; max-width: 72ch;
}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
  font-family: var(--sans); font-size: .98rem; line-height: 1.6;
}
.meta { color: var(--muted); font-size: .78rem; margin-top: .3rem; }

.src {
  border:1px solid var(--line); border-left: 3px solid var(--accent); border-radius: 8px;
  padding: .7rem .9rem; margin: .5rem 0; background: var(--surface);
}
.src-title { font-size: .85rem; font-weight: 600; margin-bottom: .2rem; }
.src-text  { font-family: var(--serif); font-size: .95rem; line-height: 1.6; color: var(--muted); }

[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 10px; background: transparent; }
[data-testid="stExpander"] summary { font-size: .9rem; }

div[data-testid="stChatInput"] { border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
div[data-testid="stChatInput"]:focus-within { border-color: var(--accent); }

@media (max-width: 640px) { .block-container { padding: 1.4rem 1rem 7rem; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================ STATE
st.session_state.setdefault("messages", [])
st.session_state.setdefault("selected_book", "All books")
st.session_state.setdefault("show_sources", True)
st.session_state.setdefault("pending_question", None)


# ============================================================ HELPERS
@st.cache_resource
def http() -> requests.Session:
    return requests.Session()


@st.cache_data(ttl=15, show_spinner=False)
def backend_online(url: str) -> bool:
    for path in ("/health", "/docs"):
        try:
            if requests.get(url + path, timeout=2).status_code < 500:
                return True
        except requests.RequestException:
            continue
    return False


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def ask_backend(question: str, book_slug: str) -> dict:
    started = time.perf_counter()
    try:
        resp = http().post(
            f"{API_URL}/chat",
            json={"question": question, "book": book_slug},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "ok": True,
            "answer": data.get("answer") or "The backend returned an empty answer.",
            "sources": data.get("sources") or [],
            "latency": time.perf_counter() - started,
        }
    except requests.exceptions.ConnectionError:
        err = f"Can't reach the backend at {API_URL}. Start the FastAPI server and try again."
    except requests.exceptions.Timeout:
        err = f"The backend took longer than {REQUEST_TIMEOUT} seconds to respond. Try a shorter question."
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else "unknown"
        err = f"The backend returned an error (HTTP {code}). Check the server logs."
    except ValueError:
        err = "The backend sent a response that isn't valid JSON."
    except requests.RequestException as exc:
        err = f"The request failed: {exc}"
    return {"ok": False, "answer": err, "sources": [], "latency": time.perf_counter() - started}


def render_sources(sources: list) -> None:
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        for item in sources:
            if isinstance(item, dict):
                book = SLUG_TO_LABEL.get(item.get("book", ""), item.get("book") or item.get("source") or "Source")
                where = ", ".join(
                    f"{k.capitalize()} {item[k]}" for k in ("chapter", "verse", "page") if item.get(k) not in (None, "")
                )
                title = f"{book} ({where})" if where else str(book)
                text = item.get("text") or item.get("content") or item.get("snippet") or ""
                text = (text[:420] + "...") if len(text) > 420 else text
            else:
                title, text = "Passage", str(item)
                text = (text[:420] + "...") if len(text) > 420 else text
            st.markdown(
                f'<div class="src"><div class="src-title">{esc(title)}</div>'
                f'<div class="src-text">{esc(text)}</div></div>',
                unsafe_allow_html=True,
            )


def render_assistant(msg: dict) -> None:
    if msg.get("error"):
        st.error(msg["content"])
    else:
        st.markdown(msg["content"])
        if st.session_state.show_sources:
            render_sources(msg.get("sources", []))
        scope = SLUG_TO_LABEL.get(msg.get("book", "all"), "your books")
        st.markdown(
            f'<div class="meta">Searched {esc(scope.lower())} in {msg.get("latency", 0):.1f} s</div>',
            unsafe_allow_html=True,
        )


def transcript_markdown() -> str:
    lines = ["# Gyan Book AI conversation", f"_Exported {datetime.now():%Y-%m-%d %H:%M}_", ""]
    for m in st.session_state.messages:
        who = "You" if m["role"] == "user" else "Gyan Book AI"
        lines += [f"**{who}**", "", m["content"], ""]
    return "\n".join(lines)


def queue_question(text: str) -> None:
    st.session_state.pending_question = text


# ============================================================ SIDEBAR
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">📚</div>'
        '<div><div class="brand-name">Gyan Book AI</div>'
        '<div class="brand-sub">Answers grounded in the texts</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-title">Knowledge source</div>', unsafe_allow_html=True)
    st.radio(
        "Knowledge source",
        list(BOOKS.keys()),
        key="selected_book",
        label_visibility="collapsed",
    )

    st.markdown('<div class="side-title">Conversation</div>', unsafe_allow_html=True)
    if st.button("New conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()
    st.toggle("Show sources", key="show_sources")
    if st.session_state.messages:
        st.download_button(
            "Download transcript",
            transcript_markdown(),
            file_name="gyan-book-ai-conversation.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown('<div class="side-title">Backend</div>', unsafe_allow_html=True)
    online = backend_online(API_URL)
    st.markdown(
        f'<span class="status"><span class="dot {"ok" if online else "err"}"></span>'
        f'{"Connected" if online else "Unreachable"}</span>',
        unsafe_allow_html=True,
    )
    st.caption(API_URL)

    st.markdown('<div class="side-title">Developer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dev"><b>Rashmi Ranjan Das</b><br>'
        '<a href="https://github.com/drashmiranjan" target="_blank" rel="noopener">GitHub</a> and '
        '<a href="https://drashmiranjan.vercel.app/" target="_blank" rel="noopener">Portfolio</a><br>'
        "Built with Python, FastAPI, LangChain and Streamlit.</div>",
        unsafe_allow_html=True,
    )

selected_label = st.session_state.selected_book
selected_slug = BOOKS[selected_label]

# ============================================================ INPUT (resolved first, pinned to bottom by Streamlit)
typed = st.chat_input(f"Ask about {selected_label.lower()}...")
question = typed or st.session_state.pop("pending_question", None)

# ============================================================ TOP BAR
st.markdown(
    f'<div class="scope">Searching <span class="chip">{esc(selected_label)}</span></div>',
    unsafe_allow_html=True,
)

# ============================================================ EMPTY STATE
if not st.session_state.messages and not question:
    st.markdown(
        '<div class="intro"><h1>Ask the texts a question.</h1>'
        "<p>Get answers drawn from the Ramayan and the Bhagavad Gita, with the "
        "passages behind each answer so you can read them in context.</p></div>",
        unsafe_allow_html=True,
    )

    cards = "".join(
        f'<div class="lib-item"><div class="g">{m["glyph"]}</div><h3>{esc(name)}</h3>'
        f'<p>{esc(m["blurb"])}</p><small>{esc(m["size"])}</small></div>'
        for name, m in BOOK_META.items()
    )
    st.markdown(f'<div class="lib">{cards}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Try asking</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, text in enumerate(SUGGESTIONS[selected_label]):
        with cols[i % 2]:
            st.button(text, key=f"s_{selected_label}_{i}", use_container_width=True,
                      on_click=queue_question, args=(text,))

# ============================================================ HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🪷" if msg["role"] == "assistant" else None):
        if msg["role"] == "assistant":
            render_assistant(msg)
        else:
            st.markdown(msg["content"])

# ============================================================ NEW TURN
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🪷"):
        with st.spinner(f"Searching {selected_label.lower()}..."):
            result = ask_backend(question, selected_slug)
        reply = {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "latency": result["latency"],
            "book": selected_slug,
            "error": not result["ok"],
        }
        render_assistant(reply)

    st.session_state.messages.append(reply)