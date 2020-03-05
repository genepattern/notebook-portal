import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.urls import resolve
from rest_framework.permissions import BasePermission, SAFE_METHODS

from library import settings
from .models import Tag, ProjectAccess, SharingInvite


class IsOwnerOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )


def create_tags(tag_list):
    if tag_list is None or len(tag_list) == 0: return;
    for label in tag_list:
        label = label.lower()
        try:
            Tag.objects.get(label=label)
        except Tag.DoesNotExist:
            Tag(label=label, protected=False, pinned=False).save()


def create_access(username, project, owner=True):
    user = User.objects.get(username=username)
    access = ProjectAccess(user=user, project=project, owner=owner)
    access.save()


def model_from_url(cls, url):
    source_path = urlparse(url).path
    resolved_func, unused_args, resolved_kwargs = resolve(source_path)
    return cls.objects.get(pk=resolved_kwargs['pk'])


def is_email(email):
    if len(email) > 7:
        if re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email.lower()) is not None:
            return True
    return False


def get_owner(project):
    try: project = ProjectAccess.objects.get(project=project, owner=True)
    except ProjectAccess.DoesNotExist: return None
    return project.user.username


def merge_access(project, current_user, data):
    messages = []

    # Summarize the list of users with existing access
    existing_access = []
    for access in project.access.all():
        if access.user: existing_access.append(access.user.username)

    # Create new ProjectAccess objects as requested
    new_access = []
    for access in data:
        new_access.append(access['user'])
        if access['user'] not in existing_access:
            # Get the user, if available, and add it to the access list
            try:
                user = User.objects.get(username=access['user'])
                ProjectAccess(project=project, user=user, group=None, owner=False).save()

            # Otherwise, check to see if this is an email
            except User.DoesNotExist:
                if is_email(access['user']):
                    invite = SharingInvite(project=project, email=access['user'])
                    invite.save()
                    send_sharing_invite(access['user'], current_user.username, project.name, invite.token)
                    messages.append(f'Email invitation sent to {access["user"]}')
                    pass
                else:  # Otherwise, report error
                    messages.append(f'User {access["user"]} could not be found')
    project.save()

    # Remove old ProjectAccess objects as requested
    to_remove = [a for a in existing_access if a not in new_access]
    for username in to_remove:
        user = User.objects.get(username=username)
        if user != current_user:
            pa = ProjectAccess.objects.get(user=user, project=project)
            ProjectAccess.delete(pa)

    return messages


def send_sharing_invite(to_addr, sender_username, notebook_name, token):
    from_addr = getattr(settings, 'SENDER_EMAIL', 'gp-info@broadinstitute.org')
    send_email(from_addr, to_addr, "Notebook Sharing Invite - GenePattern Notebook Workspace",
        f"""<p>{sender_username} has invited you to share the following notebook on the GenePattern Notebook Workspace: {notebook_name}. 
        To accept, sign in and then click the link below.</p>
        <h5>GenePattern Notebook Workspace</h5>
        <p><a href="{settings.BASE_HUB_URL}">{settings.BASE_HUB_URL}</a></p>
        <h5>Click below to accept shared notebook</h5>
        <p><a href="{settings.ALLOWED_HOSTS[0]}/rest/projects/accept/?token={token}">{settings.ALLOWED_HOSTS[0]}/rest/projects/accept/?=token{token}</a></p>
        """)


def send_email(from_email, to_email, subject, message):
    tries = [0]

    def attempt_sending():
        tries[0] += 1

        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            server = smtplib.SMTP(settings.EMAIL_SERVER, 25)
            if hasattr(settings, 'EMAIL_USERNAME'):
                server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(from_email, to_email.split(', '), text)
            server.quit()
        except:
            if tries[0] < 2:
                time.sleep(3)
                attempt_sending()

    attempt_sending()