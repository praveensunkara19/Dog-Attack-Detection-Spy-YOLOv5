import streamlit as st
from PIL import Image
import torch
import cv2
import tempfile
import numpy as np
import os
from pathlib import Path

# Streamlit page config (must be first)
st.set_page_config(page_title="Dog Attack Detection", layout="centered")

# ------------------- UI: Title and Input Type FIRST -------------------
st.title("🐶 Dog Attack Detection using YOLOv5")
st.markdown("Upload an **image or video**, or try a **test file** to detect aggressive dogs attacks in action.")

# Input type radio
input_type = st.radio("Choose Input Type:", ["Image", "Video"])

# ------------------- Model Loading -------------------
@st.cache_resource
def load_model():
    return torch.hub.load(
        'ultralytics/yolov5',
        'custom',
        path='yolov5_best.pt',
        force_reload=False
    )

model = load_model()

# -------------------- IMAGE INFERENCE --------------------
if input_type == "Image":
    use_test_img = st.button("🖼️ Use Test Image")
    uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if use_test_img:
        image_path = Path("test/testimg.jpg")
    elif uploaded_image is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tfile.write(uploaded_image.read())
        image_path = Path(tfile.name)
    else:
        image_path = None

    if image_path and image_path.exists():
        image = Image.open(image_path)
        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption="Original Image", use_container_width=True)

        results = model(image)
        results.render()

        with col2:
            st.image(results.ims[0], caption="Predicted Output", use_container_width=True)

        st.success("✅ Image prediction complete!")

# -------------------- VIDEO INFERENCE --------------------
elif input_type == "Video":
    use_test_video = st.button("▶️ Use Test Video")
    uploaded_video = st.file_uploader("Upload a Video", type=["mp4", "avi", "mov", "mpeg"])

    if use_test_video:
        video_path = Path("test/test_video.mp4")
    elif uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_video.read())
        video_path = Path(tfile.name)
    else:
        video_path = None

    if video_path and video_path.exists():
        stframe = st.empty()
        st.info("⏳ Running detection on video frame-by-frame...")

        cap = cv2.VideoCapture(str(video_path))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame_rgb)
            results.render()
            output_frame = results.ims[0]

            stframe.image(output_frame, channels="RGB", use_container_width=True)

        cap.release()
        st.success("✅ Video prediction complete!")

    elif video_path:
        st.error("❌ Could not load video.")
