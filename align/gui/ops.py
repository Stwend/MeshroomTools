import bpy

class OBJECT_OT_MRSideBtn(bpy.types.Operator):

    bl_idname = "mr.sidebutton"
    bl_label = "side"

    side = bpy.props.IntProperty(default=1)

    def execute(self, context):

        obj = context.view_layer.objects.active
        obj['AnchorSide'] = self.side

        return {'FINISHED'}



class OBJECT_OT_MRToggleLockBtn(bpy.types.Operator):
    bl_idname = "mr.togglelockbtn"
    bl_label = "Lock"

    def execute(self, context):

        toggle = []

        obj = context.object

        isLocked = context.object.get("AnchorsLocked", False)
        isAnchor = context.object.get("AlignmentAnchor", False)
        isObject = not isAnchor and context.object.get("AnchorGroup", False)

        if not isObject and not isAnchor:
            self.report({'ERROR'}, "Object not eligible.")
            return {'CANCELLED'}

        desiredLockState = not isLocked

        if isObject:
            toggle.append(obj)
            for a in context.view_layer.objects[obj['AnchorGroup']].children:
                    toggle.append(a)

        else:
            p = obj.parent.parent
            toggle.append(p)
            for a in context.view_layer.objects[p['AnchorGroup']].children:
                    toggle.append(a)


        for obj in toggle:
            obj['AnchorsLocked'] = desiredLockState
            obj.lock_location = (desiredLockState, desiredLockState, desiredLockState)
            obj.lock_rotation = (desiredLockState, desiredLockState, desiredLockState)
            obj.lock_scale = (desiredLockState, desiredLockState, desiredLockState)


        return {'FINISHED'}

class OBJECT_OT_MRLinkAttrsBtn(bpy.types.Operator):

    bl_idname = "mr.linkbtn"
    bl_label = ""

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



class OBJECT_OT_MRSelectBtn(bpy.types.Operator):

    bl_idname = "mr.selectbtn"
    bl_label = ""


    # 0=Select Group
    mode = bpy.props.IntProperty(default=0)


    def execute(self, context):

        mirror = context.object.get("MirrorPreview", None)

        is_anchor = context.object.get("AlignmentAnchor", False)
        is_object = not is_anchor and context.object.get("AnchorGroup", False)
        is_mirrored = is_object and not mirror is None

        if not (is_anchor or is_object):
            return {'FINISHED'}

        #Select Group
        if self.mode == 0:

            if is_object:
                unaffected = [context.object]
                if is_mirrored:
                    unaffected.append(context.view_layer.objects[mirror])
                unaffected.extend(t for t in context.view_layer.objects[context.object["AnchorGroup"]].children)
            else:
                p = context.object.parent.parent
                unaffected = [p]
                unaffected.extend(t for t in context.view_layer.objects[p["AnchorGroup"]].children)

            for o in context.view_layer.objects:
                o.hide_set(not o in unaffected)

        return {'FINISHED'}


class OBJECT_OT_MRTogglePreviewBtn(bpy.types.Operator):

    bl_idname = "mr.togglepreviewbtn"
    bl_label = ""


    def execute(self, context):

        mirror_name = context.object.get("MirrorPreview", None)
        isValid = not (context.object.get("AlignmentAnchor", False) or mirror_name is None)

        if isValid:

            try:
                obj_mirror = context.view_layer.objects[mirror_name]
            except:
                return {'FINISHED'}
                pass

            obj_mirror.hide_set(not obj_mirror.hide_get())
            context.object["MirrorHidden"] = obj_mirror.hide_get()


        return {'FINISHED'}