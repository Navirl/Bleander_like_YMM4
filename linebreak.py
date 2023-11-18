bl_info = {
    "name": "linebreak",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from bpy.types import Operator

class TEXT_OT_insert_newline(Operator):
    bl_idname = "text.insert_newline"
    bl_label = "Insert Newline"

    def execute(self, context):
        # 現在のカーソル位置に改行を挿入します
        bpy.ops.text.insert(text="\n")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(TEXT_OT_insert_newline)

    # Alt + Enterキーを押したときに改行を挿入するキーマップを作成します
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Text', space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new('text.insert_newline', 'RET', 'PRESS', alt=True)

def unregister():
    bpy.utils.unregister_class(TEXT_OT_insert_newline)

if __name__ == "__main__":
    register()
