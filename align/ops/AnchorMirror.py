from .base import OBJECT_OT_MRAlignBaseOperator

class OBJECT_OT_MRAnchorCreateMirrored(OBJECT_OT_MRAlignBaseOperator):

    bl_idname = "mr.mirroranchor"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        self.prepare_data(context)

        if not (self.data.active is None or self.data.active.is_locked):

            if not self.data.active.active_anchor is None:

                pos = self.data.active.active_anchor.source.matrix_world.translation.copy()
                pos.x *= -1

                side = self.data.active.active_anchor.side
                name = self.data.active.active_anchor.name

                side_inverted = abs(side - 2)

                if not side == 1:

                    for anchor in self.data.active.anchors:

                        #if a mirrored object exists, delete it
                        if anchor.side == side_inverted and anchor.name == name:
                            self.data.active.clear_anchor(anchor)
                            break

                    self.data.active.add_anchor(pos, name=name, side=side_inverted, locked=False, focus=True)

        return {'FINISHED'}
