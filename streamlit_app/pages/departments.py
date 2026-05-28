"""Departments page – compliance gauges, leaderboard, and MAP breakdown."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.api_client import api_get


DEPT_ICONS = {
    "Legal": "⚖️", "Risk": "🛡️", "IT": "💻",
    "Operations": "⚙️", "Audit": "🔍"
}
DEPT_COLORS = {
    "Legal": "#7c3aed", "Risk": "#dc2626", "IT": "#2563eb",
    "Operations": "#0891b2", "Audit": "#059669"
}


def render():
    st.markdown("## 🏢 Department Compliance Center")
    st.markdown("*Track compliance health and MAP progress per department*")
    st.markdown("---")

    depts = api_get("/departments")
    if not depts:
        st.warning("Could not load department data.")
        return

    # ── Leaderboard ───────────────────────────────────────────────────────
    st.markdown("### 🏆 Compliance Leaderboard")
    df = pd.DataFrame(depts)
    df_sorted = df.sort_values("compliance_score", ascending=False).reset_index(drop=True)

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    cols = st.columns(len(df_sorted))
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        icon = DEPT_ICONS.get(row["name"], "🏦")
        color = DEPT_COLORS.get(row["name"], "#475569")
        score = row["compliance_score"]
        score_color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
        with cols[i]:
            st.markdown(f"""
            <div style="background:white; border-radius:16px; border:1px solid #e2e8f0;
                        border-top:5px solid {color}; padding:1.25rem; text-align:center;
                        box-shadow:0 2px 12px rgba(0,0,0,0.06);">
              <div style="font-size:1.75rem;">{medals[i]} {icon}</div>
              <div style="font-weight:800; color:#1e293b; font-size:1rem; margin:0.5rem 0;">{row['name']}</div>
              <div style="font-size:2rem; font-weight:800; color:{score_color};">{score:.1f}%</div>
              <div style="font-size:0.72rem; color:#94a3b8; margin-top:4px;">Compliance Score</div>
              <hr style="margin:0.75rem 0; border-color:#f1f5f9;">
              <div style="font-size:0.75rem; color:#475569;"><strong>{row.get('head','N/A')}</strong></div>
              <div style="font-size:0.68rem; color:#94a3b8;">{row.get('contact','')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")

    # ── Radar Chart ───────────────────────────────────────────────────────
    st.markdown("### 📡 Department Compliance Radar")
    col_radar, col_detail = st.columns([1.2, 1])

    with col_radar:
        names = [r["name"] for _, r in df_sorted.iterrows()]
        scores = [r["compliance_score"] for _, r in df_sorted.iterrows()]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=names + [names[0]],
            fill="toself",
            fillcolor="rgba(255,184,0,0.15)",
            line=dict(color="#FFB800", width=2.5),
            marker=dict(size=8, color="#FFB800"),
            name="Compliance",
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=11)),
                angularaxis=dict(tickfont=dict(size=13, family="Inter", color="#1e293b")),
            ),
            height=340, margin=dict(t=30, b=30, l=40, r=40),
            paper_bgcolor="white", showlegend=False,
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_detail:
        st.markdown("### 🔎 Department Detail")
        selected = st.selectbox("Select Department", [d["name"] for d in depts])
        dept = next((d for d in depts if d["name"] == selected), None)
        if dept:
            icon = DEPT_ICONS.get(dept["name"], "🏦")
            color = DEPT_COLORS.get(dept["name"], "#475569")
            score = dept["compliance_score"]
            score_color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
            map_counts = dept.get("map_counts", {})
            total_maps = sum(map_counts.values()) or 1

            st.markdown(f"""
            <div style="background:white; border-radius:16px; border:2px solid {color};
                        padding:1.5rem; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
              <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1rem;">
                <span style="font-size:2rem;">{icon}</span>
                <div>
                  <div style="font-weight:800; color:#1e293b; font-size:1.1rem;">{dept['name']}</div>
                  <div style="font-size:0.78rem; color:#64748b;">{dept.get('head','N/A')} · {dept.get('contact','')}</div>
                </div>
              </div>
              <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                <div style="text-align:center;">
                  <div style="font-size:1.75rem; font-weight:800; color:{score_color};">{score:.1f}%</div>
                  <div style="font-size:0.72rem; color:#94a3b8;">Overall Score</div>
                </div>
                <div style="text-align:center;">
                  <div style="font-size:1.75rem; font-weight:800; color:#22c55e;">{map_counts.get('completed', 0)}</div>
                  <div style="font-size:0.72rem; color:#94a3b8;">Completed</div>
                </div>
                <div style="text-align:center;">
                  <div style="font-size:1.75rem; font-weight:800; color:#3b82f6;">{map_counts.get('in_progress', 0)}</div>
                  <div style="font-size:0.72rem; color:#94a3b8;">In Progress</div>
                </div>
                <div style="text-align:center;">
                  <div style="font-size:1.75rem; font-weight:800; color:#94a3b8;">{map_counts.get('pending', 0)}</div>
                  <div style="font-size:0.72rem; color:#94a3b8;">Pending</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Progress bar
            completed = map_counts.get("completed", 0)
            st.markdown("")
            st.progress(completed / total_maps, text=f"Progress: {completed}/{total_maps} MAPs completed")

            # Dept MAPs table
            st.markdown("**📌 Department MAPs**")
            dept_maps = api_get("/maps", params={"department": selected, "limit": 20})
            if dept_maps:
                for m in dept_maps:
                    status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "overdue": "⚠️"}.get(m["status"], "❓")
                    priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(m["priority"], "⚪")
                    st.markdown(f"""
                    <div style="background:#f8fafc; border-radius:10px; padding:0.6rem 0.9rem; margin:4px 0;
                                border-left:3px solid {color}; font-size:0.8rem;">
                      {status_icon} {priority_icon} <strong>{m['title'][:50]}</strong>
                      <span style="float:right; color:#94a3b8;">📅 {m.get('deadline','N/A')}</span>
                    </div>
                    """, unsafe_allow_html=True)
