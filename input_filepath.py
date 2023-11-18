bl_info = {
    "name": "Insert filepath",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from bpy.props import StringProperty

class SimpleOperator(bpy.types.Operator):
    bl_idname = "csv.get_file_path"
    bl_label = "Invoke File Dialog"

    filepath: StringProperty(
        name="File Path",      # プロパティ名
        default="",            # デフォルト値
        maxlen=1024,           # 最大文字列長
        subtype='DIR_PATH',   # サブタイプ
        description="",        # 説明文
    )

    def execute(self, context):
        display = "Selected file: %s" % (self.filepath)
        print(display)
        context.scene.filepath = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filepath")

class SimplePanel(bpy.types.Panel):
    bl_label = "File Dialog Panel"
    bl_idname = "SEQUENCER_PT_simple_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "File Dialog"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("csv.get_file_path")
        layout.prop(scene, "filepath")

def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(SimplePanel)
    bpy.types.Scene.filepath = StringProperty(name="File Path")

def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_class(SimplePanel)
    del bpy.types.Scene.filepath

if __name__ == "__main__":
    register()
