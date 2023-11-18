bl_info = {
    "name": "Insert Text",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import requests
import json
#import wave
import pathlib

class VOICEVOX_OT_add_sound_strip(bpy.types.Operator):
    bl_idname = "voicevox.add_sound_strip"
    bl_label = "Add Sound Strip from VOICEVOX"

    def execute(self, context):
        # VOICEVOXのエンドポイント
        # VOICEVOX_API = "http://localhost:50021"

        # 音声を生成するテキスト
        text = "こんにちは、ワールド"

        host = 'localhost'
        port = 50021
        speaker = 1
        filepath=str(pathlib.Path('./audio.wav').resolve())

        params = (
            ('text', text),
            ('speaker', speaker),
        )
        response1 = requests.post(
            f'http://{host}:{port}/audio_query',
            params=params
        )
        headers = {'Content-Type': 'application/json',}
        response2 = requests.post(
            f'http://{host}:{port}/synthesis',
            headers=headers,
            params=params,
            data=json.dumps(response1.json())
        )

        # wf = wave.open(filepath, 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(2)
        # wf.setframerate(24000)
        # wf.writeframes(response2.content)
        # wf.close()

        # レスポンスから音声ファイル（wav）を取得し保存
        with open(filepath, "wb") as f:
            f.write(response2.content)

        # BlenderのVideo Sequencerに音声ファイルを追加
        bpy.context.window.workspace = bpy.data.workspaces['Video Editing']
        
        # シーケンスエディタが存在しない場合は作成
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()

        seq = bpy.context.scene.sequence_editor

        # サウンドストリップとして音声ファイルを追加
        soundstrip = seq.sequences.new_sound("VoicevoxSound", filepath, 4, 1)

        return {'FINISHED'}

class VOICEVOX_PT_panel(bpy.types.Panel):
    bl_label = "VOICEVOX Panel"
    bl_idname = "VOICEVOX_PT_Panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("voicevox.add_sound_strip")

def register():
    bpy.utils.register_class(VOICEVOX_OT_add_sound_strip)
    bpy.utils.register_class(VOICEVOX_PT_panel)

def unregister():
    bpy.utils.unregister_class(VOICEVOX_OT_add_sound_strip)
    bpy.utils.unregister_class(VOICEVOX_PT_panel)
