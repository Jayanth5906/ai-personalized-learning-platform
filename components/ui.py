"""Shared presentation helpers for the Streamlit application."""

from html import escape

import streamlit as st


def render_page_header(eyebrow, title, description, icon=""):
    """Render a consistent, accessible heading for an application screen."""
    safe_eyebrow = escape(str(eyebrow))
    safe_title = escape(str(title))
    safe_description = escape(str(description))
    safe_icon = escape(str(icon))
    icon_html = f'<span class="page-icon" aria-hidden="true">{safe_icon}</span>' if safe_icon else ""

    st.markdown(
        f"""
        <header class="page-header">
            <div class="page-eyebrow"><span class="page-eyebrow-dot"></span>{safe_eyebrow}</div>
            <div class="page-title-row">{icon_html}<h1>{safe_title}</h1></div>
            <p>{safe_description}</p>
        </header>
        """,
        unsafe_allow_html=True,
    )
