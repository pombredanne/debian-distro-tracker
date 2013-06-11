from __future__ import unicode_literals
from email import message_from_string
from email.iterators import typed_subpart_iterator
from itertools import islice

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from control.commands import CommandFactory
from control.commands import QuitCommand

MAX_ALLOWED_ERRORS = 5


def send_response(original_message, message_text, cc=None):
    message = EmailMessage(
        subject='Re: ' + original_message.get('Subject', 'Your mail'),
        to=[original_message['From']],
        cc=cc,
        from_email='owner@packages.qa.debian.org',
        headers={
            'X-Loop': 'pts@qa.debian.org',
        },
        body=message_text,
    )

    message.send()


def send_plain_text_warning(original_message):
    WARNING_MESSAGE = render_to_string('control/email-plaintext-warning.txt')
    send_response(original_message, WARNING_MESSAGE)


def process(message):
    msg = message_from_string(message)
    if 'X-Loop' in message and 'pts@qa.debian.org' in msg.get_all('X-Loop'):
        return
    # Get the first plain-text part of the message
    plain_text_part = [part
                       for part in islice(typed_subpart_iterator(msg,
                                                                 'text',
                                                                 'plain'),
                                          1)]
    if not plain_text_part:
        # There is no plain text in the email
        send_plain_text_warning(msg)
        return

    # Decode the plain text into a unicode string
    plain_text_part = plain_text_part[0]
    charset = plain_text_part.get_content_charset('ascii')
    try:
        text = plain_text_part.get_payload(decode=True).decode(charset)
    except UnicodeDecodeError:
        send_plain_text_warning(msg)
        return

    # Process the commands
    out = []
    errors = 0
    processed = 0
    cc = []
    factory = CommandFactory(msg)
    # Each line is a separate command
    for line in text.splitlines():
        line = line.strip()
        out.append('>' + line)

        args = line.split()
        command = factory.get_command_function(*args)

        if not command:
            errors += 1
            if errors == MAX_ALLOWED_ERRORS:
                break
        else:
            command_output = command()
            if not command_output:
                command_output = ''
            out.append(command_output)
            processed += 1

        if isinstance(command, QuitCommand):
            break

    # Send a response only if there were some commands processed
    if processed:
        send_response(msg, '\n'.join(out), cc)