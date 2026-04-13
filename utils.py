import pandas as pd
from datetime import datetime
from models import SessionLocal, Contact, Application, JobOffer


def _truncate_url(url: str, max_length: int = 50) -> str:
    """Truncate URL intelligently for display."""
    if not url or len(url) <= max_length:
        return url

    # Simple truncation with ellipsis
    return url[:max_length-3] + '...'


def _create_aligned_table(headers: list, rows: list, col_widths: dict = None) -> str:
    """Create a nicely aligned markdown table with fixed column widths."""
    if not rows:
        return ""

    # Calculate column widths if not provided
    if col_widths is None:
        col_widths = {}
        for col in headers:
            col_widths[col] = len(col)
            for row in rows:
                col_widths[col] = max(col_widths[col], len(str(row.get(col, ''))))

    # Build table
    lines = []

    # Header row
    header_parts = []
    separator_parts = []
    for col in headers:
        width = col_widths[col]
        header_parts.append(f" {col:<{width}} ")
        separator_parts.append("-" * (width + 2))

    lines.append("|" + "|".join(header_parts) + "|")
    lines.append("|" + "|".join(separator_parts) + "|")

    # Data rows
    for row in rows:
        row_parts = []
        for col in headers:
            width = col_widths[col]
            value = str(row.get(col, ''))
            # Don't truncate URLs (link/linkedin columns) - let them overflow to stay clickable
            if col in ['link', 'linkedin']:
                # URLs keep full length, just pad the cell
                row_parts.append(f" {value:<{width}} ")
            else:
                # Truncate non-URL values if they exceed column width
                if len(value) > width:
                    value = value[:width-3] + '...'
                row_parts.append(f" {value:<{width}} ")
        lines.append("|" + "|".join(row_parts) + "|")

    return "\n".join(lines)


