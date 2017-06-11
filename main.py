# -*- coding: utf-8 -*-

import json
import logging
import flask
import os
from google.cloud import translate
from google.appengine.api import urlfetch
import uuid

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Set log level
logging.basicConfig(level=logging.DEBUG)


@app.route("/webhook", methods=["POST"])
def main():
    req = flask.request.get_json(force=True)
    logging.info(json.dumps(req, indent=2, ensure_ascii=False))
    user_message = req["result"]["resolvedQuery"]
    translate_client = translate.Client()
    language_detection_result = translate_client.detect_language(user_message)
    # Translate user message if it is English
    translated_message = ""
    if language_detection_result["language"] == "en":
        translation_result = translate_client.translate(user_message, target_language="ja")
        translated_message = translation_result["translatedText"].encode("utf-8")
    res = {
        "speech": translated_message,
        "displayText": "App Engine が一晩でやってくれました",
        "data": {"slack": {"text": translated_message}},
        "contextOut": [],
        "source": "AppEngine",
        # "followupEvent": {
        #     "name": "followup_event_sample",
        #     "data": None
        # },
    }
    return flask.jsonify(res)


@app.route("/time", methods=["GET"])
def time_signal():
    apiai_token = os.getenv("APIAI_TOKEN")
    headers = {
        "Authorization": "Bearer {}".format(apiai_token),
        "Content-Type": "application/json"
    }
    payload = {
        "lang": "ja",
        "event": {
            "name": "time_signal",
            "data": None
        },
        "sessionId": "hoge"
    }
    result = urlfetch.fetch(
        url="https://api.api.ai/v1/query",
        payload=json.dumps(payload),
        method=urlfetch.POST,
        headers=headers
    )
    response = json.loads(result.content)
    logging.info(response)
    return flask.jsonify(response)

