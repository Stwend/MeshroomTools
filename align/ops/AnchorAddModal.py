from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .base import OBJECT_OT_MRAlignBaseOperator
from ..._misc import external

class OBJECT_OT_MRAnchorAddModal(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.addanchor"
    bl_label = "Add Anchor"
    bl_options = {"REGISTER", "UNDO"}

    def modal(self, context, event):

        if event.type == 'ESC':
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            coord = event.mouse_region_x, event.mouse_region_y
            region = context.region
            region_3d = context.region_data

            ray_origin = region_2d_to_origin_3d(region, region_3d, coord) - self.data.active.source.location
            ray_view = region_2d_to_vector_3d(region, region_3d, coord)

            m = external.correct_worldmatrix(self.data.active.source)
            mi = m.inverted()

            ray_origin = ray_origin @ mi
            ray_view = ray_view @ mi

            ray_info = self.data.active.source.ray_cast(ray_origin, ray_view.normalized())

            if ray_info[0]:
                # add empty as pivot
                loc = ray_info[1] @ m + self.data.active.source.location

                self.data.active.add_anchor(loc)

                # reset selection
                context.view_layer.objects.active = self.data.active.source
                self.data.active.source.select_set(True)

            context.window.cursor_modal_restore()
            return {'FINISHED'}



        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.prepare_data(context)

        if self.data.active == None:

            self.report({'ERROR'}, "No active object found.")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('CROSSHAIR')
        return {'RUNNING_MODAL'}