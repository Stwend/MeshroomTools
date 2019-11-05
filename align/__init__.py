from . import classes, functions, ops, gui


def get_to_register():

    ret = [ops.OBJECT_OT_MRAnchorAddModal,
           ops.OBJECT_OT_MRAnchorClear,
           ops.OBJECT_OT_MRAnchorRemove,
           ops.OBJECT_OT_MRAnchorCreateMirrored,
           ops.OBJECT_OT_MRAnchorAlign,
           ops.OBJECT_OT_MRAlignMirrored
           ]

    ret.extend(gui.get_to_register())

    return ret
