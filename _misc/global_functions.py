import bpy

storedContext = None

def tag_garbage(obj):
    obj["Meshroom_GARBAGE"] = True

def collect_garbage():

    context = ctx()

    bpy.ops.object.select_all(action='DESELECT')

    for obj in context.scene.objects:
        if obj.get("Meshroom_GARBAGE", False):
            obj.hide_set(False)
            obj.hide_select = False
            obj.hide_viewport = False
            obj.select_set(True)

    bpy.ops.object.delete()

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def store(c):
    global storedContext
    storedContext = c


def ctx():
    return storedContext