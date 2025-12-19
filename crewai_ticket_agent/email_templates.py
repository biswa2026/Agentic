def build_email_and_escalation(data: dict) -> str:
    return f"""
<html>
<body>

<h2>Support Ticket Update</h2>

<p>Dear {data['customer_name']},</p>

<p>
Thank you for reaching out to us regarding the slow internet connection you have been experiencing.
We understand how frustrating this can be and appreciate your patience.
</p>

<p>Please provide the following information to help us proceed:</p>
<ul>
    <li>Your account number or service address</li>
    <li>Device type</li>
    <li>Any troubleshooting already attempted</li>
</ul>

<p>
We are committed to resolving this issue as quickly as possible.
</p>

<p>
Best regards,<br>
<strong>{data['agent_name']}</strong><br>
{data['agent_position']}<br>
{data['company_name']}<br>
{data['contact_info']}
</p>

<hr>

<h2>Escalation Report for Internal Review</h2>

<p><strong>Ticket ID:</strong> {data['ticket_id']}</p>
<p><strong>Customer Name:</strong> {data['customer_name']}</p>
<p><strong>Priority:</strong> {data['priority']}</p>
<p><strong>Category:</strong> {data['category']}</p>
<p><strong>Date Submitted:</strong> {data['submission_date']}</p>

<h3>Issue Description</h3>
<p>{data['issue_description']}</p>

<h3>Action Taken</h3>
<p>Initial response sent requesting additional information.</p>

<h3>Next Steps</h3>
<p>Escalate to Tier 2 support upon receipt of customer details.</p>

<p>
<strong>Prepared by:</strong><br>
{data['agent_name']}<br>
{data['agent_position']}<br>
{data['company_name']}<br>
{data['contact_info']}
</p>

</body>
</html>
"""
