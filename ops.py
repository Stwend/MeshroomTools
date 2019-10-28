import bpy
from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, region_2d_to_location_3d
from . import uv, align, glob, external



class OBJECT_OT_MRuvpack(bpy.types.Operator):

    bl_idname = "mr.uvpack"
    bl_label = "Pack UVs"

    def execute(self, context):

        glob.store(context)

        s = context.view_layer.objects.active
        uv.packUDIMS(s)

        return {'FINISHED'}


class OBJECT_OT_MRAnchorAddModal(bpy.types.Operator):

    bl_idname = "mr.addanchor"
    bl_label = "Add Anchor"

    parent = None


    def modal(self, context, event):

        if event.type == 'ESC':
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            coord = event.mouse_region_x, event.mouse_region_y
            region = context.region
            region_3d = context.region_data

            ray_origin = region_2d_to_origin_3d(region, region_3d, coord) - self.parent.location
            ray_view = region_2d_to_vector_3d(region, region_3d, coord)

            m = external.correct_worldmatrix(self.parent)
            mi = m.inverted()

            ray_origin = ray_origin @ mi
            ray_view = ray_view @ mi

            ray_info = self.parent.ray_cast(ray_origin, ray_view.normalized())


            if ray_info[0]:
                #add empty as pivot
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))

                target = context.view_layer.objects.active
                target.select_set(False)


                #initialize empty properties
                target.name = "New Anchor"
                target['AlignmentAnchor'] = True
                target['AnchorName'] = "NONE"
                target['AnchorSide'] = 1
                target['AnchorsLocked'] = False

                loc = ray_info[1] @ m + self.parent.location
                target.parent = self.grp
                target.matrix_world = Matrix.Translation(loc)

                target.lock_rotation = (True, True, True)
                target.lock_scale = (True, True, True)

                #reset selection
                context.view_layer.objects.active = self.parent
                self.parent.select_set(True)


            context.window.cursor_modal_restore()
            return {'FINISHED'}


        return {'RUNNING_MODAL'}


    def invoke(self, context, event):

        len_ok = len(context.selected_objects) == 1
        mesh_ok = context.object.type == 'MESH'
        mode_ok = context.object.mode == 'OBJECT'

        if not len_ok:
            self.report({'ERROR'}, "Only one object can be selected.")
            return {'CANCELLED'}

        if not mesh_ok:
            self.report({'ERROR'}, "Not a mesh object.")
            return {'CANCELLED'}

        if not mode_ok:
            if not len_ok:
                self.report({'ERROR'}, "Not in Object Mode.")
                return {'CANCELLED'}



        self.parent = context.object

        try:
            self.grp = context.view_layer.objects[self.parent['AnchorGroup']]

        except:
            self.generate_anchorgroup(context)
            pass


        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('CROSSHAIR')
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {'FINISHED'}


    def generate_anchorgroup(self, context):

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0),
                                 rotation=(0.0, 0.0, 0.0))
        self.grp = context.view_layer.objects.active
        self.grp.name += "_Anchors"
        self.grp.hide_viewport = True
        self.parent['AnchorGroup'] = self.grp.name
        self.parent['AnchorsLocked'] = False
        self.grp.parent = self.parent
        self.grp.matrix_world = Matrix.Identity(4)

        self.grp.select_set(False)
        self.parent.select_set(True)
        context.view_layer.objects.active = self.parent


