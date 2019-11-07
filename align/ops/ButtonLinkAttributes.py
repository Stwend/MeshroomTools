import bpy


class OBJECT_OT_MRLinkAttrsBtn(bpy.types.Operator):

    bl_idname = "mr.linkbtn"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    mirror = bpy.props.BoolProperty(default=False)

    def execute(self, context):

        sel = context.selected_objects
        source = None
        target = context.object

        for s in sel:
            if s.get("AlignmentAnchor", False):
                source = s
                break

        if source is None:
            self.report({'ERROR'}, "No anchor selected as source object.")
            return {'CANCELLED'}

        target["AnchorName"] = source["AnchorName"]

        if not self.mirror:
            target["AnchorSide"] = source["AnchorSide"]
        else:
            target["AnchorSide"] = abs(source["AnchorSide"] - 2)

        if context.scene.mr_mirror_translate:
            temp = source.matrix_world.translation.copy()
            temp.x = -temp.x
            target.matrix_world.translation = temp

        return {'FINISHED'}
