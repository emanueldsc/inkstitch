import wx

from ...i18n import _
from ..lettering.option_panel import LetteringOptionsPanel


class LetteringPatchOptionsPanel(LetteringOptionsPanel):
    def __init__(self, parent, panel):
        super().__init__(parent, panel)

        self.patch_box = wx.StaticBox(self, wx.ID_ANY, label=_("Patch"))
        patch_sizer = wx.StaticBoxSizer(self.patch_box, wx.VERTICAL)

        self.border_enabled = wx.CheckBox(self, label=_("Add patch border"))
        self.border_enabled.SetValue(True)
        self.border_enabled.Bind(wx.EVT_CHECKBOX, lambda event: panel.on_patch_change())
        patch_sizer.Add(self.border_enabled, 0, wx.ALL, 5)

        method_sizer = wx.BoxSizer(wx.HORIZONTAL)
        method_sizer.Add(wx.StaticText(self, label=_("Border method")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.border_method = wx.Choice(self, choices=[
            _("Running Stitch"),
            _("Satin Column"),
            _("E Stitch"),
            _("S Stitch"),
            _("Zig-zag")
        ])
        self.border_method.SetSelection(0)
        self.border_method.Bind(wx.EVT_CHOICE, lambda event: panel.on_patch_change())
        method_sizer.Add(self.border_method, 1)
        patch_sizer.Add(method_sizer, 0, wx.EXPAND | wx.ALL, 5)

        color_sizer = wx.BoxSizer(wx.HORIZONTAL)
        color_sizer.Add(wx.StaticText(self, label=_("Main border color")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.border_color = wx.ColourPickerCtrl(self, colour="#000000")
        self.border_color.Bind(wx.EVT_COLOURPICKER_CHANGED, lambda event: panel.on_patch_change())
        color_sizer.Add(self.border_color, 0)
        patch_sizer.Add(color_sizer, 0, wx.EXPAND | wx.ALL, 5)

        values_sizer = wx.FlexGridSizer(0, 2, 5, 5)
        values_sizer.AddGrowableCol(1)
        values_sizer.Add(wx.StaticText(self, label=_("Border distance (mm)")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.border_distance = wx.SpinCtrlDouble(self, min=0, max=100, inc=0.1, initial=1.5)
        self.border_distance.SetDigits(2)
        self.border_distance.Bind(wx.EVT_SPINCTRLDOUBLE, lambda event: panel.on_patch_change())
        values_sizer.Add(self.border_distance, 1, wx.EXPAND)
        values_sizer.Add(wx.StaticText(self, label=_("Satin width (mm)")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.satin_width = wx.SpinCtrlDouble(self, min=0.3, max=20, inc=0.1, initial=2.0)
        self.satin_width.SetDigits(2)
        self.satin_width.Bind(wx.EVT_SPINCTRLDOUBLE, lambda event: panel.on_patch_change())
        values_sizer.Add(self.satin_width, 1, wx.EXPAND)
        patch_sizer.Add(values_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.stabilization_enabled = wx.CheckBox(self, label=_("Add stabilizing outline"))
        self.stabilization_enabled.SetValue(True)
        self.stabilization_enabled.Bind(wx.EVT_CHECKBOX, lambda event: panel.on_patch_change())
        patch_sizer.Add(self.stabilization_enabled, 0, wx.ALL, 5)

        stabilization_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stabilization_sizer.Add(
            wx.StaticText(self, label=_("Stabilization stitch length (mm)")),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            5
        )
        self.stabilization_stitch_length = wx.SpinCtrlDouble(
            self,
            min=0.1,
            max=20,
            inc=0.1,
            initial=2.5
        )
        self.stabilization_stitch_length.SetDigits(2)
        self.stabilization_stitch_length.Bind(
            wx.EVT_SPINCTRLDOUBLE,
            lambda event: panel.on_patch_change()
        )
        stabilization_sizer.Add(self.stabilization_stitch_length, 0)
        patch_sizer.Add(stabilization_sizer, 0, wx.EXPAND | wx.ALL, 5)

        scope_sizer = wx.BoxSizer(wx.HORIZONTAL)
        scope_sizer.Add(wx.StaticText(self, label=_("Border scope")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.border_scope = wx.Choice(self, choices=[_("Around all text"), _("One border per text")])
        self.border_scope.SetSelection(0)
        self.border_scope.Bind(wx.EVT_CHOICE, lambda event: panel.on_patch_change())
        scope_sizer.Add(self.border_scope, 1)
        patch_sizer.Add(scope_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.extra_blocks_box = wx.StaticBox(self, wx.ID_ANY, label=_("Additional text blocks"))
        self.extra_blocks_sizer = wx.StaticBoxSizer(self.extra_blocks_box, wx.VERTICAL)
        self.extra_blocks = []
        add_block_button = wx.Button(self, label=_("Add text"))
        add_block_button.Bind(wx.EVT_BUTTON, lambda event: panel.add_text_block())
        self.extra_blocks_sizer.Add(add_block_button, 0, wx.ALL, 5)
        patch_sizer.Add(self.extra_blocks_sizer, 0, wx.EXPAND | wx.ALL, 5)

        outer_sizer = self.GetSizer()
        outer_sizer.Add(patch_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.Layout()
        self.SetupScrolling()