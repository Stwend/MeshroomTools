import bpy
from mathutils import Matrix
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

from .._misc import global_functions, external
from . import functions

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


class OBJECT_OT_MRAnchorClear(bpy.types.Operator):

    bl_idname = "mr.clearanchors"
    bl_label = ""


    def execute(self, context):

        ob = context.object

        group = context.object.get("AnchorGroup", None)
        isObject = not group is None

        if isObject:

            grp = context.view_layer.objects[group]
            global_functions.tag_garbage(grp)

            for a in grp.children:
                global_functions.tag_garbage(a)

            global_functions.collect_garbage(context)

            ob.select_set(True)
            context.view_layer.objects.active = ob

        return {'FINISHED'}


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
            anchors_target = functions.unify_targets(anchors_target, context)
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
                global_functions.collect_garbage(context)
                continue

            A = []
            B = []

            for i in range(0, l):

                #transform into source space
                A.append(anchors_combined[i][0].matrix_world.translation)
                B.append(anchors_combined[i][1].matrix_world.translation)

            affine = functions.affine_transform(A, B, 1)

            transform = Matrix.Identity(4)
            for n in range(0, 4):
                for m in range(0, 4):
                    transform[n][m] = affine[n][m]

            obj_source.matrix_world = transform @ obj_source.matrix_world
            global_functions.collect_garbage(context)

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

            functions.align_mirrored(obj_source, self, context)

        return {'FINISHED'}


