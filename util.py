import html

# adapted from https://github.com/tvst/st-annotated-text/blob/master/annotated_text/util.py

from htbuilder import H, HtmlElement, styles
from htbuilder.units import unit

# Only works in 3.7+: from htbuilder import div, span
div = H.div
span = H.span
a = H.a

# Only works in 3.7+: from htbuilder.units import px, rem, em
px = unit.px
rem = unit.rem
em = unit.em

# Colors from the Streamlit palette.
# These are red-70, orange-70, ..., violet-70, gray-70.
PALETTE = [
    "#ff4b4b",
    "#ffa421",
    "#ffe312",
    "#21c354",
    "#00d4b1",
    "#00c0f2",
    "#1c83e1",
    "#803df5",
    "#808495",
]

OPACITIES = [
    "33", "66",
]


def annotation(annot_el, activated=False, background=None, color=None, style=None, annot_style=None):
    color_style = {}
    body = annot_el["string"]
    id = annot_el["token_id"]
    gov_id = annot_el["gov_id"]
    label = annot_el["upos"]
    if color:
        color_style['color'] = color
    if not background:
        # label_sum = sum(ord(c) for c in label)
        background_color = PALETTE[0] #[label_sum % len(PALETTE)]
        background_opacity = "66" if activated else "00" # OPACITIES[label_sum % len(OPACITIES)]
        background = background_color + background_opacity

    return (
        a(
            href="#",
            id=id,
            style=styles(
                background=background,
                # border_radius=rem(0.33),
                padding=(rem(0.125), rem(0.5)),
                # overflow="hidden",
                font_size=em(1.1),
                **color_style,
                **style if style is not None else {}
            ))(

            html.escape(body),

            span(
                style=styles(
                    padding_left=rem(0.5),
                    # text_transform="uppercase",
                    font_size="6px",
                    opacity="0.2",
                    **annot_style if annot_style is not None else {}
                ))(
                label
            ),
        )
    )

