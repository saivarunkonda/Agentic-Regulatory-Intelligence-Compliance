"""
Database initialization and session management.
"""
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "suraksha.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS regulations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    source      TEXT NOT NULL,
    url         TEXT,
    raw_text    TEXT,
    status      TEXT DEFAULT 'new',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS maps (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id INTEGER REFERENCES regulations(id),
    title         TEXT NOT NULL,
    description   TEXT,
    priority      TEXT DEFAULT 'medium',
    department    TEXT NOT NULL,
    deadline      TEXT,
    status        TEXT DEFAULT 'pending',
    evidence_url  TEXT,
    created_at    TEXT DEFAULT (datetime('now')),
    updated_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS departments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT UNIQUE NOT NULL,
    head             TEXT,
    contact          TEXT,
    compliance_score REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id    INTEGER REFERENCES maps(id),
    action    TEXT,
    actor     TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    notes     TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id     INTEGER REFERENCES maps(id),
    type       TEXT,
    message    TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    resolved   INTEGER DEFAULT 0
);
"""

SEED_SQL = """
INSERT OR IGNORE INTO departments (name, head, contact, compliance_score) VALUES
    ('Legal', 'Adv. Priya Sharma', 'legal@canarabank.com', 72.5),
    ('Risk', 'Rajesh Nair', 'risk@canarabank.com', 85.0),
    ('IT', 'Ankit Verma', 'it@canarabank.com', 60.0),
    ('Operations', 'Sunita Rao', 'ops@canarabank.com', 78.3),
    ('Audit', 'Deepak Mehta', 'audit@canarabank.com', 90.0);

INSERT OR IGNORE INTO regulations (id, title, source, url, raw_text, status) VALUES
(1, 'RBI Master Direction – KYC 2024 Update', 'RBI', 'https://rbi.org.in/kyc2024',
'All Regulated Entities (REs) shall ensure that all existing accounts are re-KYC compliant by March 31, 2024. Customer Due Diligence (CDD) must be completed for high-risk accounts within 30 days of identification. Non-compliance will attract penalties under section 11(3) of the PMLA. IT systems must be upgraded to support Aadhaar-based eKYC by June 30, 2024. Legal team to review all customer contracts for updated consent clauses.', 'processed'),

(2, 'SEBI AML Circular – Enhanced Monitoring', 'SEBI', 'https://sebi.gov.in/aml2024',
'All market intermediaries must implement enhanced transaction monitoring systems by September 2024. Suspicious Transaction Reports (STRs) must be filed within 24 hours of detection. Risk classification of customers must be reviewed quarterly. Operations team to maintain records for minimum 5 years. IT department must ensure system logs are tamper-proof.', 'processed'),

(3, 'GDPR Compliance Update – Data Retention', 'EU-GDPR', 'https://gdpr.eu/2024update',
'Financial institutions processing EU customer data must update data retention policies by Q3 2024. Data Protection Impact Assessments (DPIAs) are mandatory for new data processing activities. Legal team must appoint a Data Protection Officer. IT systems must implement right-to-erasure workflows within 72 hours of request. Audit logs of all data access must be maintained for 3 years.', 'new'),

(4, 'RBI – Cyber Security Framework Update', 'RBI', 'https://rbi.org.in/cyber2024',
'Banks must conduct comprehensive cyber risk assessments by December 2024. Multi-factor authentication mandatory for all internet banking transactions. Incident response plans must be tested bi-annually. IT Security team to implement SOC 2 Type II controls. Third-party vendor risk assessments required annually.', 'new');

INSERT OR IGNORE INTO maps (id, regulation_id, title, description, priority, department, deadline, status) VALUES
(1, 1, 'Re-KYC Compliance for Existing Accounts', 'Ensure all existing customer accounts complete re-KYC verification process as per RBI Master Direction 2024.', 'high', 'Operations', '2024-03-31', 'in_progress'),
(2, 1, 'High-Risk Account CDD within 30 Days', 'Complete Customer Due Diligence for all identified high-risk accounts within 30-day mandate.', 'critical', 'Risk', '2024-02-28', 'completed'),
(3, 1, 'Aadhaar eKYC IT System Upgrade', 'Upgrade core banking IT systems to support Aadhaar-based eKYC authentication flow.', 'high', 'IT', '2024-06-30', 'in_progress'),
(4, 1, 'Customer Contract Consent Review', 'Legal team to review and update all customer contracts with new consent clauses per KYC norms.', 'medium', 'Legal', '2024-04-30', 'pending'),
(5, 2, 'Transaction Monitoring System Implementation', 'Deploy enhanced AML transaction monitoring system for all market intermediary accounts.', 'critical', 'IT', '2024-09-30', 'pending'),
(6, 2, 'STR Filing Process within 24 Hours', 'Establish SOP for filing Suspicious Transaction Reports within 24-hour window.', 'high', 'Operations', '2024-08-15', 'in_progress'),
(7, 2, 'Quarterly Risk Classification Review', 'Implement quarterly review cycle for customer risk classifications.', 'medium', 'Risk', '2024-07-31', 'pending'),
(8, 3, 'Data Retention Policy Update (GDPR)', 'Update and publish new data retention policies compliant with GDPR EU directives.', 'high', 'Legal', '2024-09-30', 'pending'),
(9, 3, 'Data Protection Officer Appointment', 'Legal team to identify, appoint, and register a qualified Data Protection Officer.', 'critical', 'Legal', '2024-08-01', 'pending'),
(10, 4, 'Cyber Risk Assessment 2024', 'Conduct comprehensive cyber risk assessment across all IT systems and infrastructure.', 'high', 'IT', '2024-12-31', 'pending');

INSERT OR IGNORE INTO audit_logs (map_id, action, actor, timestamp, notes) VALUES
(2, 'Status → completed', 'Rajesh Nair', '2024-02-20 10:30:00', 'All 1,247 high-risk accounts reviewed and CDD completed'),
(2, 'Evidence Uploaded', 'Rajesh Nair', '2024-02-20 10:28:00', 'CDD completion report attached'),
(1, 'Status → in_progress', 'Sunita Rao', '2024-01-15 09:00:00', 'Started re-KYC campaign for existing accounts'),
(3, 'Status → in_progress', 'Ankit Verma', '2024-01-20 11:00:00', 'Development sprint started for eKYC integration');

INSERT OR IGNORE INTO alerts (map_id, type, message, created_at, resolved) VALUES
(4, 'overdue', 'MAP "Customer Contract Consent Review" is due in 7 days', '2024-04-23 08:00:00', 0),
(5, 'high_priority', 'Critical MAP "Transaction Monitoring System" has no progress yet', '2024-07-01 08:00:00', 0),
(9, 'overdue', 'Critical MAP "Data Protection Officer Appointment" is overdue', '2024-08-05 08:00:00', 0);
"""


async def init_db():
    """Initialize database schema and seed data."""
    async with engine.begin() as conn:
        for statement in SCHEMA_SQL.strip().split(";"):
            s = statement.strip()
            if s:
                await conn.execute(text(s))
        for statement in SEED_SQL.strip().split(";"):
            s = statement.strip()
            if s:
                try:
                    await conn.execute(text(s))
                except Exception:
                    pass
