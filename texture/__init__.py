from . import functions, ops, gui


def get_to_register():

    ret = [ops.OBJECT_OT_MRuvpack]
    ret.extend(gui.get_to_register())
    return ret
