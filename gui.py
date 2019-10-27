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

        mainColumn = layout.column()
        mainColumn.active = not isLocked

        if isSelected:

            displayName = context.object.name if isObject else context.object["AnchorName"]

            rowInfo = mainColumn.row()
            spl = rowInfo.split(factor=0.5)
            rowName = spl.row()
            rowName.label(text=displayName)
            rowOpt = spl.row()
            rowOpt.alignment = "RIGHT"
            rowOpt.operator("mr.togglelockbtn", text="", icon=("LOCKED" if isLocked else "UNLOCKED"), emboss=False)
            op_isolate = rowOpt.operator("mr.selectbtn", text="", icon="MESH_CUBE" if isObject else "EMPTY_AXIS", emboss=False)
            op_isolate.mode = 0

            if isObject:

                if isLocked:
                    mainColumn.label(text="OBJECT LOCKED")

                else:
                    r = mainColumn.row()
                    r.prop(context.scene, "mr_anchor_default_mirror", text="Mirroring")
                    r.prop(context.scene, "mr_anchor_default_align", text="Aligning")
                    mainColumn.operator("mr.addanchor", text="Add Anchor")

                    mainColumn.separator()
                    mainColumn.label(text="Mirror")
                    mainColumn.operator("mr.alignmirrored", text="Align Mirrored")
                    mainColumn.separator()
                    mainColumn.label(text="Align")
                    mainColumn.prop(context.scene, "mr_respect_mirrored", text="Mirrored")
                    mainColumn.operator("mr.alignanchors", text="Align Anchors")



            elif isAnchor:

                if isLocked:
                    mainColumn.label(text="ANCHOR LOCKED")
                else:

                    s = context.object.get("AnchorSide", 1)

                    r_name = mainColumn.row().split(factor=0.33)
                    r_name.label(text="Name")
                    r_name.prop(context.object, '["AnchorName"]', text="")
                    r_btn = mainColumn.row(align=True)
                    left = r_btn.operator("mr.sidebutton", text="Left", depress=s == 0)
                    left.side = 0
                    center = r_btn.operator("mr.sidebutton", text="Center", depress=s == 1)
                    center.side = 1
                    right = r_btn.operator("mr.sidebutton", text="Right", depress=s == 2)
                    right.side = 2
                    r_usage = mainColumn.row()
                    r_usage.prop(context.scene, "mr_anchor_current_mirror", text="Mirroring")
                    r_usage.prop(context.scene, "mr_anchor_current_align", text="Aligning")
                    if len(context.selected_objects) == 2:
                        r_copy = mainColumn.row()
                        r_copy.operator("mr.linkbtn", icon="PASTEDOWN")

        else:
            layout.active = False
            layout.label(text="No valid object selected.")