class OBJECT_OT_MRAnchorAlign(bpy.types.Operator):

    bl_idname = "mr.alignanchors"
    bl_label = "Align Anchors"

    def execute(self, context):

        if len(context.selected_objects) == 0:
            self.report({'ERROR'}, "No mesh objects selected.")
            return {'CANCELLED'}

        is_mesh = context.object.type == 'MESH'


        f = False
        f2 = False
        for o in context.selected_objects:
            x = o.get("AnchorGroup", None)
            if not x is None:
                f = True

            x = o.get("AnchorsLocked", True)
            if not x:
                f2 = True

            if f and f2:
                break

        if not f:
            self.report({'ERROR'}, "Selection consists of unknown objects.")
            return {'CANCELLED'}

        source_locked = bool(context.object.get("AnchorsLocked", True))

        if not is_mesh:
            self.report({'ERROR'}, "No mesh objects selected.")
            return {'CANCELLED'}


        if source_locked:
            self.report({'ERROR'}, "Locked objects cannot be aligned.")
            return {'CANCELLED'}


        #Align all selected to locked

        objs_source = [o for o in context.selected_objects]

        for o in objs_source:
            if (o.get("AnchorGroup", None) is None) or (o.get("AnchorsLocked", True)):
                objs_source.remove(o)

        obj_targets = []

        for o in context.view_layer.objects:
            if not o.select_get():
                if not o.get("AnchorGroup", None) is None:
                    if o.get("AnchorsLocked", False):
                        obj_targets.append(o)

        for obj_source in objs_source:
            obj_source.rotation_mode = 'QUATERNION'


            anchors_source = []
            anchors_target = []

            for a in context.view_layer.objects[obj_source['AnchorGroup']].children:
                if not a['AnchorName'] == 'NONE':
                    if bool(a.get('AnchorUseAlign', True)):
                        anchors_source.append(a)


            for obj_target in obj_targets:
                for a in context.view_layer.objects[obj_target['AnchorGroup']].children:
                    if not a['AnchorName'] == 'NONE':
                        anchors_target.append(a)

            #process target anchors, unify duplicates
            anchors_target = align.unify_targets(anchors_target, context)
            anchors_combined = []

            for a in anchors_source:
                n = a['AnchorName']
                s = a['AnchorSide']
                for a2 in anchors_target:
                    n2 = a2['AnchorName']
                    s2 = a2['AnchorSide']
                    if n == n2 and s == s2:
                        anchors_combined.append([a, a2])
                        break

            l = len(anchors_combined)

            if l < 3:
                self.report({'ERROR'}, "At least 3 matching and locked anchors are needed.")
                glob.collect_garbage(context)
                continue

            A = []
            B = []

            for i in range(0, l):

                #transform into source space
                A.append(anchors_combined[i][0].matrix_world.translation)
                B.append(anchors_combined[i][1].matrix_world.translation)

            affine = align.affine_transform(A, B, 1)

            transform = Matrix.Identity(4)
            for n in range(0, 4):
                for m in range(0, 4):
                    transform[n][m] = affine[n][m]

            obj_source.matrix_world = transform @ obj_source.matrix_world
            glob.collect_garbage(context)

        for o in objs_source:
            o.select_set(True)

        context.view_layer.objects.active = objs_source[-1]

        return {'FINISHED'}


class OBJECT_OT_MRAlignMirrored(bpy.types.Operator):

    bl_idname = "mr.alignmirrored"
    bl_label = "Align Mirrored"

    def execute(self, context):

        if len(context.selected_objects) == 0:
            self.report({'ERROR'}, "No mesh objects selected.")
            return {'CANCELLED'}

        is_mesh = context.object.type == 'MESH'

        f = False
        f2 = False
        for o in context.selected_objects:
            x = o.get("AnchorGroup", None)
            if not x is None:
                f = True

            x = o.get("AnchorsLocked", True)
            if not x:
                f2 = True

            if f and f2:
                break

        if not f:
            self.report({'ERROR'}, "Selection consists of unknown objects.")
            return {'CANCELLED'}

        source_locked = bool(context.object.get("AnchorsLocked", True))

        if not is_mesh:
            self.report({'ERROR'}, "No mesh objects selected.")
            return {'CANCELLED'}

        if source_locked:
            self.report({'ERROR'}, "Locked objects cannot be aligned.")
            return {'CANCELLED'}

        # Align all selected to locked

        objs_source = [o for o in context.selected_objects]

        for o in objs_source:
            if (o.get("AnchorGroup", None) is None) or (o.get("AnchorsLocked", True)):
                objs_source.remove(o)


        for obj_source in objs_source:

            align.align_mirrored(obj_source, self, context)

        return {'FINISHED'}


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
    bl_label = "Copy From Selected"

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
        target["AnchorSide"] = source["AnchorSide"]
        if not source.get("AnchorUseMirror", None) is None:
            target["AnchorUseMirror"] = source["AnchorUseMirror"]
        if not source.get("AnchorUseAlign", None) is None:
            target["AnchorUseAlign"] = source["AnchorUseAlign"]

        return {'FINISHED'}



class OBJECT_OT_MRSelectBtn(bpy.types.Operator):

    bl_idname = "mr.selectbtn"
    bl_label = ""


    # 0=Select Group
    mode = bpy.props.IntProperty(default=0)


    def execute(self, context):

        isAnchor = context.object.get("AlignmentAnchor", False)
        isObject = not isAnchor and context.object.get("AnchorGroup", False)

        if not (isAnchor or isObject):
            return {'FINISHED'}

        #Select Group
        if self.mode == 0:

            if isObject:
                unaffected = [context.object]
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

            obj_mirror.hide_viewport = not obj_mirror.hide_viewport
            context.object["MirrorHidden"] = obj_mirror.hide_viewport


        return {'FINISHED'}


