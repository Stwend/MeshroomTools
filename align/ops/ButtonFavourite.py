import bpy


class OBJECT_OT_MRToggleFavBtn(bpy.types.Operator):

    bl_idname = "mr.togglefavbtn"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        is_favd = bool(context.object.get("AnchorFav", False))
        is_anchor = bool(context.object.get("AlignmentAnchor", False))

        if is_anchor:

            context.object['AnchorFav'] = not is_favd

        return {'FINISHED'}
