# 不要直接執行這個檔案
# 很可怕!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 這是用來打包的code





import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
from pytube import YouTube, Playlist
import os  # Import the os module
import sys
# from moviepy.editor import VideoFileClip
# from moviepy.editor import AudioFileClip
import moviepy.editor as mp
# import moviepy
import os
import subprocess
import win32gui
import win32con

def hide_console():
    # 获取当前窗口句柄
    window = win32gui.GetForegroundWindow()
    # 隐藏窗口
    win32gui.ShowWindow(window, win32con.SW_HIDE)

if __name__ == "__main__":
    hide_console()

def choose_download_path():
    download_path = filedialog.askdirectory(initialdir=default_download_path, title="Select Download Directory")
    if download_path:
        path_entry.delete(0, tk.END)  # Clear previous path if any
        path_entry.insert(0, download_path)
def get_common_qualities(playlist):
    common_qualities = set()
    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        available_streams = yt.streams.filter(file_extension='mp4')
        for stream in available_streams:
            if stream.resolution:
                common_qualities.add(stream.resolution)
    return common_qualities

def get_video_info():
    url = url_entry.get()
    if "playlist" in url.lower():
        playlist = Playlist(url)
        common_qualities = get_common_qualities(playlist)
        common_qualities= sorted(common_qualities)
        info_text.delete(1.0, tk.END)  # Clear previous info
        info_text.insert(tk.END, f"播放列表名稱： {playlist.title}\n")
        info_text.insert(tk.END, f"影片數量： {len(playlist.video_urls)}\n\n")
        
        for video_url in playlist.video_urls:
            yt = YouTube(video_url)
            info_text.insert(tk.END, f"影片標題： {yt.title}\n")
            info_text.insert(tk.END, f"影片作者： {yt.author}\n")
            info_text.insert(tk.END, f"影片觀看數： {yt.views}\n")
            info_text.insert(tk.END, f"影片上傳日期： {yt.publish_date}\n")
            info_text.insert(tk.END, "影片縮圖網址： ")
            info_text.insert(tk.END, yt.thumbnail_url, yt.thumbnail_url)
            info_text.insert(tk.END, "\n\n")
        # Insert playlist name into filename entry
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, playlist.title)
        quality_dropdown['values'] = common_qualities
        if common_qualities:
            quality_dropdown.set(common_qualities[-1])
        
        
        # Disable quality selection for playlist
        #quality_dropdown.config(state='disabled')
        #quality_dropdown[quality_dropdown] = common_qualities
    else:

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
        info_text.insert(tk.END, yt.thumbnail_url)
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

        # fill time in time entry
        end_hour_entry.delete(0, tk.END)
        end_second_entry.delete(0, tk.END)
        end_minute_entry.delete(0, tk.END)
        end_hour_entry.insert(0, f"{length_hours:02d}")
        end_minute_entry.insert(0, f"{length_minutes:02d}")
        end_second_entry.insert(0, f"{length_seconds:02d}")

    cut_video_buttom.config(state="disabled")
    cut_audio_buttom.config(state="disabled")

def clear_info():
    info_text.delete(1.0, tk.END)
def merge_video_audio(video_path, audio_path, output_path):
    # 构造 FFmpeg 命令
    cmd = ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', output_path]
    
    # 执行命令
    subprocess.run(cmd, capture_output=True)

def get_start_time():
    start_hour = int(start_hour_entry.get())
    start_minute = int(start_minute_entry.get())
    start_second = int(start_second_entry.get())
    #start_time = f"{start_hour}:{start_minute}:{start_second}"
    
    time = start_hour *3600 + start_minute*60 +start_second
    return time

def get_end_time():
    end_hour = int(end_hour_entry.get())
    end_minute = int(end_minute_entry.get())
    end_second = int(end_second_entry.get())
    #end_time = f"{end_hour}:{end_minute}:{end_second}"
    time = end_hour *3600 + end_minute*60 + end_second
    return time

