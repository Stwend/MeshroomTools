import bpy
import numpy as np
import math
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

            if context.scene.mr_respect_mirrored:
                align.align_mirrored(obj_source, self, context)


            anchors_source = []
            anchors_target = []

            for a in context.view_layer.objects[obj_source['AnchorGroup']].children:
                if not a['AnchorName'] == 'NONE':
                    anchors_source.append(a)


            for obj_target in obj_targets:
                for a in context.view_layer.objects[obj_target['AnchorGroup']].children:
                    if not a['AnchorName'] == 'NONE':
                        anchors_target.append(a)

            #process target anchors, unify duplicates
            anchors_target = align.unify_targets(anchors_target, context)
            anchors_combined = []

            if context.scene.mr_respect_mirrored:

                anchors_source = align.align_prep_mirrored(anchors_source, context)
                anchors_target = align.align_prep_mirrored(anchors_target, context)



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

        context.view_layer.objects.active = objs_source[-1]

        return {'FINISHED'}


class OBJECT_OT_MRSideBtn(bpy.types.Operator):

    bl_idname = "mr.sidebutton"
    bl_label = "side"

    side = "None"

    def execute(self, context):

        obj = context.view_layer.objects.active
        obj['AnchorSide'] = self.side

        return {'FINISHED'}


class OBJECT_OT_MRSideBtnCenter(OBJECT_OT_MRSideBtn):
    bl_idname = "mr.sidebutton_c"
    bl_label = "Center"

    side = 1


class OBJECT_OT_MRSideBtnLeft(OBJECT_OT_MRSideBtn):
    bl_idname = "mr.sidebutton_l"
    bl_label = "Left"

    side = 0


class OBJECT_OT_MRSideBtnRight(OBJECT_OT_MRSideBtn):
    bl_idname = "mr.sidebutton_r"
    bl_label = "Right"

    side = 2


class OBJECT_OT_MRUnlockBtn(bpy.types.Operator):

    bl_idname = "mr.unlockbutton"
    bl_label = "Unlock"

    def execute(self, context):

        mobilize = []

        objs = context.selected_objects
        for obj in objs:
            if not obj.get('AnchorsLocked', None) is None:

                obj['AnchorsLocked'] = False
                mobilize.append(obj)

                for a in context.view_layer.objects[obj['AnchorGroup']].children:
                    a['AnchorsLocked'] = False
                    mobilize.append(a)

        for obj in mobilize:
            obj.lock_location = (False, False, False)
            obj.lock_rotation = (False, False, False)
            obj.lock_scale = (False, False, False)

        return {'FINISHED'}


class OBJECT_OT_MRLockBtn(bpy.types.Operator):
    bl_idname = "mr.lockbutton"
    bl_label = "Lock"

    def execute(self, context):

        immobilize = []

        objs = context.selected_objects
        for obj in objs:
            if not obj.get('AnchorsLocked', None) is None:

                obj['AnchorsLocked'] = True
                immobilize.append(obj)

                for a in context.view_layer.objects[obj['AnchorGroup']].children:
                    a['AnchorsLocked'] = True
                    immobilize.append(a)

        for obj in immobilize:
            obj.lock_location = (True, True, True)
            obj.lock_rotation = (True, True, True)
            obj.lock_scale = (True, True, True)


        return {'FINISHED'}

