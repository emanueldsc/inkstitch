# Authors: see git history
#
# Copyright (c) 2026 Authors
# Licensed under the GNU GPL version 3.0 or later.  See the file LICENSE for details.

import sys

import inkex
import wx

from ..i18n import _
from ..gui.lettering_patch import LetteringPatchPanel
from ..gui.simulator import SplitSimulatorWindow
from ..svg import get_correction_transform
from ..svg.tags import INKSCAPE_LABEL, INKSTITCH_LETTERING_PATCH, SVG_GROUP_TAG
from ..utils.svg_data import get_pagecolor
from .base import InkstitchExtension


class LetteringPatch(InkstitchExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def get_or_create_group(self):
        for node in self.svg.selection:
            if node.tag == SVG_GROUP_TAG and INKSTITCH_LETTERING_PATCH in node.attrib:
                return node
            for group in node.iterancestors(SVG_GROUP_TAG):
                if INKSTITCH_LETTERING_PATCH in group.attrib:
                    return group

        group = inkex.Group(attrib={
            INKSCAPE_LABEL: _("Ink/Stitch Lettering Patch"),
            "transform": get_correction_transform(self.get_current_layer(), child=True),
            INKSTITCH_LETTERING_PATCH: "{}"
        })
        self.get_current_layer().append(group)
        return group

    def effect(self):
        app = wx.App()
        frame = SplitSimulatorWindow(
            title=_("Ink/Stitch Lettering Patch"),
            panel_class=LetteringPatchPanel,
            group=self.get_or_create_group(),
            on_cancel=self.cancel,
            metadata=self.get_inkstitch_metadata(),
            background_color=get_pagecolor(self.svg.namedview),
            target_duration=1
        )
        frame.Show()
        app.MainLoop()

        if self.cancelled:
            sys.exit(0)