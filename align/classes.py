import bpy
from mathutils import Matrix
from .._misc import global_functions

class Bucket:
    location = None
    def __init__(self, name, side, item):
        self.name = name
        self.side = side
        self.items = [item]


class BucketItem:
    def __init__(self, value, side = 1):
        self.value = value
        self.side = side




class AnchorProxy:
    def __init__(self, obj=None, fav=None, lock=None, name=None, side=None, matrix=None):
        if not obj is None:
            if bool(obj.get('AlignmentAnchor', False)):
                self.source = obj
                self.fav = bool(obj.get('AnchorFav', False))
                self.lock = bool(obj.get('AnchorLocked', False))
                self.name = obj.get('AnchorName', 'NONE')
                self.side = obj.get('AnchorSide', 1)
                self.matrix = obj.matrix_world
        else:
            self.fav = fav
            self.lock = lock
            self.name = name
            self.side = side
            self.matrix = matrix



class AnchorObjectProxy:
    def __init__(self, obj=None):

        context = global_functions.ctx()

        self.source = obj
        self.grp = context.view_layer.objects[obj.get('AnchorGroup')]

        #basic info
        self.name = self.source.name
        self.is_locked = bool(self.source.get('AnchorLocked', False))
        self.has_anchors = len(self.grp.children) > 0
        self.has_mirror = not self.source.get('MirrorPreview', '') == ''
        self.mirror = None
        self.anchors = []

        if self.has_mirror:
            try:
                self.mirror = context.view_layer.objects[obj.get('MirrorPreview')]
            except:
                self.has_mirror = False
                self.source['MirrorPreview'] = ''
                pass


        #collect anchors

        self.active_anchor = None

        if self.has_anchors:
            for child in self.grp.children:
                anchor = AnchorProxy(child)
                self.anchors.append(anchor)
                if context.view_layer.objects.active.name == child.name:
                    self.active_anchor = anchor



    def focus(self):

        context = global_functions.ctx()
        self.source.select_set(True)
        context.view_layer.objects.active = self.source

    def add_anchor(self, pos, name='NONE', side=1, locked=False, favourite=False, focus=False):

        context = global_functions.ctx()

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0),
                                 rotation=(0.0, 0.0, 0.0))

        target = context.view_layer.objects.active
        target.select_set(False)

        # initialize empty properties
        target.name = "New Anchor"
        target['AlignmentAnchor'] = True
        target['AnchorName'] = name
        target['AnchorSide'] = side
        target['AnchorsLocked'] = locked
        target['AnchorFav'] = favourite

        target.parent = self.grp
        target.matrix_world = Matrix.Translation(pos)

        target.lock_location = (locked, locked, locked)
        target.lock_rotation = (locked, locked, locked)
        target.lock_scale = (locked, locked, locked)

        if focus:
            context.view_layer.objects.active = target
        target.select_set(focus)

    def clear(self):

        keep_grp = False

        for anchor in self.anchors:
            if not anchor.fav:
                global_functions.tag_garbage(anchor.source)
            else:
                keep_grp = True

        if not keep_grp:
            global_functions.tag_garbage(self.grp)
            self.source['AnchorGroup'] = ''

        global_functions.collect_garbage()
        self.focus()

    def clear_anchor(self, target_anchor):

        found = False

        for anchor in self.anchors:
            if anchor.source.name == target_anchor.source.name:
                global_functions.tag_garbage(anchor.source)
                found = True
                break

        if len(self.grp.children) == 1 and found:
            global_functions.tag_garbage(self.grp)
            self.source['AnchorGroup'] = ''

        global_functions.collect_garbage()
        self.focus()

    def clear_mirror(self):

        if self.has_mirror:

            self.source['MirrorPreview'] = ''
            global_functions.tag_garbage(self.mirror)
            global_functions.collect_garbage()

        self.focus()



class AnchorSceneProxy:

    active = None
    locked = []
    unlocked = []
    valid = []


    def __init__(self, active_only=True):

        context = global_functions.ctx()

        for obj in bpy.data.objects:

            if not obj.type in ['MESH', 'EMPTY']:
                continue

            is_active = context.object.name == obj.name

            is_anchor = bool(obj.get('AlignmentAnchor', False))
            is_object = not obj.get('AnchorGroup', '') == ''

            is_valid = is_object
            is_empty = False

            try:
                temp_group = bpy.data.objects[obj.get('AnchorGroup')]
                if not len(temp_group.children) > 0:
                    is_empty = True

            except:
                is_valid = False
                is_empty = True
                pass

            is_valid = (is_valid and not is_empty) or is_anchor

            if is_anchor:
                is_locked = bool(obj.get('AnchorLocked', False))
            else:
                is_locked = bool(obj.get('AnchorsLocked', False))
            print(is_locked)

            if is_anchor and is_active:
                obj_target = obj.parent.parent
            elif not is_anchor:
                obj_target = obj
            else:
                continue


            if is_active and not is_locked:

                if not is_valid:

                    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0),
                                             rotation=(0.0, 0.0, 0.0))
                    grp = context.view_layer.objects.active
                    grp.name += "_Anchors"
                    grp.hide_viewport = True
                    obj_target['AnchorGroup'] = grp.name
                    obj_target['AnchorsLocked'] = False
                    grp.parent = obj_target
                    grp.matrix_world = Matrix.Identity(4)

                    context.view_layer.objects.active = obj_target
                    obj_target.select_set(True)

                self.active = AnchorObjectProxy(obj_target)

                if active_only:
                    break
                continue

            elif is_valid and not is_active:

                temp = AnchorObjectProxy(obj_target)
                self.valid.append(temp)

                if is_locked:
                    self.locked.append(temp)
                else:
                    self.unlocked.append(temp)