def download_video():
    global percent
    percent = 0  # Reset percent to 0
    url = url_entry.get()
    filename = filename_entry.get()
    download_path = path_entry.get()  # Get the download path
    selected_quality = quality_dropdown.get()  # Get selected quality
    print(selected_quality)
    # 清空下載完成提示
    status_label.config(text="                                  ")
    
    if not filename:
        yt = YouTube(url)
        filename = yt.title
    if "playlist" in url.lower():
        playlist = Playlist(url)
        playlist_folder = os.path.join(download_path, filename)
        os.makedirs(playlist_folder, exist_ok=True)
        
    
        for video_url in playlist.video_urls:
            
            if selected_quality =="1080P":
                audio_stream = yt.streams.filter(only_audio=True).first()  # 获取音频流
                if audio_stream:
                    # 下载视频和音频流并合并成一个完整的视频文件
                    video_stream.download(output_path=download_path, filename=f"{filename}.mp4")
                    audio_stream.download(output_path=download_path, filename=f"{filename}.mp3")
                    # 使用外部工具合并视频和音频文件
                    merge_video_audio(video_path=f"{download_path}/{filename}.mp4", audio_path=f"{download_path}/{filename}.mp3")
                    status_label.config(text="下載影片完成！")
                    info_text.insert(tk.END, path)
                else:
                    status_label.config(text="未找到音訊！")
            else:
                yt = YouTube(video_url, on_progress_callback=on_progress)
                video_stream = yt.streams.filter(file_extension='mp4', resolution=selected_quality).first()
            
            if video_stream:

                video_stream.download(output_path=playlist_folder, filename=f"{yt.title}.mp4")
        
        status_label.config(text="下載影片完成！")
        info_text.insert(tk.END, "全部影片下載完成！\n")
    else:
        yt = YouTube(url, on_progress_callback=on_progress)
        video_stream = yt.streams.filter(file_extension='mp4', resolution=selected_quality).first()
        path = "下載影片位置:"
        path += download_path +"/"+ filename +".mp4"+"\n"
        if video_stream:
            if selected_quality =="1080P":
                audio_stream = yt.streams.filter(only_audio=True).first()  # 获取音频流
                if audio_stream:
                    # 下载视频和音频流并合并成一个完整的视频文件
                    video_stream.download(output_path=download_path, filename=f"{filename}.mp4")
                    audio_stream.download(output_path=download_path, filename=f"{filename}.mp3")
                    # 使用外部工具合并视频和音频文件
                    merge_video_audio(video_path=f"{download_path}/{filename}.mp4", audio_path=f"{download_path}/{filename}.mp3")
                    status_label.config(text="下載影片完成！")
                    info_text.insert(tk.END, path)
                else:
                    status_label.config(text="未找到音訊！")
            else:
                video_stream.download(output_path=download_path, filename=f"{filename}.mp4")
                status_label.config(text="下載影片完成！")
                info_text.insert(tk.END, path)
                cut_video_buttom.config(state="normal")
        else:
            status_label.config(text="未找到影片！")

def download_audio():
    global percent
    percent = 0  # Reset percent to 0
    url = url_entry.get()
    filename = filename_entry.get()
    download_path = path_entry.get()  # Get the download path

    # 清空下載完成提示
    status_label.config(text="                                  ")
    
    if not filename:
        yt = YouTube(url)
        filename = yt.title
    if "playlist" in url.lower():
        playlist = Playlist(url)
        playlist_folder = os.path.join(download_path, filename)
        os.makedirs(playlist_folder, exist_ok=True)
        
        for video_url in playlist.video_urls:
            yt = YouTube(video_url, on_progress_callback=on_progress)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if audio_stream:
                audio_stream.download(output_path=playlist_folder, filename=f"{yt.title}.mp3")
        
        status_label.config(text="下載音訊完成！")
        info_text.insert(tk.END, "全部音訊下載完成！\n")

    else:
        yt = YouTube(url, on_progress_callback=on_progress)
        audio_stream = yt.streams.filter(only_audio=True).first()
        path = "下載音訊位置:"
        path += download_path+"/"+".mp3"+"\n"
        if audio_stream:
    
            audio_stream.download(output_path=download_path, filename=f"{filename}.mp3")
            status_label.config(text="下載音訊完成！")
            info_text.insert(tk.END, path)
            cut_audio_buttom.config(state="normal")
        else:
            status_label.config(text="未找到音訊！")

def cut_video():
    url = url_entry.get()
    yt = YouTube(url)
    length_seconds = yt.length
    filename = filename_entry.get()
    download_path = path_entry.get()
    path = download_path + "\\" + filename+".mp4"
    path = path.replace("\\", "/")
    clip = mp.VideoFileClip(path)
    start_time = get_start_time()
    end_time = get_end_time()
    if start_time > end_time or start_time > length_seconds or end_time > length_seconds:
        status_label.config(text="剪輯影片失敗！")
    else:
        new_clip = clip.subclip(start_time, end_time)
        clip_path = download_path +"\\"+filename+"_cliped.mp4"
        clip_path = clip_path.replace("\\", "/")
        new_clip.write_videofile(clip_path)
        status_label.config(text="剪輯影片完成！")