def export_to_markdown():
    """Export SQLite data to markdown table files with fixed-width columns."""
    db = SessionLocal()
    try:
        # Export contacts
        contacts = db.query(Contact).all()
        contacts_data = []
        for contact in contacts:
            contacts_data.append({
                'id': str(contact.id),
                'company': contact.company or '',
                'firstname': contact.firstname or '',
                'lastname': contact.lastname or '',
                'linkedin': contact.linkedin_link or '',
                'phone': contact.phone_number or '',
                'updated': contact.updated_date.strftime('%Y-%m-%d') if contact.updated_date else ''
            })

        # Define fixed column widths for contacts (linkedin at end to avoid breaking alignment)
        contact_widths = {
            'id': 3,
            'company': 20,
            'firstname': 12,
            'lastname': 12,
            'phone': 15,
            'updated': 10,
            'linkedin': 60  # Last column, can be longer
        }

        # Write contacts to markdown
        with open('contact.md', 'w', encoding='utf-8') as f:
            f.write("# 📞 Contacts\n\n")
            f.write(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

            # LinkedIn moved to last column
            headers = ['id', 'company', 'firstname', 'lastname', 'phone', 'updated', 'linkedin']
            table = _create_aligned_table(headers, contacts_data, contact_widths)
            f.write(table)
            f.write("\n\n")
            f.write(f"**Total contacts:** {len(contacts_data)}\n")

        # Export applications
        apps = db.query(Application).all()
        apps_data = []
        for app in apps:
            # Calculate days since application
            days_ago = ''
            if app.date:
                days = (datetime.now().date() - app.date).days
                days_ago = f"{days}d"

            # Get company name from contact relationship
            company_name = app.contact.company if app.contact else ''

            apps_data.append({
                'id': str(app.id),
                'company': company_name,
                'client': app.client or '',
                'link': app.job_link or '',
                'date': app.date.strftime('%Y-%m-%d') if app.date else '',
                'days': days_ago,
                'source': app.source or '',
                'status': app.status or '',
                'answer': app.answer or '',
                'ans_date': app.answer_date.strftime('%m-%d') if app.answer_date else '',
                'exp_rate': f"€{int(app.expected_rate)}" if app.expected_rate else '',
                'off_rate': f"€{int(app.offered_rate)}" if app.offered_rate else '',
                'duration': app.duration or '',
                'notes': app.notes or '',
                'closed': app.closed or ''
            })

        # Define fixed column widths for applications (link at end to avoid breaking alignment)
        app_widths = {
            'id': 3,
            'company': 18,
            'client': 18,
            'date': 10,
            'days': 5,
            'source': 13,
            'status': 11,
            'answer': 9,
            'ans_date': 8,
            'exp_rate': 8,
            'off_rate': 8,
            'duration': 10,
            'notes': 35,
            'closed': 6,
            'link': 60  # Last column, can be longer
        }

        # Write applications to markdown
        with open('candidature.md', 'w', encoding='utf-8') as f:
            f.write("# 📋 Job Applications\n\n")
            f.write(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

            # Summary stats
            active = len([a for a in apps if a.closed.lower() != 'yes'])
            pending = len([a for a in apps if 'not yet' in a.answer.lower()])
            accepted = len([a for a in apps if 'accept' in a.answer.lower()])

            f.write(f"**Summary:** {len(apps)} total | {active} active | {pending} pending | {accepted} accepted\n\n")

            # Link moved to last column
            headers = ['id', 'company', 'client', 'date', 'days', 'source', 'status', 'answer',
                      'ans_date', 'exp_rate', 'off_rate', 'duration', 'notes', 'closed', 'link']
            table = _create_aligned_table(headers, apps_data, app_widths)
            f.write(table)
            f.write("\n\n")

            # Add legend
            f.write("---\n\n")
            f.write("**Legend:**\n")
            f.write("- `days`: Days since application\n")
            f.write("- `ans_date`: Answer date (MM-DD format)\n")
            f.write("- `exp_rate`/`off_rate`: Expected/Offered daily rate in euros\n")
            f.write("- `link`: Job posting URL (last column to avoid breaking alignment)\n")

        # Export job offers
        offers = db.query(JobOffer).order_by(JobOffer.date_added.desc()).all()
        offers_data = []
        for offer in offers:
            offers_data.append({
                'id': str(offer.id),
                'company': offer.company or '',
                'title': offer.title or '',
                'url': offer.url or '',
                'date': offer.date_added.strftime('%Y-%m-%d') if offer.date_added else ''
            })

        # Define fixed column widths for offers
        offer_widths = {
            'id': 3,
            'company': 20,
            'title': 25,
            'date': 10,
            'url': 60  # Last column
        }

        # Write offers to markdown
        with open('job_offers.md', 'w', encoding='utf-8') as f:
            f.write("# 🔗 Job Offers\n\n")
            f.write(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

            headers = ['id', 'company', 'title', 'date', 'url']
            table = _create_aligned_table(headers, offers_data, offer_widths)
            f.write(table)
            f.write("\n\n")
            f.write(f"**Total offers:** {len(offers_data)}\n")

    finally:
        db.close()


def get_company_list() -> list[str]:
    """Get list of companies from contacts."""
    db = SessionLocal()
    try:
        contacts = db.query(Contact).all()
        companies = sorted(list(set(c.company for c in contacts if c.company)))
        return companies
    finally:
        db.close()


def generate_readable_view(output_file: str = 'VIEW.md'):
    """Generate a pretty, readable markdown view optimized for neovim."""
    db = SessionLocal()
    try:
        contacts = db.query(Contact).all()
        apps = db.query(Application).all()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Job Search Tracker - View\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")

            # Statistics
            total = len(apps)
            active = len([a for a in apps if a.closed.lower() != 'yes'])
            pending = len([a for a in apps if 'not yet' in a.answer.lower()])
            accepted = len([a for a in apps if 'accept' in a.answer.lower()])

            f.write("## 📊 Statistics\n\n")
            f.write(f"- **Total Applications:** {total}\n")
            f.write(f"- **Active:** {active}\n")
            f.write(f"- **Pending Response:** {pending}\n")
            f.write(f"- **Accepted:** {accepted}\n\n")
            f.write("---\n\n")

            # Active applications
            f.write("## 🔥 Active Applications\n\n")
            active_apps = sorted([a for a in apps if a.closed.lower() != 'yes'],
                                key=lambda x: x.date, reverse=True)

            if active_apps:
                for app in active_apps:
                    company_name = app.contact.company if app.contact else 'Unknown'
                    f.write(f"### {company_name}\n\n")
                    f.write(f"- **ID:** {app.id}\n")
                    f.write(f"- **Date:** {app.date.strftime('%Y-%m-%d') if app.date else 'N/A'}\n")
                    if app.job_link:
                        f.write(f"- **Link:** {app.job_link}\n")
                    f.write(f"- **Source:** {app.source}\n")
                    f.write(f"- **Status:** {app.status}\n")
                    f.write(f"- **Answer:** {app.answer}\n")
                    if app.expected_rate:
                        f.write(f"- **Expected Rate:** €{int(app.expected_rate)}/day\n")
                    if app.offered_rate:
                        f.write(f"- **Offered Rate:** €{int(app.offered_rate)}/day\n")
                    if app.duration:
                        f.write(f"- **Duration:** {app.duration}\n")
                    if app.notes:
                        f.write(f"- **Notes:** {app.notes}\n")
                    f.write("\n")
            else:
                f.write("*No active applications*\n\n")

            f.write("---\n\n")

            # Closed applications
            f.write("## ❌ Closed Applications\n\n")
            closed_apps = sorted([a for a in apps if a.closed.lower() == 'yes'],
                                key=lambda x: x.date, reverse=True)

            if closed_apps:
                for app in closed_apps:
                    company_name = app.contact.company if app.contact else 'Unknown'
                    f.write(f"- **{company_name}** ({app.date.strftime('%Y-%m-%d') if app.date else 'N/A'}) - {app.answer}\n")
            else:
                f.write("*No closed applications*\n")

            f.write("\n---\n\n")

            # Contacts
            f.write("## 📞 Contacts\n\n")
            if contacts:
                for contact in contacts:
                    name = f"{contact.firstname} {contact.lastname}".strip() if contact.firstname and contact.lastname else ''
                    f.write(f"### {contact.company}")
                    if name:
                        f.write(f" - {name}")
                    f.write("\n\n")
                    if contact.linkedin_link:
                        f.write(f"- **LinkedIn:** {contact.linkedin_link}\n")
                    if contact.phone_number:
                        f.write(f"- **Phone:** {contact.phone_number}\n")
                    f.write("\n")
            else:
                f.write("*No contacts*\n")

    finally:
        db.close()
