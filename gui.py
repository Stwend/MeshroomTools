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

        layout.separator()
        layout.operator("mr.addanchor", text="Add Anchor")
        layout.separator()
        b = layout.box()
        b.operator("mr.alignmirrored", text="Align Mirrored")
        b = layout.box()
        b.prop(context.scene, "mr_respect_mirrored", text="Mirrored")
        b.operator("mr.alignanchors", text="Align Anchors")

        a = context.view_layer.objects.active
        n = a.get("AnchorName", None)
        o = a.get("AnchorGroup", None)

        if not n == None and a.select_get():

            s = a.get("AnchorSide", 1)
            c = a.get("AnchorConfidence", 1)

            layout.separator()
            layout.label(text="Anchor")
            b = layout.box()
            r_name = b.row()
            r_name.prop(a, '["AnchorName"]', text="Name")
            layout.separator()
            r_btnl = b.row()
            r_btnl.label(text="Side:")
            r_btn = b.row(align=True)
            r_btn.operator("mr.sidebutton_l", depress=s == 0)
            r_btn.operator("mr.sidebutton_c", depress=s == 1)
            r_btn.operator("mr.sidebutton_r", depress=s == 2)

            layout.separator()

        elif not o == None and a.select_get():

            l = a.get("AnchorsLocked")

            b = layout.box()
            r_lock = b.row(align=True)
            r_lock.operator("mr.lockbutton")
            r_lock.operator("mr.unlockbutton")


