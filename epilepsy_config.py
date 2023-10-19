from io import BytesIO
from pptx import Presentation
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT as PP_ALIGN
from pptx.enum.text import MSO_VERTICAL_ANCHOR as MSO_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR_INDEX as MSO_THEME_COLOR
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from PIL import Image, ImageDraw

PLACEHOLDERS = {
    'IMAGES': {
        'EVENT': {
            'ANATOMICAL': {
                'AXIAL_VIEW': 15,
                'CORONAL_VIEW': 13,
                'SAGITTAL_VIEW': 14
            },

            'PHYSIOLOGICAL': {
                'EEG_WAVEFORMS': 16,
                'MEG_WAVEFORMS': 17,
                'SENSOR_MAP': 31
            }
        },

        'NON-EVENT': {
            'SLICE': 11,
            'SLICE_NUMBER': 13
        }
    },

    'TEXTBOX': {
        'AXIAL_LEFT': (29, 'L'),
        'AXIAL_RIGHT': (28, 'R'),
        'CORONAL_LEFT': (26, 'L'),
        'CORONAL_RIGHT': (25, 'R'),
        'EEG': (18, 'EEG'),
        'EEG_BANDPASS': (19, '(1-70Hz)'),
        'MAP_LEFT': (37, 'L'),
        'MAP_RIGHT': (38, 'R'),
        'MEG_BANDPASS_LEFT': (23, '(1-70Hz)'),
        'MEG_BANDPASS_RIGHT': (24, '(1-70Hz)'),
        'MEG_CHANNELS_CENTRAL': (32, "Central Channels"),
        'MEG_CHANNELS_FRONTAL': (33, 'Frontal Channels'),
        'MEG_CHANNELS_OCCIPITAL': (34, "Occipital Channels"),
        'MEG_CHANNELS_PARIETAL': (35, "Parietal Channels"),
        'MEG_CHANNELS_TEMPORAL': (36, "Temporal Channels (+EKG)"),
        'MEG_LEFT': (21, 'MEG Left'),
        'MEG_RIGHT': (22, 'MEG Right'),
        'SAGITTAL_ANTERIOR': (20, 'A'),
        'SAGITTAL_POSTERIOR': (27, 'P')
    }
}

SHAPES = {
    'RIGHT_BRACE': MSO_SHAPE.RIGHT_BRACE,
    'TRIANGLE': MSO_SHAPE.ISOSCELES_TRIANGLE,
    'RECTANGLE': MSO_SHAPE.RECTANGLE,
    'CIRCLE': MSO_SHAPE.OVAL
}

COLORS = {
    'BLACK': RGBColor(0,0,0),
    'CYAN': RGBColor(0,255,255),
    'GREEN': RGBColor(0,246,0),
    'MAGENTA': RGBColor(255,0,255),
    'RED': RGBColor(255,31,65),
    'WHITE': RGBColor(255,255,255),
    'YELLOW': RGBColor(255,255,0)
}

POSITIONS = {
    'LEGEND': {
        'TEXTBOX': {
            1: (0.29, 0.03),
            2: (0.29, 0.29),
            3: (0.29, 0.55),
            4: (0.29, 0.81),
            5: (0.29, 1.07),
            6: (0.29, 1.33),
            7: (1.63, 0.03),
            8: (1.63, 0.29),
            9: (1.63, 0.55),
            10: (1.63, 0.81),
            11: (1.63, 1.07),
            12: (1.63, 1.33)
        },

        'SHAPE': {
            1: (0.06, 0.06),
            2: (0.06, 0.32),
            3: (0.06, 0.58),
            4: (0.06, 0.84),
            5: (0.06, 1.1),
            6: (0.06, 1.36),
            7: (1.4, 0.06),
            8: (1.4, 0.32),
            9: (1.4, 0.58),
            10: (1.4, 0.84),
            11: (1.4, 1.1),
            12: (1.4, 1.36)
        },

        'INDICATOR': {
            1: (0.02, 0.02),
            2: (0.02, 0.28),
            3: (0.02, 0.54),
            4: (0.02, 0.8),
            5: (0.02, 1.06),
            6: (0.02, 1.32),
            7: (1.36, 0.02),
            8: (1.36, 0.28),
            9: (1.36, 0.54),
            10: (1.36, 0.8),
            11: (1.36, 1.06),
            12: (1.36, 1.32)
        }
    },

    'BRACES': {
        'CENTRAL': (8.51, 1.58),
        'FRONTAL': (8.51, 2.63),
        'OCCIPITAL': (8.51, 4.06),
        'PARIETAL': (8.51, 4.87),
        'TEMPORAL': (8.51, 5.78),
    },

    'HEADER': {
        'DEMOGRAPHICS': (5, 0),
        'SUBTITLE': (3.11, 0.68),
        'TITLE': (3.8, 0.37)
    }
}

