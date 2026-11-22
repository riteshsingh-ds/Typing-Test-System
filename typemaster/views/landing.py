"""Public landing page shown to visitors who are not signed in."""
from __future__ import annotations

from datetime import date
from typing import Callable

import streamlit as st

from .. import config, rewards, ui
from ..database import Database, DatabaseError
from ..progress import BY_ID
from .home import FEATURES, STEPS

FAQ = (
    ("Is TypeMaster free?",
     "Yes. Practice tests, the Daily Challenge, Key Doctor, badges and certificates are free to use."),
    ("Why sign in with Google?",
     "So your scores, streaks and certificates follow you to any device, and nobody else can use your name. "
     "There is no password to remember or leak. Your email is only used to recognise you and is never shown to other players."),
    ("How do the certificates work?",
     "Every certificate is approved and signed by the founder and has a signed ID. Anyone can verify it inside the app under Rewards."),
    ("Do I need to install anything?",
     "No. TypeMaster runs in your browser on desktop and mobile."),
    ("Can I delete my account?",
     "Yes. Open the account menu after signing in and choose Delete my account. Your scores and certificates are removed permanently."),
)


@st.cache_data(show_spinner=False)
def _sample_certificate() -> bytes:
    ach = BY_ID["streak5"]
    return rewards.certificate_png(ach, "Your Name Here", date.today(), "TM-0000-STREAK5-SAMPLE",
                                   rewards.certificate_body(ach))


def _preview() -> None:
    ui.html_block(
        '<div class="lp-preview-wrap"><div class="lp-preview">'
        '<div class="lp-pv-bar"><i></i><i></i><i></i><span>typemaster</span></div>'
        '<div class="lp-pv-stats"><div><span>Time left</span><b class="amber">0:38</b></div>'
        '<div><span>Speed</span><b>64</b></div><div><span>Accuracy</span><b class="mint">97%</b></div></div>'
        '<div class="lp-pv-text"><span class="ok">Speed is just rhythm that you </span><span class="bad">l</span>'
        '<span class="ok">earned to repeat, </span><span class="caret"></span>'
        '<span class="rest">one steady key after another until it feels easy.</span></div>'
        '<div class="lp-pv-foot">Example run</div></div>'
        '<div class="lp-float one"><b>Key Doctor</b><span>Finds the keys you miss</span></div>'
        '<div class="lp-float two"><b>5-day streak</b><span>Badge and certificate</span></div></div>'
    )


def _stats(db: Database) -> None:
    try:
        s = db.platform_stats(date.today().isoformat())
    except DatabaseError:
        return
    if s["tests"] == 0:
        ui.html_block('<div class="lp-strip solo">Be among the first typists on the board.</div>')
        return
    cells = (
        (f'{s["tests"]:,}', "tests completed"),
        (f'{s["players"]:,}', "typists"),
        (f'{s["top_wpm"]:.0f} WPM', "fastest so far"),
        (f'{s["daily_players"]:,}', "in today\'s challenge"),
    )
    ui.html_block('<div class="lp-strip">' + "".join(
        f'<div><b>{ui.esc(v)}</b><span>{ui.esc(label)}</span></div>' for v, label in cells) + "</div>")


def _heading(title: str, sub: str = "") -> None:
    sub_html = f'<p>{ui.esc(sub)}</p>' if sub else ""
    ui.html_block(f'<div class="lp-heading"><div class="t">{ui.esc(title)}</div>{sub_html}</div>')


def render(db: Database, cta: Callable[[str], None]) -> None:
    """``cta(where)`` draws the sign-in control (Google button, or a name box in local mode)."""
    _, main, _ = st.columns([0.45, 6, 0.45])
    with main:
        # ---------------------------------------------------------------- top bar
        brand, action = st.columns([3, 1], vertical_alignment="center")
        with brand:
            ui.html_block(f'<div class="tm-brand"><div class="tm-logo">TM</div><div><div class="tm-title">{config.APP_NAME}</div></div></div>')
        with action:
            with st.container(key="lp_nav_cta"):
                cta("nav")

        # ------------------------------------------------------------------- hero
        left, right = st.columns([1.12, 1], gap="large", vertical_alignment="center")
        with left:
            ui.html_block(
                '<div class="lp-pill">Free typing trainer</div>'
                '<div class="lp-h1"><span>Type faster.</span><span class="amb">Type cleaner.</span><span>Every day.</span></div>'
                '<p class="lp-sub">TypeMaster finds the keys you miss, races your own best run and rewards your '
                'consistency with streaks, badges and certificates signed by the founder.</p>'
            )
            with st.container(key="lp_hero_cta"):
                cta("hero")
            ui.html_block(
                '<div class="lp-trust"><span>No password</span><span>Email kept private</span>'
                '<span>Works on mobile</span></div>'
            )
        with right:
            _preview()

        _stats(db)

        # --------------------------------------------------------------- features
        _heading("Built to make you better, not just busy",
                 "Six things you will not find in an ordinary typing test.")
        ui.html_block('<div class="tm-features">' + "".join(
            f'<div class="tm-feature"><span class="tag">{i + 1:02d}</span><h4>{ui.esc(t)}</h4><p>{ui.esc(b)}</p></div>'
            for i, (t, b) in enumerate(FEATURES)) + "</div>")

        # ---------------------------------------------------- certificate showcase
        ui.html_block('<div class="lp-spacer"></div>')
        cert_col, text_col = st.columns([1.5, 1], gap="large", vertical_alignment="center")
        with cert_col:
            ui.call_stretch(st.image, _sample_certificate())
        with text_col:
            ui.html_block(
                '<div class="lp-pill">Signed and verifiable</div>'
                '<div class="lp-h2">Earn certificates worth sharing</div>'
                '<p class="lp-sub small">Your first test earns a Certificate of Participation. Keep a 5-day streak for a '
                'Certificate of Consistency, or reach 40, 60, 80 and 100 WPM for Speed certificates.</p>'
                f'<ul class="lp-list"><li>Approved and signed by {ui.esc(config.FOUNDER_NAME)}, {ui.esc(config.FOUNDER_TITLE)}</li>'
                '<li>Download as PNG or PDF</li><li>Every certificate has an ID anyone can verify</li></ul>'
            )

        # ------------------------------------------------------------ how it works
        _heading("How it works")
        ui.html_block('<div class="tm-steps">' + "".join(
            f'<div class="tm-step"><span class="n">{n}</span><h4>{ui.esc(t)}</h4><p>{ui.esc(b)}</p></div>'
            for n, t, b in STEPS) + "</div>")

        # -------------------------------------------------------------------- faq
        _heading("Questions, answered")
        for question, answer in FAQ:
            with st.expander(question):
                st.write(answer)

        # ---------------------------------------------------------- closing banner
        ui.html_block('<div class="lp-final"><div class="t">Ready for your first test?</div>'
                      '<p>It takes less than a minute to start. Your first certificate is waiting.</p></div>')
        with st.container(key="lp_final_cta"):
            cta("final")

        ui.html_block(
            f'<div class="tm-footer"><div><b>{config.APP_NAME}</b> &middot; {config.APP_TAGLINE}</div>'
            f'<div>{config.FOUNDER_TITLE}: <b>{ui.esc(config.FOUNDER_NAME)}</b></div></div>'
        )
