import subprocess
import os
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def convert_video(source, resolution, label):
    """
    Converts the video to the specified resolution and saves it with the specified label like => 480p, 720p and 1080p.
    """
    target = source.replace('.mp4', f'_{label}.mp4')
    cmd = 'ffmpeg -i "{}" -s {} -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, resolution, target)
    subprocess.run(cmd, shell=True)
    return target



def delete_original_file(file_path):
    print(f"Attempting to delete file: {file_path}")
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"Uploadfile deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    else:
        print(f"Uploadfile not found: {file_path}")



def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f"{request.scheme}://{request.get_host()}/api/activate/{uid}/{token}/"

    subject = 'Please Confirm your E-mail'
    from_email = 'noreply@streamada.com'
    recipient_list = [user.email]

    html_message = render_to_string('send_activation_link.html', {
        'user': user,
        'activation_link': activation_link
    })

    email = EmailMultiAlternatives(
        subject=subject,
        body=f'Hallo {user.first_name} {user.last_name},\nPlease click the link below to activate your account:\n{activation_link}',
        from_email=from_email,
        to=recipient_list
    )
    email.attach_alternative(html_message, "text/html")
    email.send()