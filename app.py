import streamlit as st
import GPUtil
import pyperclip
import joblib
import cohere
from sklearn.preprocessing import StandardScaler

st.title("AI Software Project Dashboard")
st.sidebar.header("Controls")

# Try to import optional modules safely
try:
    import cv2
    import sounddevice as sd
    webcam_available = True
except Exception:
    webcam_available = False

choice_list = ["GPU Info", "Clipboard"]
if webcam_available:
    choice_list.extend(["Webcam", "Audio"])

choice = st.sidebar.selectbox("Choose an operation", choice_list)

if choice == "GPU Info":
    gpus = GPUtil.getGPUs()
    if not gpus:
        st.warning("No GPU detected.")
    for gpu in gpus:
        st.write(f"Name: {gpu.name}")
        st.write(f"Load: {gpu.load*100:.2f}%")
        st.write(f"Memory Used: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

elif choice == "Webcam" and webcam_available:
    st.write("Opening webcam...")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        st.image(frame, channels="BGR")
    cam.release()

elif choice == "Audio" and webcam_available:
    st.write("Recording 3 seconds of audio...")
    fs = 44100
    duration = 3
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    st.write("Audio captured successfully!")

elif choice == "Clipboard":
    content = pyperclip.paste()
    st.write("Clipboard content:")
    st.write(content)
