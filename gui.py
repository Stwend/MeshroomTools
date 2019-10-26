from bpy.types import Panel

###--PANELS--###

class RENDER_PT_MRmainPanel(Panel):
    bl_idname = "mr.panel._PT_main"
    bl_label = "Meshroom"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"

    def draw(self, context):
        return


class RENDER_PT_MRUVPanel(Panel):
    bl_idname = "mr.panel._PT_uv"
    bl_label = "UV/Texture"
    bl_parent_id = "mr.panel._PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"

    def draw(self, context):
        layout = self.layout

        box = layout.split(factor=0.5)
        box.label(text="Resolution:")

        box.prop(context.scene, "mr_pack_res", text="")

        layout.operator("mr.uvpack", text="Pack")



class RENDER_PT_MRAlignPanel(Panel):
    bl_idname = "mr.panel._PT_align"
    bl_label = "Align"
    bl_parent_id = "mr.panel._PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"


    def draw(self, context):

        layout = self.layout

        isSelected = context.object.select_get()
        isLocked = context.object.get("AnchorsLocked", False)
        isAnchor = context.object.get("AlignmentAnchor", False)
        isObject = not isAnchor and context.object.get("AnchorGroup", False)

        layout.active = not isLocked

        if isSelected:
            rowInfo = layout.row()
            rowInfo.alignment = "LEFT"
            rowInfo.operator("mr.togglelockbtn", text=context.object.name, icon=("LOCKED" if isLocked else "UNLOCKED"), emboss=False)

            if isObject:

                if isLocked:
                    layout.label(text="OBJECT LOCKED")

                else:
                    r = layout.row()
                    r.prop(context.scene, "mr_anchor_default_mirror", text="Mirroring")
                    r.prop(context.scene, "mr_anchor_default_align", text="Aligning")
                    layout.operator("mr.addanchor", text="Add Anchor")

                    layout.separator()
                    layout.label(text="Mirror")
                    layout.operator("mr.alignmirrored", text="Align Mirrored")
                    layout.separator()
                    layout.label(text="Align")
                    layout.prop(context.scene, "mr_respect_mirrored", text="Mirrored")
                    layout.operator("mr.alignanchors", text="Align Anchors")



            elif isAnchor:

                if isLocked:
                    layout.label(text="ANCHOR LOCKED")
                else:

                    s = context.object.get("AnchorSide", 1)

                    r_name = layout.row().split(factor=0.33)
                    r_name.label(text="Name")
                    r_name.prop(context.object, '["AnchorName"]', text="")
                    r_btn = layout.row(align=True)
                    r_btn.operator("mr.sidebutton_l", depress=s == 0)
                    r_btn.operator("mr.sidebutton_c", depress=s == 1)
                    r_btn.operator("mr.sidebutton_r", depress=s == 2)
                    r_usage = layout.row()
                    r_usage.prop(context.scene, "mr_anchor_current_mirror", text="Mirroring")
                    r_usage.prop(context.scene, "mr_anchor_current_align", text="Aligning")
                    if len(context.selected_objects) == 2:
                        r_copy = layout.row()
                        r_copy.operator("mr.linkbtn")


