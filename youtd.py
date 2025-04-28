import streamlit as st
import yt_dlp
import os
import subprocess

def get_ffmpeg_path():
    """Retorna o caminho completo do ffmpeg.exe, baseado na pasta do próprio script."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "ffmpeg.exe")

def get_estimated_size(info_dict, option):
    total = 0
    if option == "Vídeo (MP4)":
        best_video = best_audio = None
        for fmt in info_dict.get("formats", []):
            if fmt.get("vcodec") != "none":
                size = fmt.get("filesize_approx") or fmt.get("filesize") or 0
                if size and (best_video is None or size > best_video):
                    best_video = size
            if fmt.get("acodec") != "none":
                size = fmt.get("filesize_approx") or fmt.get("filesize") or 0
                if size and (best_audio is None or size > best_audio):
                    best_audio = size
        total = (best_video or 0) + (best_audio or 0)
    else:  # Áudio (MP3)
        for fmt in info_dict.get("formats", []):
            if fmt.get("acodec") != "none":
                total = fmt.get("filesize_approx") or fmt.get("filesize") or 0
                break
    return total

def download_video_or_audio(url, option, progress_bar, status_text):
    try:
        mp4_path = "./downloads/videos"
        mp3_path = "./downloads/audios"
        webps_path = "./downloads/webps"
        for path in (webps_path, mp4_path, mp3_path):
            os.makedirs(path, exist_ok=True)

        ffmpeg_path = get_ffmpeg_path()

        ydl_opts_info = {
            "outtmpl": os.path.join(webps_path, "%(title)s.%(ext)s"),
            "ffmpeg_location": ffmpeg_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get("title", "output").replace("/", "-")

        total_size = get_estimated_size(info_dict, option)
        if total_size > 50 * 1024 * 1024:
            st.warning("⚠ O arquivo é grande (>50 MB). O download pode demorar.")

        def progress_hook(d):
            if d.get("status") == "downloading":
                tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                dl = d.get("downloaded_bytes", 0)
                pct = int(dl / tot * 100)
                progress_bar.progress(pct)
                status_text.text(f"Baixando... {pct}%")
            elif d.get("status") == "finished":
                progress_bar.progress(100)
                status_text.text("Download concluído!")

        if option == "Vídeo (MP4)":
            video_path = os.path.join(webps_path, f"{title}_video.webm")
            audio_path = os.path.join(webps_path, f"{title}_audio.webm")
            mp4_output = os.path.join(mp4_path, f"{title}.mp4")

            video_opts = {
                "format": "bestvideo",
                "outtmpl": video_path,
                "progress_hooks": [progress_hook],
                "ffmpeg_location": ffmpeg_path,
            }
            audio_opts = {
                "format": "bestaudio",
                "outtmpl": audio_path,
                "progress_hooks": [progress_hook],
                "ffmpeg_location": ffmpeg_path,
            }

            status_text.text("Baixando vídeo...")
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])

            progress_bar.progress(0)
            status_text.text("Baixando áudio...")
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])

            status_text.text("Unindo vídeo e áudio...")
            cmd = [
                ffmpeg_path, "-i", video_path, "-i", audio_path,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-strict", "experimental", mp4_output, "-y"
            ]
            subprocess.run(cmd, check=True)

            status_text.text("📁 Arquivo pronto!")
            return mp4_output

        # Áudio (MP3)
        audio_path = os.path.join(webps_path, f"{title}_audio.webm")
        mp3_output = os.path.join(mp3_path, f"{title}.mp3")
        ydl_mp3_opts = {
            "format": "bestaudio",
            "outtmpl": audio_path,
            "progress_hooks": [progress_hook],
            "ffmpeg_location": ffmpeg_path,
        }
        status_text.text("Baixando áudio...")
        with yt_dlp.YoutubeDL(ydl_mp3_opts) as ydl:
            ydl.download([url])

        status_text.text("Convertendo para MP3...")
        cmd2 = [
            ffmpeg_path, "-i", audio_path, "-vn", "-acodec", "libmp3lame",
            "-b:a", "192k", mp3_output, "-y"
        ]
        subprocess.run(cmd2, check=True)

        status_text.text("📁 Arquivo pronto!")
        return mp3_output

    except Exception as e:
        status_text.text("")
        st.error(f"Ocorreu um erro: {e}")
        return None

# Interface Streamlit
st.title("YouTube Downloader")
url = st.text_input("Digite a URL do vídeo do YouTube")
if url:
    video_id = url.split("v=")[-1].split("&")[0]
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <iframe width="100%" height="400"
                src="{embed_url}"
                frameborder="0"
                allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )
option = st.radio("Escolha o formato de download", ("Vídeo (MP4)", "Áudio (MP3)"))
progress_bar = st.progress(0)
status_text = st.empty()

if st.button("Baixar"):
    if not ("youtube.com" in url or "youtu.be" in url):
        st.error("Por favor, insira uma URL válida do YouTube.")
    elif not os.path.isfile(get_ffmpeg_path()):
        st.error("⚠ O ffmpeg.exe não foi encontrado na pasta do projeto.")
    else:
        out = download_video_or_audio(url, option, progress_bar, status_text)
        if out and os.path.exists(out):
            with open(out, "rb") as f:
                st.download_button("Baixar arquivo", f, file_name=os.path.basename(out))
        else:
            st.error("Ocorreu um erro ao baixar o arquivo.")
