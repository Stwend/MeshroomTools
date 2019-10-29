import bpy

from . import functions
from misc import global_functions


class OBJECT_OT_MRuvpack(bpy.types.Operator):

    bl_idname = "mr.uvpack"
    bl_label = "Pack UVs"

    def execute(self, context):

        global_functions.store(context)

        s = context.view_layer.objects.active
        functions.packUDIMS(s)

        return {'FINISHED'}