import bpy
from misc import global_functions


def initialize_props():
    bpy.types.Scene.mr_pack_res = bpy.props.IntProperty(default=4096, min=1)
    bpy.types.Scene.mr_mirror_preview = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.mr_mirror_translate = bpy.props.BoolProperty(default=False)

    side_enums = [("LEFT", "Left", "Left"), ("CENTER", "Center", "Center"), ("RIGHT", "Right", "Right")]
    bpy.types.Scene.mr_current_side = bpy.props.EnumProperty(items=side_enums, default="CENTER",
                                                             update=lambda self, context: global_functions.update_prop(context, "mr_current_side", "AnchorSide"))