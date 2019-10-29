from . import gui, ops


def get_to_register():
    return [gui.RENDER_PT_MRAlignPanel,
            ops.OBJECT_OT_MRTogglePreviewBtn,
            ops.OBJECT_OT_MRToggleLockBtn,
            ops.OBJECT_OT_MRSelectBtn,
            ops.OBJECT_OT_MRLinkAttrsBtn,
            ops.OBJECT_OT_MRSideBtn]