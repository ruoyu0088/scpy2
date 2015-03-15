
def rotate(src, angle):
    import cv2
    h, w = src.shape[:2]
    m = cv2.getRotationMatrix2D((h*0.5, w*0.5), angle, 1.0)
    return cv2.warpAffine(src, m, (w, h), flags=cv2.INTER_CUBIC)


def concat_images(images, margin=10):
    import numpy as np
    width = sum(img.shape[1] for img in images) + (len(images)-1)*margin
    height = max(img.shape[0] for img in images)
    image = np.empty((height, width, 3), dtype=np.uint8)
    image.fill(255)
    x = 0
    
    for img in images:
        if img.dtype in (np.float32, np.float64):
            img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        h, w = img.shape[:2]
        if img.ndim == 2:
            img = img[:, :, None]
        elif img.ndim == 3:
            img = img[:, :, :3]
        image[:h, x:x+w, :] = img[:, :, :]
        x += w + margin

    return image


def display_image(image):
    import io
    from matplotlib.image import imsave
    from IPython import display
    buf = io.BytesIO()
    imsave(buf, image)
    return display.display_png(display.Image(buf.getvalue()))


def concat_keypoints(image, key_points, nrow, ncol, scale=1):
    import numpy as np
    import cv2

    def crop_keypoint(image, key_point):
        size = key_point.size
        x, y = key_point.pt
        d = int(round(size * 2**0.5 / 2))
        img2 = image[y-d:y+d, x-d:x+d].copy()
        img3 = rotate(img2, key_point.angle)
        d = int(round(size / 2))

        w, h = img3.shape
        cx, cy = w//2, h//2
        return img3[cy-d:cy+d, cx-d:cy+d].copy()



    key_points = key_points[:]
    key_points.sort(key=lambda kp:kp.size, reverse=True)
    kp_images = [crop_keypoint(image, kp) for kp in key_points[:nrow * ncol]]

    if scale != 1:
        for i, kp_image in enumerate(kp_images):
            w = int(kp_image.shape[0] * scale)
            kp_images[i] = cv2.resize(kp_image, (w, w))

    width = (max(kp_image.shape[0] for kp_image in kp_images) + 4)
    res_image = np.full((width * nrow, width * ncol, 3), 255, np.uint8)

    for i, kp_image in enumerate(kp_images):
        r, c = i // ncol, i % ncol
        cx, cy = c * width + width // 2, r * width + width // 2
        w = kp_image.shape[0]
        res_image[cy-w//2:cy-w//2+w, cx-w//2:cx-w//2+w, :] = kp_image[:, :, None]

    return  res_image