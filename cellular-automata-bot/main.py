import json
import logging
import os
import telebot

import cloud

bot = telebot.TeleBot(os.environ['TG_TOKEN'])


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'It works!')


@bot.message_handler(content_types=['document'])
def handle_request(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    logging.getLogger("bot").warning(f"downloaded_file: ${downloaded_file}")

    request_json = downloaded_file.decode("utf-8")
    request = json.loads(request_json)
    request['requestor'] = message.from_user.username
    request['chat_id'] = message.chat.id
    cloud.create_request(json.dumps(request))

    bot.send_message(message.chat.id, 'Request accepted')


def new_update_handler(update_json):
    update = telebot.types.Update.de_json(update_json)
    bot.process_new_updates([update])


def new_result_handler(result_json):
    result = json.loads(result_json)
    chat_id = result["chat_id"]
    result_url = result["url"]
    filename = result["filename"]

    bot.send_document(chat_id, result_url)
    cloud.delete_file(filename)


def handler(event, context):
    logging.getLogger("bot").warning(f"event: ${event}")
    logging.getLogger("bot").warning(f"context: ${context}")

    if "messages" in event:  # send result from queue
        for message in event["messages"]:
            message_json = message["details"]["message"]["body"]
            new_result_handler(message_json)
    else:  # receive request from user
        update_json = event['body']
        new_update_handler(update_json)

    return {
        'statusCode': 200,
        'body': ''
    }
