from bpy.types import Panel




class RENDER_PT_MRAlignPanel(Panel):
    bl_idname = "mr.panel._PT_align"
    bl_label = "Align"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshroom"


    def draw(self, context):

        layout = self.layout

        if not context.object is None:
            isSelected = context.object.select_get()
            isLocked = context.object.get("AnchorsLocked", False)
            isAnchor = context.object.get("AlignmentAnchor", False)
            isObject = not isAnchor and context.object.get("AnchorGroup", False)
            isHaveMirror = isObject and context.object.get("MirrorPreview", False)
            isMirrorHidden = isHaveMirror and context.object.get("MirrorHidden", False)
        else:
            isSelected, isLocked, isAnchor, isObject, isHaveMirror, isMirrorHidden = False, False, False, False, False, False

        mainColumn = layout.column()
        mainColumn.active = not isLocked

        if isSelected:

            displayName = context.object.name if not isAnchor else context.object["AnchorName"]

            rowInfo = mainColumn.row()
            spl = rowInfo.split(factor=0.5)
            rowName = spl.row()
            rowName.label(text=displayName)
            rowOpt = spl.row()
            rowOpt.alignment = "RIGHT"
            rowOpt.operator("mr.togglelockbtn", text="", icon=("LOCKED" if isLocked else "UNLOCKED"), emboss=False)
            if isHaveMirror:
                rowOpt.operator("mr.togglepreviewbtn", text="", icon="HIDE_ON" if isMirrorHidden else "HIDE_OFF", emboss=False)
            op_isolate = rowOpt.operator("mr.selectbtn", text="", icon="MESH_CUBE" if not isAnchor else "EMPTY_AXIS", emboss=False)
            op_isolate.mode = 0

            if not isAnchor:

                if isLocked:
                    mainColumn.label(text="OBJECT LOCKED")

                else:
                    mainColumn.operator("mr.addanchor", text="Add Anchor")
                    mainColumn.operator("mr.clearanchors", text="Clear Anchors")

                    mainColumn.separator()
                    mainColumn.label(text="Mirror")
                    mainColumn.prop(context.scene, "mr_mirror_preview", text="Preview")
                    mainColumn.operator("mr.alignmirrored", text="Align Mirrored")
                    mainColumn.separator()
                    mainColumn.label(text="Align")
                    mainColumn.operator("mr.alignanchors", text="Align Anchors")



            else:

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

                    if len(context.selected_objects) == 2:
                        r_copy = mainColumn.row()
                        if not context.selected_objects[0].parent == context.selected_objects[1].parent:
                            cop = r_copy.operator("mr.linkbtn", text="Copy Attributes", icon="PASTEDOWN")
                            cop.mirror = False
                        else:
                            r_copy_s = r_copy.split(factor=0.33)
                            r_copy_s.prop(context.scene, "mr_mirror_translate", text="Location")
                            cop = r_copy_s.operator("mr.linkbtn", text="Copy Mirrored", icon="PASTEDOWN")
                            cop.mirror = True

        else:
            layout.active = False
            layout.label(text="No valid object selected.")
