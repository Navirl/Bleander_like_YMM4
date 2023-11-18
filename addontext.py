bl_info = {
    "name": "Insert Text",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy

class SimpleOperator(bpy.types.Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    
    text = bpy.props.StringProperty(name="Text")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'SEQUENCE_EDITOR'

    def execute(self, context):
        scene = context.scene
        text_strip = scene.sequence_editor.sequences.new_effect(
            name="Text Strip",
            type='TEXT',
            channel=1, 
            frame_start=1,
            frame_end=100
        )
        # text_strip.text = self.text
        text_strip.text = scene.my_string_prop
        return {'FINISHED'}

class SimpleOperatorPanel(bpy.types.Panel):
    bl_label = "Simple Operator Panel"
    bl_idname = "OBJECT_PT_simple_operator"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "my_string_prop")
        row.operator("object.simple_operator", text="Insert")

def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(SimpleOperatorPanel)
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(name="Text")

def unregister():
    bpy.utils.unregister_class(SimpleOperatorPanel)
    bpy.utils.unregister_class(SimpleOperator)
    del bpy.types.Scene.my_string_prop

if __name__ == "__main__":
    register()
