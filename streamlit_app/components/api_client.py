"""Shared API client for Streamlit pages."""
import httpx
import streamlit as st

API_BASE = "http://localhost:8000"


def api_get(endpoint: str, params: dict = None):
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None


def api_post(endpoint: str, json: dict = None):
    try:
        r = httpx.post(f"{API_BASE}{endpoint}", json=json, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None


def api_patch(endpoint: str, json: dict = None):
    try:
        r = httpx.patch(f"{API_BASE}{endpoint}", json=json, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None


def priority_badge(priority: str) -> str:
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    icon = icons.get(priority, "⚪")
    return f'<span class="badge badge-{priority}">{icon} {priority.upper()}</span>'


def status_badge(status: str) -> str:
    icons = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "overdue": "⚠️", "escalated": "🚨"}
    icon = icons.get(status, "❓")
    label = status.replace("_", " ").title()
    return f'<span class="badge badge-{status}">{icon} {label}</span>'
