import requests
import urllib.parse
import json
import wave

# 音素データ生成
text = urllib.parse.quote("これはテスト出力です")
response = requests.post("http://localhost:50021/audio_query?text=" + text + "&speaker=1")

# 音声合成
response = requests.post("http://localhost:50021/synthesis", headers={"Content-Type": "application/json"}, data=json.dumps(response.json()))

# WAVファイルとして保存
with open('output.wav', 'wb') as f:
    f.write(response.content)
