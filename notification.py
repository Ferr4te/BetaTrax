from django.core.mail import send_mail
from django.conf import settings

# This send email notification to the tester when the status of a defect report changes
# In each PBI that change the status you can use this function to send email notification to the tester
# Get old_status with old_status = defect.status before updating the status
# Call send_defect_status_change_notification(defect, old_status, defect.status) after updating the status
# The email and its content will be shown in the terminal

def send_defect_status_change_notification(defect, old_status, new_status):
    if not defect.tester_email:
        return

    subject = f"Defect #{defect.id} status changed: {old_status} to {new_status}"
    message = (
        f"Defect: {defect.title}\n"
        f"Description: {defect.description}\n"
        f"New status: {new_status}\n"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [defect.tester_email],
        fail_silently=False,
    )

# Notify the tester who reported the original defect that their report has been duplicated by another defect report
def send_duplicate_notification(original_defect, duplicate_defect):
    if not original_defect.tester_email:
        return

    subject = f"Defect #{original_defect.id} has been duplicated"
    message = (
        f"A duplicate defect report has been linked to your original report:\n\n"
        f"Original defect: {original_defect.title} (ID: {original_defect.id})\n"
        f"Duplicate defect: {duplicate_defect.title} (ID: {duplicate_defect.id})\n"
        f"Current status of duplicate: {duplicate_defect.status}\n\n"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [original_defect.tester_email],
        fail_silently=False,
    )