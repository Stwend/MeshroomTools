import bpy
import math
import os

from .._misc import global_functions


def packUDIMS(selObj):

    ctx = global_functions.ctx()
    bin = []

    for o in ctx.scene.objects:
        o.hide_render = True

    selObj.hide_render = True


    slots = len(selObj.material_slots)

    c = 0
    cursor = 1

    while cursor < slots:
        c += 1
        cursor = c * c

    print("Space needed: " + str(cursor) + " charts, total rows/columns: " + str(c))

    c = max(1, c)

    scale = 1/c
    placement = []


    for i in range(0, slots):

        column = i%c
        row = int((i - column)/c)

        placement.append((row * scale, column * scale))


    uvl = selObj.data.uv_layers.active


    counter = 0
    total = len(uvl.data)

    for v in uvl.data:

        id = int(math.floor(v.uv[0])) + 10 * int(math.floor(v.uv[1]))

        v.uv[0] = (v.uv[0] % 1) * scale + placement[id][0]
        v.uv[1] = (v.uv[1] % 1) * scale + placement[id][1]

        counter += 1

        if (counter%100 == 0):

            x = (counter*100)/total

            print("Packing... %.1f" % x + r'%', end='\r')

    print("")


    textures = []

    m = selObj.material_slots[0].material
    nodes = m.node_tree.nodes
    img = nodes.get("Image Texture").image
    path = os.path.join(os.path.dirname(img.filepath), "packed.png")

    for i in range(0, slots):
        m = selObj.material_slots[i].material
        textures.append(m)

    for i in range(1, slots):

        selObj.active_material_index = i
        bpy.ops.object.material_slot_select()
        bpy.ops.object.material_slot_remove()

    bpy.ops.object.camera_add(enter_editmode=False, location=(0.0, 0.0, 1), rotation=(0.0, 0.0, 0.0))

    cam = ctx.scene.camera

    cam.data.ortho_scale = 1.
    cam.data.show_background_images = True
    cam.data.type = "ORTHO"

    bin.append(cam)

    ctx.scene.render.resolution_x = ctx.scene.mr_pack_res
    ctx.scene.render.resolution_y = ctx.scene.mr_pack_res
    ctx.scene.render.resolution_percentage = 100

    for i in range(0, len(textures)):

        m = textures[i]

        x = placement[i][0] + 0.5 * scale - .5
        y = placement[i][1] + 0.5 * scale - .5

        bpy.ops.mesh.primitive_plane_add(size=scale, calc_uvs=True, enter_editmode=False, location=(x, y, 0.0), rotation=(0.0, 0.0, 0.0))
        obj = ctx.object

        bin.append(obj)

        obj.data.materials.append(m)

    rnd_eng = ctx.scene.render.engine
    rnd_path = ctx.scene.render.filepath
    rnd_comp = ctx.scene.render.use_compositing
    rnd_seq = ctx.scene.render.use_sequencer
    shd_col = ctx.scene.display.shading.color_type
    shd_l = ctx.scene.display.shading.light



    ctx.scene.render.engine = "BLENDER_WORKBENCH"
    ctx.scene.render.use_compositing = False
    ctx.scene.render.use_sequencer = False
    ctx.scene.render.filepath = path

    ctx.scene.display.shading.color_type = "TEXTURE"
    ctx.scene.display.shading.light = "FLAT"

    ctx.scene.view_settings.view_transform = "Standard"

    bpy.ops.render.render(write_still=True)

    ctx.scene.render.engine = rnd_eng
    ctx.scene.render.filepath = rnd_path
    ctx.scene.render.use_compositing = rnd_comp
    ctx.scene.render.use_sequencer = rnd_seq
    ctx.scene.display.shading.color_type = shd_col
    ctx.scene.display.shading.light = shd_l



    m = bpy.data.materials.new(name="packed")
    m.use_nodes = True
    tree = m.node_tree

    imgN = tree.nodes.new('ShaderNodeTexImage')

    img = bpy.data.images.load(path)

    imgN.image = img

    tree.links.new(tree.nodes.get('Principled BSDF').inputs[0], imgN.outputs[0])


    selObj.data.materials[0] = m

    bpy.ops.object.select_all(action="DESELECT")

    for b in bin:
        b.select_set(True)

    bpy.ops.object.delete()

    selObj.hide_render = False