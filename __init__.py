import bpy



from . import gui, ops, glob



bl_info = {
    "name": "Meshroom Tools",
    "category": "Object",
    "author": "Stefan Wendling",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
}




#properties
def initialize_props():
    bpy.types.Scene.mr_pack_res = bpy.props.IntProperty(default=4096, min=1)
    bpy.types.Scene.mr_mirror_preview = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.mr_mirror_translate = bpy.props.BoolProperty(default=False)

    side_enums = [("LEFT", "Left", "Left"), ("CENTER", "Center", "Center"), ("RIGHT", "Right", "Right")]
    bpy.types.Scene.mr_current_side = bpy.props.EnumProperty(items=side_enums, default="CENTER",
                                                             update=lambda self, context: glob.update_prop(context, "mr_current_side", "AnchorSide"))




classes = (gui.RENDER_PT_MRmainPanel,
           gui.RENDER_PT_MRUVPanel,
           gui.RENDER_PT_MRAlignPanel,
           ops.OBJECT_OT_MRuvpack,
           ops.OBJECT_OT_MRAnchorAddModal,
           ops.OBJECT_OT_MRAnchorClear,
           ops.OBJECT_OT_MRAnchorAlign,
           ops.OBJECT_OT_MRAlignMirrored,
           ops.OBJECT_OT_MRSideBtn,
           ops.OBJECT_OT_MRToggleLockBtn,
           ops.OBJECT_OT_MRLinkAttrsBtn,
           ops.OBJECT_OT_MRSelectBtn,
           ops.OBJECT_OT_MRTogglePreviewBtn
           )


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    initialize_props()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
