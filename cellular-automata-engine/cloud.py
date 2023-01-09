import json
import os

import boto3
import yandexcloud
from yandex.cloud.lockbox.v1.payload_service_pb2 import GetPayloadRequest
from yandex.cloud.lockbox.v1.payload_service_pb2_grpc import PayloadServiceStub


boto_session = None
storage_client = None
ymq_queue = None


def get_boto_session():
    global boto_session
    if boto_session is not None:
        return boto_session

    # initialize lockbox and read secret value
    yc_sdk = yandexcloud.SDK()
    channel = yc_sdk._channels.channel("lockbox-payload")
    lockbox = PayloadServiceStub(channel)
    response = lockbox.Get(GetPayloadRequest(secret_id=os.environ['SECRET_ID']))

    # extract values from secret
    access_key = None
    secret_key = None
    for entry in response.entries:
        if entry.key == 'ACCESS_KEY_ID':
            access_key = entry.text_value
        elif entry.key == 'SECRET_ACCESS_KEY':
            secret_key = entry.text_value
    if access_key is None or secret_key is None:
        raise Exception("secrets required")
    print("Key id: " + access_key)

    # initialize boto session
    boto_session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return boto_session


def get_storage_client():
    global storage_client
    if storage_client is not None:
        return storage_client

    storage_client = get_boto_session().client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        region_name='ru-central1'
    )
    return storage_client


def get_ymq_queue():
    global ymq_queue
    if ymq_queue is not None:
        return ymq_queue

    ymq_queue = get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(os.environ['YMQ_QUEUE_URL'])
    return ymq_queue


def upload_file(file_path, object_name):
    client = get_storage_client()
    bucket = os.environ['S3_BUCKET']
    client.upload_file(file_path, bucket, object_name)


def send_results_to_queue(filename, chat_id):
    bucket = os.environ['S3_BUCKET']
    url = get_storage_client().generate_presigned_url('get_object',
                                                      Params={'Bucket': bucket, 'Key': filename},
                                                      ExpiresIn=900)

    result = {
        "url": url,
        "chat_id": chat_id,
        "filename": filename
    }
    result_json = json.dumps(result)

    queue = get_ymq_queue()
    queue.send_message(MessageBody=result_json)
