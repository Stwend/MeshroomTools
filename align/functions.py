import bpy
from mathutils import Vector, Matrix
import numpy as np

from misc import global_functions, external
from .classes import Bucket, BucketItem

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

        global_functions.tag_garbage(temp)

        target2.append(temp)

    return target2





def average_anchors(anchors, context):
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

                p1M, p2M = p1.copy(), p2.copy()

                p1M.x = -p1M.x
                p2M.x = -p2M.x

                p1New = (p1 + p2M) / 2
                p2New = (p2 + p1M) / 2

                loc.extend([p1New, p2New])
                loc_old.extend([p1,p2])

    return [loc_old,loc]



def align_mirrored(obj_source, self, context):

    obj_source.rotation_mode = 'QUATERNION'

    anchors_source = []

    for a in context.view_layer.objects[obj_source['AnchorGroup']].children:
        if not a.get('AnchorName', "NONE") == "NONE":
            anchors_source.append(a)

    avg = average_anchors(anchors_source, context)

    if len(avg[0]) < 3:
        self.report({'ERROR'}, "More than 3 mirrored or centered anchors are needed.")
        return {'CANCELLED'}

    affine = affine_transform(avg[0], avg[1], 1, scale=False)

    transform = Matrix.Identity(4)
    for n in range(0, 4):
        for m in range(0, 4):
            transform[n][m] = affine[n][m]

    obj_source.matrix_world = transform @ obj_source.matrix_world



    obj_prev_name = obj_source.get('MirrorPreview', None)
    if not obj_prev_name is None:
        try:
            to_delete = context.view_layer.objects[obj_prev_name]
            global_functions.tag_garbage(to_delete)
        except:
            pass

    global_functions.collect_garbage(context)

    if(context.scene.mr_mirror_preview):

        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.object.duplicate({"object": obj_source, "selected_objects": [obj_source]}, linked=False)
        obj_prev = context.object
        obj_source['MirrorPreview'] = obj_prev.name
        bpy.ops.object.transform_apply({"object": obj_prev, "selected_objects": [obj_prev]}, location=True, rotation=True, scale=True)
        obj_prev.scale.x = -1.0
        obj_prev.select_set(False)
        obj_source["MirrorHidden"] = False





    context.view_layer.objects.active = obj_source
    obj_source.select_set(True)























