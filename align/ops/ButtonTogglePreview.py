import bpy


class OBJECT_OT_MRTogglePreviewBtn(bpy.types.Operator):

    bl_idname = "mr.togglepreviewbtn"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        mirror_name = context.object.get("MirrorPreview", None)
        is_valid = not (context.object.get("AlignmentAnchor", False) or mirror_name is None)

        if is_valid:

            try:
                obj_mirror = context.view_layer.objects[mirror_name]
            except:
                return {'FINISHED'}
                pass

            obj_mirror.hide_set(not obj_mirror.hide_get())
            context.object["MirrorHidden"] = obj_mirror.hide_get()

        return {'FINISHED'}
