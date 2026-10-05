"""Legend configuration, heat-layer metadata, and shared layout helpers."""

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from string import Formatter

import staticmaps
from PIL import ImageFont


Position = Union[str, Tuple[float, float]]
ColorSpec = Union[
    str, staticmaps.Color, Tuple[int, int, int], Tuple[int, int, int, int]
]
_POSITIONS = {
    "top-left": (0, 0),
    "top-center": (0.5, 0),
    "top-right": (1, 0),
    "center-left": (0, 0.5),
    "center": (0.5, 0.5),
    "center-right": (1, 0.5),
    "bottom-left": (0, 1),
    "bottom-center": (0.5, 1),
    "bottom-right": (1, 1),
}


@dataclass(frozen=True)
class LegendOptions:
    """Options for the on-map heat legend.

    ``position`` is a named anchor or an ``(x, y)`` coordinate. Coordinates
    use pixels by default; fractions are measured against the output dimensions.
    ``background_opacity`` scales the panel color's alpha from 0 to 1 without
    changing text, swatch, border, or shadow opacity.
    """

    position: Position = "top-right"
    units: str = "pixels"
    anchor: Optional[str] = None
    offset: Tuple[float, float] = (0, 0)
    margin: float = 12
    allow_clipping: bool = False
    title: Optional[str] = "Observations per cell"
    label_format: str = "{count}"
    font_size: int = 13
    title_font_size: Optional[int] = None
    section_font_size: Optional[int] = None
    label_font_size: Optional[int] = None
    font_family: str = "DejaVu Sans"
    title_weight: str = "bold"
    section_weight: str = "bold"
    label_weight: str = "normal"
    title_align: str = "left"
    text_color: ColorSpec = "#17212f"
    title_color: Optional[ColorSpec] = None
    section_color: Optional[ColorSpec] = None
    label_color: Optional[ColorSpec] = None
    background_color: ColorSpec = (255, 255, 255, 248)
    border_color: ColorSpec = "#d8dee8"
    border_width: int = 1
    corner_radius: int = 12
    shadow: bool = True
    shadow_color: ColorSpec = "#17212f"
    shadow_opacity: float = 0.10
    shadow_offset: Tuple[float, float] = (2, 3)
    divider_color: Optional[ColorSpec] = None
    divider_width: float = 1
    title_spacing: int = 14
    section_spacing: int = 8
    padding: int = 14
    swatch_size: int = 16
    swatch_radius: float = 4
    label_gap: int = 8
    row_spacing: int = 8
    column_spacing: int = 20
    columns: int = 1
    count_order: str = "descending"
    background_opacity: float = 1.0
    title_wrap: bool = True
    title_max_width: Optional[int] = None
    title_line_spacing: int = 3


@dataclass(frozen=True)
class HeatLayerInfo:
    """Immutable summary and final colors for one occupied heat layer."""

    grid: str
    precision: int
    label: Optional[str]
    observation_count: int
    cell_count: int
    counts: Tuple[int, ...]
    count_colors: Tuple[Tuple[int, Tuple[int, int, int, int]], ...]
    legend_ranges: Tuple[Tuple[int, int, Tuple[int, int, int, int]], ...] = ()


@dataclass(frozen=True)
class LegendRow:
    label: str
    color: Tuple[int, int, int, int]


@dataclass(frozen=True)
class LegendSection:
    title: str
    rows: Tuple[LegendRow, ...]


@dataclass(frozen=True)
class LegendLayout:
    x: float
    y: float
    width: float
    height: float
    column_widths: Tuple[float, ...]
    title: Optional[str]
    sections: Tuple[Tuple[str, Tuple[Tuple[LegendRow, ...], ...]], ...]
    title_lines: Tuple[str, ...] = ()


