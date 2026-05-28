"""Dashboard page – KPIs, compliance chart, recent regulations, alerts."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.api_client import api_get, priority_badge, status_badge


def render():
    st.markdown("## 🏠 Compliance Command Center")
    st.markdown("*Real-time regulatory intelligence dashboard*")
    st.markdown("---")

    stats = api_get("/dashboard/stats")
    if not stats:
        st.warning("⚠️ Could not connect to SuRaksha API. Make sure the backend is running on port 8000.")
        _render_demo_dashboard()
        return

    # ── KPI Row ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📜 Regulations", stats.get("total_regulations", 0))
    c2.metric("📌 Total MAPs", stats.get("total_maps", 0))
    c3.metric("⏳ Pending", stats.get("pending_maps", 0))
    c4.metric("🔄 In Progress", stats.get("in_progress_maps", 0))
    c5.metric("✅ Completed", stats.get("completed_maps", 0))
    c6.metric("⚠️ Overdue", stats.get("overdue_maps", 0), delta=None)

    st.markdown("")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### 📊 Overall Compliance Score")
        score = stats.get("compliance_score", 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            delta={"reference": 75, "increasing": {"color": "#22c55e"}, "decreasing": {"color": "#ef4444"}},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"size": 12}},
                "bar": {"color": "#FFB800"},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 75], "color": "#fef9c3"},
                    {"range": [75, 100], "color": "#dcfce7"},
                ],
                "threshold": {
                    "line": {"color": "#0a1628", "width": 3},
                    "thickness": 0.75,
                    "value": 75,
                },
            },
            number={"suffix": "%", "font": {"size": 48, "color": "#0a1628"}},
            title={"text": "Bank Compliance Score", "font": {"size": 16, "color": "#64748b"}},
        ))
        fig_gauge.update_layout(
            height=280, margin=dict(t=40, b=20, l=30, r=30),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Department compliance bar chart
        st.markdown("### 🏢 Department Compliance")
        dept_data = stats.get("department_breakdown", [])
        if dept_data:
            df_dept = pd.DataFrame(dept_data)
            fig_bar = px.bar(
                df_dept, x="department", y="score",
                color="score",
                color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#22c55e"]],
                text="score",
                labels={"score": "Compliance %", "department": "Department"},
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.update_layout(
                height=280, margin=dict(t=20, b=20, l=10, r=10),
                paper_bgcolor="white", plot_bgcolor="white",
                showlegend=False, coloraxis_showscale=False,
                xaxis=dict(tickfont=dict(size=13, family="Inter")),
                yaxis=dict(range=[0, 110]),
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # ── MAP Status Donut ──────────────────────────────────────────────
        st.markdown("### 📌 MAP Status Breakdown")
        labels = ["Pending", "In Progress", "Completed", "Overdue"]
        values = [
            stats.get("pending_maps", 0),
            stats.get("in_progress_maps", 0),
            stats.get("completed_maps", 0),
            stats.get("overdue_maps", 0),
        ]
        colors = ["#94a3b8", "#3b82f6", "#22c55e", "#ef4444"]
        fig_donut = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.6, marker_colors=colors,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} MAPs<extra></extra>",
        ))
        fig_donut.update_layout(
            height=250, margin=dict(t=20, b=20, l=10, r=10),
            paper_bgcolor="white", showlegend=False,
            font=dict(family="Inter"),
            annotations=[dict(text=f"<b>{sum(values)}</b><br>Total", x=0.5, y=0.5,
                              font_size=16, showarrow=False, font_color="#0a1628")],
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        # ── Active Alerts ──────────────────────────────────────────────
        st.markdown("### 🚨 Active Alerts")
        alerts = api_get("/alerts")
        if alerts:
            for alert in alerts[:5]:
                icon = "🔴" if alert.get("type") == "overdue" else "🟠"
                st.markdown(f"""
                <div class="alert-box">
                  <div style="font-weight:600; color:#1e293b; font-size:0.85rem;">{icon} {alert.get('message','')}</div>
                  <div style="color:#94a3b8; font-size:0.72rem; margin-top:4px;">MAP #{alert.get('map_id')} · {alert.get('created_at','')[:10]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">✅ No active alerts</div>', unsafe_allow_html=True)

        # ── Recent Regulations ────────────────────────────────────────
        st.markdown("### 📋 Recent Regulations")
        regs = stats.get("recent_regulations", [])
        for r in regs[:4]:
            src_color = {"RBI": "#1d4ed8", "SEBI": "#7c3aed", "EU-GDPR": "#059669", "PDF Upload": "#b45309"}.get(r.get("source", ""), "#475569")
            st.markdown(f"""
            <div class="info-box">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; color:#1e293b; font-size:0.82rem;">{r.get('title','')[:55]}…</span>
                <span style="background:{src_color}; color:white; padding:2px 8px; border-radius:999px; font-size:0.65rem; font-weight:700;">{r.get('source','')}</span>
              </div>
              <div style="color:#94a3b8; font-size:0.72rem; margin-top:4px;">{r.get('created_at','')[:10]}</div>
            </div>""", unsafe_allow_html=True)


def _render_demo_dashboard():
    """Render a beautiful demo view when API is offline."""
    st.info("🎭 Showing demo data. Start the backend with `uvicorn main:app` in the backend directory.")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📜 Regulations", 4)
    c2.metric("📌 Total MAPs", 10)
    c3.metric("⏳ Pending", 6)
    c4.metric("🔄 In Progress", 3)
    c5.metric("✅ Completed", 1)
    c6.metric("⚠️ Overdue", 2)
