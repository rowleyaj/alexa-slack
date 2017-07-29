from pylexa.app import handle_launch_request
from pylexa.intent import handle_intent
from pylexa.response import LinkAccountCard, PlainTextSpeech, Response

from alexa_slack.slack import post_to_slack
from alexa_slack.response_builder import make_confirm_message_response, make_set_channel_response, make_set_message_response

def require_access_token(func):
    def inner(request):
        if not request.access_token:
            return Response(
                speech=PlainTextSpeech('You must sign in first'),
                card=LinkAccountCard(),
            )
        else:
            return func(request)
    return inner


@handle_intent('SetChannel')
@require_access_token
def handle_set_channel_intent(request):
    message = request.session.get('message')
    channel = request.slots.get('channel')
    if not channel:
        return make_set_channel_response(message)
    elif message and channel:
        return make_confirm_message_response(message, channel)
    elif request.session.get('channel'):
        # if channel was already set, assume this was misinterpreted and should
        # be a SetMessage intent
        request.slots['message'] = channel
        return handle_set_message_intent(request)
    else:
        return Response(
            speech=PlainTextSpeech('Did you say {}?'.format(channel)),
            should_end_session=False,
            session={'confirming_channel': True, 'channel': channel}
        )


@handle_intent('SetMessage')
@require_access_token
def handle_set_message_intent(request):
    message = request.slots.get('message')
    channel = request.session.get('channel')
    if not message:
        return make_set_message_response(channel)
    elif message and channel:
        return make_confirm_message_response(message, channel)
    elif request.session.get('message'):
        # if message was already set, assume this was misinterpreted and should
        # be a SetChannel intent
        request.slots['channel'] = message
        return handle_set_channel_intent(request)
    else:
        return make_set_channel_response(message)


@handle_intent('SetChannelMessage')
@require_access_token
def handle_set_channel_message_intent(request):
    channel = request.slots.get('channel')
    message = request.slots.get('message')
    if not message:
        return make_set_message_response(channel)
    elif not channel:
        return make_set_channel_response(message)
    return make_confirm_message_response(message, channel)


@handle_intent('AMAZON.YesIntent')
@require_access_token
def handle_confirmation(request):
    if request.session.get('confirming_channel'):
        return make_set_message_response(request.session.get('channel'))
    elif request.session.get('confirming_message'):
        channel = request.session.get('channel')
        message = request.session.get('message')
        token = request.access_token
        return post_to_slack(channel, message, token)
    else:
        return Response(
            speech=PlainTextSpeech("I'm sorry, I didn't understand your request"),
            session=request.session,
            should_end_session=False,
        )


@handle_intent('AMAZON.NoIntent')
@require_access_token
def handle_no(request):
    if request.session.get('confirming_channel'):
        return make_set_channel_response(message=request.session.get('message'), retry=True)
    elif request.session.get('confirming_message'):
        return make_set_message_response(request.session.get('channel'), retry=True)
    else:
        return PlainTextSpeech('Goodbye')


@handle_intent('StartMessage')
@handle_launch_request
@require_access_token
def handle_start_message(request):
    return make_set_channel_response()


@handle_intent('unrecognized_intent')
def handle_unrecognized_intent(request):
    return PlainTextSpeech("I'm sorry, I didn't understand that")


@handle_intent('AMAZON.StopIntent')
@handle_intent('AMAZON.CancelIntent')
def handle_cancel_intent(request):
    return PlainTextSpeech('Goodbye')


@handle_intent('AMAZON.StartOverIntent')
@require_access_token
def handle_start_over_intent(request):
    return make_set_channel_response()


def get_help_text(session):
    channel = session.get('channel')
    message = session.get('message')
    default_text = (
        "You can begin by saying the name of the channel you would like to "
        "post to. After that, you'll be prompted for the message to post. "
        "Once you confirm the message and channel, your message will be "
        "posted. What channel would you like to post to?"
    )

    if not message and not channel:
        return default_text

    if session.get('confirming_channel'):
        return (
            "Do you want to post to the {} channel? Say yes if that channel is "
            "correct, or say no if you would like to specify another channel."
        ).format(channel)

    if session.get('confirming_message'):
        return (
            "Do you want to post {} to {}? Say yes if the channel and message "
            "are correct, or say no if you would like to specify another message."
        ).format(message, channel)

    if not message:
        return (
            "You can now say the message you want to post to {}. What message "
            "would you like to post?"
        ).format(channel)

    if not channel:
        return "What channel would you like to post your message to?"

    return default_text


@handle_intent('AMAZON.HelpIntent')
def handle_help_intent(request):
    text = get_help_text(request.session)
    return Response(
        speech=PlainTextSpeech(text),
        should_end_session=False,
        session=request.session,
    )
