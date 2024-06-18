import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import yt_dlp as youtube_dl
import os

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("500x200")
        
        self.url_var = tk.StringVar()
        self.download_path = tk.StringVar(value=os.getcwd())
        self.yt_info = None
        self.streams = []
        
        self.create_widgets()

    def create_widgets(self):
        self.url_label = tk.Label(self.root, text="YouTube URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = tk.Entry(self.root, textvariable=self.url_var, width=50)
        self.url_entry.pack(pady=5)
        
        self.next_button = tk.Button(self.root, text="Next", command=self.validate_url)
        self.next_button.pack(pady=5)
        
    def validate_url(self):
        url = self.url_var.get()
        if not url:
            messagebox.showerror("Error", "URL field cannot be empty")
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'noplaylist': True,
                'extract_flat': 'in_playlist'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                self.yt_info = ydl.extract_info(url, download=False)
            self.show_media_options()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video: {e}")
    
    def show_media_options(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.media_type = tk.StringVar(value="mp4")
        self.resolution_var = tk.StringVar()
        
        self.type_label = tk.Label(self.root, text="Select media type:")
        self.type_label.pack(pady=5)
        
        self.mp4_radio = tk.Radiobutton(self.root, text="Video (mp4)", variable=self.media_type, value="mp4", command=self.update_options)
        self.mp4_radio.pack(pady=5)
        
        self.mp3_radio = tk.Radiobutton(self.root, text="Audio (mp3)", variable=self.media_type, value="mp3", command=self.update_options)
        self.mp3_radio.pack(pady=5)
        
        self.option_label = tk.Label(self.root, text="Select resolution/format:")
        self.option_label.pack(pady=5)
        
        self.option_menu = ttk.Combobox(self.root, textvariable=self.resolution_var)
        self.option_menu.pack(pady=5)
        
        self.folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(pady=5)
        
        self.download_button = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.pack(pady=5)
        
        self.update_options()
    
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
    
    def start_download(self):
        selected_option = self.option_menu.get()
        if not selected_option:
            messagebox.showerror("Error", "Please select a resolution/format")
            return
        
        index = self.option_menu.current()
        if index < 0 or index >= len(self.streams):  # Verifica se o índice está dentro dos limites
            messagebox.showerror("Error", "Invalid option selected")
            return
        
        stream = self.streams[index]
        
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        Thread(target=self.download_file, args=(stream,)).start()

    def update_options(self):
        media_type = self.media_type.get()
        formats = self.yt_info['formats']
        if media_type == "mp4":
            self.streams = [f for f in formats if f['ext'] == media_type]
        else:
            self.streams = [f for f in formats if f['ext'] == 'webm' and 'audio' in f['acodec']]
        
        options = [f"{stream['ext']} - {stream.get('height', 'audio only')}p - {stream.get('tbr', '')}k" for stream in self.streams]
        self.option_menu['values'] = options
        if options:
            self.option_menu.current(0)
        else:
            messagebox.showerror("Error", "No available streams for selected media type")
    
    def download_file(self, stream):
        media_type = self.media_type.get()
        ydl_opts = {
            'format': f"{stream['format_id']}",
            'outtmpl': os.path.join(self.download_path.get(), '%(title)s.%(ext)s'),
            'progress_hooks': [self.on_progress]
        }
        
        if media_type == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.yt_info['webpage_url']])
            messagebox.showinfo("Success", "Download completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}")
        self.reset_ui()
    
    def on_progress(self, d):
        if d['status'] == 'downloading':
            total_size = d.get('total_bytes') or d.get('total_bytes_estimate')
            bytes_downloaded = d.get('downloaded_bytes')
            percent = int(bytes_downloaded / total_size * 100)
            self.progress['value'] = percent
    
    def reset_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()