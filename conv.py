from svgli import svg2rlg
from reportlab.graphics import renderPDF, renderPM

drawing = svg2rlg(
    "http://commons.wikimedia.org/wiki/Special:FilePath/LocationFinland.svg")
renderPM.drawToFile(drawing, "file.png", fmt="PNG")
