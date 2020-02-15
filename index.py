import json
import logging

import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
        AbstractRequestHandler, AbstractExceptionHandler,
        AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

import config


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type('LaunchRequest')(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('launch request handler')

        text = "What's up?"

        handler_input.response_builder.speak(text).ask(text)

        return handler_input.response_builder.response


class BanTeamspeakIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name('BanTeamspeakIntent')(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('ban teamspeak intent handler')

        slots = handler_input.request_envelope.request.intent.slots

        logger.debug(f'slots: {slots}')

        name = str(slots['name'].value)

        headers = {'content-type': 'application/json', 'api-key': config.API_KEY}
        data = {'name': name}

        r = requests.post(config.BAN_TEAMSPEAK_URL, headers=headers, data=json.dumps(data))

        if r.status_code >= 200 and r.status_code <= 299:
            text = f'Successfully banned {name} from TeamSpeak.'
        else:
            logger.error(f'http status: {r.status_code}')
            logger.error(f'response: {r.text}')

            text = 'There was an error with the server.'

            if r.status_code == 501:
                text = f'{name} is not in the server.'

        handler_input.response_builder.speak(text)
        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class UpdateWeightIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name('UpdateWeightIntent')(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('update weight intent handler')

        slots = handler_input.request_envelope.request.intent.slots

        logger.debug(f'slots: {slots}')

        if not slots['weight']:
            text = 'What is your weight?'

            handler_input.response_builder.speak(text).ask(text)

            return handler_input.response_builder.response

        # have to do this because alexa doesn't allow float values, just integers
        full = int(slots['weight'].value)

        fraction = slots['fraction'].value

        if fraction:
            full = float(f'{full}.{fraction}')
        else:
            full = float(full)

        headers = {'content-type': 'application/json', 'api-key': config.API_KEY}
        data = {'weight': full}

        r = requests.post(config.UPDATE_WEIGHT_URL, headers=headers, data=json.dumps(data))

        if r.status_code >= 200 and r.status_code <= 299:
            text = f'Successfully updated weight to {full} pounds.'
        else:
            text = 'There was an error with the server.'

            logger.error(f'response: {r.text}')

        handler_input.response_builder.speak(text)
        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name('AMAZON.FallbackIntent')(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('fallback intent handler')

        text = 'What?'

        handler_input.response_builder.speak(text).ask(text)

        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (is_intent_name('AMAZON.CancelIntent')(handler_input) or
                is_intent_name('AMAZON.StopIntent')(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('cancel or stop intent handler')

        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type('SessionEndedRequest')(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.debug('session ended request handler')

        logger.info(f'session ended: {handler_input.request_envelope.request.reason}')

        return handler_input.response_builder.response


class ExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.debug('exception handler')

        logger.error(f'exception: {exception}', exc_info=True)

        handler_input.response_builder.speak('There was an error.')

        return handler_input.response_builder.response


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BanTeamspeakIntentHandler())
sb.add_request_handler(UpdateWeightIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(ExceptionHandler())

handler = sb.lambda_handler()
