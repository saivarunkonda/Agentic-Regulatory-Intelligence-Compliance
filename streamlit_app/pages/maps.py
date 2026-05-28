"""MAPs page – full filterable table with status updates."""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.api_client import api_get, api_patch, priority_badge, status_badge


def render():
    st.markdown("## 📌 Measurable Action Points (MAPs)")
    st.markdown("*All compliance tasks generated from regulatory obligations*")
    st.markdown("---")

    # ── Filters ────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox("Department", ["All", "Legal", "Risk", "IT", "Operations", "Audit"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "pending", "in_progress", "completed", "overdue"])
    with col3:
        priority_filter = st.selectbox("Priority", ["All", "critical", "high", "medium", "low"])

    params = {}
    if dept_filter != "All": params["department"] = dept_filter
    if status_filter != "All": params["status"] = status_filter
    if priority_filter != "All": params["priority"] = priority_filter

    maps = api_get("/maps", params=params)
    if not maps:
        st.warning("No MAPs found matching your filters.")
        return

    # ── Summary strip ────────────────────────────────────────────────────
    total = len(maps)
    completed = sum(1 for m in maps if m.get("status") == "completed")
    critical = sum(1 for m in maps if m.get("priority") == "critical")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total MAPs", total)
    c2.metric("✅ Completed", completed, f"{round(completed/total*100 if total else 0, 1)}%")
    c3.metric("🔴 Critical", critical)

    st.markdown("---")

    # ── Card view ────────────────────────────────────────────────────────
    view = st.radio("View", ["🃏 Cards", "📊 Table"], horizontal=True)

    if view == "🃏 Cards":
        _render_cards(maps)
    else:
        _render_table(maps)


def _render_cards(maps):
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    maps_sorted = sorted(maps, key=lambda m: priority_order.get(m.get("priority", "low"), 4))

    for i in range(0, len(maps_sorted), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(maps_sorted):
                m = maps_sorted[i + j]
                with col:
                    _render_map_card(m)


def _render_map_card(m):
    priority = m.get("priority", "medium")
    status = m.get("status", "pending")
    border_colors = {"critical": "#dc2626", "high": "#ea580c", "medium": "#ca8a04", "low": "#16a34a"}
    border_color = border_colors.get(priority, "#94a3b8")

    st.markdown(f"""
    <div style="background:white; border-radius:16px; border:1px solid #e2e8f0;
                border-left:5px solid {border_color}; padding:1.25rem;
                box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:0.5rem;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
        <div style="font-weight:700; color:#1e293b; font-size:0.9rem; line-height:1.4; flex:1; margin-right:8px;">
          {m.get('title', 'Untitled')}
        </div>
        <span style="font-size:0.65rem; color:#94a3b8; white-space:nowrap;">#{m.get('id')}</span>
      </div>
      <div style="color:#64748b; font-size:0.78rem; margin-bottom:0.75rem; line-height:1.5;">
        {m.get('description', '')[:150]}{'…' if len(m.get('description','')) > 150 else ''}
      </div>
      <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:0.75rem;">
        {priority_badge(priority)}
        {status_badge(status)}
        <span class="badge" style="background:#eff6ff; color:#2563eb; border:1px solid #93c5fd;">
          🏢 {m.get('department', 'N/A')}
        </span>
      </div>
      <div style="color:#94a3b8; font-size:0.72rem;">
        📅 Deadline: <strong style="color:#475569;">{m.get('deadline', 'N/A')}</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"⚙️ Manage MAP #{m.get('id')}", expanded=False):
        new_status = st.selectbox(
            "Update Status",
            ["pending", "in_progress", "completed", "overdue", "escalated"],
            index=["pending", "in_progress", "completed", "overdue", "escalated"].index(status) if status in ["pending", "in_progress", "completed", "overdue", "escalated"] else 0,
            key=f"status_sel_{m.get('id')}",
        )
        actor = st.text_input("Updated by", value="Department Head", key=f"actor_{m.get('id')}")
        notes = st.text_area("Notes", placeholder="Add completion notes...", key=f"notes_{m.get('id')}", height=80)
        if st.button("💾 Save Update", key=f"save_{m.get('id')}"):
            result = api_patch(f"/maps/{m.get('id')}/status", {"status": new_status, "actor": actor, "notes": notes})
            if result:
                st.success("✅ MAP status updated!")
                st.rerun()


def _render_table(maps):
    df = pd.DataFrame(maps)
    if df.empty:
        st.info("No data to display.")
        return
    display_cols = ["id", "title", "priority", "department", "status", "deadline"]
    df_display = df[[c for c in display_cols if c in df.columns]]
    df_display.columns = ["ID", "Title", "Priority", "Department", "Status", "Deadline"]
    st.dataframe(df_display, use_container_width=True, height=500)
