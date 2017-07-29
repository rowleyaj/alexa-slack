import requests

from pylexa.response import PlainTextSpeech
from alexa_slack.response_builder import make_set_channel_response


def post_to_slack(channel, text, token):
    url = 'https://slack.com/api/chat.postMessage'
    res = requests.post(url, {
        'token': token,
        'channel': channel,
        'text': text,
        'as_user': False,
    })
    if res.json()['ok']:
        return PlainTextSpeech("Okay. Your message has been posted.")
    else:
        error = res.json().get('error')
        if error == 'channel_not_found':
            return make_set_channel_response(session.message, not_found=True)
        return PlainTextSpeech('Oh no, something went wrong.')

