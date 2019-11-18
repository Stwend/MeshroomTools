from mathutils import Matrix
from .base import OBJECT_OT_MRAlignBaseOperator
from .. import functions
from ..._misc import global_functions

class OBJECT_OT_MRAnchorAlign(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.alignanchors"
    bl_label = "Align Anchors"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        self.prepareFull = True
        self.prepare_data(context)

        if self.data.active is None:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}


        #Align all selected to locked

        self.data.active.source.rotation_mode = 'QUATERNION'


        anchors_source = self.data.active.anchors
        anchors_target = []

        print(self.data.locked)

        for obj_proxy in self.data.locked:
            anchors_target.extend(obj_proxy.anchors)

        #process target anchors, unify duplicates
        anchors_target = functions.unify_targets(anchors_target)
        anchors_combined = []

        for a in anchors_source:
            for a2 in anchors_target:
                if a.name == a2.name and a.side == a2.side:
                    anchors_combined.append([a, a2])
                    break

        l = len(anchors_combined)

        if l < 3:
            self.report({'ERROR'}, "At least 3 matching and locked anchors are needed.")
            global_functions.collect_garbage()
            return {'CANCELLED'}

        sources = []
        targets = []

        for i in range(0, l):

            #transform into source space
            sources.append(anchors_combined[i][0].matrix.translation)
            targets.append(anchors_combined[i][1].matrix.translation)

        affine = functions.affine_transform(sources, targets)

        transform = Matrix.Identity(4)
        for n in range(0, 4):
            for m in range(0, 4):
                transform[n][m] = affine[n][m]

        self.data.active.source.matrix_world = transform @ self.data.active.source.matrix_world
        global_functions.collect_garbage()

        self.data.active.focus()

        return {'FINISHED'}