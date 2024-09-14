from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_custom_email(subject, recipient_list, template_path, context):
    # Load the HTML template and render it with the provided context
    html_message = render_to_string(template_path, context)

    # Remove HTML tags to create a plaintext version of the email
    plain_message = strip_tags(html_message)

    # Send the email
    send_mail(
        subject,
        plain_message,
        'zahidislam375@gmail.com',  # Use a valid sender email address
        recipient_list,
        html_message=html_message,  # Attach the HTML version of the email
    )
