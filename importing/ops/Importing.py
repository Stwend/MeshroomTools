import bpy
import os


class OBJECT_OT_MRimport(bpy.types.Operator):

    bl_idname = "mr.importing"
    bl_label = "Import"

    def execute(self, context):

        tex_path = os.path.join('MeshroomCache','Texturing')
        mesh_path = os.path.join('MeshroomCache','Meshing')

        pre_path = os.path.dirname(context.scene.mr_import_path)

        if pre_path is None:
            self.report({'ERROR'}, "Project not found.")
            return {'CANCELLED'}

        tex_path = os.path.join(pre_path, tex_path)
        mesh_path = os.path.join(pre_path, mesh_path)

        tex_files = os.listdir(tex_path)
        mesh_files = os.listdir(mesh_path)

        tex_empty = tex_files is None or len(tex_files) == 0
        mesh_empty = mesh_files is None or len(mesh_files) == 0

        prefer_tex = context.scene.mr_import_textured
        prefer_mesh = context.scene.mr_import_mesh
        prefer_same = prefer_tex == prefer_mesh

        pick_textured = (not prefer_mesh or prefer_same) and not tex_empty
        pick_mesh = (not prefer_tex or prefer_same) and not mesh_empty

        print("Pick Mesh: " + str(pick_mesh))
        print("Pick Tex: " + str(pick_textured))

        files_full = []

        if pick_textured:

            file = r'texturedMesh.obj'

            for f in tex_files:
                full_path = os.path.join(tex_path, f, file)
                if os.path.isfile(full_path):
                    files_full.append(full_path)


        if pick_mesh:

            file = r'mesh.obj'

            for f in mesh_files:
                full_path = os.path.join(mesh_path, f, file)
                print(full_path)
                if os.path.isfile(full_path):
                    files_full.append(full_path)

        if len(files_full) == 0:
            self.report({'ERROR'}, "No geometry found.")
            return {'CANCELLED'}

        file = max(files_full, key=os.path.getmtime)

        bpy.ops.import_scene.obj(filepath=file)

        imported = context.object

        print(imported)

        return {'FINISHED'}
