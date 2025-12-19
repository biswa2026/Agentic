import yaml
import pandas as pd
from crewai import Crew

from agents import (
    classifier_agent,
    responder_agent,
    escalation_agent,
    mail_agent
)

from tasks import (
    classify_ticket,
    generate_response,
    escalate_ticket,
    generate_mail
)

from gmail_smtp_mailer import send_email_gmail
from email_templates import build_email_and_escalation


def run():
    # Load Crew config
    with open("config/crew.yaml", "r") as f:
        crew_config = yaml.safe_load(f)

    crew = Crew(
        name=crew_config.get("name", "Customer Support Crew"),
        description=crew_config.get("description", ""),
        agents=[
            classifier_agent,
            responder_agent,
            escalation_agent,
            mail_agent
        ],
        tasks=[
            classify_ticket,
            generate_response,
            escalate_ticket,
            generate_mail
        ],
        process="sequential",
        verbose=True
    )

    # Load tickets from Excel
    df = pd.read_excel("config/tickets.xlsx", engine="openpyxl")
    df=df.head(5)

    print(f"\n=== Processing {len(df)} Tickets ===")

    results = []

    for _, row in df.iterrows():
        ticket_id = row["ticket_id"]
        customer_name = row["customer_name"]
        customer_email = row["email"]

        email_data = {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "priority": row["priority"],
            "category": row["category"],
            "issue_description": row["ticket_description"],
            "submission_date": row["submission_date"],
            "agent_name": row["agent_name"],
            "agent_position": row["agent_position"],
            "company_name": row["company_name"],
            "contact_info": row["contact_info"]
        }

        html_email = build_email_and_escalation(email_data)

        send_email_gmail(
            to_email=customer_email,
            subject=f"Support Ticket Update - #{ticket_id}",
            html_content=html_email
        )

        results.append({
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "email": customer_email,
            "status": "Email Sent"
        })

    pd.DataFrame(results).to_excel("results.xlsx", index=False)

    print("\n✅ ALL TICKETS PROCESSED SUCCESSFULLY")


if __name__ == "__main__":
    run()
