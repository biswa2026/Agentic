import os
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

from sendgrid_mailer import send_email_sendgrid


def run():
    # -------------------------------
    # Load Crew configuration
    # -------------------------------
    with open("config/crew.yaml", "r") as f:
        crew_config = yaml.safe_load(f)

    # -------------------------------
    # Build Crew
    # -------------------------------
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

    # -------------------------------
    # Load tickets from Excel
    # -------------------------------
    df = pd.read_excel("config/ticket.xlsx", engine="openpyxl")

    print(f"\n=== Processing {len(df)} Tickets ===")

    results = []

    # -------------------------------
    # Process each ticket
    # -------------------------------
    for idx, row in df.iterrows():
        ticket_id = row["ticket_id"]
        customer_name = row["customer_name"]
        customer_email = row["email"]
        ticket_text = row["ticket_description"]

        print(f"\n---- Processing Ticket #{ticket_id} for {customer_name} ----")

        crew_input = {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "ticket": ticket_text
        }

        # -------------------------------
        # Run CrewAI
        # -------------------------------
        crew_output = crew.kickoff(crew_input)

        # IMPORTANT: Extract HTML string
        html_email = crew_output.raw

        if not isinstance(html_email, str):
            raise TypeError("Crew output is not a string HTML email")

        # -------------------------------
        # Send Email via SendGrid
        # -------------------------------
        subject = f"Support Update for Ticket #{ticket_id}"
        send_email_sendgrid(
            to_email=customer_email,
            subject=subject,
            html_content=html_email
        )

        # -------------------------------
        # Store results
        # -------------------------------
        results.append({
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "email": customer_email,
            "ticket_description": ticket_text,
            "html_email": html_email
        })

    # -------------------------------
    # Save all results
    # -------------------------------
    output_file = "results.xlsx"
    pd.DataFrame(results).to_excel(output_file, index=False)

    print(f"\n=== ALL TICKETS PROCESSED ===")
    print(f"📁 Results saved to {output_file}")
    print(f"📧 Emails sent successfully via SendGrid")


if __name__ == "__main__":
    run()
