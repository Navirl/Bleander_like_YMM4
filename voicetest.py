import json
import requests
import wave

def generate_wav(text, speaker=1, filepath='./audio.wav'):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )

    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )

    

    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers={"Content-Type": "application/json"},
        params=params,
        data=json.dumps(response1.json())
    )

    # wf = wave.open(filepath, 'wb')
    # wf.setnchannels(1)
    # wf.setsampwidth(2)
    # wf.setframerate(24000)
    # wf.writeframes(response2.content)
    # wf.close()

    with open("output.wav", "wb") as f:
        f.write(response2.content)

if __name__ == '__main__':
    text = 'こんにちは！'
    generate_wav(text)