def _color_tuple(color: ColorSpec, option: str) -> Tuple[int, int, int, int]:
    try:
        parsed = staticmaps.parse_color(color) if isinstance(color, str) else color
        if isinstance(parsed, staticmaps.Color):
            rgba = parsed.int_rgba()
            return (rgba[0], rgba[1], rgba[2], rgba[3])
        if isinstance(parsed, (tuple, list)) and len(parsed) in (3, 4):
            values = tuple(parsed) + ((255,) if len(parsed) == 3 else ())
            if all(isinstance(value, int) and 0 <= value <= 255 for value in values):
                return values  # type: ignore[return-value]
    except (TypeError, ValueError):
        pass
    raise ValueError(
        "{} must be a color name, hex string, Color, or RGB(A) tuple".format(option)
    )


def _size(options: LegendOptions, name: str) -> int:
    return getattr(options, "{}_font_size".format(name)) or options.font_size


def _weight(options: LegendOptions, name: str) -> bool:
    return bool(getattr(options, "{}_weight".format(name)) == "bold")


def _style_color(options: LegendOptions, name: str) -> ColorSpec:
    color = getattr(options, "{}_color".format(name))
    return options.text_color if color is None else color


def validate_legend_options(options: LegendOptions) -> None:
    if not isinstance(options, LegendOptions):
        raise TypeError("legend must be a bool or LegendOptions")
    position = options.position
    if isinstance(position, str):
        if position not in _POSITIONS:
            raise ValueError("unknown legend position: {}".format(position))
    elif not (
        isinstance(position, tuple)
        and len(position) == 2
        and all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in position
        )
    ):
        raise ValueError("position must be a named position or a finite (x, y) tuple")
    if options.units not in ("pixels", "fraction"):
        raise ValueError("units must be 'pixels' or 'fraction'")
    if options.anchor is not None and options.anchor not in _POSITIONS:
        raise ValueError("anchor must be one of the nine named positions")
    for name, pair in (("offset", options.offset),):
        if (
            not isinstance(pair, tuple)
            or len(pair) != 2
            or not all(
                isinstance(value, (int, float)) and math.isfinite(value)
                for value in pair
            )
        ):
            raise ValueError("{} must be a finite pair of numbers".format(name))
    numeric_positive = ("font_size", "swatch_size", "columns")
    for name in numeric_positive:
        value = getattr(options, name)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("{} must be a positive integer".format(name))
    for name in (
        "margin",
        "border_width",
        "corner_radius",
        "padding",
        "divider_width",
        "title_spacing",
        "title_line_spacing",
        "section_spacing",
        "label_gap",
        "row_spacing",
        "column_spacing",
        "swatch_radius",
    ):
        value = getattr(options, name)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("{} must be a finite non-negative number".format(name))
    if not isinstance(options.allow_clipping, bool):
        raise ValueError("allow_clipping must be bool")
    if not isinstance(options.shadow, bool):
        raise ValueError("shadow must be bool")
    if not isinstance(options.title_wrap, bool):
        raise ValueError("title_wrap must be bool")
    if options.title_max_width is not None and (
        isinstance(options.title_max_width, bool)
        or not isinstance(options.title_max_width, int)
        or options.title_max_width <= 0
    ):
        raise ValueError("title_max_width must be a positive integer or None")
    for name in ("shadow_opacity", "background_opacity"):
        value = getattr(options, name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError("{} must be between 0 and 1".format(name))
    for name in ("title_font_size", "section_font_size", "label_font_size"):
        value = getattr(options, name)
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
        ):
            raise ValueError("{} must be a positive integer or None".format(name))
    for name in ("title_weight", "section_weight", "label_weight"):
        if getattr(options, name) not in ("normal", "bold"):
            raise ValueError("{} must be 'normal' or 'bold'".format(name))
    if not isinstance(options.font_family, str) or not options.font_family.strip():
        raise ValueError("font_family must be a non-empty string")
    if options.title_align not in ("left", "center", "right"):
        raise ValueError("title_align must be 'left', 'center', or 'right'")
    if (
        not isinstance(options.shadow_offset, tuple)
        or len(options.shadow_offset) != 2
        or not all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in options.shadow_offset
        )
    ):
        raise ValueError("shadow_offset must be a finite pair of numbers")
    if options.title is not None and not isinstance(options.title, str):
        raise ValueError("title must be a string or None")
    if not isinstance(options.label_format, str):
        raise ValueError("label_format must be a string")
    if options.count_order not in ("descending", "ascending"):
        raise ValueError("count_order must be 'descending' or 'ascending'")
    try:
        options.label_format.format(count=1)
        if not any(
            field == "count"
            for _, field, _, _ in Formatter().parse(options.label_format)
        ):
            raise ValueError("label_format must contain {count}")
    except (IndexError, KeyError, ValueError) as exc:
        raise ValueError(
            "label_format must be a format string containing {count}"
        ) from exc
    for name in (
        "text_color",
        "title_color",
        "section_color",
        "label_color",
        "background_color",
        "border_color",
        "shadow_color",
        "divider_color",
    ):
        color = getattr(options, name)
        if color is not None:
            _color_tuple(color, name)


