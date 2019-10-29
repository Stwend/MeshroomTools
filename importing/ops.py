import bpy
import os


class OBJECT_OT_MRimport(bpy.types.Operator):

    bl_idname = "mr.importing"
    bl_label = "Import"

    def execute(self, context):

        texpath = r'MeshroomCache/Texturing'
        meshpath = r'MeshroomCache/Meshing'

        prepath = os.path.dirname(context.scene.mr_import_path)

        texpath = os.path.join(prepath, texpath)
        meshpath = os.path.join(prepath, meshpath)

        candT = [os.path.join(texpath,f) for f in os.listdir(texpath)]
        candM = [os.path.join(meshpath,f) for f in os.listdir(meshpath)]

        tex_empty = len(candT) == 0
        mesh_empty = len(candM) == 0

        if tex_empty and mesh_empty:
            self.report({'ERROR'}, "Geometry folders are empty.")
            return {'CANCELLED'}

        pathT = max(candT, key=os.path.getmtime)
        pathM = max(candM, key=os.path.getmtime)

        path = pathM
        pickedTextured = False

        prefT = context.scene.mr_import_textured
        prefM = context.scene.mr_import_mesh

        if prefT and prefM:
            prefT, prefM = False, False

        if not tex_empty:
            if prefT or mesh_empty:
                path = pathT
                pickedTextured = True
            elif not prefM:
                if not mesh_empty:
                    dateT = os.path.getmtime(pathT)
                    dateM = os.path.getmtime(pathM)

                    if dateT > dateM:
                        path = pathT
                        pickedTextured = True





        if pickedTextured:
            file = r'texturedMesh.obj'
        else:
            file = r'mesh.obj'


        file = os.path.join(path,file)

        bpy.ops.import_scene.obj(filepath=file)

        imported = context.object

        print(imported)







        return {'FINISHED'}