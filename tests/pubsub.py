from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    MessageMetadata,
    TopicPath,
)

project_number = 1061584703174
cloud_region = "europe-west1"
zone_id = "b"
topic_id = "nmea"

location = CloudZone(CloudRegion(cloud_region), zone_id)

topic_path = TopicPath(project_number, location, topic_id)

# PublisherClient() must be used in a `with` block or have __enter__() called before use.
with PublisherClient() as publisher_client:
    data = "Hello world!"
    api_future = publisher_client.publish(topic_path, data.encode("utf-8"))
    # result() blocks. To resolve API futures asynchronously, use add_done_callback().
    message_id = api_future.result()
    message_metadata = MessageMetadata.decode(message_id)
    print(
        f"Published a message to {topic_path} with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
    )