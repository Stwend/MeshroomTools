import bpy
import math
from mathutils import Vector, Matrix
import numpy as np

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



    obj_source.rotation_mode = 'QUATERNION'

    anchors_source = []

    for a in context.view_layer.objects[obj_source['AnchorGroup']].children:
        if not a.get('AnchorName', "NONE") == "NONE":
            if bool(a.get('AnchorUseMirror', True)):
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

    glob.collect_garbage(context)

    obj_source.select_set(True)
























