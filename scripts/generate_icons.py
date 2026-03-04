from PIL import Image
import os

split_path = r"C:\Users\User\.gemini\antigravity\brain\8c39f48e-c5b9-4b97-8188-49bdca725565\funnel_closed_split_1772648413441.png"
img = Image.open(split_path).convert("RGBA")

width, height = img.size
left_half = img.crop((0, 0, width // 2, height))
right_half = img.crop((width // 2, 0, width, height))

def make_square(img_half):
    w, h = img_half.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    right = (w + size) // 2
    bottom = (h + size) // 2
    return img_half.crop((left, top, right, bottom))

square_dark = make_square(left_half)
square_light = make_square(right_half)

def make_transparent(img, bg_color, threshold=25):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    
    r_bg, g_bg, b_bg = bg_color
    
    for item in datas:
        # Check if color is close to background color
        r, g, b, a = item
        if abs(r - r_bg) < threshold and abs(g - g_bg) < threshold and abs(b - b_bg) < threshold:
            # calculate how close it is to blend the alpha slightly for anti-aliasing
            dist = max(abs(r - r_bg), abs(g - g_bg), abs(b - b_bg))
            alpha = int((dist / threshold) * 255)
            newData.append((r, g, b, alpha))
        else:
            newData.append(item)
            
    img.putdata(newData)
    return img

# Dark mode has black background (0,0,0)
transparent_dark = make_transparent(square_dark, (0, 0, 0), threshold=30)
# Light mode has white background (255,255,255)
transparent_light = make_transparent(square_light, (255, 255, 255), threshold=30)

# Also let's crop it tightly to the content so it's not a tiny funnel in a huge transparent box
def auto_crop(img):
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img
    
transparent_dark = auto_crop(transparent_dark)
transparent_light = auto_crop(transparent_light)

# ensure it's square again after tightly cropping
def make_square_pad(img):
    w, h = img.size
    size = max(w, h)
    new_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    new_img.paste(img, ((size - w) // 2, (size - h) // 2))
    return new_img
    
transparent_dark = make_square_pad(transparent_dark)
transparent_light = make_square_pad(transparent_light)


icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
public_dir = r"c:\Users\User\Documents\MyProjects\PlaylistSorter\frontend\public"

transparent_dark.save(os.path.join(public_dir, "logo-dark.png"))
transparent_dark.save(os.path.join(public_dir, "favicon-dark.ico"), format="ICO", sizes=icon_sizes)

transparent_light.save(os.path.join(public_dir, "logo-light.png"))
transparent_light.save(os.path.join(public_dir, "favicon-light.ico"), format="ICO", sizes=icon_sizes)

print("Generated transparent icons successfully!")
