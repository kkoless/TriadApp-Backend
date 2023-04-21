from PIL import Image, ImageColor
import numpy as np
from sklearn.cluster import KMeans
import io


def get_colors_from_image(image, colors_count):
    byte_stream = io.BytesIO(image)
    img = Image.open(byte_stream)

    image_array = np.array(img)

    # Reshape the array to a 2D array of pixels
    pixels = image_array.reshape((-1, 3))

    # Apply KMeans clustering to the pixel values to extract the dominant colors
    kmeans = KMeans(n_clusters=colors_count)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    # Print the dominant colors
    for color in colors:
        print("RGB values:", color)

    return colors


def replace_image_colors(image, target_colors):
    target_colors = np.array(list(map(lambda color: ImageColor.getrgb(color['hex']), target_colors)), dtype=int)
    print(target_colors)
    from_colors = get_colors_from_image(image, len(target_colors))
    # Load image
    byte_stream = io.BytesIO(image)
    img = Image.open(byte_stream)

    for y in range(img.height):
        for x in range(img.width):
            try:
                # Get the original color of the pixel
                pixel_color = tuple(img.getpixel((x, y)))

                # Find the index of the closest original color
                color_distances = np.sum((from_colors - pixel_color) ** 2, axis=1)
                closest_color_index = np.argmin(color_distances)

                # Replace the pixel with the corresponding new color
                new_color = target_colors[closest_color_index]
                img.putpixel((x, y), tuple(new_color))
            except:
                print("Something wrong")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    return img_bytes

