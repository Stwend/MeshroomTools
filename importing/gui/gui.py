import bpy
from bpy.types import Panel

class RENDER_PT_MRImportPanel(Panel):
    bl_idname = "mr.panel._PT_import"
    bl_label = "Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"

    def draw(self, context):
        layout = self.layout
        box = layout.split(factor=0.33)
        box.label(text="Project:")
        box.prop(context.scene, "mr_import_path", text="")
        layout.prop(context.scene, "mr_import_textured", text="Prefer Textured")
        layout.operator("mr.importing", text="Import")