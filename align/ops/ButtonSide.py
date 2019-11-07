import bpy


class OBJECT_OT_MRSideBtn(bpy.types.Operator):

    bl_idname = "mr.sidebutton"
    bl_label = "side"
    bl_options = {"REGISTER", "UNDO"}

    side = bpy.props.IntProperty(default=1)

    def execute(self, context):

        obj = context.view_layer.objects.active
        obj['AnchorSide'] = self.side

        return {'FINISHED'}
