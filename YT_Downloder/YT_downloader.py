import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import webbrowser
from pytube import YouTube
import os  # Import the os module

def choose_download_path():
    download_path = filedialog.askdirectory(initialdir=default_download_path, title="Select Download Directory")
    if download_path:
        path_entry.delete(0, tk.END)  # Clear previous path if any
        path_entry.insert(0, download_path)

def get_video_info():
    url = url_entry.get()
    yt = YouTube(url)
    info_text.delete(1.0, tk.END)  # Clear previous info
    
    # Convert seconds to hours, minutes, and seconds
    length_seconds = yt.length
    length_hours = length_seconds // 3600
    length_minutes = (length_seconds % 3600) // 60
    length_seconds = length_seconds % 60
    
    info_text.insert(tk.END, f"影片標題： {yt.title}\n")
    info_text.insert(tk.END, f"影片長度： {length_hours:02d}:{length_minutes:02d}:{length_seconds:02d}\n")
    info_text.insert(tk.END, f"影片作者： {yt.author}\n")
    info_text.insert(tk.END, f"影片觀看數： {yt.views}\n")
    info_text.insert(tk.END, f"影片上傳日期： {yt.publish_date}\n")
    
    # Insert hyperlink for thumbnail URL
    info_text.insert(tk.END, "影片縮圖網址： ")
    info_text.insert(tk.END, yt.thumbnail_url, hyperlink(yt.thumbnail_url))
    info_text.insert(tk.END, "\n")
    
    available_streams = yt.streams.filter()
    resolutions = sorted(set([stream.resolution for stream in available_streams if stream.resolution]))
    quality_dropdown['values'] = resolutions
    
    # Set default selection to highest resolution
    if resolutions:
        quality_dropdown.set(resolutions[-1])
    
    # Automatically fill the filename entry with default name
    if not filename_entry.get():
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, yt.title)
    else:
        # Update filename if it's already set
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, yt.title)

def clear_info():
    info_text.delete(1.0, tk.END)

def download_video():
    global percent
    percent = 0  # Reset percent to 0
    url = url_entry.get()
    filename = filename_entry.get()
    download_path = path_entry.get()  # Get the download path
    selected_quality = quality_dropdown.get()  # Get selected quality

    # 清空下載完成提示
    status_label.config(text="                    ")
    
    if not filename:
        yt = YouTube(url)
        filename = yt.title
    
    yt = YouTube(url, on_progress_callback=on_progress)
    video_stream = yt.streams.filter(file_extension='mp4', resolution=selected_quality).first()
    
    if video_stream:
        video_stream.download(output_path=download_path, filename=f"{filename}.mp4")
        status_label.config(text="下載完成！")
    else:
        status_label.config(text="未找到影片！")

def download_audio():
    global percent
    percent = 0  # Reset percent to 0
    url = url_entry.get()
    filename = filename_entry.get()
    download_path = path_entry.get()  # Get the download path

    # 清空下載完成提示
    status_label.config(text="                    ")
    
    if not filename:
        yt = YouTube(url)
        filename = yt.title
    
    yt = YouTube(url, on_progress_callback=on_progress)
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    if audio_stream:
        audio_stream.download(output_path=download_path, filename=f"{filename}.mp3")
        status_label.config(text="下載音訊完成！")
    else:
        status_label.config(text="未找到音訊！")

percent = 0
def on_progress(stream, chunk, remains):
    global percent
    total = stream.filesize                     
    percent = (total-remains) / total * 100   
    print(percent)  
    progress_label.config(text=f'下載中… {percent:05.2f}%')
    download_progress["value"] = percent  # Update progress bar value

    # Force main thread to handle events
    root.update_idletasks()

def hyperlink(url):
    def open_url(event):
        webbrowser.open_new(url)
    return open_url

# Get the directory of the Python file
# default_download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download") # 在python同層下再開download file
default_download_path = os.path.dirname(os.path.abspath(__file__))
# Create main window
root = tk.Tk()
root.title("YouTube 影片下載器")

# Create progress bar
download_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", value=0)
download_progress.grid(row=9, column=0, columnspan=4, padx=10, pady=5)

# Create components
url_label = tk.Label(root, text="輸入 YouTube 影片網址：")
url_entry = tk.Entry(root, width=50)
filename_label = tk.Label(root, text="輸入下載後的檔名：")
filename_entry = tk.Entry(root, width=50)
path_label = tk.Label(root, text="輸入下載路徑：")
path_entry = tk.Entry(root, width=50)
path_entry.insert(0, default_download_path)  # Insert default download path
choose_path_button = tk.Button(root, text="選擇路徑", command=choose_download_path)
get_info_button = tk.Button(root, text="取得影片資訊", command=get_video_info)
clear_info_button = tk.Button(root, text="清空資訊", command=clear_info)

quality_label = tk.Label(root, text="選擇畫質：")
quality_dropdown = ttk.Combobox(root, state='readonly')
download_video_button = tk.Button(root, text="下載影片", command=download_video)
download_audio_button = tk.Button(root, text="下載音訊", command=download_audio)
progress_label = tk.Label(root, text="")
status_label = tk.Label(root, text="")
info_label = tk.Label(root, text="影片資訊：")
info_text = tk.Text(root, width=70, height=10, wrap="word", font=('Helvetica', 10), spacing1=2, spacing2=2, spacing3=2)

# Position components
url_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5)
get_info_button.grid(row=0, column=3, padx=10, pady=5)
filename_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
filename_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5)
path_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
path_entry.grid(row=2, column=1, padx=5, pady=5)
choose_path_button.grid(row=2, column=2, padx=5, pady=5)

quality_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
quality_dropdown.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

download_video_button.grid(row=4, column=1, padx=10, pady=5)
download_audio_button.grid(row=4, column=2, padx=10, pady=5)

info_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
info_text.grid(row=5, column=1, columnspan=3, padx=10, pady=5, sticky="w")
clear_info_button.grid(row=6, column=1, columnspan=2, padx=10, pady=5)

progress_label.grid(row=7, column=0, columnspan=4, padx=10, pady=5)
status_label.grid(row=8, column=0, columnspan=4, padx=10, pady=5)

# Configure tag for hyperlink
info_text.tag_config("hyperlink", foreground="blue", underline=True)
info_text.tag_bind("hyperlink", "<Button-1>", hyperlink)

# Run the main loop
root.mainloop()
