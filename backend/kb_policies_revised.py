"""HR Helpdesk Bot KB loader and access-control helpers."""

from pathlib import Path
import csv


# ---------------------------------------------------------
# FILE LOCATIONS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

POLICIES_FILE = BASE_DIR / "policies_approved.csv"
FAQ_FILE = BASE_DIR / "hr_faq_approved_final.csv"
CONTACTS_FILE = BASE_DIR / "contacts.csv"


# ---------------------------------------------------------
# ROLES
# ---------------------------------------------------------

ROLES = [
    "intern",
    "associate",
    "store_manager",
    "vp",
    "ceo",
    "hr"
]


# ---------------------------------------------------------
# SENSITIVE TOPICS
# ---------------------------------------------------------

SENSITIVE_TERMS = {
    "harass",
    "harassment",
    "harassed",
    "sexual harassment",
    "retaliation",
    "retaliated",
    "termination",
    "terminated",
    "medical",
    "legal",
    "whistleblowing",
    "bully",
    "bullying",
    "bullied",
    "discrimination",
    "discriminatory",
    "hostile work environment",
    "stalking",
    "unwanted touching",
    "blackmail",
    "coercion",
    "quid pro quo",
    "racist",
    "sexist",
    "homophobia",
    "transphobia",
    "ageism",
    "ableism",
    "slur",
    "threat",
    "threatened",
    "kill",
    "hurt",
    "harm",
    "attack",
    "weapon",
    "gun",
    "knife",
    "suicide",
    "kill myself",
    "end my life",
    "fraud",
    "embezzlement",
    "bribery",
    "kickback",
    "insider trading",
    "corruption",
    "intellectual property",
    "data breach",
    "trade secrets",
    "eeoc",
    "osha",
    "department of labor",
    "lawsuit",
    "legal action",
    "union busting",
    "compliance breach",
    "drugs",
    "cocaine",
    "heroin",
    "methamphetamine",
    "narcotics",
    "intoxicated",
    "drunk at work",
    "substance abuse",
    "resign",
    "resigning",
    "quitting",
    "walk out",
    "strike",
    "unionize",
    "boycott",
    "competitor offer",
    "non-compete",
    "severance",
    "wrongful termination"
}


# ---------------------------------------------------------
# CSV LOADING
# ---------------------------------------------------------

def load_csv(path):
    """Load a CSV file and return a list of dictionaries."""

    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_policies():
    """Load approved HR policies."""
    return load_csv(POLICIES_FILE)


def load_faq():
    """Load approved HR FAQs."""
    return load_csv(FAQ_FILE)


def load_contacts():
    """Load HR contact information."""
    return load_csv(CONTACTS_FILE)


# ---------------------------------------------------------
# ROLE / REGION ACCESS CONTROL
# ---------------------------------------------------------

def allowed_for_user(row, role, region):
    """
    Check whether a policy/FAQ row is accessible
    to the given role and region.
    """

    roles = {
        x.strip().lower()
        for x in row.get("allowed_roles", "").split(";")
    }

    regions = {
        x.strip().lower()
        for x in row.get("regions", "").split(";")
    }

    role_allowed = (
        "all" in roles
        or role.lower() in roles
    )

    region_allowed = (
        "all" in regions
        or region.lower() in regions
    )

    return role_allowed and region_allowed


def filter_by_access(rows, role, region):
    """Return only rows accessible to the user."""

    return [
        row
        for row in rows
        if allowed_for_user(row, role, region)
    ]


# ---------------------------------------------------------
# SENSITIVE QUERY DETECTION
# ---------------------------------------------------------

def is_sensitive(query):
    """
    Detect sensitive HR topics before knowledge-base retrieval.
    """

    q = query.lower().strip()

    return any(
        term in q
        for term in SENSITIVE_TERMS
    )


# ---------------------------------------------------------
# POLICY CITATIONS
# ---------------------------------------------------------

def citation(row):
    """Create a citation for a policy row."""

    return (
        f'{row["policy_name"]} §{row["section"]} '
        f'(v{row["version"]}, effective {row["effective_date"]})'
    )


def citation_is_valid(chunk_id, retrieved_rows):
    """
    Verify that a citation refers to a chunk
    actually retrieved from the authorized dataset.
    """

    return any(
        row["chunk_id"] == chunk_id
        for row in retrieved_rows
    )