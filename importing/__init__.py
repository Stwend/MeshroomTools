from . import gui, ops


def get_to_register():

    ret = ops.get_to_register()
    ret.extend(gui.get_to_register())
    return ret