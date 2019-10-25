import bpy
import math
from mathutils import Vector, Matrix
import numpy as np
from . import preferences

from . import external, glob
from .glob import Bucket, BucketItem

def swap_vec3_format(vectors, swap_back = False):

    if swap_back:

        swapped = []

        for i in range(0, len(vectors[0])):
            vec = np.zeros(shape=[4,1])
            vec[0], vec[1], vec[2] = vectors[0][i], vectors[1][i], vectors[2][i]
            vec[3] = 1

            swapped.append(vec)


    else:
        swapped = np.zeros(shape=[3, len(vectors)])

        for i in range(0, len(vectors)):

            vec = vectors[i]

            swapped[0][i], swapped[1][i], swapped[2][i] = vec[0], vec[1], vec[2]

    return swapped


def affine_transform(points_source, points_target, iterations = 1, scale = True):

    S = swap_vec3_format(points_source)
    T = swap_vec3_format(points_target)


    M = external.affine_matrix_from_points(S, T, shear=False, scale=scale, usesvd=True)

    return M


def unify_targets(target_objects, context):

    prefs = preferences.getPreferences()
    bias = prefs.pref_confidence_bias

    buckets = []

    for anchor in target_objects:

        x = BucketItem(anchor)
        n = anchor.get("AnchorName")
        s = anchor.get("AnchorSide")

        if len(buckets) == 0:
            buckets.append(Bucket(n, s, x))
            continue

        for b in buckets:
            if b.name == n and b.side == s:
                b.items.append(x)
                continue

        buckets.append(Bucket(n, s, x))

    target2 = []

    for b in buckets:

        total_loc = Vector.Fill(3)
        total_weight = 0

        for val in b.items:

            total_loc += val.value.matrix_world.translation
            total_weight += 1

        if not total_weight == 0:
            total_loc /= total_weight

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=total_loc,
                                 rotation=(0.0, 0.0, 0.0))
        temp = context.view_layer.objects.active

        temp["AnchorName"] = b.name
        temp["AnchorSide"] = b.side

        glob.tag_garbage(temp)

        target2.append(temp)

    return target2


def align_prep_mirrored(objects, context):

    ret = []

    buckets = []

    loc = []
    names = []
    sides = []

    for anchor in objects:

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

        if b.side == 1 or not len(b.items) == 2:

            it = b.items[0]
            loc.append(it.value.matrix_world.translation)
            names.append(b.name)
            sides.append(it.side)

        else:

            it1 = b.items[0]
            it2 = b.items[1]

            p1, p2 = it1.value.matrix_world.translation,  it2.value.matrix_world.translation

            p1m, p2m = Vector((-p1.x, p1.y, p1.z)), Vector((-p2.x, p2.y, p2.z))

            loc.extend([(p1 + p2m) / 2, (p2 + p1m) / 2])
            names.extend([b.name, b.name])
            sides.extend([it1.side, it2.side])


    for i in range(0, len(loc)):

        l = loc[i]
        n = names[i]
        s = sides[i]

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, align='WORLD', location=l,
                                 rotation=(0.0, 0.0, 0.0))
        temp = context.view_layer.objects.active

        temp["AnchorName"] = n
        temp["AnchorSide"] = s

        glob.tag_garbage(temp)

        ret.append(temp)

    return ret





def flatten_anchors(anchors, context):

    buckets = []

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

        else:

            if not len(b.items) < 2:
                p1, p2 = b.items[0].value.matrix_world.translation,  b.items[1].value.matrix_world.translation

                loc.append((p1 + p2) / 2)



    return loc


def align_mirrored(obj_source, self, context):

    grp = context.view_layer.objects[obj_source['AnchorGroup']]
    obj_source.rotation_mode = 'QUATERNION'

    anchors_source = []

    for a in context.view_layer.objects[obj_source['AnchorGroup']].children:
        if not a['AnchorName'] == 'NONE':
            anchors_source.append(a)

    flattened = flatten_anchors(anchors_source, context)

    if len(flattened) < 3:
        self.report({'ERROR'}, "More than 3 mirrored anchors are needed.")
        return {'CANCELLED'}

    targets = []
    l = len(flattened)
    angle = (math.pi * 2) / l
    current = 0

    for i in range(0, l):
        c = math.cos(current)
        s = math.sin(current)

        p = Vector((0.0, -s * 10, c * 10))

        targets.append(p)

        current += angle

    affine = affine_transform(flattened, targets, 1, scale=False)

    transform = Matrix.Identity(4)
    for n in range(0, 4):
        for m in range(0, 4):
            transform[n][m] = affine[n][m]

    obj_source.matrix_world = transform @ obj_source.matrix_world

    old = obj_source.matrix_world

    context.view_layer.objects.active = obj_source

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    grp.matrix_world = old @ grp.matrix_basis

    glob.collect_garbage(context)
























