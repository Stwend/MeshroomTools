import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty, BoolProperty


class MeshroomTools(AddonPreferences):

    bl_idname = __package__

    pref_confidence_bias = FloatProperty(
        name="(WIP) Confidence Bias",
        description="Bias calculations in favour of anchors with higher confidence.",
        default=0.5,
        min=0.0,
        max=1.0
    )


    def draw(self, context):
        layout = self.layout

        r = layout.row()
        spl = r.split(factor=0.5)
        spl.label(text="Confidence Bias")
        spl.prop(self, "pref_confidence_bias", text="")


def getPreferences():
    return bpy.context.preferences.addons.get(__package__).preferences
