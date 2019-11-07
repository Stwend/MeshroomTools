from . import classes, functions, ops, gui


def get_to_register():

    ret = []

    ret.extend(ops.get_to_register())
    ret.extend(gui.get_to_register())

    return ret