def layout_legend(
    layers: Tuple[HeatLayerInfo, ...], options: LegendOptions, width: int, height: int
) -> Optional[LegendLayout]:
    """Measure legend content and return its image-coordinate bounds."""
    sections = []
    multiple = len(layers) > 1
    for index, layer in enumerate(layers):
        if layer.legend_ranges:
            values = tuple(
                LegendRow(
                    options.label_format.format(
                        count=(str(low) if low == high else "{}-{}".format(low, high))
                    ),
                    color,
                )
                for low, high, color in layer.legend_ranges
            )
        else:
            values = tuple(
                LegendRow(options.label_format.format(count=count), color)
                for count, color in layer.count_colors
            )
        rows = values if options.count_order == "ascending" else tuple(reversed(values))
        if rows:
            section_title = layer.label or "{} layer {}".format(
                layer.grid.upper(), index + 1
            )
            sections.append(
                (section_title if multiple else "", _columns(rows, options.columns))
            )
    if not sections:
        return None

    label_font = _font(
        _size(options, "label"),
        bold=_weight(options, "label"),
        family=options.font_family,
    )
    title_font = _font(
        _size(options, "title"),
        bold=_weight(options, "title"),
        family=options.font_family,
    )
    section_font = _font(
        _size(options, "section"),
        bold=_weight(options, "section"),
        family=options.font_family,
    )
    column_widths = [0.0] * max(len(columns) for _, columns in sections)
    for _, columns in sections:
        for index, rows in enumerate(columns):
            label_width = max(_text_width(label_font, row.label) for row in rows)
            column_widths[index] = max(
                column_widths[index],
                options.swatch_size + options.label_gap + label_width,
            )
    heading_widths = [
        _text_width(section_font, title) for title, _ in sections if title
    ]
    heading_width = max(heading_widths or [0])
    number_of_columns = max(len(columns) for _, columns in sections)
    content_width = max(
        sum(column_widths) + options.column_spacing * max(0, number_of_columns - 1),
        heading_width,
    )
    title_lines: Tuple[str, ...] = ()
    if options.title:
        if options.title_wrap:
            word_width = max(
                [_text_width(title_font, word) for word in options.title.split()] or [0]
            )
            wrap_width = options.title_max_width or max(content_width, word_width)
            title_lines = _wrap_title(options.title, title_font, wrap_width)
        else:
            title_lines = tuple(options.title.split("\n"))
    panel_width = options.padding * 2 + max(
        content_width,
        max([_text_width(title_font, line) for line in title_lines] or [0]),
    )
    title_height = _title_height(title_font, title_lines, options.title_line_spacing)
    section_content_height = 0
    for section_index, (section_title, cols) in enumerate(sections):
        section_rows = max(len(column_rows) for column_rows in cols)
        section_content_height += _text_height(section_font, section_title) + (
            options.section_spacing if section_title else 0
        )
        section_content_height += (
            max(_text_height(label_font, "M"), options.swatch_size) * section_rows
        )
        section_content_height += options.row_spacing * max(0, section_rows - 1)
        if section_index < len(sections) - 1:
            section_content_height += options.section_spacing + options.row_spacing
    panel_height = (
        options.padding * 2
        + title_height
        + (options.title_spacing if title_height else 0)
        + section_content_height
    )

    if isinstance(options.position, str):
        px, py = _POSITIONS[options.position]
        x = width * px
        y = height * py
        anchor = options.anchor or options.position
        ax, ay = _POSITIONS[anchor]
        x -= panel_width * ax
        y -= panel_height * ay
        x += options.margin * (1 if px == 0 else -1 if px == 1 else 0)
        y += options.margin * (1 if py == 0 else -1 if py == 1 else 0)
    else:
        x, y = options.position
        if options.units == "fraction":
            x, y = x * width, y * height
        ax, ay = _POSITIONS[options.anchor or "top-left"]
        x -= panel_width * ax
        y -= panel_height * ay
    x += options.offset[0]
    y += options.offset[1]
    if not options.allow_clipping and (
        x < 0 or y < 0 or x + panel_width > width or y + panel_height > height
    ):
        raise ValueError(
            "legend does not fit inside the {}x{} canvas; use more columns, smaller styling, "
            "a larger output, or allow_clipping=True".format(width, height)
        )
    return LegendLayout(
        x,
        y,
        panel_width,
        panel_height,
        tuple(column_widths),
        options.title,
        tuple(sections),
        title_lines,
    )


