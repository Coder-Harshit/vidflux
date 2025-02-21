import yt_dlp
from signals import DownloadSignals


class DownloadWorker:
    def __init__(self):
        self.signals = DownloadSignals()

    def format_selector(self, ctx, ext):
        """ Select the best video and the best audio that won't result in an mkv.
        NOTE: This is just an example and does not handle all cases """

        # formats are already sorted worst to best
        formats = ctx.get('formats')[::-1]

        # acodec='none' means there is no audio
        if ext:
            best_video = next((f for f in formats
                        if f['vcodec'] != 'none' and f['acodec'] == 'none' and f['ext']==ext),None)
            if not best_video:
                    print(f"No suitable video format found for preferred extension: {ext}.")
                    best_video = next((f for f in formats if f['vcodec'] != 'none' and f['acodec'] == 'none'))

        else: # if extension is not provided by the user
            best_video = next((f for f in formats if f['vcodec'] != 'none' and f['acodec'] == 'none')) 


        # find compatible audio extension
        audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
        # vcodec='none' means there is no video
        best_audio = next(f for f in formats if (
            f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

        # These are the minimum required fields for a merged format
        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            # Must be + separated list of protocols
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }

    def update_progress(self, d):
       
    #    to do modify the cnvert functions such that one is good enough for all
        def cnv(value,units,factor=1000):
            indx:int = 0
            while (value>factor):
                value//=factor
                indx+=1
            return f"{value} {units[indx]}"
       
        def eta_cnv(eta):
            output = ""
            eta = int(eta)

            if eta==0:
                return "00:00"
            
            time_vals = []
            while (eta>0):
                time_vals.append(eta%60)
                eta//=60
            # time_vals has values: [sec, min, hrs, ....]
            
            n: int = len(time_vals)
            for indx in range(n-1,0,-1):
                # loop goes like=> [hrs, min, sec ....]
                if time_vals[indx]<10:
                    output+=f"0{time_vals[indx]}:"
                else:
                    output+=f"{time_vals[indx]}:"
            if time_vals[0]<10:
                    output+=f"0{time_vals[0]}"
            else:
                    output+=f"{time_vals[0]}"
            if len(output)<=2:
                 output = "00:" + output
            return output
        
        file_name = d.get('filename')
        file_name_str = f"{file_name}" if file_name!=None else 'N/A'

        file_size = d.get('total_bytes')
        file_size_units = ['B','KiB','MiB','GiB','TiB']
        file_size_str = f"{cnv(file_size,file_size_units,1000)}" if file_size!=None else 'N/A'

        downloaded_size = d.get('downloaded_bytes')

        percent = int(downloaded_size)/int(file_size)
        percent_str = f"{percent*100:.2f}%"

        speed = d.get('speed')
        speed_units = ['B/s','KiB/s','MiB/s','GiB/s','TiB/s']
        speed_str = f"{cnv(speed,speed_units,1000)}" if speed!=None else 'N/A'
        
        eta = d.get('eta')
        eta_str = f"{eta_cnv(eta)}" if eta!=None else 'N/A'
        message = f"File: {file_name_str}\nProgress: {percent_str} of {file_size_str}, Speed: {speed_str}, ETA: {eta_str}\n"


        self.signals.progress_update.emit(message)
        
    def download(self, url, preferred_ext=None):
        ydl_opts = {
            'format': lambda ctx: self.format_selector(ctx,preferred_ext),
            'progress_hooks': [lambda d: self.update_progress(d)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try: 
                # self.signals.progress_update.emit()
                ydl.download(url)
                self.signals.download_finished.emit()
            except Exception as ex:
                print("ERROR Occured: ",ex)
                self.signals.download_error.emit(str(ex))