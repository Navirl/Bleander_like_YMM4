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

def extract_chara_setting(charadata):
    captiondata = {}
    captiondata["api"] = charadata["Voice"]["API"] 
    captiondata["styleid"] = charadata["VoiceParameter"]["StyleID"]
    captiondata["speed"] = charadata["VoiceParameter"]["Speed"]
    captiondata["pitch"] = charadata["VoiceParameter"]["Pitch"]
    captiondata["intonation"] = charadata["VoiceParameter"]["Intonation"]
    captiondata["atime"] = charadata["AdditionalTime"]
    captiondata["posx"] = charadata["X"]["Values"][0]["Value"]
    captiondata["posy"] = charadata["Y"]["Values"][0]["Value"]
    captiondata["font"] = charadata["Font"]
    captiondata["fontsize"] = charadata["FontSize"]["Values"][0]["Value"]
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

def make_sound_strip(text, chara_setting, frame_start, seq, context):
    # 音声を生成するテキスト
    host = 'localhost'
    port = 50021
    file_path=str(pathlib.Path('./audio.wav').resolve())

    params = (
        ('text', text),
        ('speaker', chara_setting["styleid"])
    )
    
    # 音声合成用の情報を引き出す
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )

    resjson = response1.json()
    resjson["speedScale"] = chara_setting["speed"] / 100.0
    resjson["pitchScale"] = chara_setting["pitch"] / 100.0
    resjson["intonationScale"] = chara_setting["intonation"] / 100.0
    resjson["postPhonemeLength"] = chara_setting["atime"]

    # 音声合成
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        params=params,
        data=json.dumps(resjson)
    )

    # レスポンスから音声ファイル（wav）を取得し保存
    with open(file_path, "wb") as f:
        f.write(response2.content)

    # BlenderのVideo Sequencerに音声ファイルを追加
    context.window.workspace = bpy.data.workspaces['Video Editing']

    # パッキング
    # サウンドストリップとして音声ファイルを追加
    sound_strip = seq.sequences.new_sound("VoicevoxSound", file_path, 6, frame_start)
    frame_start = sound_strip.frame_final_end
    # すべてのストリップの選択を解除します
    for s in seq.sequences_all:
        s.select = False
    # 追加したサウンドストリップを選択状態にします
    seq.active_strip = sound_strip
    bpy.ops.sound.pack()

    return sound_strip