def _columns(
    rows: Tuple[LegendRow, ...], count: int
) -> Tuple[Tuple[LegendRow, ...], ...]:
    count = min(count, len(rows))
    return tuple(tuple(rows[index::count]) for index in range(count))


def _font(size: int, bold: bool = False, family: str = "DejaVu Sans") -> Any:
    bundled = str(
        Path(__file__).with_name("fonts")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    )
    if family.strip().lower() in ("dejavu sans", "sans", "sans-serif"):
        return ImageFont.truetype(bundled, size)
    if family.lower().endswith((".ttf", ".otf")):
        suffix = family[-4:]
        names = ([family[:-4] + "-Bold" + suffix] if bold else []) + [family]
    else:
        names = ([family.replace(" ", "") + "-Bold.ttf"] if bold else []) + [family]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.truetype(bundled, size)


def _text_width(font: Any, text: str) -> int:
    return int(math.ceil(font.getlength(text)))


def _text_height(font: Any, text: Optional[str]) -> int:
    if not text:
        return 0
    ascent, descent = font.getmetrics()
    return int(ascent + descent)


def _text_baseline(font: Any) -> int:
    return int(font.getmetrics()[0])


def _wrap_title(title: str, font: Any, width: float) -> Tuple[str, ...]:
    """Wrap at word boundaries, splitting overlong words for explicit width caps."""
    lines = []
    for paragraph in title.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = "{} {}".format(line, word) if line else word
            if _text_width(font, candidate) <= width:
                line = candidate
                continue
            if line:
                lines.append(line)
            while _text_width(font, word) > width and len(word) > 1:
                cut = 1
                while cut < len(word) and _text_width(font, word[: cut + 1]) <= width:
                    cut += 1
                lines.append(word[:cut])
                word = word[cut:]
            line = word
        lines.append(line)
    return tuple(lines)


def _title_height(font: Any, lines: Tuple[str, ...], spacing: int) -> int:
    return _text_height(font, "M") * len(lines) + spacing * max(0, len(lines) - 1)


def color_to_rgba(color: ColorSpec) -> Tuple[int, int, int, int]:
    """Return a validated RGBA tuple for a public color specification."""
    return _color_tuple(color, "color")


