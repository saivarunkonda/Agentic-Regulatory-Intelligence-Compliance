"""Regulations page – ingestion feed, source filter, parse & generate MAPs."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.api_client import api_get, api_post


SOURCE_COLORS = {
    "RBI": "#1d4ed8", "SEBI": "#7c3aed",
    "EU-GDPR": "#059669", "Manual": "#b45309", "PDF Upload": "#b45309"
}


def render():
    st.markdown("## 📋 Regulatory Feed")
    st.markdown("*Monitor and ingest regulations from RBI, SEBI, GDPR, and other sources*")
    st.markdown("---")

    tabs = st.tabs(["📡 Live Feed", "✍️ Manual Ingest", "📄 PDF Upload"])

    # ── Tab 1: Live Feed ────────────────────────────────────────────────────
    with tabs[0]:
        col_filter, col_btn = st.columns([3, 1])
        with col_filter:
            source_filter = st.selectbox(
                "Filter by Source", ["All Sources", "RBI", "SEBI", "EU-GDPR", "Manual", "PDF Upload"],
                key="reg_source_filter"
            )
        with col_btn:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.button("🔄 Trigger Live Scrape", use_container_width=True):
                with st.spinner("🔍 Scanning regulatory portals..."):
                    result = api_post("/regulations/ingest", {})
                    if result:
                        st.success("✅ Ingestion started! Refresh in a few seconds.")

        params = {}
        if source_filter != "All Sources":
            params["source"] = source_filter

        regs = api_get("/regulations", params=params)
        if not regs:
            st.warning("No regulations found. Ingest some data first or check that the API is running.")
            return

        st.markdown(f"**{len(regs)} regulations found**")
        st.markdown("")

        for reg in regs:
            src = reg.get("source", "Unknown")
            src_color = SOURCE_COLORS.get(src, "#475569")
            status = reg.get("status", "new")
            status_icon = "✅" if status == "processed" else "🆕"

            with st.expander(f"{status_icon}  **{reg.get('title', 'Untitled')}**  ·  `{src}`  ·  {reg.get('created_at', '')[:10]}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style="display:flex; gap:8px; margin-bottom:12px; align-items:center;">
                      <span style="background:{src_color}; color:white; padding:3px 12px; border-radius:999px; font-size:0.72rem; font-weight:700;">{src}</span>
                      <span style="background:{'#dcfce7' if status=='processed' else '#f1f5f9'}; color:{'#16a34a' if status=='processed' else '#64748b'}; padding:3px 12px; border-radius:999px; font-size:0.72rem; font-weight:700;">{status.upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    text_preview = reg.get("raw_text", "")[:500]
                    st.text_area("Regulation Text (preview)", value=text_preview, height=150, key=f"reg_text_{reg['id']}", disabled=True)

                with col2:
                    st.markdown(f"**Regulation ID:** `{reg.get('id')}`")
                    st.markdown(f"**URL:** {reg.get('url', 'N/A')[:40] or 'N/A'}")
                    if status != "processed":
                        if st.button(f"⚡ Generate MAPs", key=f"gen_maps_{reg['id']}", use_container_width=True):
                            with st.spinner("🤖 NLP Agent extracting obligations..."):
                                result = api_post(f"/maps/generate/{reg['id']}")
                                if result:
                                    st.success(f"✅ {result.get('maps_generated', 0)} MAPs generated!")
                                    st.rerun()
                    else:
                        st.success("✅ MAPs Generated")
                        if st.button("♻️ Re-generate MAPs", key=f"regen_maps_{reg['id']}", use_container_width=True):
                            with st.spinner("🤖 Re-running NLP pipeline..."):
                                result = api_post(f"/maps/generate/{reg['id']}")
                                if result:
                                    st.success(f"✅ {result.get('maps_generated', 0)} new MAPs!")
                                    st.rerun()

    # ── Tab 2: Manual Ingest ───────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### ✍️ Paste Regulation Text")
        st.markdown("*Manually add a regulation by pasting its text content*")

        col_a, col_b = st.columns(2)
        with col_a:
            title = st.text_input("Regulation Title", placeholder="e.g. RBI Master Circular – KYC Norms 2024")
        with col_b:
            source = st.selectbox("Source", ["RBI", "SEBI", "EU-GDPR", "IRDAI", "MCA", "Manual"])

        regulation_text = st.text_area(
            "Regulation Text",
            placeholder="""Paste the full regulation text here...

Example:
All banks shall ensure that Customer Due Diligence (CDD) is completed for all existing accounts by March 31, 2024. 
High-risk accounts must be reviewed within 30 days. 
IT systems shall be upgraded to support Aadhaar-based eKYC authentication. 
Legal team must update all customer consent clauses.
Operations team shall file STRs within 24 hours of detection.""",
            height=280,
        )

        auto_generate = st.checkbox("⚡ Auto-generate MAPs after ingestion", value=True)

        if st.button("📥 Ingest Regulation", use_container_width=False):
            if not title or not regulation_text:
                st.error("Please fill in both Title and Regulation Text.")
            else:
                with st.spinner("📥 Ingesting regulation..."):
                    result = api_post("/regulations/ingest/text", {
                        "title": title, "source": source, "text": regulation_text
                    })
                    if result:
                        reg_id = result.get("id")
                        st.success(f"✅ Regulation ingested with ID #{reg_id}")
                        if auto_generate:
                            with st.spinner("🤖 NLP Agent generating MAPs..."):
                                maps_result = api_post(f"/maps/generate/{reg_id}")
                                if maps_result:
                                    n = maps_result.get("maps_generated", 0)
                                    st.success(f"⚡ {n} MAPs generated and assigned to departments!")
                                    st.balloons()

    # ── Tab 3: PDF Upload ──────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### 📄 Upload Regulatory PDF")
        st.markdown("*Upload a PDF circular, gazette notification, or directive*")

        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file:
            st.info(f"📄 **{uploaded_file.name}** · {uploaded_file.size / 1024:.1f} KB")
            auto_gen_pdf = st.checkbox("⚡ Auto-generate MAPs after upload", value=True)
            if st.button("📤 Upload & Process PDF", use_container_width=False):
                with st.spinner("📑 Parsing PDF and extracting text..."):
                    import httpx
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        r = httpx.post("http://localhost:8000/regulations/ingest/file", files=files, timeout=20)
                        result = r.json()
                        reg_id = result.get("id")
                        st.success(f"✅ PDF parsed – Regulation #{reg_id} created")
                        if auto_gen_pdf:
                            with st.spinner("🤖 NLP Agent analyzing document..."):
                                maps_result = api_post(f"/maps/generate/{reg_id}")
                                if maps_result:
                                    st.success(f"⚡ {maps_result.get('maps_generated', 0)} MAPs generated!")
                                    st.balloons()
                    except Exception as e:
                        st.error(f"❌ Upload failed: {e}")
