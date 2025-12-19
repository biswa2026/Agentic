from crewai import Task
from agents import classifier_agent, responder_agent, escalation_agent,mail_agent

# Task: Classify ticket
classify_ticket = Task(
    description="Analyze the customer ticket text and assign category and priority.",
    expected_output="Category and priority level.",
    agent=classifier_agent
)

# Task: Generate response
generate_response = Task(
    description="Using the classified ticket info, draft a professional response.",
    expected_output="A draft reply ready to send to the customer.",
    agent=responder_agent
)

# Task: Escalate if needed
escalate_ticket = Task(
    description="If ticket is complex or high priority, generate escalation notes for human agent.",
    expected_output="Escalation report for internal review.",
    agent=escalation_agent
)

generate_mail = Task(
    description=(
        "Create a fully formatted HTML email using the results of previous tasks. "
        "Include:\n"
        "- Customer name\n"
        "- Ticket ID\n"
        "- Classification results\n"
        "- Support response\n"
        "- Escalation decision\n\n"
        "The email MUST be valid HTML containing <html>, <body>, <h2>, <p>, and <div> tags."
    ),
    agent=mail_agent,
    expected_output="A professionally styled HTML email ready to send."
)