def legend_colors(options: LegendOptions) -> Dict[str, Tuple[int, int, int, int]]:
    background = _color_tuple(options.background_color, "background_color")
    return {
        "text": _color_tuple(options.text_color, "text_color"),
        "title": _color_tuple(_style_color(options, "title"), "title_color"),
        "section": _color_tuple(_style_color(options, "section"), "section_color"),
        "label": _color_tuple(_style_color(options, "label"), "label_color"),
        "background": (
            *background[:3],
            round(background[3] * options.background_opacity),
        ),
        "border": _color_tuple(options.border_color, "border_color"),
        "shadow": _color_tuple(options.shadow_color, "shadow_color"),
        "divider": _color_tuple(
            options.border_color
            if options.divider_color is None
            else options.divider_color,
            "divider_color",
        ),
    }


def draw_svg_legend(
    drawing: Any,
    layers: Tuple[HeatLayerInfo, ...],
    options: LegendOptions,
    width: int,
    height: int,
) -> None:
    """Add the legend to an svgwrite drawing in image coordinates."""
    layout = layout_legend(layers, options, width, height)
    if layout is None:
        return
    colors = legend_colors(options)
    background = "#{:02x}{:02x}{:02x}".format(*colors["background"][:3])
    border = "#{:02x}{:02x}{:02x}".format(*colors["border"][:3])
    divider = "#{:02x}{:02x}{:02x}".format(*colors["divider"][:3])
    shadow = "#{:02x}{:02x}{:02x}".format(*colors["shadow"][:3])
    group = drawing.g()
    if options.shadow:
        group.add(
            drawing.rect(
                insert=(
                    layout.x + options.shadow_offset[0],
                    layout.y + options.shadow_offset[1],
                ),
                size=(layout.width, layout.height),
                rx=options.corner_radius,
                ry=options.corner_radius,
                fill=shadow,
                fill_opacity=options.shadow_opacity * colors["shadow"][3] / 255,
            )
        )
    group.add(
        drawing.rect(
            insert=(layout.x, layout.y),
            size=(layout.width, layout.height),
            rx=options.corner_radius,
            ry=options.corner_radius,
            fill=background,
            fill_opacity=colors["background"][3] / 255,
            stroke=border,
            stroke_opacity=colors["border"][3] / 255,
            stroke_width=options.border_width,
        )
    )
    label_size = _size(options, "label")
    title_size = _size(options, "title")
    section_size = _size(options, "section")
    label_font = _font(
        label_size, bold=_weight(options, "label"), family=options.font_family
    )
    title_font = _font(
        title_size, bold=_weight(options, "title"), family=options.font_family
    )
    section_font = _font(
        section_size, bold=_weight(options, "section"), family=options.font_family
    )
    y = layout.y + options.padding
    if layout.title:
        if options.title_align == "center":
            title_x, text_anchor = layout.x + layout.width / 2, "middle"
        elif options.title_align == "right":
            title_x, text_anchor = layout.x + layout.width - options.padding, "end"
        else:
            title_x, text_anchor = layout.x + options.padding, "start"
        line_height = _text_height(title_font, "M")
        for index, line in enumerate(layout.title_lines):
            group.add(
                drawing.text(
                    line,
                    insert=(
                        title_x,
                        y
                        + index * (line_height + options.title_line_spacing)
                        + _text_baseline(title_font),
                    ),
                    text_anchor=text_anchor,
                    fill="#{:02x}{:02x}{:02x}".format(*colors["title"][:3]),
                    fill_opacity=colors["title"][3] / 255,
                    font_size=title_size,
                    font_weight=options.title_weight,
                    font_family=options.font_family,
                )
            )
        title_height = _title_height(
            title_font, layout.title_lines, options.title_line_spacing
        )
        if options.divider_width:
            divider_y = y + title_height + max(1, options.title_spacing / 2)
            group.add(
                drawing.line(
                    start=(layout.x + options.padding, divider_y),
                    end=(layout.x + layout.width - options.padding, divider_y),
                    stroke=divider,
                    stroke_opacity=colors["divider"][3] / 255,
                    stroke_width=options.divider_width,
                )
            )
        y += title_height + options.title_spacing
    row_height = max(_text_height(label_font, "M"), options.swatch_size)
    for section_title, columns in layout.sections:
        if section_title:
            group.add(
                drawing.text(
                    section_title,
                    insert=(
                        layout.x + options.padding,
                        y + _text_baseline(section_font),
                    ),
                    fill="#{:02x}{:02x}{:02x}".format(*colors["section"][:3]),
                    fill_opacity=colors["section"][3] / 255,
                    font_size=section_size,
                    font_weight=options.section_weight,
                    font_family=options.font_family,
                )
            )
            y += _text_height(section_font, section_title) + options.section_spacing
        max_rows = max(len(column) for column in columns)
        for column_index, column in enumerate(columns):
            x = (
                layout.x
                + options.padding
                + sum(layout.column_widths[:column_index])
                + options.column_spacing * column_index
            )
            for row_index, row in enumerate(column):
                top = y + row_index * (row_height + options.row_spacing)
                group.add(
                    drawing.rect(
                        insert=(
                            x,
                            top + max(0, (row_height - options.swatch_size) / 2),
                        ),
                        size=(options.swatch_size, options.swatch_size),
                        rx=min(options.swatch_radius, options.swatch_size / 2),
                        ry=min(options.swatch_radius, options.swatch_size / 2),
                        fill="#{:02x}{:02x}{:02x}".format(*row.color[:3]),
                        fill_opacity=row.color[3] / 255,
                    )
                )
                group.add(
                    drawing.text(
                        row.label,
                        insert=(
                            x + options.swatch_size + options.label_gap,
                            top
                            + (row_height - _text_height(label_font, "M")) / 2
                            + _text_baseline(label_font),
                        ),
                        fill="#{:02x}{:02x}{:02x}".format(*colors["label"][:3]),
                        fill_opacity=colors["label"][3] / 255,
                        font_size=label_size,
                        font_weight=options.label_weight,
                        font_family=options.font_family,
                    )
                )
        y += max_rows * row_height + (max_rows - 1) * options.row_spacing
        y += options.section_spacing + options.row_spacing
    drawing.add(group)


