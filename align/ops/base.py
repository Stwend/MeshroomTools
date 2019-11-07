import bpy
from ..._misc import global_functions
from ..classes import AnchorSceneProxy

class OBJECT_OT_MRAlignBaseOperator(bpy.types.Operator):

    bl_idname = "mr.alignbase"
    bl_label = ""

    prepareFull = bpy.props.BoolProperty(default=False)

    def execute(self, context):
        return {'FINISHED'}


    def prepare_data(self, context):
        global_functions.store(context)
        self.data = AnchorSceneProxy(active_only=not self.prepareFull)
