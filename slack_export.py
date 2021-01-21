#!/usr/bin/env python
import os
import json
import sys
import time

from slack_sdk import WebClient
from tqdm import tqdm


SLACK_TOKEN = os.getenv('SLACK_TOKEN')


def main():
    print('ASTORIA DIGITAL SLACK EXPORTER\n')

    api = WebClient(token=SLACK_TOKEN)

    # Gather all the channels
    channels = []
    for page in api.conversations_list(types='public_channel,private_channel',
                                       exclude_archived=True):
        channels += page.data['channels']

    for i, channel in enumerate(channels):
        # Print which channel we're processing
        print(f'> {i + 1}/{len(channels)}: {channel["name"]} ')
        sys.stdout.flush()

        # Try to join the channel
        try:
            api.conversations_join(channel=channel['id'])
        except Exception:
            pass

        # Gather all the messages on the channel
        messages = []
        for page in api.conversations_history(channel=channel['id'], limit=1000):
            messages += page.data['messages']
            time.sleep(1)

        # Go through all the messages and add any replies
        total_replies = 0
        for message in tqdm(messages, ncols=80):
            message['replies'] = []

            if 'reply_count' in message:
                for page in api.conversations_replies(channel=channel['id'], ts=message['ts']):
                    message['replies'] += page.data['messages']
                    time.sleep(1)

            total_replies += len(message['replies'])

        # Save the output to a file
        with open(f'archive/{channel["name"]}.json', 'w') as f:
            json.dump(messages, f)

        # Print how many messages we processed
        print(f'{len(messages) + total_replies} messages gathered\n')


if __name__ == "__main__":
    main()
