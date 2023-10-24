from PIL import Image, ImageDraw

TRANSPARENT = (0, 0, 0, 0)

def circular_mask(x,y,diameter,size):
    '''
    This function generates a mask image.
    x,y indicate the center of the circle
    size = size of the image which will be cropped
    '''
    x1 = x - diameter/2
    y1 = y - diameter/2 + 3 # correction for DataEditor MAP not being a perfect circle
    x2 = x + diameter/2
    y2 = y + diameter/2 - 5 # correction for DataEditor MAP not being a perfect circle

    image = Image.new('L', size, color="black")

    draw = ImageDraw.Draw(image)

    draw.ellipse((x1, y1, x2, y2), fill = 'white', outline ='white')

    return image

def crop_snap(snap, coordinates: tuple, image_type=None):
    '''
    Expects tuple of (left, top, right, bottom) pixel values in original img
    '''

    cropped_image = Image.open(snap).crop(coordinates)

    if image_type == 'SENSOR_MAP':
        cropped_image = cropped_image.convert('RGBA')
        cropped_pixels = cropped_image.load()

        masked_image = circular_mask(75, 75, 150, cropped_image.size)
        masked_pixels = masked_image.load()
        width, height = masked_image.size

        for y in range(height):
            for x in range(width):
                pixel_value = masked_pixels[x, y]

                if pixel_value == 0:
                    cropped_pixels[x, y] = TRANSPARENT

    return cropped_image
