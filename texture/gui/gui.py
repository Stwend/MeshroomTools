import bpy
from bpy.types import Panel

class RENDER_PT_MRUVPanel(Panel):
    bl_idname = "mr.panel._PT_uv"
    bl_label = "UV/Texture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"

    def draw(self, context):

        layout = self.layout

        if not context.object is None:
            is_valid = context.object.material_slots[0].name == 'TextureAtlas_1001'
        else:
            is_valid = False

        if not is_valid:
            layout.active = False
            layout.label(text="No valid object selected.")
            return

        box = layout.split(factor=0.33)
        box.label(text="Resolution:")

        box.prop(context.scene, "mr_pack_res", text="")

        layout.operator("mr.uvpack", text="Pack")
