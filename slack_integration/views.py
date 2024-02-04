# slack_integration/views.py

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import hmac
import hashlib
from django.conf import settings

SLACK_SIGNING_SECRET = settings.SLACK_SIGNING_SECRET


@require_POST
@csrf_exempt
def slack_events(request):
    # Verify the request from Slack
    if not verify_slack_request(request):
        return HttpResponse('Request verification failed', status=403)

    event_data = json.loads(request.body.decode('utf-8'))

    if 'challenge' in event_data:
        # Verification request from Slack
        return JsonResponse({'challenge': event_data['challenge']})

    if 'event' in event_data:
        event = event_data['event']

        # Check if the event is a message and does not have a subtype (ignore bot messages, etc.)
        if event.get('type') == 'message' and 'subtype' not in event:
            # Log the message to Django console
            log_message_to_console(event.get('text'))

    return HttpResponse('', status=200)


def log_message_to_console(message):
    """Log the received message to the Django console."""
    print(f"Received Slack message: {message}")


def verify_slack_request(request):
    """Verify the request signature using your app's signing secret."""
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    request_body = request.body.decode('utf-8')
    sig_basestring = f"v0:{timestamp}:{request_body}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    slack_signature = request.headers.get('X-Slack-Signature', '')
    return hmac.compare_digest(my_signature, slack_signature)
