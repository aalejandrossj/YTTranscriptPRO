import streamlit as st
import yt_dlp
import os
import whisper
import tempfile

# Path to your cookies file, assuming it is in the same folder as the script
COOKIES_FILE = 'cookies.txt'

st.title("Transcripción de Audio de YouTube")


youtube_url = st.text_input("Ingrese la URL de YouTube")
ffmpeg_path = 'ffmpeg/bin/ffmpeg.exe'
@st.cache_resource

def ensure_audio_file_absent(audio_filename):
    if os.path.exists(audio_filename):
        os.remove(audio_filename)

def download_audio(youtube_url, ffmpeg_path):
    # Create a temporary file for audio output
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        audio_filename = tmp_file.name

    ensure_audio_file_absent(audio_filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.splitext(audio_filename)[0],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,
        'cookiefile': COOKIES_FILE  # Add cookies for authenticated requests
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            final_output_path = audio_filename
            if os.path.exists(final_output_path):
                st.success(f"Audio descargado exitosamente en {final_output_path}")
            else:
                st.error(f"Error al guardar el audio en {final_output_path}")
            return final_output_path
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None

def mark_times(result):
    marked_transcription = ""
    for segment in result["segments"]:
        start_time = segment["start"]
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        timestamp = f"{minutes:02}:{seconds:02}"
        marked_transcription += f" {timestamp}: {segment['text']}\n"
    return marked_transcription

def run_transcription(audio_filename, model):
    try:
        result = model.transcribe(audio_filename)
        return mark_times(result)
    except Exception as e:
        return f"Ocurrió un error durante la transcripción: {e}"


def load_whisper_model():
    return whisper.load_model("base")



if st.button("Transcribir"):
    if youtube_url:
        with st.spinner("Descargando audio..."):
            audio_filename = download_audio(youtube_url, ffmpeg_path)

        if audio_filename:
            with st.spinner("Transcribiendo..."):
                model = load_whisper_model()
                transcription = run_transcription(audio_filename, model)
            
            st.subheader("Transcripción:")
            st.text_area("", value=transcription, height=300)

            # Limpieza de archivos temporales
            ensure_audio_file_absent(audio_filename)
        else:
            st.error("Error al descargar el audio.")
    else:
        st.warning("Por favor, ingrese una URL de YouTube")
