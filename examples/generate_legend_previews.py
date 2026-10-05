"""Render a visual matrix of all legend positions at three native sizes.

Run from an editable checkout with:
    python examples/generate_legend_previews.py

OpenStreetMap tiles require network access on a cold cache.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import heatfall
from generate_doc_maps import synthetic_tampa_observations


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)
    context = heatfall.Context()
    lats, lons = synthetic_tampa_observations()
    context.add_heat_h3s(lats, lons, precision=9, legend_label="H3 cells")
    families = (
        ((320, 240), 11, 12, 10, 3, "top"),
        ((440, 300), 14, 16, 14, 1, "center"),
        ((480, 340), 18, 22, 18, 2, "bottom"),
    )
    gallery = Image.new("RGB", (1560, 1120), "#edf1f5")
    draw = ImageDraw.Draw(gallery)
    font_dir = Path(heatfall.__file__).parent / "fonts"
    heading = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 20)
    caption = ImageFont.truetype(str(font_dir / "DejaVuSans.ttf"), 14)
    draw.text((20, 16), "Legend placement and sizing", font=heading, fill="#17212f")
    y = 60
    for size, font_size, swatch_size, padding, columns, vertical in families:
        for column, horizontal in enumerate(("left", "center", "right")):
            position = (
                "center"
                if vertical == horizontal == "center"
                else "{}-{}".format(vertical, horizontal)
            )
            context.set_legend(
                heatfall.LegendOptions(
                    position=position,
                    font_size=font_size,
                    swatch_size=swatch_size,
                    padding=padding,
                    columns=columns,
                    margin=24 if vertical == "bottom" else 12,
                    row_spacing=6 if font_size == 11 else 8,
                    column_spacing=14 if font_size == 11 else 20,
                )
            )
            x = column * 520 + (520 - size[0]) // 2
            draw.text((column * 520 + 20, y), position, font=heading, fill="#17212f")
            draw.text(
                (column * 520 + 20, y + 28),
                "{} x {} / {} px type / {} {}".format(
                    *size, font_size, columns, "column" if columns == 1 else "columns"
                ),
                font=caption,
                fill="#526070",
            )
            gallery.paste(context.render_pillow(*size).convert("RGB"), (x, y + 56))
        y += size[1] + 64
    gallery.save(output / "legend-positions.png")

    transparency = Image.new("RGB", (1500, 360), "#edf1f5")
    transparency_draw = ImageDraw.Draw(transparency)
    for column, opacity in enumerate((1.0, 0.65, 0.35)):
        transparency_draw.text(
            (column * 500 + 10, 12),
            "Background opacity: {:.0%}".format(opacity),
            font=heading,
            fill="#17212f",
        )
        context.set_legend(
            heatfall.LegendOptions(
                position="center",
                background_color="white",
                background_opacity=opacity,
                shadow=False,
            )
        )
        transparency.paste(
            context.render_pillow(480, 300).convert("RGB"), (column * 500 + 10, 50)
        )
    transparency.save(output / "legend-opacity.png")

    # Also exercise independent heading sizes and multiple labelled layers.
    context.add_heat_hashes(lats, lons, precision=7, legend_label="Geohash cells")
    context.set_legend(
        heatfall.LegendOptions(
            position="top-left",
            title="Activity by grid",
            title_font_size=18,
            section_font_size=12,
            label_font_size=14,
            section_color="#526070",
            columns=3,
            section_spacing=10,
        )
    )
    context.render_pillow(800, 500).save(output / "legend-layers.png")
    print("Rendered legend previews to {}".format(output))


if __name__ == "__main__":
    main()
