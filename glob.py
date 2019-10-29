import bpy

storedContext = None

def tag_garbage(obj):
    obj["Meshroom_GARBAGE"] = True

def collect_garbage(context):

    bpy.ops.object.select_all(action='DESELECT')

    for obj in context.scene.objects:
        if obj.get("Meshroom_GARBAGE", False):
            obj.hide_set(False)
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


def update_prop(context, data, propname):
    try:
        context.object[propname] = context.scene[data]
        store(context)
    except:
        pass


class Bucket:
    location = None
    def __init__(self, name, side, item):
        self.name = name
        self.side = side
        self.items = [item]


class BucketItem:
    def __init__(self, value, weight = 1, side = 1):
        self.value = value
        self.weight = weight
        self.side = side