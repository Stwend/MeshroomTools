import bpy
import os


class OBJECT_OT_MRimport(bpy.types.Operator):

    bl_idname = "mr.importing"
    bl_label = "Import"

    def execute(self, context):

        tex_path = r'MeshroomCache\Texturing'
        mesh_path = r'MeshroomCache\Meshing'

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

        pick_textured = prefer_tex and not tex_empty
        pick_mesh = not pick_textured and not mesh_empty

        files_full = []

        file = r'texturedMesh.obj'

        for f in tex_files:
            full_path = os.path.join(tex_path, f, file)
            if os.path.isfile(full_path):
                files_full.append(full_path)

        if len(files_full) == 0:
            pick_textured = False
            pick_mesh = not mesh_empty

        if pick_mesh:

            file = r'mesh.obj'

            for f in mesh_files:
                full_path = os.path.join(mesh_path, f, file)
                print(full_path)
                if os.path.isfile(full_path):
                    files_full.append(full_path)

            if len(files_full) == 0:
                pick_mesh = False

        if not (pick_textured or pick_mesh):
            self.report({'ERROR'}, "No geometry found.")
            return {'CANCELLED'}

        file = max(files_full, key=os.path.getmtime)

        bpy.ops.import_scene.obj(filepath=file)

        imported = context.object

        print(imported)

        return {'FINISHED'}
