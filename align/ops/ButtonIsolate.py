import bpy


class OBJECT_OT_MRSelectBtn(bpy.types.Operator):

    bl_idname = "mr.selectbtn"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    # 0=Select Group
    mode = bpy.props.IntProperty(default=0)

    def execute(self, context):

        mirror = context.object.get("MirrorPreview", '')

        is_anchor = context.object.get("AlignmentAnchor", False)
        is_object = not is_anchor and context.object.get("AnchorGroup", False)
        is_mirrored = is_object and not mirror == ''

        if not (is_anchor or is_object):
            return {'FINISHED'}

        if self.mode == 0:

            if is_object:
                unaffected = [context.object]
                if is_mirrored:
                    try:
                        unaffected.append(context.view_layer.objects[mirror])
                    except:
                        pass
                try:
                    unaffected.extend(t for t in context.view_layer.objects[context.object["AnchorGroup"]].children)
                except:
                    pass
            else:
                p = context.object.parent.parent
                unaffected = [p]
                unaffected.extend(t for t in context.view_layer.objects[p["AnchorGroup"]].children)

            for o in context.view_layer.objects:
                o.hide_set(not o in unaffected)

        return {'FINISHED'}
