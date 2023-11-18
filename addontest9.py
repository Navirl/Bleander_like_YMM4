bl_info = {
    "name": "Insert Text",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import requests
import json
import pathlib
import csv
import json

def extractCharaSettings(charadata):
    captiondata = {}
    captiondata["api"] = charadata["Voice"]["API"] 
    captiondata["styleid"] = charadata["VoiceParameter"]["StyleID"]
    captiondata ["speed"] = charadata["VoiceParameter"]["Speed"]
    captiondata ["pitch"] = charadata["VoiceParameter"]["Pitch"]
    captiondata ["intonation"] = charadata["VoiceParameter"]["Intonation"]
    captiondata ["atime"] = charadata["AdditionalTime"]
    captiondata ["posx"] = charadata["X"]["Values"][0]["Value"]
    captiondata ["posy"] = charadata["Y"]["Values"][0]["Value"]
    captiondata ["font"] = charadata["Font"]
    captiondata ["fontsize"] = charadata["FontSize"]["Values"][0]["Value"]
    captiondata["fontcolor"] = charadata["FontColor"]
    captiondata["style"] = charadata["Style"]
    captiondata["stylecolor"] = charadata["StyleColor"]
    captiondata["bold"] = charadata["Bold"]
    return captiondata

def hex_to_rgb(hex):
    h = hex.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4, 6))

def duplicate_strip(strip,context):
    dup_strip = context.scene.sequence_editor.sequences.new_effect(
        name=strip.name + ' copy',
        type='TEXT',
        channel=strip.channel+2, 
        frame_start=int(strip.frame_start),
        frame_end=strip.frame_final_end
    )
    dup_strip.text = strip.text
    dup_strip.transform.offset_x = strip.transform.offset_x
    dup_strip.transform.offset_y = strip.transform.offset_y
    dup_strip.font = strip.font
    dup_strip.use_bold = strip.use_bold
    dup_strip.font_size = strip.font_size
    dup_strip.color[0] = strip.color[0]
    dup_strip.color[1] = strip.color[1]
    dup_strip.color[2] = strip.color[2]
    dup_strip.color[3] = strip.color[3]
    return dup_strip

