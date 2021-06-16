from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def load_svg(filepath):
    return svg2rlg(filepath)

def render_svg(svg_image, dpi=72, *options):
    return renderPM.drawToPIL(svg_image, dpi=dpi, *options)

def load_svg_to_PIL(filepath, dpi=72, width=None, height=None, *options):
    svg_image = load_svg(filepath)
    temp = render_svg(svg_image, dpi=72, *options)
    if width is not None:
        return render_svg(svg_image, dpi=int(72*temp.size[0]/width))
    elif height is not None:
        return render_svg(svg_image, dpi=int(72*temp.size[1]/height))
    return temp