def draw_cairo_legend(
    surface: Any,
    layers: Tuple[HeatLayerInfo, ...],
    options: LegendOptions,
    width: int,
    height: int,
) -> None:
    """Paint the legend over a Cairo image surface."""
    layout = layout_legend(layers, options, width, height)
    if layout is None:
        return
    import cairo  # type: ignore

    colors = legend_colors(options)
    context = cairo.Context(surface)

    def rgba(value: Tuple[int, int, int, int]) -> Tuple[float, float, float, float]:
        return tuple(channel / 255 for channel in value)  # type: ignore[return-value]

    def rounded_rectangle(
        x: float,
        y: float,
        rectangle_width: float,
        rectangle_height: float,
        radius: float,
    ) -> None:
        radius = min(radius, rectangle_width / 2, rectangle_height / 2)
        context.new_path()
        context.move_to(x + radius, y)
        context.line_to(x + rectangle_width - radius, y)
        context.arc(x + rectangle_width - radius, y + radius, radius, -math.pi / 2, 0)
        context.line_to(x + rectangle_width, y + rectangle_height - radius)
        context.arc(
            x + rectangle_width - radius,
            y + rectangle_height - radius,
            radius,
            0,
            math.pi / 2,
        )
        context.line_to(x + radius, y + rectangle_height)
        context.arc(
            x + radius, y + rectangle_height - radius, radius, math.pi / 2, math.pi
        )
        context.line_to(x, y + radius)
        context.arc(x + radius, y + radius, radius, math.pi, 3 * math.pi / 2)
        context.close_path()

    if options.shadow:
        shadow_x, shadow_y = options.shadow_offset
        rounded_rectangle(
            layout.x + shadow_x,
            layout.y + shadow_y,
            layout.width,
            layout.height,
            options.corner_radius,
        )
        shadow = colors["shadow"]
        context.set_source_rgba(
            shadow[0] / 255,
            shadow[1] / 255,
            shadow[2] / 255,
            shadow[3] / 255 * options.shadow_opacity,
        )
        context.fill()
    context.set_source_rgba(*rgba(colors["background"]))
    rounded_rectangle(
        layout.x, layout.y, layout.width, layout.height, options.corner_radius
    )
    context.fill_preserve()
    context.set_source_rgba(*rgba(colors["border"]))
    context.set_line_width(options.border_width)
    context.stroke()

    def select_font(size: int, bold: bool) -> None:
        weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
        context.select_font_face(options.font_family, cairo.FONT_SLANT_NORMAL, weight)
        context.set_font_size(size)

    label_size = _size(options, "label")
    title_size = _size(options, "title")
    section_size = _size(options, "section")
    label_font = _font(
        label_size, bold=_weight(options, "label"), family=options.font_family
    )
    title_font = _font(
        title_size, bold=_weight(options, "title"), family=options.font_family
    )
    section_font = _font(
        section_size, bold=_weight(options, "section"), family=options.font_family
    )

    def baseline(top: float, line_height: float) -> float:
        ascent, descent, _, _, _ = context.font_extents()
        return float(top + (line_height - ascent - descent) / 2 + ascent)

    y = layout.y + options.padding
    if layout.title:
        select_font(title_size, _weight(options, "title"))
        line_height = _text_height(title_font, "M")
        title_height = _title_height(
            title_font, layout.title_lines, options.title_line_spacing
        )
        title_color = colors["title"]
        context.set_source_rgba(*rgba(title_color))
        for index, line in enumerate(layout.title_lines):
            advance = context.text_extents(line)[4]
            if options.title_align == "center":
                title_x = layout.x + (layout.width - advance) / 2
            elif options.title_align == "right":
                title_x = layout.x + layout.width - options.padding - advance
            else:
                title_x = layout.x + options.padding
            context.move_to(
                title_x,
                baseline(
                    y + index * (line_height + options.title_line_spacing), line_height
                ),
            )
            context.show_text(line)
        if options.divider_width:
            divider_y = y + title_height + max(1, options.title_spacing / 2)
            context.set_source_rgba(*rgba(colors["divider"]))
            context.set_line_width(options.divider_width)
            context.move_to(layout.x + options.padding, divider_y)
            context.line_to(layout.x + layout.width - options.padding, divider_y)
            context.stroke()
        y += title_height + options.title_spacing
    row_height = max(_text_height(label_font, "M"), options.swatch_size)
    for section_title, columns in layout.sections:
        if section_title:
            select_font(section_size, _weight(options, "section"))
            section_height = _text_height(section_font, section_title)
            context.set_source_rgba(*rgba(colors["section"]))
            context.move_to(layout.x + options.padding, baseline(y, section_height))
            context.show_text(section_title)
            y += section_height + options.section_spacing
        max_rows = max(len(column) for column in columns)
        for column_index, column in enumerate(columns):
            x = (
                layout.x
                + options.padding
                + sum(layout.column_widths[:column_index])
                + options.column_spacing * column_index
            )
            for row_index, row in enumerate(column):
                top = y + row_index * (row_height + options.row_spacing)
                context.set_source_rgba(*rgba(row.color))
                rounded_rectangle(
                    x,
                    top + max(0, (row_height - options.swatch_size) / 2),
                    options.swatch_size,
                    options.swatch_size,
                    min(options.swatch_radius, options.swatch_size / 2),
                )
                context.fill()
                select_font(label_size, _weight(options, "label"))
                context.set_source_rgba(*rgba(colors["label"]))
                context.move_to(
                    x + options.swatch_size + options.label_gap,
                    baseline(top, row_height),
                )
                context.show_text(row.label)
        y += max_rows * row_height + (max_rows - 1) * options.row_spacing
        y += options.section_spacing + options.row_spacing
