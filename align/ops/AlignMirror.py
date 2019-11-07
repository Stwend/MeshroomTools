from .base import OBJECT_OT_MRAlignBaseOperator
from .. import functions
from ..._misc import global_functions

class OBJECT_OT_MRAlignMirrored(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.alignmirrored"
    bl_label = "Align Mirrored"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        self.prepareFull = True
        self.prepare_data(context)

        if self.data.active is None:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}


        functions.align_mirrored(self.data.active.source, self)

        return {'FINISHED'}