def make_text_strip(text, chara_setting, soundstrip, seq, context):
    # 字幕の追加
    scene = context.scene
    text_strip = scene.sequence_editor.sequences.new_effect(
        name=text,
        type='TEXT',
        channel=soundstrip.channel+1, 
        frame_start=int(soundstrip.frame_start),
        frame_end=soundstrip.frame_final_end
    )
    # text_strip.text = scene.my_string_prop

    # テキスト位置やフォントの設定
    text_strip.text = text
    text_strip.transform.offset_x = chara_setting["posx"]
    text_strip.transform.offset_y = -(chara_setting["posy"])
    # add font absolute path
    # text_strip.font = bpy.data.fonts.load("GenEiMonoCode-Regular.ttf")
    text_strip.use_bold = chara_setting["bold"]
    text_strip.font_size = chara_setting["fontsize"]
    textcolor = hex_to_rgb(chara_setting["fontcolor"])
    # 透明度分のズレを補正
    text_strip.color[0] = textcolor[1]
    text_strip.color[1] = textcolor[2]
    text_strip.color[2] = textcolor[3]
    text_strip.color[3] = textcolor[0]

    # 縁取り用事前複製
    dup_strip = duplicate_strip(text_strip, context)

    # 縁取り
    text_outline = scene.sequence_editor.sequences.new_effect(
        name=text + 'ef',
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

    seq.active_strip = text_outline
    bpy.ops.sequencer.strip_modifier_add(type="COLOR_BALANCE")
    outlinecolor = hex_to_rgb(chara_setting["stylecolor"])
    text_outline.modifiers["Color Balance"].color_balance.gain[0] = outlinecolor[1]
    text_outline.modifiers["Color Balance"].color_balance.gain[1] = outlinecolor[2]
    text_outline.modifiers["Color Balance"].color_balance.gain[2] = outlinecolor[3]

    return {"text": text_strip, "dup": dup_strip, "outline": text_outline}

# 文字列拾ってテキストと音声作る関数
def make_meta_strip(text, chara_setting, frame_start, seq, context):

    sound_strip = make_sound_strip(text, chara_setting, frame_start, seq, context)
    text_strip = make_text_strip(text, chara_setting, sound_strip, seq, context)

    # metastrip作成
    # 最後に選んだstripのchannelに入る
    text_strip["text"].select = True
    text_strip["dup"].select = True
    text_strip["outline"].select = True
    sound_strip.select = True

    bpy.ops.sequencer.meta_make()


class VOICEVOX_OT_make_meta_strip(bpy.types.Operator):
    bl_idname = "voicevox.make_meta_strip"
    bl_label = "Make meta Strip with VOICEVOX"

    filepath: bpy.props.StringProperty(
        name="File Path",      # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        subtype='DIR_PATH',   # サブタイプ
        description="",        # 説明文
    )

    def execute(self, context):

        # シーケンスエディタが存在しない場合は作成
        if not context.scene.sequence_editor:
            context.scene.sequence_editor_create()

        seq = context.scene.sequence_editor

        script_file = context.scene.filepath

        # 台本ファイルを開く
        with open(script_file, 'r') as script:
            # JSONファイルを開く
            with open('YukkuriMovieMaker.Settings.CharacterSettings.json', 'r', encoding='utf-8-sig') as chara_data:
                script_csv = csv.reader(script)
                chara_data_json = json.load(chara_data)
                frame_start = 1
                chara_data_cache = {}

                # 台本の各行を処理
                for script_line in script_csv:
                    print(script_line)

                    # キャッシュ取る
                    if script_line[0] in chara_data_cache:
                        chara_setting = chara_data_cache[script_line[0]]

                    else:
                        for script in chara_data_json["Characters"]:
                            if script.get('Name') == script_line[0]:
                                chara_setting = extract_chara_setting(script)
                                chara_data_cache[script_line[0]] = chara_setting

                    # script_line[1]にテキスト
                    make_meta_strip(script_line[1], chara_setting, frame_start, seq, context)

        return {'FINISHED'}
    

class get_csv_file_path(bpy.types.Operator):
    bl_idname = "csv.get_file_path"
    bl_label = "Invoke File Dialog"

    filepath: bpy.props.StringProperty(
        name="File Path",      # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        subtype='DIR_PATH',   # サブタイプ
        description="",        # 説明文
    )

    def execute(self, context):
        context.scene.filepath = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VOICEVOX_PT_panel(bpy.types.Panel):
    bl_label = "VOICEVOX Panel"
    bl_idname = "VOICEVOX_PT_Panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        # layoutを取得
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "filepath")
        row.operator("csv.get_file_path")
        # 行作成
        row = layout.row()
        # 現在のsceneのmy_string_propプロパティを表示
        row.prop(context.scene, "my_string_prop")
        # オペレータ(ボタン)配置
        row.operator("voicevox.make_meta_strip")


def register():
    bpy.utils.register_class(VOICEVOX_OT_make_meta_strip)
    bpy.utils.register_class(VOICEVOX_PT_panel)
    bpy.utils.register_class(get_csv_file_path)
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(name="my_string_prop")
    bpy.types.Scene.csvfile = bpy.props.StringProperty(name="csvfile")
    bpy.types.Scene.filepath = bpy.props.StringProperty(name="File Path")

def unregister():
    del bpy.types.Scene.my_string_prop
    del bpy.types.Scene.csvfile
    del bpy.types.Scene.filepath
    bpy.utils.unregister_class(VOICEVOX_OT_make_meta_strip)
    bpy.utils.unregister_class(VOICEVOX_PT_panel)
    bpy.utils.unregister_class(get_csv_file_path)
