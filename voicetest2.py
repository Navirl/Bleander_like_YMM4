# 必要なライブラリをインポート
import requests
import base64
import wave
import os

# エンジンのURLと話者IDを指定
engine_url = "http://localhost:50021"
speaker_id = 0

# 音声合成するテキストを指定
text = "こんにちは、VOICEVOXです。"

# テキストからアクセント句と音声パラメータを生成するAPIを呼び出す
query_url = engine_url + "/audio_query"
response = requests.post(query_url, json={"text": text, "speaker": str(speaker_id)})
if response.status_code != 200:
    print("Error: " + response.text)
    exit()

# アクセント句と音声パラメータを取得
audio_query = response.json()

# 話速とイントネーションの強弱を変更する
# 話速はspeedScaleで指定できる（デフォルトは1.0）
# イントネーションの強弱はintoneScaleで指定できる（デフォルトは1.0）
for accent_phrase in audio_query["accent_phrases"]:
    accent_phrase["speedScale"] = 1.5 # 話速を1.5倍にする
    accent_phrase["intoneScale"] = 0.5 # イントネーションの強弱を0.5倍にする

# 音声パラメータから音声波形を生成するAPIを呼び出す
synthesis_url = engine_url + "/synthesis"
response = requests.post(synthesis_url, json={"audio_query": audio_query, "speaker": str(speaker_id)})
if response.status_code != 200:
    print("Error: " + response.text)
    exit()

# 音声波形を取得
wav_data = base64.b64decode(response.json()["wav"])

# 音声波形をファイルに保存する
with wave.open("output.wav", "wb") as wav_file:
    wav_file.setnchannels(1) # チャンネル数
    wav_file.setsampwidth(2) # サンプル幅（バイト数）
    wav_file.setframerate(24000) # サンプリングレート（Hz）
    wav_file.writeframes(wav_data) # 音声データ

# 音声ファイルを再生する（Windowsの場合）
os.system("start output.wav")
