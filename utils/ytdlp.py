import json
import threading
import yt_dlp
from signals import DownloadSignals
import os
import pandas as pd

class DownloadWorker:
    def __init__(self):
        self.signals = DownloadSignals()

    # def format_selector(self, ctx, ext):
    #     """Select the best video and the best audio that won't result in an mkv.
    #     NOTE: This is just an example and does not handle all cases"""

    #     # formats are already sorted worst to best
    #     formats = ctx.get("formats")[::-1]

    #     # acodec='none' means there is no audio
    #     if ext:
    #         best_video = next(
    #             (
    #                 f
    #                 for f in formats
    #                 if f["vcodec"] != "none"
    #                 and f["acodec"] == "none"
    #                 and f["ext"] == ext
    #             ),
    #             None,
    #         )
    #         if not best_video:
    #             print(f"No suitable video format found for preferred extension: {ext}.")
    #             best_video = next(
    #                 (
    #                     f
    #                     for f in formats
    #                     if f["vcodec"] != "none" and f["acodec"] == "none"
    #                 )
    #             )

    #     else:  # if extension is not provided by the user
    #         best_video = next(
    #             (f for f in formats if f["vcodec"] != "none" and f["acodec"] == "none")
    #         )

    #     # find compatible audio extension
    #     audio_ext = {"mp4": "m4a", "webm": "webm"}[best_video["ext"]]
    #     # vcodec='none' means there is no video
    #     best_audio = next(
    #         f
    #         for f in formats
    #         if (
    #             f["acodec"] != "none"
    #             and f["vcodec"] == "none"
    #             and f["ext"] == audio_ext
    #         )
    #     )

    #     # These are the minimum required fields for a merged format
    #     yield {
    #         "format_id": f'{best_video["format_id"]}+{best_audio["format_id"]}',
    #         "ext": best_video["ext"],
    #         "requested_formats": [best_video, best_audio],
    #         # Must be + separated list of protocols
    #         "protocol": f'{best_video["protocol"]}+{best_audio["protocol"]}',
    #     }

    def update_progress(self, d):

        #    to do modify the cnvert functions such that one is good enough for all
        def cnv(value, units, factor=1000):
            indx: int = 0
            while value > factor:
                value //= factor
                indx += 1
            return f"{value} {units[indx]}"

        def eta_cnv(eta):
            output = ""
            eta = int(eta)

            if eta == 0:
                return "00:00"

            time_vals = []
            while eta > 0:
                time_vals.append(eta % 60)
                eta //= 60
            # time_vals has values: [sec, min, hrs, ....]

            n: int = len(time_vals)
            for indx in range(n - 1, 0, -1):
                # loop goes like=> [hrs, min, sec ....]
                if time_vals[indx] < 10:
                    output += f"0{time_vals[indx]}:"
                else:
                    output += f"{time_vals[indx]}:"
            if time_vals[0] < 10:
                output += f"0{time_vals[0]}"
            else:
                output += f"{time_vals[0]}"
            if len(output) <= 2:
                output = "00:" + output
            return output

        file_name = d.get("filename")
        file_name_str = f"{file_name}" if file_name is not None else "N/A"

        file_size = d.get("total_bytes")
        file_size_units = ["B", "KiB", "MiB", "GiB", "TiB"]
        file_size_str = (
            f"{cnv(file_size,file_size_units,1000)}" if file_size is not None else "N/A"
        )

        downloaded_size = d.get("downloaded_bytes")

        # Check if both downloaded_size and file_size are available before calculating percentage
        if downloaded_size is not None and file_size is not None and file_size > 0:
            percent = int(downloaded_size) / int(file_size)
            percent_str = f"{percent*100:.2f}%"
        else:
            percent_str = "N/A" # Or some other placeholder

        speed = d.get("speed")
        speed_units = ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"]
        speed_str = f"{cnv(speed,speed_units,1000)}" if speed != None else "N/A"

        eta = d.get("eta")
        eta_str = f"{eta_cnv(eta)}" if eta != None else "N/A"
        message = f"File: {file_name_str}\nProgress: {percent_str} of {file_size_str}, Speed: {speed_str}, ETA: {eta_str}\n"

        self.signals.progress_update.emit(message)

    def formatSelection(self, url):

        # with yt_dlp.YoutubeDL({'listformats':True}) as ydl:
        #     ydl.download(url)

        # with yt_dlp.YoutubeDL() as ydl:
            # self.format_handler(url, ydl)
        self.format_handler(url)

    # def download(self, url, download_dir="", preferred_ext=None):
    def download(self, url, download_dir="", fmt_string=None):
        # with yt_dlp.YoutubeDL() as ydl:
        #     self.format_handler(url, ydl)

        # print(url)
        # print(download_dir)

        ydl_opts = {
            # "format": lambda ctx: self.format_selector(ctx, preferred_ext),
            "format": fmt_string,
            "progress_hooks": [lambda d: self.update_progress(d)],
            "outtmpl": {
                "default": os.path.join(download_dir, "%(title)s.%(ext)s"),
                "chapter": os.path.join(
                    download_dir,
                    "%(title)s - %(section_number)03d %(section_title)s.%(ext)s",
                ),
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # self.format_handler(url, ydl)
                # print(ydl_opts)
                # self.signals.progress_update.emit()
                info = ydl.extract_info(url, download=False)
                # print(ydl_opts)
                # final_path = ydl.prepare_filename(info, ydl_opts['outtmpl'])
                final_path = ydl.prepare_filename(info)
                # print(final_path)
                ydl.download(url)
                self.signals.download_finished.emit(final_path)
            except Exception as ex:
                print("ERROR Occured: ", ex)
                self.signals.download_error.emit(str(ex))

    # def format_handler(self, url, ydl: yt_dlp.YoutubeDL):
    def format_handler(self, url):
        with yt_dlp.YoutubeDL() as ydl:  # Capture the available formats and store them in a dictionary
            info = ydl.extract_info(url, download=False)

            # DEBUG
            # # Save formats to JSON file
            # formats_data = info.get('formats', [])
            # video_id = info.get('id', 'unknown')
            # video_title = info.get('title', 'video').replace('/', '_').replace('\\', '_')  # Sanitize filename
            # json_filename = f"{video_id}_{video_title}_formats.json"
            # with open(json_filename, 'w', encoding='utf-8') as json_file:
            #     json.dump(formats_data, json_file, indent=4)
            # print(f"Formats saved to {json_filename}")

            formats_table = {}
            for fmt in info.get("formats", []):
                format_id = fmt.get("format_id")
                lang = fmt.get("language")
                ext = fmt.get("ext")
                resolution = fmt.get("resolution")
                acodec = fmt.get("acodec")
                vcodec = fmt.get("vcodec")
                if (vcodec == "none" or vcodec == None) and (
                    acodec == "none" or acodec == None
                ):
                    continue
                if vcodec == "audio only" and (acodec == "none" or acodec == None):
                    continue
                if acodec == "video only" and (vcodec == "none" or vcodec == None):
                    continue

                filesize = fmt.get("filesize") or fmt.get("filesize_approx")
                # if filesize is None:
                #     continue
                br = fmt.get("tbr")
                if br == 0:
                    continue

                # converting the vp09 codec to the offical name i.e. 'vp9'
                if vcodec.split(".")[0] == "vp09":
                    vcodec = "vp9"
                if acodec.split(".")[0] == "vp09":
                    acodec = "vp9"

                formats_table[format_id] = {
                    "ext": ext,
                    "resolution": resolution,
                    "acodec": acodec.split(".")[0],
                    "vcodec": vcodec.split(".")[0],
                    "filesize": filesize,
                    "bitrate": br,
                    "language": lang,
                }
            # print("Available formats:")
            # for fmt_id, fmt_info in formats_table.items():
            #     print(f"Format ID: {fmt_id}, Info: {fmt_info}")

            df = pd.DataFrame(formats_table).T
            print(df)

            # print(df['acodec'].unique())
            # print(df['vcodec'].unique())

            # You can now use formats_table as needed, e.g., pass to a signal or UI
            self.signals.formats_listed.emit(df)
            # here within the download_starting signal's emit pass all the formats to the format selector
