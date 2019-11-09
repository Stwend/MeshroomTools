import bpy

side_enums = [("LEFT", "Left", "Left"), ("CENTER", "Center", "Center"), ("RIGHT", "Right", "Right")]


def update_obj_prop(context, data, propname):
    try:
        context.object[propname] = context.scene[data]
    except:
        pass


def initialize_props():

    #UV
    bpy.types.Scene.mr_pack_res = bpy.props.IntProperty(default=4096, min=1)

    #Align
    bpy.types.Scene.mr_mirror_preview = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.mr_mirror_translate = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.mr_current_side = bpy.props.EnumProperty(items=side_enums, default="CENTER",
                                                             update=lambda self, context: update_obj_prop(context, "mr_current_side", "AnchorSide"))
    #Import
    bpy.types.Scene.mr_import_path = bpy.props.StringProperty(default="", subtype="FILE_PATH")
    bpy.types.Scene.mr_import_textured = bpy.props.BoolProperty(default=True)
