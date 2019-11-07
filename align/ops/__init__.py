from . import base, Align, AlignMirror, AnchorAddModal, AnchorClear, AnchorMirror, AnchorRemove, MirrorPreviewClear, ButtonIsolate, ButtonLinkAttributes, ButtonSide, ButtonToggleLock, ButtonTogglePreview, ButtonFavourite

def get_to_register():

    ret = [base.OBJECT_OT_MRAlignBaseOperator,
           Align.OBJECT_OT_MRAnchorAlign,
           AlignMirror.OBJECT_OT_MRAlignMirrored,
           AnchorAddModal.OBJECT_OT_MRAnchorAddModal,
           AnchorClear.OBJECT_OT_MRAnchorClear,
           AnchorMirror.OBJECT_OT_MRAnchorCreateMirrored,
           AnchorRemove.OBJECT_OT_MRAnchorRemove,
           MirrorPreviewClear.OBJECT_OT_MRRemoveMirrorPreview,
           ButtonToggleLock.OBJECT_OT_MRToggleLockBtn,
           ButtonTogglePreview.OBJECT_OT_MRTogglePreviewBtn,
           ButtonSide.OBJECT_OT_MRSideBtn,
           ButtonLinkAttributes.OBJECT_OT_MRLinkAttrsBtn,
           ButtonIsolate.OBJECT_OT_MRSelectBtn,
           ButtonFavourite.OBJECT_OT_MRToggleFavBtn
           ]

    return ret