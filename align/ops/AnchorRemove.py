from .base import OBJECT_OT_MRAlignBaseOperator

class OBJECT_OT_MRAnchorRemove(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.removeanchor"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        target = context.object

        self.prepare_data(context)

        self.data.active.clear_anchor(target)

        return {'FINISHED'}