class VOICEVOX_OT_add_sound_strip(bpy.types.Operator):
    bl_idname = "voicevox.add_sound_strip"
    bl_label = "Add Sound Strip from VOICEVOX"

    def execute(self, context):
        with open('sample.csv', 'r') as c:
            # JSONファイルを開く
            with open('YukkuriMovieMaker.Settings.CharacterSettings.json', 'r', encoding='utf-8-sig') as j:
                reader = csv.reader(c)
                data = json.load(j)

                framestart = 1
                namedatacache = {}

                # 各行を処理
                for row in reader:
                    print(row)

                    if row[0] in namedatacache:
                        captiondata = namedatacache[row[0]]

                    else:
                        for item in data["Characters"]:
                            if item.get('Name') == row[0]:
                                captiondata = extractCharaSettings(item)
                                namedatacache[row[0]] = captiondata

                    # row[1]にテキスト

                    # 音声を生成するテキスト
                    host = 'localhost'
                    port = 50021
                    filepath=str(pathlib.Path('./audio.wav').resolve())

                    params = (
                        ('text', row[1]),
                        ('speaker', captiondata["styleid"])
                    )
                    
                    # 音声合成用の情報を引き出す
                    response1 = requests.post(
                        f'http://{host}:{port}/audio_query',
                        params=params
                    )

                    resjson = response1.json()
                    resjson["speedScale"] = captiondata["speed"] / 100.0
                    resjson["pitchScale"] = captiondata["pitch"] / 100.0
                    resjson["intonationScale"] = captiondata["intonation"] / 100.0
                    resjson["postPhonemeLength"] = captiondata["atime"]

                    # 音声合成
                    response2 = requests.post(
                        f'http://{host}:{port}/synthesis',
                        params=params,
                        data=json.dumps(resjson)
                    )

                    # レスポンスから音声ファイル（wav）を取得し保存
                    with open(filepath, "wb") as f:
                        f.write(response2.content)

                    # BlenderのVideo Sequencerに音声ファイルを追加
                    bpy.context.window.workspace = bpy.data.workspaces['Video Editing']
                    
                    # シーケンスエディタが存在しない場合は作成
                    if not bpy.context.scene.sequence_editor:
                        bpy.context.scene.sequence_editor_create()

                    seq = bpy.context.scene.sequence_editor

                    # パッキング
                    # サウンドストリップとして音声ファイルを追加
                    soundstrip = seq.sequences.new_sound("VoicevoxSound", filepath, 6, framestart)
                    framestart = soundstrip.frame_final_end
                    # すべてのストリップの選択を解除します
                    for s in seq.sequences_all:
                        s.select = False
                    # 追加したサウンドストリップを選択状態にします
                    seq.active_strip = soundstrip
                    bpy.ops.sound.pack()

                    # 字幕の追加
                    scene = context.scene
                    text_strip = scene.sequence_editor.sequences.new_effect(
                        name=row[1],
                        type='TEXT',
                        channel=soundstrip.channel+1, 
                        frame_start=int(soundstrip.frame_start),
                        frame_end=soundstrip.frame_final_end
                    )
                    # text_strip.text = scene.my_string_prop

                    # テキスト位置やフォントの設定
                    text_strip.text = row[1]
                    text_strip.transform.offset_x = captiondata["posx"]
                    text_strip.transform.offset_y = -(captiondata["posy"])
                    #add font
                    text_strip.use_bold = captiondata["bold"]
                    text_strip.font_size = captiondata["fontsize"]
                    textcolor = hex_to_rgb(captiondata["fontcolor"])
                    text_strip.color[0] = textcolor[1]
                    text_strip.color[1] = textcolor[2]
                    text_strip.color[2] = textcolor[3]
                    text_strip.color[3] = textcolor[0]

                    # 縁取り用事前複製
                    dup_strip = duplicate_strip(text_strip,context)

                    # 縁取り
                    text_outline = scene.sequence_editor.sequences.new_effect(
                        name=row[1] + 'ef',
                        type='GLOW',
                        channel=text_strip.channel + 1, 
                        frame_start=int(soundstrip.frame_start),
                        frame_end=soundstrip.frame_final_end,
                        seq1=text_strip
                    )

                    # s60 = o2.8
                    outline_width = (text_strip.font_size / 20) * (2.8/3)  # Dynamic outline width
                    text_outline.blur_radius = outline_width
                    text_outline.threshold = 0
                    text_outline.boost_factor = 1
                    text_outline.quality = 1
                    text_outline.use_only_boost = True
                    text_outline.color_multiply = 20  # Outline opacity
                    text_outline.blend_type = "ALPHA_OVER"

                    sequencer = bpy.ops.sequencer

                    seq.active_strip = text_outline
                    sequencer.strip_modifier_add(type="COLOR_BALANCE")
                    outlinecolor = hex_to_rgb(captiondata["stylecolor"])
                    text_outline.modifiers["Color Balance"].color_balance.gain[0] = outlinecolor[1]
                    text_outline.modifiers["Color Balance"].color_balance.gain[1] = outlinecolor[2]
                    text_outline.modifiers["Color Balance"].color_balance.gain[2] = outlinecolor[3]

                    # metastrip作成

                    text_strip.select = True
                    dup_strip.select = True
                    text_outline.select = True
                    soundstrip.select = True
                    sequencer.meta_make()

        return {'FINISHED'}

class VOICEVOX_PT_panel(bpy.types.Panel):
    bl_label = "VOICEVOX Panel"
    bl_idname = "VOICEVOX_PT_Panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        # layoutを取得
        layout = self.layout
        # 行作成
        row = layout.row()
        # 現在のsceneのmy_string_propプロパティを表示
        row.prop(context.scene, "my_string_prop")
        # オペレータ(ボタン)配置
        row.operator("voicevox.add_sound_strip")


def register():
    bpy.utils.register_class(VOICEVOX_OT_add_sound_strip)
    bpy.utils.register_class(VOICEVOX_PT_panel)
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(name="my_string_prop")
    bpy.types.Scene.csvfile = bpy.props.StringProperty(name="csvfile")

def unregister():
    del bpy.types.Scene.my_string_prop
    del bpy.types.Scene.csvfile 
    bpy.utils.unregister_class(VOICEVOX_OT_add_sound_strip)
    bpy.utils.unregister_class(VOICEVOX_PT_panel)