PROMPTS = {
    'NAME_REQUEST': "What is the patient's name?",
    'FIRST_NAME': 'First: ',
    'LAST_NAME': 'Last: ',
    'MEG': 'MEG Date (M/D/YYYY): ',
    'MRI': 'MRI Date (M/D/YYYY): ',
}

SIZES = {
    'BRACES': {
        'CENTRAL': (0.47, 1.05),
        'FRONTAL': (0.47, 1.43),
        'OCCIPITAL': (0.47, 0.81),
        'PARIETAL': (0.47, 0.91),
        'TEMPORAL': (0.47, 1.51),
    },

    'DEMOGRAPHICS': (4.98, 0.3),
    'INDICATOR': (1.34, 0.23),
    'SHAPE': (0.17, 0.16),
    'SUBTITLE': (3.97, 0.3),
    'TEXTBOX': (1.39, 0.24),
    'TITLE': (2.57, 0.37)

}

TEXT_PARAMETERS = {
    'LEGEND': (10, PP_ALIGN.LEFT, MSO_THEME_COLOR.TEXT_1),
    'DEMOGRAPHICS': (10, PP_ALIGN.RIGHT, MSO_THEME_COLOR.TEXT_1),
    'TITLE': (16, PP_ALIGN.CENTER),
    'SUBTITLE': (12, PP_ALIGN.CENTER)
}

TYPE_COLORS = {
    'spike': (SHAPES['TRIANGLE'], COLORS['YELLOW'], COLORS['WHITE']),
    'poly': (SHAPES['TRIANGLE'], COLORS['CYAN'], COLORS['WHITE']),
    'champ': (SHAPES['CIRCLE'], COLORS['CYAN'], COLORS['WHITE']),
    'ica': (SHAPES['CIRCLE'], COLORS['MAGENTA'], COLORS['WHITE']),
    'sam': (SHAPES['CIRCLE'], COLORS['GREEN'], COLORS['WHITE']),
    'average': (SHAPES['TRIANGLE'], COLORS['RED'], COLORS['WHITE']),
    'motor': (SHAPES['CIRCLE'], COLORS['YELLOW'], COLORS['WHITE']),
    'bird': (SHAPES['TRIANGLE'], COLORS['WHITE'], COLORS['WHITE']),
    'pfa': (SHAPES['TRIANGLE'], COLORS['WHITE'], COLORS['WHITE']),
    'slow': (SHAPES['CIRCLE'], COLORS['RED'], COLORS['WHITE']),
    'sef': (SHAPES['RECTANGLE'], COLORS['GREEN'], COLORS['WHITE']),
    'seizure': (SHAPES['TRIANGLE'], COLORS['MAGENTA'], COLORS['WHITE'])
}

TYPE_LIST = ('seizure', 'spike', 'poly', 'average',
             'bird', 'slow', 'champ', 'pfa', 'sam',
             'cor', 'sef', 'motor'
)

LEGEND_TEXT = {
    'AVERAGE': 'spike average',
    'BIRD': 'BIRD',
    'PFA': 'PFA',
    'CHAMP': 'champagne',
    'ICA': 'ICA',
    'MOTOR': 'motor',
    'POLY': 'polyspike',
    'SAM': 'SAM(g2)',
    'SEF': 'somatosensory',
    'SEIZURE': 'seizure onset',
    'SLOW': 'slow wave',
    'SPIKE': 'spike',
}

MRI_ONLY = ('cor', 'sef', 'motor')

CROP_COORDINATES = {
    # left, top, right, bottom
    'EVENT': {
        'AXIAL_VIEW': (17, 392, 249, 648),
        'CORONAL_VIEW': (17, 63, 249, 319),
        'SAGITTAL_VIEW': (280, 63, 512, 319),
        'EEG_WAVEFORMS': (9, 137, 294, 884),
        'MEG_WAVEFORMS': (9, 137, 589, 884),
        'SENSOR_MAP': (600, 99, 750, 249)
    },

    'NON-EVENT': {
        'COR': {
            'SLICE': (5, 63, 261, 319),
            'SLICE_NUMBER': (5, 319, 69, 339)
        },

        'MOTOR': {
            'SLICE': (5, 392, 261, 648),
            'SLICE_NUMBER': (5, 648, 69, 668),
        },

        'SEF': {
            'SLICE': (5, 392, 261, 648),
            'SLICE_NUMBER': (5, 648, 69, 668),
        }
    }
}
