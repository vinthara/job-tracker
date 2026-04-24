import streamlit as st
import pandas as pd
import html
from datetime import datetime
from models import SessionLocal, Contact, Application, JobOffer, init_db
from utils import export_to_markdown, get_company_list, generate_readable_view

# Page configuration
st.set_page_config(
    page_title="Job Search Tracker",
    page_icon="💼",
    layout="wide"
)

# Custom CSS styling - inspired by word-sync
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #11131d;
        --bg-panel: #16161e;
        --bg-soft: #1f2335;
        --border: #414868;
        --text-main: #e6e9f2;
        --text-soft: #a9b1d6;
        --accent: #7dcfff;
        --accent-strong: #bb9af7;
        --shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
    }

    .stApp {
        color: var(--text-main);
        background:
            radial-gradient(circle at 15% 5%, #23263a 0%, transparent 35%),
            radial-gradient(circle at 85% 20%, #1f2340 0%, transparent 30%),
            linear-gradient(170deg, var(--bg-main), #141725 60%, #101420);
        font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-panel);
        border-right: 1px solid var(--border);
    }

    .stDeployButton, [data-testid="stToolbar"], #MainMenu {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
    }

    h1 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: 0.2px;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--accent-strong);
    }

    h2 {
        color: var(--accent-strong);
        font-weight: 600;
        margin-top: 2rem;
    }

    h3 {
        color: var(--accent-strong);
        font-weight: 600;
    }

    p, span, label {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: var(--text-main);
    }

    .stButton>button {
        border-radius: 8px;
        padding: 0.55rem 1.25rem;
        font-weight: 500;
        border: none;
        transition: all 0.25s ease;
        background-color: #24283b;
        color: var(--accent-strong);
        border: 1px solid var(--border);
    }

    .stButton>button:hover {
        background-color: #414868;
        box-shadow: var(--shadow);
        transform: translateY(-2px);
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-strong), #95a3ff);
        color: #1a1b26;
        border: none;
        font-weight: 600;
    }

    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 4px 12px rgba(187, 154, 247, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-panel);
        padding: 4px;
        border: 1px solid var(--border);
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        padding: 0.75rem 1.25rem;
        font-weight: 500;
        color: var(--accent-strong);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #24283b;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--accent-strong) !important;
        color: #1a1b26 !important;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(22, 22, 30, 0.82);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }

    div[data-testid="stMetric"] label {
        color: var(--accent) !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--accent-strong) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stTextArea"] textarea {
        background-color: #16161e;
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-soft);
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stDateInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #7aa2f7;
        box-shadow: 0 0 0 0.08rem rgba(125, 207, 255, 0.2);
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stDataEditor"] {
        border-radius: 12px;
        border: 1px solid var(--border);
        overflow: hidden;
        box-shadow: var(--shadow);
    }

    [data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
        --gdg-bg-cell: #1a1b26;
        --gdg-bg-cell-medium: #24283b;
        --gdg-text-dark: #a9b1d6;
        --gdg-text-medium: #9aa5ce;
        --gdg-text-light: #565f89;
        --gdg-text-header: #c0caf5;
        --gdg-bg-header: #16161e;
        --gdg-bg-header-has-focus: #24283b;
        --gdg-border-color: #2f354d;
        --gdg-accent-color: var(--accent-strong);
    }

    .stToast {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--accent-strong) !important;
        color: var(--text-main) !important;
    }

    div[data-testid="stExpander"] {
        background-color: var(--bg-panel);
        border: 1px solid var(--border);
        border-radius: 8px;
    }

    div[data-testid="stExpander"] summary {
        color: var(--accent-strong) !important;
        font-weight: 600;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #7dcfff 0%, #bb9af7 100%);
    }

    .stCaption {
        color: var(--text-soft) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid var(--border);
        background-color: #24283b !important;
    }

    a {
        color: var(--accent) !important;
    }

    .auth-hero {
        padding: 1rem 1.1rem;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: linear-gradient(130deg, rgba(125, 207, 255, 0.12), rgba(187, 154, 247, 0.1));
        margin-bottom: 0.8rem;
    }
    .auth-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
    .auth-subtitle {
        margin-top: 0.2rem;
        color: var(--text-soft);
        font-size: 0.95rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background: rgba(22, 22, 30, 0.82) !important;
        box-shadow: var(--shadow) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] h3 {
        margin-top: 0;
    }
    .auth-note {
        color: var(--text-soft);
        font-size: 0.92rem;
        margin-bottom: 0.4rem;
    }
    .floating-user-card {
        position: fixed;
        top: 72px;
        right: 18px;
        z-index: 999;
        width: 220px;
        border: 1px solid #414868;
        border-radius: 12px;
        background: rgba(22, 22, 30, 0.92);
        backdrop-filter: blur(8px);
        padding: 0.8rem;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
    }
    .floating-user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
    }
    .floating-user-fallback {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 700;
        color: #11131d;
        background: linear-gradient(135deg,#7dcfff,#bb9af7);
    }
    .floating-user-name {
        margin-top: 0.35rem;
        color: #e6e9f2;
        font-weight: 700;
        font-size: 0.92rem;
    }
    .floating-user-email {
        color: #a9b1d6;
        font-size: 0.78rem;
        word-break: break-all;
    }
    .floating-user-logout {
        display: block;
        margin-top: 0.6rem;
        width: 100%;
        text-align: center;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.45rem 0.55rem;
        border-radius: 8px;
        border: 1px solid #414868;
        color: #a9b1d6 !important;
        background: #24283b;
    }
    .floating-user-logout:hover {
        background: #2d3250;
        color: #e6e9f2 !important;
    }
    @media (max-width: 980px) {
        .floating-user-card {
            position: static;
            width: 100%;
            margin: 0.6rem 0 0 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize database
init_db()

# ============================================
# AUTHENTICATION (Native Streamlit OAuth)
# ============================================

# Get allowed emails from secrets
allowed_emails_str = st.secrets.get("auth", {}).get("allowed_emails", "")
allowed_emails = [email.strip() for email in allowed_emails_str.split(",") if email.strip()]

# Check if user is logged in
if not st.user.is_logged_in:
    st.markdown(
        """
        <div class="auth-hero">
            <div class="auth-title">Job Search Tracker</div>
            <div class="auth-subtitle">Track applications, responses, and contacts in one focused workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left_col, center_col, right_col = st.columns([1, 1.2, 1])
    with center_col:
        with st.container(border=True):
            st.markdown("### Welcome")
            st.markdown('<div class="auth-note">Sign in to access your application dashboard.</div>', unsafe_allow_html=True)
            st.button("Log in with Google", on_click=st.login, type="primary", width="stretch")
    st.stop()

# User is logged in - check email whitelist
user_email = st.user.email or ""
display_name = st.user.name or "User"

if allowed_emails and user_email not in allowed_emails:
    st.markdown(
        """
        <div class="auth-hero">
            <div class="auth-title">Job Search Tracker</div>
            <div class="auth-subtitle">Track applications, responses, and contacts in one focused workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left_col, center_col, right_col = st.columns([1, 1.2, 1])
    with center_col:
        with st.container(border=True):
            st.error("🚫 Access Denied")
            st.warning(f"Your email address ({user_email}) is not authorized to access this application.")
            st.info("Please contact your administrator to request access.")
            st.button("Log out", on_click=st.logout, width="stretch")
    st.stop()

# ============================================
# AUTHENTICATED USER - SHOW MAIN APP
# ============================================
if st.query_params.get("action") == "logout":
    st.query_params.clear()
    st.logout()
    st.stop()

profile_picture = (
    getattr(st.user, "picture", None)
    or getattr(st.user, "avatar_url", None)
    or (st.user.to_dict().get("picture") if hasattr(st.user, "to_dict") else None)
    or (st.user.to_dict().get("photo") if hasattr(st.user, "to_dict") else None)
)
initial = html.escape(display_name[:1].upper()) if display_name else "U"
avatar_html = (
    (
        "<div style='position:relative;width:48px;height:48px;'>"
        f"<img src='{profile_picture}' class='floating-user-avatar' "
        "onerror=\"this.style.display='none';this.nextElementSibling.style.display='flex';\" />"
        f"<div class='floating-user-fallback' style='display:none;position:absolute;inset:0;'>{initial}</div>"
        "</div>"
    )
    if profile_picture
    else f"<div class='floating-user-fallback'>{initial}</div>"
)
st.markdown(
    (
        "<div class='floating-user-card'>"
        f"{avatar_html}"
        f"<div class='floating-user-name'>{html.escape(display_name)}</div>"
        f"<div class='floating-user-email'>{html.escape(user_email)}</div>"
        "<a class='floating-user-logout' href='?action=logout'>Log out</a>"
        "</div>"
    ),
    unsafe_allow_html=True,
)

# Header
st.markdown("# 💼 Job Search Tracker")
st.markdown("---")


@st.cache_data(ttl=5)
def load_applications():
    """Load applications from database."""
    db = SessionLocal()
    try:
        apps = db.query(Application).all()
        apps_data = []
        for app in apps:
            # Get company name from the contact relationship
            company_name = app.contact.company if app.contact else ''

            apps_data.append({
                'id': app.id,
                'company': company_name,  # Display name from contact
                'company_id': app.company_id,  # Actual FK (hidden from UI)
                'client': app.client or '',
                'job_link': app.job_link or '',
                'date': pd.Timestamp(app.date) if app.date else pd.NaT,
                'source': app.source,
                'status': app.status,
                'answer': app.answer,
                'answer_date': pd.Timestamp(app.answer_date) if app.answer_date else pd.NaT,
                'expected_rate': app.expected_rate,
                'offered_rate': app.offered_rate,
                'duration': app.duration or '',
                'start_date': pd.Timestamp(app.start_date) if app.start_date else pd.NaT,
                'notes': app.notes or '',
                'closed': app.closed
            })
        return pd.DataFrame(apps_data)
    finally:
        db.close()


@st.cache_data(ttl=5)
def load_contacts():
    """Load contacts from database."""
    db = SessionLocal()
    try:
        contacts = db.query(Contact).all()
        contacts_data = []
        for contact in contacts:
            contacts_data.append({
                'id': contact.id,
                'company': contact.company,
                'firstname': contact.firstname or '',
                'lastname': contact.lastname or '',
                'linkedin_link': contact.linkedin_link or '',
                'phone_number': contact.phone_number or '',
                'updated_date': pd.Timestamp(contact.updated_date) if contact.updated_date else pd.NaT
            })
        return pd.DataFrame(contacts_data)
    finally:
        db.close()


@st.cache_data(ttl=5)
def load_job_offers():
    """Load job offers from database."""
    db = SessionLocal()
    try:
        offers = db.query(JobOffer).order_by(JobOffer.date_added.desc()).all()
        if not offers:
            return pd.DataFrame(columns=["id", "company", "title", "url", "date_added"])
        offers_data = []
        for offer in offers:
            offers_data.append({
                'id': offer.id,
                'company': offer.company,
                'title': offer.title,
                'url': offer.url or '',
                'date_added': pd.Timestamp(offer.date_added) if offer.date_added else pd.NaT
            })
        return pd.DataFrame(offers_data)
    finally:
        db.close()


# Load data
candidature_df = load_applications()
contact_df = load_contacts()
offers_df = load_job_offers()

# Get company list and create name-to-id mapping
company_list = get_company_list()
db_temp = SessionLocal()
contacts = db_temp.query(Contact).all()
contact_name_to_id = {c.company: c.id for c in contacts}
db_temp.close()

# Default row ordering: newest first
if len(candidature_df) > 0:
    candidature_df = candidature_df.sort_values(by=["date", "id"], ascending=[False, False], na_position="last")
if len(contact_df) > 0:
    contact_df = contact_df.sort_values(by=["updated_date", "id"], ascending=[False, False], na_position="last")

# Calculate follow-up metrics
if len(candidature_df) > 0:
    today = pd.Timestamp.now()
    candidature_df['days_since_application'] = (today - candidature_df['date']).dt.days
    candidature_df['response_time'] = (candidature_df['answer_date'] - candidature_df['date']).dt.days
else:
    candidature_df['days_since_application'] = []
    candidature_df['response_time'] = []

# Check for urgent follow-ups
if len(candidature_df) > 0:
    urgent_followups = len(candidature_df[
        (candidature_df['answer'].str.lower().str.contains('not yet', na=False)) &
        (candidature_df['days_since_application'] > 14) &
        (candidature_df['closed'] == 'no')
    ])
    if urgent_followups > 0:
        st.error(f"🚨 **URGENT**: {urgent_followups} application(s) pending for over 14 days!")

# Statistics
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📝 Total", len(candidature_df))
with col2:
    pending = len(candidature_df[candidature_df['answer'].str.lower().str.contains('not yet', na=False)])
    st.metric("⏳ Pending", pending)
with col3:
    accepted = len(candidature_df[candidature_df['answer'].str.lower().str.contains('accept', na=False)])
    st.metric("✅ Accepted", accepted)
with col4:
    avg_response = candidature_df['response_time'].dropna().mean()
    avg_display = f"{int(avg_response)}d" if pd.notna(avg_response) else "N/A"
    st.metric("📊 Avg Response", avg_display)
with col5:
    answered = len(candidature_df[candidature_df['answer_date'].notna()])
    response_rate = (answered / len(candidature_df) * 100) if len(candidature_df) > 0 else 0
    st.metric("📈 Response", f"{response_rate:.0f}%")

st.markdown("---")

# Quick analytics section
if len(candidature_df) > 0:
    with st.expander("📊 Quick Analytics", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Response Rate by Source")
            source_stats = candidature_df.groupby('source').agg({
                'id': 'count',
                'answer_date': lambda x: x.notna().sum()
            }).reset_index()
            source_stats.columns = ['Source', 'Total', 'Responded']
            source_stats['Response Rate'] = (source_stats['Responded'] / source_stats['Total'] * 100).round(1)
            source_stats['Rate %'] = source_stats['Response Rate'].apply(lambda x: f"{x}%")
            st.dataframe(
                source_stats[['Source', 'Total', 'Responded', 'Rate %']],
                hide_index=True,
                width='stretch',
                column_config={
                    "Source": st.column_config.TextColumn("Source", width="medium"),
                    "Total": st.column_config.NumberColumn("Total Apps", width="small"),
                    "Responded": st.column_config.NumberColumn("Responses", width="small"),
                    "Rate %": st.column_config.TextColumn("Success Rate", width="medium")
                }
            )

        with col2:
            st.markdown("### 📅 Applications Timeline")
            # Group by month
            candidature_df['month'] = pd.to_datetime(candidature_df['date']).dt.to_period('M')
            timeline = candidature_df.groupby('month').size().reset_index(name='Applications')
            timeline['month'] = timeline['month'].astype(str)
            st.bar_chart(timeline.set_index('month'))

        # Additional insights
        st.markdown("---")
        st.markdown("### 💡 Quick Insights")
        insight_col1, insight_col2, insight_col3 = st.columns(3)

        with insight_col1:
            active_apps = candidature_df[candidature_df['closed'] == 'no']
            if len(active_apps) > 0:
                best_source = source_stats.loc[source_stats['Response Rate'].idxmax(), 'Source']
                st.info(f"**Best performing source:** {best_source}")

        with insight_col2:
            avg_days = candidature_df[candidature_df['answer'] == 'not yet']['days_since_application'].mean()
            if pd.notna(avg_days):
                st.info(f"**Avg pending time:** {int(avg_days)} days")

        with insight_col3:
            last_week = candidature_df[candidature_df['days_since_application'] <= 7]
            st.info(f"**Applications this week:** {len(last_week)}")

st.markdown("---")

# Visual progress funnel
if len(candidature_df) > 0:
    active_df = candidature_df[candidature_df['closed'] == 'no']
    if len(active_df) > 0:
        st.markdown("### 🎯 Application Funnel")
        funnel_col1, funnel_col2, funnel_col3, funnel_col4 = st.columns(4)

        total_active = len(active_df)
        responded_count = len(active_df[active_df['answer_date'].notna()])
        negotiation_count = len(active_df[active_df['status'] == 'negotiation'])
        accepted_count = len(active_df[active_df['answer'].str.lower().str.contains('accept', na=False)])

        with funnel_col1:
            st.metric("📤 Sent", total_active)
            st.progress(1.0)

        with funnel_col2:
            response_rate = responded_count / total_active if total_active > 0 else 0
            st.metric("💬 Responses", responded_count)
            st.progress(response_rate)

        with funnel_col3:
            negotiation_rate = negotiation_count / total_active if total_active > 0 else 0
            st.metric("🤝 Negotiation", negotiation_count)
            st.progress(negotiation_rate)

        with funnel_col4:
            success_rate = accepted_count / total_active if total_active > 0 else 0
            st.metric("✅ Accepted", accepted_count)
            st.progress(success_rate)

        st.markdown("---")

# Tab navigation
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0

t1, t2, t3 = st.columns(3)
with t1:
    if st.button("📋 Applications", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 0 else "secondary"):
        st.session_state.active_tab = 0
with t2:
    if st.button("📞 Contacts", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 1 else "secondary"):
        st.session_state.active_tab = 1
with t3:
    if st.button("🔗 Job Offers", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 2 else "secondary"):
        st.session_state.active_tab = 2

active_tab = st.session_state.active_tab
st.markdown("---")

if active_tab == 0:
    st.markdown("## 📋 Job Applications")

    # Quick rate summary
    if len(candidature_df) > 0:
        summary_col1, summary_col2, summary_col3 = st.columns([1, 1, 1])
        with summary_col1:
            avg_expected = candidature_df['expected_rate'].dropna().mean()
            if pd.notna(avg_expected):
                st.info(f"💰 Avg Expected: **€{int(avg_expected)}/day**")
        with summary_col2:
            avg_offered = candidature_df['offered_rate'].dropna().mean()
            if pd.notna(avg_offered):
                diff = avg_offered - avg_expected if pd.notna(avg_expected) else 0
                diff_text = f" (+€{int(diff)})" if diff > 0 else f" ({int(diff)})" if diff < 0 else ""
                st.info(f"💵 Avg Offered: **€{int(avg_offered)}/day**{diff_text}")
        with summary_col3:
            completed_contracts = len(candidature_df[candidature_df['start_date'].notna()])
            st.info(f"✅ Contracts Started: **{completed_contracts}**")

    # Add new application form
    with st.expander("➕ Add New Application", expanded=False):
        with st.form("add_application"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_company = st.selectbox("Company", options=company_list if company_list else [""])
                new_client = st.text_input("Client (optional)", placeholder="e.g., Servier, France TV").strip()
                new_job_link = st.text_input("Job Link", placeholder="https://...").strip()
                new_date = st.date_input("Application Date", value=datetime.now())
                new_source = st.selectbox("Source", ["linkedin", "job board", "referral", "direct contact", "other"])
            with col2:
                new_status = st.selectbox("Status", ["sent", "responded", "negotiation", "accepted", "rejected"])
                new_answer = st.selectbox("Answer", ["not yet", "refused", "accepted", "too late"])
                new_answer_date = st.date_input("Answer Date (optional)", value=None)
                new_duration = st.text_input("Duration", placeholder="e.g., 3 months, 6 months").strip()
            with col3:
                new_expected_rate = st.number_input("Expected Rate (€/day)", min_value=0, value=0, step=50)
                new_offered_rate = st.number_input("Offered Rate (€/day)", min_value=0, value=0, step=50)
                new_start_date = st.date_input("Start Date (optional)", value=None)
                new_notes = st.text_area("Notes", placeholder="Tech stack, requirements, etc.").strip()

            submitted = st.form_submit_button("Add Application", type="primary")
            if submitted and new_company:
                db = SessionLocal()
                try:
                    # Convert company name to company_id
                    if new_company not in contact_name_to_id:
                        st.error(f"Company '{new_company}' not found in contacts. Please add it to contacts first.")
                    else:
                        new_app = Application(
                            company_id=contact_name_to_id[new_company],
                            client=new_client if new_client else None,
                            job_link=new_job_link if new_job_link else None,
                            date=new_date,
                            source=new_source,
                            status=new_status,
                            answer=new_answer,
                            answer_date=new_answer_date if new_answer_date else None,
                            expected_rate=new_expected_rate if new_expected_rate > 0 else None,
                            offered_rate=new_offered_rate if new_offered_rate > 0 else None,
                            duration=new_duration if new_duration else None,
                            start_date=new_start_date if new_start_date else None,
                            notes=new_notes if new_notes else None,
                            closed='no'
                        )
                        db.add(new_app)
                        db.commit()
                        export_to_markdown()
                        generate_readable_view()
                        st.success("✅ Application added! (Markdown files updated)")
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()

    # Filter options
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        search_term = st.text_input("Search Company", "", placeholder="Type to search...", label_visibility="collapsed").strip()
        st.caption("🔍 Search")
    with col2:
        status_filter = st.selectbox("Answer Status", options=["All", "Pending", "Accepted", "Refused"], index=0, label_visibility="collapsed")
        st.caption("📊 Answer Status")
    with col3:
        source_filter = st.selectbox("Application Source",
            options=["All"] + sorted(candidature_df['source'].dropna().unique().tolist()) if len(candidature_df) > 0 else ["All"],
            index=0,
            label_visibility="collapsed")
        st.caption("📍 Source")
    with col4:
        st.write("")
        show_closed = st.checkbox("Closed", value=False)
        st.caption("🔒 Show")

    # Apply filters
    filtered_df = candidature_df.copy()

    if not show_closed and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['closed'].str.lower() != 'yes']

    if status_filter == "Pending" and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['answer'].str.lower().str.contains('not yet', na=False)]
    elif status_filter == "Accepted" and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['answer'].str.lower().str.contains('accept', na=False)]
    elif status_filter == "Refused" and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['answer'].str.lower().str.contains('refused', na=False)]

    if source_filter != "All" and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['source'] == source_filter]

    if search_term and len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['company'].str.contains(search_term, case=False, na=False)]

    # Show count and follow-up alerts with progress bar
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        # Show active filters
        active_filters = []
        if search_term:
            active_filters.append(f"🔍 '{search_term}'")
        if status_filter != "All":
            active_filters.append(f"📊 {status_filter}")
        if source_filter != "All":
            active_filters.append(f"📍 {source_filter}")
        if show_closed:
            active_filters.append("🔒 Closed")

        filter_text = " | ".join(active_filters) if active_filters else "No filters"
        st.caption(f"📋 Showing {len(filtered_df)} of {len(candidature_df)} • {filter_text}")
    with col2:
        if len(filtered_df) > 0:
            needs_followup = len(filtered_df[
                (filtered_df['answer'].str.lower().str.contains('not yet', na=False)) &
                (filtered_df['days_since_application'] > 7)
            ])
            if needs_followup > 0:
                st.warning(f"⚠️ {needs_followup} need follow-up (>7 days)")
    with col3:
        # Quick stats progress
        if len(candidature_df) > 0:
            closed_pct = len(candidature_df[candidature_df['closed'] == 'yes']) / len(candidature_df)
            st.progress(closed_pct, text=f"{int(closed_pct*100)}% closed")

    # Editable table
    if len(filtered_df) > 0:
        # Add color-coded status column for visual feedback
        def get_status_color(row):
            answer = str(row['answer']).lower()
            days = row['days_since_application']

            if 'accept' in answer:
                return '🟢 Accepted'
            elif 'refused' in answer:
                return '🔴 Refused'
            elif 'too late' in answer:
                return '⚫ Too Late'
            elif 'not yet' in answer:
                if days > 14:
                    return '🔴🔴 URGENT (>14d)'
                elif days > 7:
                    return '🟡 Follow-up (>7d)'
                else:
                    return '🟡 Pending'
            return answer

        filtered_df['_status_display'] = filtered_df.apply(get_status_color, axis=1)

        # Reset index to avoid hide_index warning with dynamic rows
        display_df = filtered_df.reset_index(drop=True)

        edited_candidature = st.data_editor(
            display_df,
            key="candidature_editor",
            width='stretch',
            num_rows="dynamic",
            disabled=["id", "days_since_application", "_status_display"],
            column_config={
                "_status_display": st.column_config.TextColumn(
                    "🎯 Status",
                    help="Visual status indicator with urgency",
                    width="small"
                ),
                "id": st.column_config.NumberColumn("#", width="small"),
                "company": st.column_config.SelectboxColumn("🏢 Company", options=company_list, required=True, width="medium"),
                "client": st.column_config.TextColumn("👔 Client", width="medium", help="Final client you work with (e.g., Servier, Aptenia)"),
                "job_link": st.column_config.LinkColumn("🔗", display_text="Link", width="small"),
                "date": st.column_config.DateColumn("📅 Date", format="YYYY-MM-DD", width="small"),
                "days_since_application": st.column_config.NumberColumn("⏱️ Days", help="Days since application (🟢<3d 🟡3-7d 🔴>7d)", width="small"),
                "source": st.column_config.SelectboxColumn("📍 Source", options=["linkedin", "job board", "referral", "direct contact", "other"], width="small"),
                "status": st.column_config.SelectboxColumn("📊 Status", options=["sent", "responded", "negotiation", "accepted", "rejected"], width="small"),
                "answer": st.column_config.SelectboxColumn("💬 Answer", options=["not yet", "refused", "accepted", "too late"], width="small"),
                "answer_date": st.column_config.DateColumn("📬 Ans", format="MM-DD", width="small"),
                "expected_rate": st.column_config.NumberColumn("💰 Exp", format="€%d/d", width="small"),
                "offered_rate": st.column_config.NumberColumn("💵 Off", format="€%d/d", width="small"),
                "duration": st.column_config.TextColumn("⏳ Dur", width="small"),
                "start_date": st.column_config.DateColumn("🚀 Start", format="MM-DD", width="small"),
                "notes": st.column_config.TextColumn("📝 Notes", width="medium"),
                "closed": st.column_config.SelectboxColumn("🔒", options=["yes", "no"], width="small"),
                "response_time": None,
            },
            column_order=["id", "_status_display", "company", "client", "job_link", "date", "days_since_application", "status", "answer", "source", "expected_rate", "offered_rate", "duration", "notes", "closed"],
            hide_index=True
        )

        # Buttons
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button("🔄 Reload", width='content'):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("💾 Save", type="primary", width='stretch'):
                db = SessionLocal()
                try:
                    # Build company name to ID mapping
                    contacts = db.query(Contact).all()
                    company_to_id = {c.company: c.id for c in contacts if c.company}

                    save_df = edited_candidature.drop(columns=['days_since_application', 'response_time', '_status_display'], errors='ignore')
                    for _, row in save_df.iterrows():
                        app = db.query(Application).filter(Application.id == row['id']).first()
                        if app:
                            # Convert company name to company_id
                            if row['company'] in company_to_id:
                                app.company_id = company_to_id[row['company']]

                            app.client = row['client'].strip() if pd.notna(row['client']) and row['client'] else None
                            app.job_link = row['job_link'].strip() if pd.notna(row['job_link']) and row['job_link'] else None
                            app.date = row['date'].date() if pd.notna(row['date']) else None
                            app.source = row['source'].strip() if pd.notna(row['source']) else None
                            app.status = row['status'].strip() if pd.notna(row['status']) else None
                            app.answer = row['answer'].strip() if pd.notna(row['answer']) else None
                            app.answer_date = row['answer_date'].date() if pd.notna(row['answer_date']) else None
                            app.expected_rate = row['expected_rate'] if pd.notna(row['expected_rate']) else None
                            app.offered_rate = row['offered_rate'] if pd.notna(row['offered_rate']) else None
                            app.duration = row['duration'].strip() if pd.notna(row['duration']) and row['duration'] else None
                            app.start_date = row['start_date'].date() if pd.notna(row['start_date']) else None
                            app.notes = row['notes'].strip() if pd.notna(row['notes']) and row['notes'] else None
                            app.closed = row['closed'].strip() if pd.notna(row['closed']) else None

                    db.commit()
                    export_to_markdown()
                    generate_readable_view()
                    st.cache_data.clear()
                    st.toast("✅ Saved & exported!", icon="💾")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()

        # Closed Applications Section
        closed_apps = candidature_df[candidature_df['closed'] == 'yes'].copy()
        if len(closed_apps) > 0:
            st.markdown("---")
            st.markdown("### 📦 Closed Applications")
            st.caption(f"Showing {len(closed_apps)} closed applications")

            # Add calculated columns
            closed_apps['_status_display'] = closed_apps.apply(get_status_color, axis=1)

            # Display closed applications (read-only)
            st.dataframe(
                closed_apps[['id', '_status_display', 'company', 'client', 'date', 'days_since_application',
                            'status', 'answer', 'answer_date', 'source', 'expected_rate',
                            'offered_rate', 'duration', 'notes']],
                column_config={
                    "_status_display": st.column_config.TextColumn("🎯 Status", width="small"),
                    "id": st.column_config.NumberColumn("#", width="small"),
                    "company": st.column_config.TextColumn("🏢 Company", width="medium"),
                    "client": st.column_config.TextColumn("👔 Client", width="medium"),
                    "date": st.column_config.DateColumn("📅 Date", format="YYYY-MM-DD", width="small"),
                    "days_since_application": st.column_config.NumberColumn("⏱️ Days", width="small"),
                    "source": st.column_config.TextColumn("📍 Source", width="small"),
                    "status": st.column_config.TextColumn("📊 Status", width="small"),
                    "answer": st.column_config.TextColumn("💬 Answer", width="small"),
                    "answer_date": st.column_config.DateColumn("📬 Ans", format="MM-DD", width="small"),
                    "expected_rate": st.column_config.NumberColumn("💰 Exp", format="€%d/d", width="small"),
                    "offered_rate": st.column_config.NumberColumn("💵 Off", format="€%d/d", width="small"),
                    "duration": st.column_config.TextColumn("⏳ Dur", width="small"),
                    "notes": st.column_config.TextColumn("📝 Notes", width="medium"),
                },
                hide_index=True,
                width='stretch'
            )
    else:
        st.info("No applications found")

