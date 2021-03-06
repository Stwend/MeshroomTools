import bpy
from mathutils import Vector, Matrix
import numpy as np

from .._misc import global_functions, external
from .classes import Bucket, BucketItem, AnchorProxy


def add_anchor(grp, pos, name='NONE', side=1, locked=False, select=True):

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

    target.parent = grp
    target.matrix_world = Matrix.Translation(pos)

    target.lock_location = (locked, locked, locked)
    target.lock_rotation = (locked, locked, locked)
    target.lock_scale = (locked, locked, locked)

    if select:
        context.view_layer.objects.active = target
    target.select_set(select)

    return target


def swap_vec3_format(vectors, swap_back=False):

    if swap_back:

        swapped = []

        for i in range(0, len(vectors[0])):

            vec = np.zeros(shape=[4, 1])
            vec[0], vec[1], vec[2] = vectors[0][i], vectors[1][i], vectors[2][i]
            vec[3] = 1
            swapped.append(vec)

    else:
        swapped = np.zeros(shape=[3, len(vectors)])

        for i in range(0, len(vectors)):

            vec = vectors[i]
            swapped[0][i], swapped[1][i], swapped[2][i] = vec[0], vec[1], vec[2]

    return swapped


def affine_transform(points_source, points_target, scale=True):

    s = swap_vec3_format(points_source)
    t = swap_vec3_format(points_target)

    m = external.affine_matrix_from_points(s, t, shear=False, scale=scale, usesvd=True)

    return m


def unify_targets(target_objects):

    context = global_functions.ctx()

    buckets = []

    for anchor in target_objects:

        if len(buckets) == 0:
            buckets.append(Bucket(anchor.name, anchor.side, BucketItem(anchor)))
            continue

        for b in buckets:
            if b.name == anchor.name and b.side == anchor.side:
                b.items.append(BucketItem(anchor))
                continue

        buckets.append(Bucket(anchor.name, anchor.side, BucketItem(anchor)))

    proxies = []

    for b in buckets:

        total_loc = Vector.Fill(3)
        total_weight = 0

        for val in b.items:

            total_loc += val.value.matrix.translation
            total_weight += 1

        if not total_weight == 0:
            total_loc /= total_weight

        proxies.append(AnchorProxy(fav=False, lock=True, name=b.name, side=b.side, matrix=Matrix.Translation(total_loc)))


    return proxies


def average_anchors(anchors):
    buckets = []

    loc_old = []
    loc = []

    for anchor in anchors:

        n = anchor.get("AnchorName")
        s = anchor.get("AnchorSide")
        x = BucketItem(anchor, side=s)

        if len(buckets) == 0:
            buckets.append(Bucket(n, s, x))
            continue

        for b in buckets:
            if b.name == n:
                b.items.append(x)
                continue

        buckets.append(Bucket(n, s, x))

    for b in buckets:

        if b.side == 1:
            loc.append(b.items[0].value.matrix_world.translation)
            loc_old.append(b.items[0].value.matrix_world.translation)

        else:

            if not len(b.items) < 2:
                p1, p2 = b.items[0].value.matrix_world.translation,  b.items[1].value.matrix_world.translation

                p1m, p2m = p1.copy(), p2.copy()

                p1m.x = -p1m.x
                p2m.x = -p2m.x

                p1_new = (p1 + p2m) / 2
                p2_new = (p2 + p1m) / 2

                loc.extend([p1_new, p2_new])
                loc_old.extend([p1,p2])

    return [loc_old,loc]


def align_mirrored(obj_source, self):

    context = global_functions.ctx()

    obj_source.rotation_mode = 'QUATERNION'

    anchors_source = []
    try:
        grp = context.view_layer.objects[obj_source['AnchorGroup']]
    except:
        pass
        obj_source['AnchorGroup'] = ''
        self.report({'ERROR'}, "More than 3 mirrored or centered anchors are needed.")
        return {'CANCELLED'}

    for a in grp.children:
        if not a.get('AnchorName', "NONE") == "NONE":
            anchors_source.append(a)

    avg = average_anchors(anchors_source)

    if len(avg[0]) < 3:
        self.report({'ERROR'}, "More than 3 mirrored or centered anchors are needed.")
        return {'CANCELLED'}

    affine = affine_transform(avg[0], avg[1])

    transform = Matrix.Identity(4)
    for n in range(0, 4):
        for m in range(0, 4):
            transform[n][m] = affine[n][m]

    obj_source.matrix_world = transform @ obj_source.matrix_world

    obj_prev_name = obj_source.get('MirrorPreview', None)
    if not obj_prev_name is None:
        try:
            to_delete = context.view_layer.objects[obj_prev_name]
            obj_source['MirrorPreview'] = ''
            global_functions.tag_garbage(to_delete)
        except:
            pass

    global_functions.collect_garbage()

    if(context.scene.mr_mirror_preview):

        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.object.duplicate({"object": obj_source, "selected_objects": [obj_source]}, linked=False)
        obj_prev = context.object
        obj_source['MirrorPreview'] = obj_prev.name
        obj_prev['MirrorParent'] = obj_source.name
        bpy.ops.object.transform_apply({"object": obj_prev, "selected_objects": [obj_prev]}, location=True, rotation=True, scale=True)
        obj_prev.scale.x = -1.0
        obj_prev.select_set(False)
        obj_prev.hide_select = True
        obj_source["MirrorHidden"] = False

    context.view_layer.objects.active = obj_source
    obj_source.select_set(True)
