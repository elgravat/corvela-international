"""
app.py: Streamlit UI for Vela — Corvela International's AI insurance guide
Run with: streamlit run app.py
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Vela · Corvela International",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Brand tokens
# ---------------------------------------------------------------------------

NAVY        = "#1B2A4A"
NAVY_MID    = "#243352"
NAVY_LIGHT  = "#2D3E60"
AMBER       = "#E8A23A"
AMBER_DARK  = "#C8831A"
MIST        = "#F5F7FA"
BORDER      = "#E2E5EB"
TEXT_MAIN   = "#1A202C"
TEXT_MUTED  = "#64748B"
WHITE       = "#FFFFFF"

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
  /* ---- Page shell ---- */
  .stApp {{ background: {MIST}; }}
  [data-testid="stAppViewContainer"] > .main {{ padding-top: 0; }}

  /* ---- Hide default Streamlit chrome ---- */
  header[data-testid="stHeader"],
  [data-testid="stToolbar"] {{ display: none !important; }}
  .stDeployButton {{ display: none !important; }}

  /* ---- Sidebar ---- */
  [data-testid="stSidebar"] {{
    background: {NAVY} !important;
    border-right: none;
  }}
  [data-testid="stSidebar"] section {{
    background: {NAVY} !important;
  }}
  /* Override all sidebar text to light */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] li,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] .stCaption {{
    color: rgba(255,255,255,0.65) !important;
  }}
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] strong {{
    color: {WHITE} !important;
  }}
  [data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.12) !important;
  }}
  /* Sidebar button */
  [data-testid="stSidebar"] .stButton > button {{
    background: transparent;
    color: {WHITE} !important;
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 8px;
    width: 100%;
    font-size: 13px;
    transition: background 0.15s, border-color 0.15s;
  }}
  [data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.45);
  }}

  /* ---- Chat messages ---- */
  [data-testid="stChatMessage"] {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 6px 4px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  /* User messages get a subtle amber-tinted background */
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: #FFFBF3;
    border-color: {AMBER}44;
  }}

  /* ---- Links inside chat (quote buttons) ---- */
  [data-testid="stChatMessage"] a {{
    display: inline-block;
    margin-top: 10px;
    background: {NAVY};
    color: {WHITE} !important;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 18px;
    border-radius: 8px;
    text-decoration: none !important;
    transition: background 0.15s;
  }}
  [data-testid="stChatMessage"] a:hover {{
    background: {NAVY_MID};
  }}

  /* ---- Chat input ---- */
  [data-testid="stChatInput"] {{
    border-radius: 12px;
    background: {WHITE};
    border: 1.5px solid {BORDER};
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  [data-testid="stChatInput"]:focus-within {{
    border-color: {AMBER};
    box-shadow: 0 0 0 3px {AMBER}28, 0 2px 8px rgba(0,0,0,0.06);
  }}
  [data-testid="stChatInput"] textarea {{
    font-size: 15px;
    color: {TEXT_MAIN};
  }}
  [data-testid="stChatInput"] button {{
    background: {NAVY} !important;
    border-radius: 8px !important;
  }}
  [data-testid="stChatInput"] button:hover {{
    background: {NAVY_MID} !important;
  }}

  /* ---- Vela header card ---- */
  .vela-header {{
    background: linear-gradient(130deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
    border-radius: 16px;
    padding: 22px 26px;
    margin: 20px 0 20px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .vela-header .av {{
    font-size: 34px;
    line-height: 1;
    flex-shrink: 0;
  }}
  .vela-header .copy {{ flex: 1; }}
  .vela-header .title {{
    font-size: 20px;
    font-weight: 700;
    color: {WHITE};
    margin: 0;
    line-height: 1.2;
  }}
  .vela-header .sub {{
    font-size: 12px;
    color: rgba(255,255,255,0.58);
    margin: 3px 0 0;
  }}
  .vela-header .badge {{
    background: {AMBER};
    color: {NAVY};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
    white-space: nowrap;
    flex-shrink: 0;
  }}

  /* ---- Spinner text ---- */
  .stSpinner p {{ color: {TEXT_MUTED} !important; font-size: 14px; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Greeting (hardcoded — no API cost on page load)
# ---------------------------------------------------------------------------

VELA_GREETING = """\
Hi! I'm **Vela**, your Corvela International insurance guide.

