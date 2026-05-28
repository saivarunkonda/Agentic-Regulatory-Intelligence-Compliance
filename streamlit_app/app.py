"""
SuRaksha – Streamlit Web Dashboard
Option A: Main entry point
"""
import streamlit as st

st.set_page_config(
    page_title="SuRaksha | Agentic Regulatory Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS Theme ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Dark sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d2144 60%, #091929 100%);
    border-right: 1px solid rgba(255,184,0,0.15);
  }
  section[data-testid="stSidebar"] * { color: #e8edf5 !important; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] p { color: #94a3b8 !important; }

  /* Main background */
  .main .block-container {
    background: #f0f4fb;
    padding-top: 1.5rem;
  }

  /* Metric cards */
  div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  }
  div[data-testid="metric-container"] label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
  div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1e293b !important; font-size: 2rem !important; font-weight: 800; }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #FFB800 0%, #FF8C00 100%);
    color: #0a1628 !important;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.875rem;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(255,184,0,0.3);
  }
  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255,184,0,0.4);
  }

  /* Dataframe */
  .stDataFrame { border-radius: 12px; overflow: hidden; }

  /* Headers */
  h1 { color: #0a1628 !important; font-weight: 800 !important; }
  h2 { color: #1e293b !important; font-weight: 700 !important; }
  h3 { color: #334155 !important; font-weight: 600 !important; }

  /* Pills / badges */
  .badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .badge-critical { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }
  .badge-high     { background: #fff7ed; color: #ea580c; border: 1px solid #fdba74; }
  .badge-medium   { background: #fefce8; color: #ca8a04; border: 1px solid #fde68a; }
  .badge-low      { background: #f0fdf4; color: #16a34a; border: 1px solid #86efac; }

  .badge-pending     { background: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }
  .badge-in_progress { background: #eff6ff; color: #2563eb; border: 1px solid #93c5fd; }
  .badge-completed   { background: #f0fdf4; color: #16a34a; border: 1px solid #86efac; }
  .badge-overdue     { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }

  /* Info/Alert boxes */
  .info-box {
    background: white;
    border-left: 4px solid #FFB800;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  .alert-box {
    background: #fff5f5;
    border-left: 4px solid #ef4444;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
  }

  /* Section cards */
  .section-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: #64748b;
    border-radius: 8px 8px 0 0;
  }
  .stTabs [aria-selected="true"] {
    color: #0a1628 !important;
    border-bottom: 3px solid #FFB800 !important;
  }

  /* Sidebar logo area */
  .sidebar-logo {
    text-align: center;
    padding: 1.5rem 1rem;
    border-bottom: 1px solid rgba(255,184,0,0.2);
    margin-bottom: 1rem;
  }
  .sidebar-logo h2 {
    color: #FFB800 !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
  }
  .sidebar-logo p {
    color: #94a3b8 !important;
    font-size: 0.75rem !important;
    margin: 0.25rem 0 0 !important;
  }

  div[data-testid="stSidebarNav"] { display: none; }

  /* Hide Streamlit branding */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🏦 SuRaksha</h2>
        <p>Agentic Regulatory Intelligence</p>
        <p style="color:#FFB800 !important; font-size:0.65rem !important; margin-top:4px !important;">
          Canara Bank · Powered by AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "📋 Regulations", "📌 MAPs", "🏢 Departments", "✅ Validation"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("""
    <div style="padding: 1rem; background: rgba(255,184,0,0.08); border-radius: 12px; border: 1px solid rgba(255,184,0,0.2);">
      <p style="color:#FFB800 !important; font-weight:700; font-size:0.8rem; margin-bottom:0.5rem;">🤖 Active Agents</p>
      <p style="color:#94a3b8 !important; font-size:0.72rem; margin:0.2rem 0;">✅ IngestionAgent</p>
      <p style="color:#94a3b8 !important; font-size:0.72rem; margin:0.2rem 0;">✅ NLPAgent</p>
      <p style="color:#94a3b8 !important; font-size:0.72rem; margin:0.2rem 0;">✅ RoutingAgent</p>
      <p style="color:#94a3b8 !important; font-size:0.72rem; margin:0.2rem 0;">✅ ValidationAgent</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("SuRaksha v1.0 · SuRaksha 2024")

# ── Routing ───────────────────────────────────────────────────────────────────
import importlib, sys, os
sys.path.insert(0, os.path.dirname(__file__))

if page == "🏠 Dashboard":
    from pages import dashboard
    dashboard.render()
elif page == "📋 Regulations":
    from pages import regulations
    regulations.render()
elif page == "📌 MAPs":
    from pages import maps
    maps.render()
elif page == "🏢 Departments":
    from pages import departments
    departments.render()
elif page == "✅ Validation":
    from pages import validation
    validation.render()
