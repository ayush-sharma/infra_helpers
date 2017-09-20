import requests
import json

if __name__ == '__main__':

    wekbook_url = '--your-webhook-url-goes-here--'

    data = {
        'text': 'I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.',
        'username': 'HAL',
        'icon_emoji': ':robot_face:'
    }

    response = requests.post(wekbook_url, data=json.dumps(
        data), headers={'Content-Type': 'application/json'})

    print('Response: ' + str(response.text))
    print('Response code: ' + str(response.status_code))
