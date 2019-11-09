from . import functions, gui, ops


def get_to_register():

    ret = gui.get_to_register()
    ret.extend(gui.get_to_register())
    return ret