if active_tab == 1:
    st.markdown("## Contacts")

    # Add new contact form
    with st.expander("➕ Add New Contact", expanded=False):
        with st.form("add_contact"):
            col1, col2 = st.columns(2)
            with col1:
                new_contact_company = st.text_input("Company Name", placeholder="Company").strip()
                new_firstname = st.text_input("First Name", placeholder="John").strip()
                new_lastname = st.text_input("Last Name", placeholder="Doe").strip()
            with col2:
                new_linkedin = st.text_input("LinkedIn Link", placeholder="https://www.linkedin.com/in/...").strip()
                new_phone = st.text_input("Phone Number", placeholder="+33 6 12 34 56 78").strip()

            submitted_contact = st.form_submit_button("Add Contact", type="primary")
            if submitted_contact and new_contact_company:
                db = SessionLocal()
                try:
                    new_contact = Contact(
                        company=new_contact_company,
                        firstname=new_firstname if new_firstname else None,
                        lastname=new_lastname if new_lastname else None,
                        linkedin_link=new_linkedin if new_linkedin else None,
                        phone_number=new_phone if new_phone else None,
                        updated_date=datetime.now().date()
                    )
                    db.add(new_contact)
                    db.commit()
                    export_to_markdown()
                    generate_readable_view()
                    st.success("✅ Contact added! (Markdown files updated)")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()

    # Display and edit contacts table
    st.markdown("### Current Contacts")

    if len(contact_df) > 0:
        # Reset index to avoid hide_index warning with dynamic rows
        display_contact_df = contact_df.reset_index(drop=True)

        edited_contacts = st.data_editor(
            display_contact_df,
            key="contact_editor",
            width='stretch',
            num_rows="dynamic",
            disabled=["id", "updated_date"],
            column_config={
                "id": st.column_config.NumberColumn("#", width="small"),
                "company": st.column_config.TextColumn("🏢 Company", width="medium", required=True),
                "firstname": st.column_config.TextColumn("👤 First Name", width="medium"),
                "lastname": st.column_config.TextColumn("👤 Last Name", width="medium"),
                "linkedin_link": st.column_config.LinkColumn("🔗 LinkedIn", display_text="Profile"),
                "phone_number": st.column_config.TextColumn("📞 Phone", width="medium"),
                "updated_date": st.column_config.DateColumn("📅 Updated", format="YYYY-MM-DD"),
            },
            hide_index=True,
        )

        # Buttons
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button("🔄 Reload Contacts", width='content', key="reload_contacts"):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("💾 Save", type="primary", width='stretch', key="save_contacts"):
                db = SessionLocal()
                try:
                    for _, row in edited_contacts.iterrows():
                        contact = db.query(Contact).filter(Contact.id == row['id']).first()
                        if contact:
                            contact.company = row['company'].strip() if pd.notna(row['company']) else None
                            contact.firstname = row['firstname'].strip() if pd.notna(row['firstname']) and row['firstname'] else None
                            contact.lastname = row['lastname'].strip() if pd.notna(row['lastname']) and row['lastname'] else None
                            contact.linkedin_link = row['linkedin_link'].strip() if pd.notna(row['linkedin_link']) and row['linkedin_link'] else None
                            contact.phone_number = row['phone_number'].strip() if pd.notna(row['phone_number']) and row['phone_number'] else None
                            # Note: No need to update applications - the FK relationship handles it automatically

                    db.commit()
                    export_to_markdown()
                    generate_readable_view()
                    st.toast("✅ Contacts saved!", icon="💾")
                    st.cache_data.clear()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()
    else:
        st.info("No contacts found")

