from .base import OBJECT_OT_MRAlignBaseOperator

class OBJECT_OT_MRRemoveMirrorPreview(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.deletepreview"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        self.prepare_data(context)

        self.data.active.clear_mirror()

        return {'FINISHED'}
