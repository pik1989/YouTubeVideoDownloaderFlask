from flask import Flask, request, send_file,render_template, redirect
from pytube import YouTube
import logging
import sys
from io import BytesIO
from tempfile import TemporaryDirectory

with TemporaryDirectory() as tmp:
    print(tmp)
 
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
app = Flask(__name__)
 
@app.route("/", methods=["GET", "POST"])
def youtube_downloader():
    if request.method == "GET":
        return render_template("index.html")
    else:
        
        if not request.form["URL"]:
            return redirect("/")
        else:
            URL = request.form["URL"]
            try:
                video = YouTube(URL)
                video.check_availability()
            except:
                return render_template("fail.html")
            if request.form.get("submit_audio"):
                return render_template("download_audio.html",  URL = URL)
            else:
                resolutions = {}
                for stream in video.streams.filter(progressive=True):
                    resolutions[stream.resolution] = stream.resolution
                
                return render_template("download.html", resolutions = resolutions, URL = URL)

 
@app.route("/download_video", methods=["POST"])
def download_video():
    if request.method == "POST":
        if not request.form["URL"] or not request.form["resolution"]:
            return redirect("/")
        try:
            youtube_url = request.form["URL"]
            resolution = request.form["resolution"]

            with TemporaryDirectory() as tmp_dir:
                print(tmp_dir)
                download_path = YouTube(youtube_url).streams.filter(res=resolution, progressive=True).first().download(tmp_dir)
                vid_name = download_path.split("\\")[-1]
                file_bytes = b""
                with open(download_path, "rb") as f:
                    file_bytes = f.read()

                return send_file(BytesIO(file_bytes), attachment_filename=vid_name, as_attachment=True)
            
        except:
            logging.exception("Failed download")
            return render_template("fail.html")
    
@app.route("/download_audio", methods=["POST"])
def download_audio():
    if request.method == "POST":
        if not request.form["URL"]:
            return redirect("/")
        try:
            youtube_url = request.form["URL"]
           
            with TemporaryDirectory() as tmp_dir:
                print(tmp_dir)
                stream = YouTube(youtube_url).streams.filter(only_audio=True).all()
                download_path=stream[0].download(tmp_dir)
                audio_name = download_path.split("\\")[-1]
                file_bytes = b""
                with open(download_path, "rb") as f:
                    file_bytes = f.read()

                return send_file(BytesIO(file_bytes), attachment_filename=audio_name, as_attachment=True)
            
        except:
            logging.exception("Failed download")
            return render_template("fail.html")
        
if __name__ == "__main__":
    app.run(debug=False)