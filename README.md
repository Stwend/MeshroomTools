# MeshroomTools

A few useful tools for processing Meshroom scans inside Blender, loosely based on
https://github.com/patmo141/object_alignment 

## Table Of Contents
- [MeshroomTools](#meshroomtools)
  * [Import](#import)
  * [UV/Texture](#uv-texture)
  * [Align](#align)
    * [Object Panel](#object-panel)
    * [Anchor Panel](#anchor-panel)





## Import



![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/import.png) 



Imports a mesh from your specified Meshroom project. Unless specified otherwise, it will always import the latest mesh, regardless of whether it is textured or not.



- Project: Your Meshroom project.
- Prefer Mesh Only: If checked, it will import the newest untextured mesh. If there are no untextured meshes available, it will import a textured mesh instead.
- Prefer Textured: The importer won't search for untextured meshes unless there is no textured mesh available.





## UV/Texture

![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/texture.png) 

In case there is no object currently selected or the selected object doesn't have Meshroom UDIMs, this panel will show only the line "No valid object selected".



![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/texture_active.PNG) 

If the selected object is deemed valid, the menu appears. Packing will rearrange your existing textures in a suitable grid (e.g. 4 textures in a 2x2 grid, up to 9 textures in a 3x3 grid and so on) and render out a new texture. Your UVs will be rearranged accordingly.

- Resolution: The desired resolution of the packed texture.



## Align

![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/align.png) 

In a similar fashion to the UV panel, the Align panel won't show anything until suitable objects have been selected.



##### Object Panel

![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/align_active_object.PNG) 

If an object is selected, regardless of it having anchors or not, this panel appears.

- A: The selected object's name.
- B: Clicking this icon will lock (unlock if the object is already locked) your object together with all its anchors. Locked objects can't be moved, scaled or rotated and you can't access anchor or object properties.
- C: Clicking this icon will isolate your object and hide every other object in the scene.
- Add Anchor: Place an anchor marker on the surface of your selected object.
- Clear Anchors: Remove all of the objects' anchors.
- Preview: If checked, Align Mirrored will also show you a mirrored version of your object. The preview object is deleted each time you press the button, so there's no use of editing it.
- Align Mirrored: Aligns your object to the X-axis according to your set anchors.
  - For this to work, the object needs to have at least 3 pairs of anchors.
- Align Anchors: Aligns your selected object to any locked objects in the scene.
  - Both the selected object and the locked objects combined have to have at least 3 anchors.



##### Anchor Panel

![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/align_active_anchor.PNG) 

In case you have selected an anchor, this panel will show up.

- A: The selected object's name.
- B: Clicking this icon will lock (unlock if the object is already locked) your object together with all its anchors. Locked objects can't be moved, scaled or rotated and you can't access anchor or object properties.
- C: Clicking this icon will isolate your object and hide every other object in the scene. The icon will display an axis icon if the selected object is an anchor, and a cube otherwise.
- Name: Here you can change the name of your anchor. This name will be used to pair anchors of different objects  together.
- Left/Center/Right: Set the side of your anchor. This will be used for both mirroring and aligning.



![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/align_active_anchor_pair.PNG) 

You can select a pair of anchors, too. In this case the anchor panel will show additional functions:

- Copy Mirrored: Copy all attributes of the selected anchor over to the active and mirror them.
  - The name will be the same.
  - The side will be mirrored.
- Location: When copying, move the active anchor over to the mirrored position of the other one.



![](https://github.com/Stwend/MeshroomTools/blob/master/__readme_img/align_active_anchor_pair_2.PNG) 

This button will show up if you have selected two anchors and they belong to different objects.

- Copy Attributes: Copy all attributes from the selected anchor over to the active one.
  - Name and side will be the same.