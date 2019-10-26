import bpy
import glob


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
        r = layout.row()
        r.alignment = "LEFT"
        l = context.object.get("AnchorsLocked", False)
        r.operator("mr.togglelockbtn", text=context.object.name, icon=("LOCKED" if l else "UNLOCKED"), emboss=False)
        layout.operator("mr.addanchor", text="Add Anchor")

        a = context.view_layer.objects.active
        n = a.get("AnchorName", None)

        if not n == None and a.select_get():

            s = a.get("AnchorSide", 1)

            b = layout.box()
            r_name = b.row()
            r_name.prop(a, '["AnchorName"]', text="Name")
            r_btn = b.row(align=True)
            r_btn.operator("mr.sidebutton_l", depress=s == 0)
            r_btn.operator("mr.sidebutton_c", depress=s == 1)
            r_btn.operator("mr.sidebutton_r", depress=s == 2)
            r_usage = b.row()
            r_usage.prop(context.scene, "mr_anchor_current_mirror", text="Mirroring")
            r_align = b.row()
            r_align.prop(context.scene, "mr_anchor_current_align", text="Aligning")


        layout.separator()
        layout.label(text="Mirror")
        layout.operator("mr.alignmirrored", text="Align Mirrored")
        layout.separator()
        layout.label(text="Align")
        layout.prop(context.scene, "mr_respect_mirrored", text="Mirrored")
        layout.operator("mr.alignanchors", text="Align Anchors")