if active_tab == 2:
    st.markdown("## 🔗 Job Offers")

    # Add form
    with st.expander("➕ Add Job Offer"):
        with st.form("add_offer"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_company = st.text_input("Company *", key="offer_company").strip()
            with col2:
                new_title = st.text_input("Job Title *", key="offer_title").strip()
            with col3:
                new_url = st.text_input("Job URL", key="offer_url").strip()
            submitted = st.form_submit_button("Add Offer", type="primary")
            if submitted and new_company and new_title:
                db = SessionLocal()
                try:
                    offer = JobOffer(
                        company=new_company,
                        title=new_title,
                        url=new_url if new_url else None,
                        date_added=datetime.now().date()
                    )
                    db.add(offer)
                    db.commit()
                    st.toast("✅ Offer added!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    db.close()

    # Display and edit offers
    if not offers_df.empty:
        st.markdown("### 📄 Offers")
        edited_offers = st.data_editor(
            offers_df,
            key="offers_editor",
            num_rows="dynamic",
            disabled=["id", "date_added"],
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "company": st.column_config.TextColumn("Company"),
                "title": st.column_config.TextColumn("Job Title"),
                "url": st.column_config.LinkColumn("Job URL"),
                "date_added": st.column_config.DateColumn("Date Added"),
            },
            hide_index=True
        )

        # Save button
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button("🔄 Reload Offers", width='content', key="reload_offers"):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("💾 Save", type="primary", width='stretch', key="save_offers"):
                db = SessionLocal()
                try:
                    for _, row in edited_offers.iterrows():
                        if pd.isna(row.get("id")):
                            continue
                        offer = db.query(JobOffer).filter(JobOffer.id == int(row["id"])).first()
                        if offer:
                            offer.company = row["company"].strip() if pd.notna(row["company"]) else None
                            offer.title = row["title"].strip() if pd.notna(row["title"]) else None
                            offer.url = row["url"].strip() if pd.notna(row["url"]) and row["url"] else None
                    db.commit()
                    export_to_markdown()
                    generate_readable_view()
                    st.toast("✅ Offers saved!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()

        # Promote to application
        st.markdown("### 🚀 Promote to Application")
        offer_labels = [f"{r['company']} — {r['title']}" for _, r in offers_df.iterrows()]
        selected_label = st.selectbox("Select offer to promote", offer_labels, key="promote_offer_select")
        selected_idx = offer_labels.index(selected_label)
        selected_offer = offers_df.iloc[selected_idx]

        col_promote, col_delete = st.columns(2)
        with col_promote:
            if st.button("🚀 Promote to Application", type="primary", use_container_width=True):
                db = SessionLocal()
                try:
                    # Find or create Contact
                    contact = db.query(Contact).filter(Contact.company == selected_offer["company"]).first()
                    if not contact:
                        contact = Contact(
                            company=selected_offer["company"],
                            updated_date=datetime.now().date()
                        )
                        db.add(contact)
                        db.flush()

                    # Create Application
                    app = Application(
                        company_id=contact.id,
                        job_link=selected_offer["url"] if selected_offer["url"] else None,
                        date=datetime.now().date(),
                        source="direct",
                        status="not yet",
                        answer="pending",
                        closed="no"
                    )
                    db.add(app)

                    # Delete offer
                    offer_obj = db.query(JobOffer).filter(JobOffer.id == int(selected_offer["id"])).first()
                    if offer_obj:
                        db.delete(offer_obj)

                    db.commit()
                    export_to_markdown()
                    generate_readable_view()
                    st.toast(f"✅ Promoted {selected_offer['company']} to Applications!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()

        with col_delete:
            if st.button("🗑️ Delete", use_container_width=True):
                db = SessionLocal()
                try:
                    offer_obj = db.query(JobOffer).filter(JobOffer.id == int(selected_offer["id"])).first()
                    if offer_obj:
                        company = offer_obj.company
                        db.delete(offer_obj)
                        db.commit()
                        export_to_markdown()
                        generate_readable_view()
                        st.toast(f"✅ Deleted {company}")
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()
    else:
        st.info("No job offers yet. Add one to get started!")
