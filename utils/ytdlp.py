import yt_dlp


def format_selector(ctx, ext):
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

def update_progress(d,console):
    # if d['status'] == 'downloading':
    percent_str = d.get('_percent_str', 'N/A')  # Handle potential missing key
    speed_str = d.get('_speed_str', 'N/A')
    eta_str = d.get('_eta_str', 'N/A')
    message = f"Progress: {percent_str}, Speed: {speed_str}, ETA: {eta_str}"
    console.appendPlainText(message) 

def download(url,console,preferred_ext=None):     
    ydl_opts = {
        'format': lambda ctx: format_selector(ctx,preferred_ext),
        'progress_hooks': [lambda d: update_progress(d,console)],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try: 
            ydl.download(url)

        except Exception as ex:
            print("ERROR Occured: ",ex)