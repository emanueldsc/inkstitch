import json

import wx
from inkex import Group

from ...i18n import _
from ...svg import PIXELS_PER_MM
from ...svg.tags import INKSTITCH_LETTERING_PATCH
from ...utils.patch_geometry import combined_outline, combined_outlines, create_running_path, create_satin_path, polygon_paths
from ..lettering.main_panel import LetteringPanel
from .option_panel import LetteringPatchOptionsPanel


class LetteringPatchPanel(LetteringPanel):
    options_panel_class = LetteringPatchOptionsPanel
    border_methods = ("running_stitch", "satin_column", "e_stitch", "s_stitch", "zigzag")

    def load_settings(self):
        super().load_settings()
        self.settings.update({
            "border_enabled": True,
            "border_method": "running_stitch",
            "border_distance_mm": 1.5,
            "satin_width_mm": 2.0,
            "stabilization_enabled": True,
            "stabilization_stitch_length_mm": 2.5,
            "border_scope": "all",
            "border_color": "#000000",
            "extra_blocks": [],
        })
        if INKSTITCH_LETTERING_PATCH in self.group.attrib:
            try:
                self.settings.update(json.loads(self.group.get(INKSTITCH_LETTERING_PATCH)))
            except (TypeError, ValueError, json.decoder.JSONDecodeError):
                pass
        if self.settings.border_method == "satin":
            self.settings.border_method = "satin_column"
        if self.settings.border_method not in self.border_methods:
            self.settings.border_method = "running_stitch"
        if self.settings.border_scope not in ("all", "individual"):
            self.settings.border_scope = "all"

    def apply_settings(self):
        super().apply_settings()
        options = self.options_panel
        options.border_enabled.SetValue(bool(self.settings.border_enabled))
        options.border_method.SetSelection(self.border_methods.index(self.settings.border_method))
        options.border_distance.SetValue(self.settings.border_distance_mm)
        options.satin_width.SetValue(self.settings.satin_width_mm)
        options.stabilization_enabled.SetValue(bool(self.settings.stabilization_enabled))
        options.stabilization_stitch_length.SetValue(self.settings.stabilization_stitch_length_mm)
        options.border_scope.SetSelection(0 if self.settings.border_scope == "all" else 1)
        options.border_color.SetColour(self.settings.border_color)
        for block in self.settings.extra_blocks:
            self.add_text_block(block)

    def save_settings(self):
        super().save_settings()
        self.group.set(INKSTITCH_LETTERING_PATCH, json.dumps({
            "border_enabled": self.settings.border_enabled,
            "border_method": self.settings.border_method,
            "border_distance_mm": self.settings.border_distance_mm,
            "satin_width_mm": self.settings.satin_width_mm,
            "stabilization_enabled": self.settings.stabilization_enabled,
            "stabilization_stitch_length_mm": self.settings.stabilization_stitch_length_mm,
            "border_scope": self.settings.border_scope,
            "border_color": self.settings.border_color,
            "extra_blocks": self.extra_block_settings(),
        }))

    def on_patch_change(self):
        options = self.options_panel
        self.settings.border_enabled = options.border_enabled.GetValue()
        self.settings.border_method = self.border_methods[options.border_method.GetSelection()]
        self.settings.border_distance_mm = options.border_distance.GetValue()
        self.settings.satin_width_mm = options.satin_width.GetValue()
        self.settings.stabilization_enabled = options.stabilization_enabled.GetValue()
        self.settings.stabilization_stitch_length_mm = options.stabilization_stitch_length.GetValue()
        self.settings.border_scope = "all" if options.border_scope.GetSelection() == 0 else "individual"
        self.settings.border_color = options.border_color.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_preview()

    def add_text_block(self, data=None):
        data = data or {"text": "", "font": "", "scale": 100, "color": "#000000", "x_mm": 0, "y_mm": 0}
        options = self.options_panel
        row = wx.Panel(options)
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(row, style=wx.TE_MULTILINE, size=(220, 45), value=data.get("text", ""))
        font = wx.ComboBox(row, choices=list(self.fonts), style=wx.CB_READONLY)
        if data.get("font") in self.fonts:
            font.SetValue(data["font"])
        elif self.fonts:
            font.SetSelection(0)
        scale = wx.SpinCtrl(row, min=1, max=1000, initial=int(data.get("scale", 100)))
        color = wx.ColourPickerCtrl(row, colour=data.get("color", "#000000"))
        x_position = wx.SpinCtrlDouble(row, min=-1000, max=1000, inc=0.5, initial=float(data.get("x_mm", 0)))
        x_position.SetDigits(1)
        y_position = wx.SpinCtrlDouble(row, min=-1000, max=1000, inc=0.5, initial=float(data.get("y_mm", 0)))
        y_position.SetDigits(1)
        remove = wx.Button(row, label=_("Remove"))
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.Add(font, 1, wx.RIGHT, 5)
        controls.Add(scale, 0, wx.RIGHT, 5)
        controls.Add(color, 0, wx.RIGHT, 5)
        controls.Add(wx.StaticText(row, label=_("X")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        controls.Add(x_position, 0, wx.RIGHT, 5)
        controls.Add(wx.StaticText(row, label=_("Y")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        controls.Add(y_position, 0, wx.RIGHT, 5)
        controls.Add(remove, 0)
        sizer.Add(text, 1, wx.EXPAND | wx.BOTTOM, 5)
        sizer.Add(controls, 0, wx.EXPAND)
        row.SetSizer(sizer)
        options.extra_blocks_sizer.Insert(options.extra_blocks_sizer.GetItemCount() - 1, row, 0, wx.EXPAND | wx.ALL, 5)
        block = {
            "panel": row, "text": text, "font": font, "scale": scale, "color": color,
            "x_mm": x_position, "y_mm": y_position
        }
        options.extra_blocks.append(block)
        remove.Bind(wx.EVT_BUTTON, lambda event, block=block: self.remove_text_block(block))
        text.Bind(wx.EVT_TEXT, lambda event: self.update_preview())
        font.Bind(wx.EVT_COMBOBOX, lambda event: self.update_preview())
        scale.Bind(wx.EVT_SPINCTRL, lambda event: self.update_preview())
        color.Bind(wx.EVT_COLOURPICKER_CHANGED, lambda event: self.update_preview())
        x_position.Bind(wx.EVT_SPINCTRLDOUBLE, lambda event: self.update_preview())
        y_position.Bind(wx.EVT_SPINCTRLDOUBLE, lambda event: self.update_preview())
        options.Layout()
        options.SetupScrolling()
        self.update_preview()

    def remove_text_block(self, block):
        block["panel"].Destroy()
        self.options_panel.extra_blocks.remove(block)
        self.update_preview()

    def extra_block_settings(self):
        settings = []
        for block in self.options_panel.extra_blocks:
            settings.append({
                "text": block["text"].GetValue(),
                "font": block["font"].GetValue(),
                "scale": block["scale"].GetValue(),
                "color": block["color"].GetColour().GetAsString(wx.C2S_HTML_SYNTAX),
                "x_mm": block["x_mm"].GetValue(),
                "y_mm": block["y_mm"].GetValue(),
            })
        return settings

    def update_lettering(self, raise_error=False):
        super().update_lettering(raise_error)
        destination_group = self.group[-1] if len(self.group) else None
        if destination_group is None:
            return

        lettering_groups = [destination_group]
        extra_groups = []
        for block in self.options_panel.extra_blocks:
            font = self.fonts.get(block["font"].GetValue())
            text = block["text"].GetValue()
            if font is None or not text.strip():
                continue
            extra_group = Group()
            extra_group.label = _("Lettering")
            font.render_text(text, extra_group, scale=block["scale"].GetValue())
            extra_group.set("transform", "translate(%s,%s) scale(%s)" % (
                block["x_mm"].GetValue() * PIXELS_PER_MM,
                block["y_mm"].GetValue() * PIXELS_PER_MM,
                block["scale"].GetValue() / 100
            ))
            self.group.append(extra_group)
            lettering_groups.append(extra_group)
            extra_groups.append(extra_group)

        if self.settings.border_scope == "all":
            outlines = [combined_outlines(lettering_groups, self.settings.border_distance_mm)]
        else:
            outlines = [combined_outline(group, self.settings.border_distance_mm) for group in lettering_groups]
        outlines = [outline for outline in outlines if outline is not None]
        if not outlines:
            return

        stabilization_group = Group()
        stabilization_group.label = _("Stabilization")
        border_group = Group()
        border_group.label = _("Patch Border")

        if self.settings.stabilization_enabled:
            for outline in outlines:
                for points in polygon_paths(outline):
                    stabilization_group.append(create_running_path(
                        points,
                        _("Stabilization"),
                        self.settings.stabilization_stitch_length_mm
                    ))

        if self.settings.border_enabled:
            for index, outline in enumerate(outlines):
                color = self.settings.border_color
                if self.settings.border_scope == "individual" and index > 0:
                    block = self.options_panel.extra_blocks[index - 1]
                    color = block["color"].GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
                for points in polygon_paths(outline):
                    if self.settings.border_method == "running_stitch":
                        border = create_running_path(points, _("Patch Border"), 2.5, color=color)
                    else:
                        border = create_satin_path(
                            points,
                            _("Patch Border"),
                            self.settings.satin_width_mm,
                            satin_method=self.settings.border_method,
                            color=color
                        )
                        if border is None:
                            border = create_running_path(points, _("Patch Border"), 2.5, color=color)
                    border_group.append(border)

        lettering_group = Group()
        lettering_group.label = _("Lettering")
        self.group.remove(destination_group)
        for extra_group in extra_groups:
            self.group.remove(extra_group)
        lettering_group.append(destination_group)
        for extra_group in extra_groups:
            lettering_group.append(extra_group)
        if len(stabilization_group):
            self.group.append(stabilization_group)
        if len(border_group):
            self.group.append(border_group)
        self.group.append(lettering_group)
