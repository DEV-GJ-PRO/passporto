import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance
import cv2
from rembg import remove
import io
import os
import streamlit.components.v1 as components

# # Function to remove background
# def remove_background(image):
#     image_np = np.array(image)
#     output = remove(image_np)
#     return Image.fromarray(output)

def remove_background(image, remove_bg=True):
    if not remove_bg:
        return image  # Return original image if keeping background
    image_np = np.array(image)
    output = remove(image_np)  # Remove background
    output_img = Image.fromarray(output)
    
    # Create a grey background
    grey_bg = Image.new('RGB', output_img.size, (255, 255, 255))  # RGB(128, 128, 128) for grey
    if output_img.mode == 'RGBA':
        # Paste the foreground using the alpha channel as a mask
        grey_bg.paste(output_img, (0, 0), output_img.split()[3])  # Use alpha channel as mask
    else:
        grey_bg.paste(output_img, (0, 0))
    
    return grey_bg.convert('RGB')  # Ensure RGB mode


# Function to detect and center face
def detect_and_center_face(image):
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        x, y, w, h = faces[0]  # Use the first detected face
        face_center_x, face_center_y = x + w // 2, y + h // 2
        img_height, img_width = image_np.shape[:2]
        
        # Calculate crop region (1.5x face size to include some context)
        crop_size = int(max(w, h) * 1.5)
        crop_x1 = max(face_center_x - crop_size // 2, 0)
        crop_y1 = max(face_center_y - crop_size // 2, 0)
        crop_x2 = min(face_center_x + crop_size // 2, img_width)
        crop_y2 = min(face_center_y + crop_size // 2, img_height)
        
        cropped = image_np[crop_y1:crop_y2, crop_x1:crop_x2]
        return Image.fromarray(cropped)
    return image  # Return original if no face detected

# Function to enhance image
def enhance_image(image):
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)  # Slight brightness boost
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)  # Slight contrast boost
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)  # Moderate sharpness boost
    return image

# Function to resize image
def resize_image(image, target_width, target_height):
    image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
    return image

# # Function to compress image to target file size
# def compress_to_size(image, target_size_kb):
#     target_size = target_size_kb * 1024  # Convert KB to bytes
#     quality = 95
#     while quality > 10:
#         buffer = io.BytesIO()
#         image.save(buffer, format="JPEG", quality=quality)
#         size = buffer.tell()
#         if size <= target_size:
#             return buffer.getvalue()
#         quality -= 5
#     # If still too large, reduce dimensions slightly
#     image = image.resize((int(image.width * 0.9), int(image.height * 0.9)), Image.Resampling.LANCZOS)
#     buffer = io.BytesIO()
#     image.save(buffer, format="JPEG", quality=50)
#     return buffer.getvalue()

# Function to compress image to target file size
def compress_to_size(image, target_size_kb):
    target_size = target_size_kb * 1024  # Convert KB to bytes
    quality = 95
    # Convert image to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    while quality > 10:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()
        if size <= target_size:
            return buffer.getvalue()
        quality -= 5
    # If still too large, reduce dimensions slightly
    image = image.resize((int(image.width * 0.9), int(image.height * 0.9)), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=50)
    return buffer.getvalue()

# Streamlit app
st.title("Photo Background Remover and Editor")
st.write("Upload a photo, remove its background, resize it, and enhance it for download.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)
    

        # Background option
    bg_option = st.radio("Background Option", ("Keep Background", "Remove Background"))
    remove_bg = bg_option == "Remove Background"


    # User inputs for target size
    target_width = st.number_input("Target Width (pixels)", min_value=100, max_value=4000, value=800)
    target_height = st.number_input("Target Height (pixels)", min_value=100, max_value=4000, value=600)
    target_size_kb = st.number_input("Target File Size (KB)", min_value=10, max_value=5000, value=100)
    
    if st.button("Process Image"):
        with st.spinner("Processing..."):
            # Process background
            image = remove_background(image, remove_bg)
            
            # Detect and center face
            image = detect_and_center_face(image)
            
            # Enhance image
            image = enhance_image(image)
            
            # Resize image
            image = resize_image(image, target_width, target_height)
            
            # Compress to target file size
            processed_image_bytes = compress_to_size(image, target_size_kb)
            
            # Display processed image
            st.image(processed_image_bytes, caption="Processed Image", use_column_width=True)
            
            # Provide download link
            st.download_button(
                label="Download Processed Image",
                data=processed_image_bytes,
                file_name="processed_image.jpg",
                mime="image/jpeg"
            )

st.write("Note: Face detection may not work perfectly for all images. Ensure the image has a clear face for best results.")

qr_path = "qr.jpeg"

image = Image.open(qr_path)
st.image(image, caption="Scan to Buy Me a Coffee", width=200)

# PropellerAds banner ad
components.html("""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5277332122718000"
     crossorigin="anonymous"></script>
""", height=250)