I can help you compare and choose between our two contracted carriers — \
**Cigna Global** and **IMG Global** (Patriot plans) — based on your specific situation.

I'll ask you a few quick questions, give you a plain-English recommendation, \
and send you straight to a quote.

To get started: are you looking for **short-term travel medical insurance** \
(for a trip), or **international health insurance** (for living or working abroad \
long-term)?\
"""

# ---------------------------------------------------------------------------
# Session state — bot is created once per session
# ---------------------------------------------------------------------------

if "initialized" not in st.session_state:
    try:
        from chatbot import VelaChatbot
        with st.spinner("Loading plan documents…"):
            _bot = VelaChatbot()
        # Seed history with the greeting so Vela has context on first reply
        _bot.history.append({"role": "assistant", "content": VELA_GREETING})
        st.session_state.bot = _bot
        st.session_state.messages = [
            {"role": "assistant", "content": VELA_GREETING}
        ]
        st.session_state.initialized = True
    except EnvironmentError as exc:
        st.error(f"**Configuration error:** {exc}")
        st.info("Set your `ANTHROPIC_API_KEY` environment variable, then restart the app.")
        st.stop()
    except FileNotFoundError as exc:
        st.error(f"**Missing plan document:** {exc}")
        st.info("Check that all three PDFs are present in the `Docs/` folder.")
        st.stop()
    except Exception as exc:
        st.error(f"**Failed to start Vela:** {exc}")
        st.stop()

bot = st.session_state.bot

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## Vela")
    st.markdown(
        "An AI guide for **Corvela International**, an independent health "
        "insurance broker based in Austin, Texas."
    )
    st.divider()

    st.markdown("**Carriers I know**")
    st.markdown(
        "- **Cigna Global** — international health\n"
        "- **IMG Patriot Lite** — travel medical\n"
        "- **IMG Patriot Platinum** — travel medical (premium)"
    )
    st.divider()

    st.markdown("**What I can help with**")
    st.markdown(
        "- Comparing plans side by side\n"
        "- Understanding benefits, exclusions & networks\n"
        "- Matching the right plan to your situation\n"
        "- Getting a direct broker quote link"
    )
    st.divider()

    if st.button("↺  New conversation"):
        bot.reset()
        bot.history.append({"role": "assistant", "content": VELA_GREETING})
        st.session_state.messages = [
            {"role": "assistant", "content": VELA_GREETING}
        ]
        st.rerun()

    st.divider()
    st.caption(
        "Vela answers only from plan documents and never quotes specific premiums. "
        "For complex situations, ask to be connected with Jeff at hello@corvela.com."
    )

# ---------------------------------------------------------------------------
# Main — brand header
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="vela-header">
      <div class="av">🌊</div>
      <div class="copy">
        <p class="title">Vela</p>
        <p class="sub">Corvela International · Insurance Guide</p>
      </div>
      <span class="badge">AI · Powered</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Conversation display
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    role   = msg["role"]
    avatar = "🌊" if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input + streaming response
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Ask Vela about international health insurance…"):
    # ---- User turn ----
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # ---- Vela's reply — streamed ----
    with st.chat_message("assistant", avatar="🌊"):
        try:
            full_reply = st.write_stream(bot.stream_chat(prompt))
        except Exception as exc:
            err_msg = (
                "I ran into a problem fetching a response. "
                f"Please try again or contact Jeff at hello@corvela.com. "
                f"*(Error: {exc})*"
            )
            st.markdown(err_msg)
            full_reply = err_msg
            # Roll back the user message from bot history so history stays clean
            if bot.history and bot.history[-1]["role"] == "user":
                bot.history.pop()

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
