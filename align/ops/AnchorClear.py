from .base import OBJECT_OT_MRAlignBaseOperator

class OBJECT_OT_MRAnchorClear(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.clearanchors"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        self.prepare_data(context)

        if not self.data.active is None:
            self.data.active.clear()

        return {'FINISHED'}