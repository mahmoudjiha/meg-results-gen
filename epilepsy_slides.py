import re
from epilepsy_config import *
from epilepsy_crop import *

def initialize_slide(template, master_slide):
    return template.slides.add_slide(master_slide)

def image_to_stream(image_object):
    stream = BytesIO()
    image_object.save(stream, "PNG")
    return stream

def insert_image(current_slide, placeholder, img):
    if isinstance(img, Image.Image):
        img = image_to_stream(img)

    current_slide.placeholders[placeholder].insert_picture(img)

def insert_autoshape(current_slide, position, size, shape_class: MSO_SHAPE, fore_color = None, line_color = None):
    shape = current_slide.shapes.add_shape(
        shape_class, Inches(position[0]), Inches(position[1]),
        Inches(size[0]), Inches(size[1])
    )

    shape.shadow.inherit = False
    shape_fill = shape.fill
    shape_line = shape.line

    if fore_color and line_color:
        shape_fill.solid()
        shape_fill.fore_color.rgb = fore_color
        shape_line.color.rgb = line_color
    elif line_color:
        shape_line.color.rgb = line_color
        shape_fill.background()
    else:
        shape_line.fill.background()
        shape_fill.background()

    return shape

def configure_textbox(current_slide, position: tuple, size):
    textbox = insert_autoshape(current_slide, position, size, MSO_SHAPE.RECTANGLE)
    text_frame = textbox.text_frame
    text_frame.margin_bottom = Inches(0.08)
    text_frame.margin_left = 0
    text_frame.vertical_anchor = MSO_ANCHOR.TOP
    text_frame.word_wrap = False
    text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

    return text_frame

def insert_text(current_slide, textbox, text, font_size=None, alignment=None, color=None):
    '''
    if placeholder is given, insert text string into placeholder
    else
    accept tuple with (text str, size int, MSO_THEME_COLOR)
    '''
    if font_size and alignment and color:
        paragraph = textbox.paragraphs[0]
        paragraph.alignment = alignment
        run = paragraph.add_run()
        run.text = text

        font = run.font
        font.name = 'Helvetica'
        font.size = Pt(font_size)
        font.bold = True
        font.italic = None

        if isinstance(color, MSO_THEME_COLOR):
            font.color.theme_color = color
        elif isinstance(color, RGBColor):
            font.color.rgb = color
    else:
        current_slide.placeholders[textbox].text = text

def populate_legend(current_slide, data_types: list, slide_type):
    '''
    '''
    i = 1
    for data_type in data_types:
        text_frame = configure_textbox(current_slide, POSITIONS['LEGEND']['TEXTBOX'][i], SIZES['TEXTBOX'])
        insert_text(current_slide, text_frame, LEGEND_TEXT[data_type.upper()], *TEXT_PARAMETERS['LEGEND'])
        insert_autoshape(current_slide, POSITIONS['LEGEND']['SHAPE'][i], SIZES['SHAPE'], *TYPE_COLORS[data_type])

        if data_type == slide_type:
            insert_autoshape(current_slide, POSITIONS['LEGEND']['INDICATOR'][i], SIZES['INDICATOR'], SHAPES['RECTANGLE'],line_color=COLORS['RED'])

        i += 1

def insert_braces(current_slide):
    for key in POSITIONS['BRACES']:
        insert_autoshape(current_slide, POSITIONS['BRACES'][key], SIZES['BRACES'][key], SHAPES['RIGHT_BRACE'], COLORS['BLACK'], COLORS['WHITE'])

def populate_demographics(current_slide, demographics):
    text_frame = configure_textbox(current_slide, POSITIONS['HEADER']['DEMOGRAPHICS'], SIZES['DEMOGRAPHICS'])
    insert_text(current_slide, text_frame, demographics, *TEXT_PARAMETERS['DEMOGRAPHICS'])

def populate_header(current_slide, slide_type, meg_file):
    match slide_type:
        case 'sam':
            SAMG2_PATTERN =  re.compile(r"R(\d{1,2})V(\d{1,2})")
            peak = SAMG2_PATTERN.search(meg_file)
            title_text = f"SAM(g2) Analysis - Run {peak.group(1)}, V{peak.group(2)}"
            subtitle_text = 'Representative Waveforms Example ' + meg_file[-5]
            text_color = COLORS['GREEN']
        case 'champ':
            title_text = 'Champagne Distributed Source Analysis'
            subtitle_text = ''
            text_color = COLORS['CYAN']
        case 'motor':
            title_text = 'SAM Beamforming Analysis - Motor'
            subtitle_text = ''
            text_color = COLORS['WHITE']
        case 'sef':
            title_text = 'Somatosensory Mapping'
            subtitle_text = ''
            text_color = COLORS['WHITE']

    text_frame = configure_textbox(current_slide, POSITIONS['HEADER']['TITLE'], SIZES['TITLE'])
    insert_text(current_slide, text_frame, title_text, *TEXT_PARAMETERS['TITLE'], text_color)

    text_frame = configure_textbox(current_slide, POSITIONS['HEADER']['SUBTITLE'], SIZES['SUBTITLE'])
    insert_text(current_slide, text_frame, subtitle_text, *TEXT_PARAMETERS['SUBTITLE'], text_color)

def populate_mri_images(current_slide, slide_type, image_path):
    if slide_type in MRI_ONLY:
        for key in PLACEHOLDERS['IMAGES']['NON-EVENT']:
            image = crop_snap(image_path, CROP_COORDINATES['NON-EVENT'][slide_type.upper()][key])
            insert_image(current_slide, PLACEHOLDERS['IMAGES']['NON-EVENT'][key], image)
    else:
        for key in PLACEHOLDERS['IMAGES']['EVENT']['ANATOMICAL']:
            image = crop_snap(image_path, CROP_COORDINATES['EVENT'][key])
            insert_image(current_slide, PLACEHOLDERS['IMAGES']['EVENT']['ANATOMICAL'][key], image)

def populate_waveforms(current_slide, images):
    for key in PLACEHOLDERS['IMAGES']['EVENT']['PHYSIOLOGICAL']:
        match key:
            case 'EEG_WAVEFORMS':
                image_path = images[2]
            case 'MEG_LEFT_WAVEFORMS' | 'MEG_RIGHT_WAVEFORMS' | 'SENSOR_MAP':
                image_path = images[1]

        image = crop_snap(image_path, CROP_COORDINATES['EVENT'][key], key)

        insert_image(current_slide, PLACEHOLDERS['IMAGES']['EVENT']['PHYSIOLOGICAL'][key], image)

def populate_labels(current_slide):
    for key in PLACEHOLDERS['TEXTBOX']:
        insert_text(current_slide, *PLACEHOLDERS['TEXTBOX'][key])

def create_slide(presentation, slide_type, images, header, event_types):
    """
    """
    if slide_type in MRI_ONLY:
        layout = presentation.slide_layouts[0]
    else:
        layout = presentation.slide_layouts[1]

    current_slide = initialize_slide(presentation, layout)

    if slide_type in MRI_ONLY:
        populate_mri_images(current_slide, slide_type, images)
    else:
        populate_mri_images(current_slide, slide_type, images[0])
        populate_waveforms(current_slide, images)
        insert_braces(current_slide)
        populate_labels(current_slide)

    if slide_type in ('sam', 'sef', 'motor', 'champ'):
        populate_header(current_slide, slide_type, images[1])


    populate_legend(current_slide, event_types, slide_type)
    populate_demographics(current_slide, header)

    return current_slide