def cut_audio():
    url = url_entry.get()
    yt = YouTube(url)
    length_seconds = yt.length
    filename = filename_entry.get()
    download_path = path_entry.get()
    path = download_path + "\\" + filename + ".mp3"
    path = path.replace("\\", "/")
    clip = mp.AudioFileClip(path)
    start_time = get_start_time()
    end_time = get_end_time()
    if start_time > end_time or start_time > length_seconds or end_time > length_seconds:
        status_label.config(text="剪輯音訊失敗！")
    else:
        new_clip = clip.subclip(start_time, end_time)
        clip_path = download_path + "\\" + filename + "_cliped.mp3"
        clip_path = clip_path.replace("\\", "/")
        new_clip.write_audiofile(clip_path)
        status_label.config(text="剪輯音訊完成！")

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

def validate_input(text):
    if text.isdigit():
        if 0 <= int(text) <= 59:
            return True
        else:
            return False
    elif text == "":
        return True
    else:
        return False



# Get the directory of the Python file
# default_download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download") # 在python同層下再開download file
# default_download_path = os.path.dirname(os.path.abspath(__file__))
# 取得執行檔所在的目錄
exe_path = sys.executable
exe_dir = os.path.dirname(os.path.abspath(exe_path))

# 設定下載路徑為執行檔同一個資料夾下
default_download_path = exe_dir
# Create main window
root = tk.Tk()
root.title("YouTube 影片下載器")

# Configure style for ttk widgets
style = ttk.Style()
style.theme_use("flatly")  # You can choose a different theme here as well

# Create progress bar
download_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", value=0, bootstyle="success-striped") 
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

start_time_label = tk.Label(root, text="開始時間")
start_hour_label = tk.Label(root, text="時：")
start_hour_entry = tk.Entry(root, width=3)
start_minute_label = tk.Label(root, text="分：")
start_minute_entry = tk.Entry(root, width=3)
start_second_label = tk.Label(root, text="秒：")
start_second_entry = tk.Entry(root, width=3)

end_time_label = tk.Label(root, text="結束時間")
end_hour_label = tk.Label(root, text="時：")
end_hour_entry = tk.Entry(root, width=3)
end_minute_label = tk.Label(root, text="分：")
end_minute_entry = tk.Entry(root, width=3)
end_second_label = tk.Label(root, text="秒：")
end_second_entry = tk.Entry(root, width=3)

cut_video_buttom = tk.Button(root, text="剪輯影片", command=cut_video)
cut_audio_buttom = tk.Button(root, text="剪輯音訊", command=cut_audio)

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

start_time_label.grid(row=10, column=0, sticky="w", padx=2, pady=2)
start_hour_label.grid(row=10, column=1, sticky="w", padx=2, pady=2)
start_hour_entry.grid(row=10, column=2, sticky="w",padx=2, pady=2)
start_minute_label.grid(row=10, column=3, sticky="w", padx=2, pady=2)
start_minute_entry.grid(row=10, column=4, sticky="w",padx=2, pady=2)
start_second_label.grid(row=10, column=5, sticky="w", padx=2, pady=2)
start_second_entry.grid(row=10, column=6, sticky="w",padx=2, pady=2)

end_time_label.grid(row=11, column=0, sticky="w", padx=2, pady=2)
end_hour_label.grid(row=11, column=1, sticky="w", padx=2, pady=2)
end_hour_entry.grid(row=11, column=2, sticky="w",padx=2, pady=2)
end_minute_label.grid(row=11, column=3, sticky="w", padx=2, pady=2)
end_minute_entry.grid(row=11, column=4, sticky="w",padx=2, pady=2)
end_second_label.grid(row=11, column=5, sticky="w", padx=2, pady=2)
end_second_entry.grid(row=11, column=6, sticky="w",padx=2, pady=2)

cut_video_buttom.grid(row=12, column=1, columnspan=2, padx=10, pady=5)
cut_audio_buttom.grid(row=12, column=2, columnspan=2, padx=10, pady=5)

cut_video_buttom.config(state="disabled")
cut_audio_buttom.config(state="disabled")

validate_func = root.register(validate_input)

# 将 validatefunc 应用到 entry 元件
start_hour_entry.config(validate="key", validatecommand=(validate_func, "%P"))
start_minute_entry.config(validate="key", validatecommand=(validate_func, "%P"))
start_second_entry.config(validate="key", validatecommand=(validate_func, "%P"))
end_hour_entry.config(validate="key", validatecommand=(validate_func, "%P"))
end_minute_entry.config(validate="key", validatecommand=(validate_func, "%P"))
end_second_entry.config(validate="key", validatecommand=(validate_func, "%P"))

start_hour_entry.insert(0, "00")
start_minute_entry.insert(0, "00")
start_second_entry.insert(0, "00")

end_hour_entry.insert(0, "00")
end_minute_entry.insert(0, "00")
end_second_entry.insert(0, "00")

# Run the main loop
# root.iconbitmap('d.ico')

root.mainloop()