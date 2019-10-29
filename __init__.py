import bpy



from . import texture, align, misc, importing



bl_info = {
    "name": "Meshroom Tools",
    "category": "Object",
    "author": "Stefan Wendling",
    "version": (0, 5, 0),
    "blender": (2, 80, 0),
    }



def register():
    from bpy.utils import register_class

    classes = []
    classes.extend(importing.get_to_register())
    classes.extend(texture.get_to_register())
    classes.extend(align.get_to_register())

    for cls in (classes):
        register_class(cls)

    misc.properties.initialize_props()


def unregister():
    from bpy.utils import unregister_class

    classes = []
    classes.extend(importing.get_to_register())
    classes.extend(texture.get_to_register())
    classes.extend(align.get_to_register())

    for cls in reversed(classes):
        unregister_class(cls)
