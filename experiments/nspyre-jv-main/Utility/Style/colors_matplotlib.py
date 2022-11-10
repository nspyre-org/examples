from collections import OrderedDict

C0 = (31, 119, 180)
C1 = (255, 127, 14)
C2 = (44, 160, 44)
C3 = (214, 39, 40)
C4 = (148, 103, 189)
C5 = (140, 86, 75)
C6 = (227, 119, 194)
C7 = (127, 127, 127)
C8 = (188, 189, 34)
C9 = (23, 190, 207)
blackish = (24, 24, 24)

colors = OrderedDict(
    [
        ('C0', C0),
        ('C1', C1),
        ('C2', C2),
        ('C3', C3),
        ('C4', C4),
        ('C5', C5),
        ('C6', C6),
        ('C7', C7),
        ('C8', C8),
        ('C9', C9),
        ('black', blackish),
    ]
)

cyclic_colors = [
    colors['C0'],
    colors['C1'],
    colors['C2'],
    colors['C3'],
    colors['C4'],
    colors['C5'],
    colors['C6'],
    colors['C7'],
    colors['C8'],
    colors['C9'],
]
