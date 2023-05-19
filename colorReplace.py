from PIL import Image, ImageColor
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import io
import cv2


def get_colors_from_image(image, colors_count):
    byte_stream = io.BytesIO(image)
    img = cv2.imdecode(np.frombuffer(byte_stream.read(), np.uint8), cv2.IMREAD_COLOR)

    # Convert image to numpy array
    image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Apply MiniBatchKMeans clustering to extract dominant colors
    kmeans = MiniBatchKMeans(n_clusters=colors_count)
    pixels = image_array.reshape((-1, 3))
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    # Print the dominant colors
    for color in colors:
        print("RGB values:", color)

    return colors


def replace_image_colors(image, target_colors):
    target_colors = np.array(list(map(lambda color: ImageColor.getrgb(color['hex']), target_colors)), dtype=int)
    from_colors = get_colors_from_image(image, len(target_colors))

    # Load image
    byte_stream = io.BytesIO(image)
    img = Image.open(byte_stream)

    # Convert image to NumPy array
    img_array = np.array(img)

    # Get the original colors of all pixels
    pixel_colors = img_array.reshape((-1, 3))

    # Find the indices of the closest original colors
    color_distances = np.sum((from_colors[:, np.newaxis] - pixel_colors) ** 2, axis=2)
    closest_color_indices = np.argmin(color_distances, axis=0)

    # Replace the pixels with the corresponding new colors
    new_colors = target_colors[closest_color_indices]
    img_array = new_colors.reshape(img_array.shape)

    # Convert the NumPy array back to an image
    img = Image.fromarray(img_array.astype(np.uint8))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    return from_colors, img_bytes

