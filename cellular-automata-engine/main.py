import logging
import time

import moviepy.editor as mpy

import cloud
import request_parser
from drawer import make_cellular_automata_frame_generator
import json


def generate_filename(request):
    return f"{request.type}_by_{request.requestor}_at_{int(time.time())}.{request.format}"


def receive_reqeust_handler(request_json):
    request = request_parser.create_request(request_json)
    filename = generate_filename(request)

    frame_generator = make_cellular_automata_frame_generator(request)

    clip = mpy.VideoClip(frame_generator, duration=request.duration)

    file_path = f"/tmp/{filename}"
    if request.format == 'gif':
        clip.write_gif(file_path, fps=request.fps)
    elif request.format == 'mp4':
        clip.write_videofile(file_path, fps=request.fps)
    else:
        pass  # FIXME

    cloud.upload_file(file_path, filename)
    cloud.send_results_to_queue(filename, request.chat_id)


def handler(event, context):
    logging.getLogger("engine").warning(f"event: ${event}")
    logging.getLogger("engine").warning(f"context: ${context}")

    if "messages" in event:
        for message in event["messages"]:
            request = json.loads(message["details"]["message"]["body"])
            receive_reqeust_handler(request)

    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'event': event,
                'context': context,
            },
            default=vars,
        ),
    }