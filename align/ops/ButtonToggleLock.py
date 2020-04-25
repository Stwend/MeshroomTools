import bpy

class OBJECT_OT_MRToggleLockBtn(bpy.types.Operator):
    bl_idname = "mr.togglelockbtn"
    bl_label = "Lock"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        toggle = []

        obj = context.object

        is_locked = context.object.get("AnchorsLocked", False)
        is_anchor = context.object.get("AlignmentAnchor", False)
        is_object = not is_anchor and context.object.get("AnchorGroup", False)

        if not is_object and not is_anchor:
            self.report({'ERROR'}, "Object not eligible.")
            return {'CANCELLED'}

        desired_lock_state = not is_locked

        if is_object:
            toggle.append(obj)
            try:
                for a in context.view_layer.objects[obj['AnchorGroup']].children:
                    toggle.append(a)
                    a.hide_select = desired_lock_state
            except:
                pass

        else:
            p = obj.parent.parent
            toggle.append(p)
            for a in context.view_layer.objects[p['AnchorGroup']].children:
                    toggle.append(a)
                    a.hide_select = desired_lock_state

        for obj in toggle:
            obj['AnchorsLocked'] = desired_lock_state
            obj.lock_location = (desired_lock_state, desired_lock_state, desired_lock_state)
            obj.lock_rotation = (desired_lock_state, desired_lock_state, desired_lock_state)
            obj.lock_scale = (desired_lock_state, desired_lock_state, desired_lock_state)
            #obj.hide_select = desired_lock_state

        return {'FINISHED'}
