"""Validation page – run validation agent, view audit logs, evidence upload."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.api_client import api_get, api_post, api_patch, priority_badge, status_badge


def render():
    st.markdown("## ✅ Autonomous Validation Engine")
    st.markdown("*Validate MAP completions using AI agents — audit trail, evidence checks, deadline compliance*")
    st.markdown("---")

    tabs = st.tabs(["🤖 Run Validation", "📋 Audit Trail", "🚨 Alerts"])

    # ── Tab 1: Run Validation ──────────────────────────────────────────────
    with tabs[0]:
        maps = api_get("/maps")
        if not maps:
            st.warning("No MAPs found. Generate some first.")
            return

        col_a, col_b = st.columns([2, 1])
        with col_a:
            map_options = {f"#{m['id']} – {m['title'][:60]} [{m['department']}]": m["id"] for m in maps}
            selected_label = st.selectbox("Select MAP to Validate", list(map_options.keys()))
            selected_id = map_options[selected_label]

        with col_b:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            validate_btn = st.button("🤖 Run Validation Agent", use_container_width=True)

        # Show selected MAP info
        selected_map = next((m for m in maps if m["id"] == selected_id), None)
        if selected_map:
            p = selected_map.get("priority", "medium")
            s = selected_map.get("status", "pending")
            st.markdown(f"""
            <div style="background:white; border-radius:14px; border:1px solid #e2e8f0;
                        padding:1.25rem; margin:0.75rem 0; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
              <div style="font-weight:700; font-size:1rem; color:#1e293b; margin-bottom:0.5rem;">
                {selected_map.get('title', '')}
              </div>
              <div style="color:#64748b; font-size:0.8rem; margin-bottom:0.75rem;">
                {selected_map.get('description', '')}
              </div>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                {priority_badge(p)}
                {status_badge(s)}
                <span class="badge" style="background:#eff6ff; color:#2563eb; border:1px solid #93c5fd;">
                  🏢 {selected_map.get('department', '')}
                </span>
                <span class="badge" style="background:#f8fafc; color:#475569; border:1px solid #e2e8f0;">
                  📅 {selected_map.get('deadline', 'N/A')}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if validate_btn:
            with st.spinner("🤖 ValidationAgent running checks..."):
                result = api_post(f"/validate/{selected_id}")
                if result:
                    _render_validation_result(result)

        # Quick status update + evidence upload
        st.markdown("---")
        st.markdown("### 📤 Upload Evidence & Update Status")
        col1, col2 = st.columns(2)
        with col1:
            new_status = st.selectbox("New Status", ["pending", "in_progress", "completed", "overdue", "escalated"])
            actor = st.text_input("Updated by", value="Compliance Officer")
            notes = st.text_area("Completion Notes", placeholder="Describe what was done...", height=100)
        with col2:
            evidence_file = st.file_uploader("Upload Evidence (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])
            if evidence_file:
                st.success(f"📎 Evidence ready: {evidence_file.name}")

        if st.button("💾 Update MAP Status", use_container_width=False):
            if selected_id:
                result = api_patch(f"/maps/{selected_id}/status", {
                    "status": new_status, "actor": actor, "notes": notes
                })
                if result:
                    st.success(f"✅ MAP #{selected_id} updated to `{new_status}`")

    # ── Tab 2: Audit Trail ────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 📋 Full Audit Trail")
        maps = api_get("/maps")
        if not maps:
            return
        map_options2 = {f"#{m['id']} – {m['title'][:55]}": m["id"] for m in maps}
        sel2 = st.selectbox("Select MAP", list(map_options2.keys()), key="audit_sel")
        sel_id2 = map_options2[sel2]

        detail = api_get(f"/maps/{sel_id2}")
        if detail:
            logs = detail.get("audit_logs", [])
            if logs:
                for log in logs:
                    icon = "🤖" if log.get("actor", "").endswith("Agent") else "👤"
                    st.markdown(f"""
                    <div style="background:white; border-radius:12px; border:1px solid #e2e8f0;
                                border-left:4px solid #FFB800; padding:1rem 1.25rem; margin:6px 0;
                                box-shadow:0 1px 6px rgba(0,0,0,0.04);">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:600; color:#1e293b; font-size:0.85rem;">
                          {icon} {log.get('action', '')}
                        </div>
                        <div style="font-size:0.72rem; color:#94a3b8;">{log.get('timestamp', '')[:19]}</div>
                      </div>
                      <div style="display:flex; justify-content:space-between; margin-top:4px;">
                        <div style="font-size:0.75rem; color:#64748b;">By: <strong>{log.get('actor', '')}</strong></div>
                        <div style="font-size:0.75rem; color:#64748b;">{log.get('notes', '')[:100]}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No audit log entries for this MAP yet.")

    # ── Tab 3: Alerts ────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### 🚨 Active Compliance Alerts")
        alerts = api_get("/alerts")
        if not alerts:
            st.success("✅ No active alerts! All MAPs are on track.")
            return

        for alert in alerts:
            alert_type = alert.get("type", "")
            icon = "🔴" if "overdue" in alert_type else "🟠" if "critical" in alert_type else "🟡"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="alert-box">
                  <div style="font-weight:700; color:#1e293b; font-size:0.9rem;">{icon} {alert.get('message', '')}</div>
                  <div style="color:#94a3b8; font-size:0.72rem; margin-top:4px;">
                    MAP #{alert.get('map_id')} · Type: {alert_type} · {alert.get('created_at','')[:10]}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅ Resolve", key=f"resolve_{alert['id']}"):
                    api_patch(f"/alerts/{alert['id']}/resolve", {})
                    st.rerun()


def _render_validation_result(result):
    score = result.get("validation_score", 0)
    passed = result.get("overall_passed", False)
    checks = result.get("checks", [])

    if passed:
        st.success(f"✅ **Validation PASSED** — Score: {score}%")
    else:
        st.error(f"❌ **Validation FAILED** — Score: {score}%")

    # Score progress bar
    color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    st.markdown(f"""
    <div style="background:#f1f5f9; border-radius:999px; height:12px; margin:0.75rem 0;">
      <div style="background:{color}; width:{score}%; height:12px; border-radius:999px; transition:width 0.5s;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Validation Checks:**")
    for check in checks:
        ok = check.get("passed", False)
        icon = "✅" if ok else "❌"
        name = check.get("check", "")
        detail = check.get("detail", check.get("reason", ""))
        st.markdown(f"""
        <div style="background:{'#f0fdf4' if ok else '#fef2f2'}; border-radius:10px;
                    border:1px solid {'#86efac' if ok else '#fca5a5'};
                    padding:0.65rem 1rem; margin:4px 0; font-size:0.83rem;">
          {icon} <strong>{name}</strong>
          {f'<span style="color:#64748b; margin-left:8px; font-size:0.75rem;">{detail}</span>' if detail else ''}
        </div>
        """, unsafe_allow_html=True)
