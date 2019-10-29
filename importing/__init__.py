from . import ops, gui


def get_to_register():

    ret = [ops.OBJECT_OT_MRimport]
    ret.extend(gui.get_to_register())
    return ret