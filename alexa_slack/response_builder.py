from pylexa.response import PlainTextSpeech, Response


def make_set_channel_response(message=None, retry=False, not_found=False):
    text = 'What channel would you like to post your message to?'
    if retry:
        text = "Ok, let's try that again. {}".format(text)
    if not_found:
        text = "Sorry that channel wasn't found. Let's try that again. {}".format(text)
    speech = PlainTextSpeech(text)
    reprompt = PlainTextSpeech('Say the name of the channel you would like to post to')
    session = {
        'message': message,
    }
    return Response(
        speech=speech,
        reprompt=reprompt,
        should_end_session=False,
        session=session
    )


def make_set_message_response(channel, retry=False):
    text = 'What would you like to post?'
    if retry:
        text = "Ok, let's try that again. {}".format(text)
    return Response(
        speech=PlainTextSpeech(text),
        reprompt=PlainTextSpeech('Say the message you would like me to post'),
        session={'channel': channel},
        should_end_session=False,
    )


def make_confirm_message_response(message, channel):
    return Response(
        speech=PlainTextSpeech('Great. Would you like me to post {} to {}?'.format(message, channel)),
        session={'channel': channel, 'message': message, 'confirming_message': True},
        should_end_session=False,
    )
