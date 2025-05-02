AUDIO_CODECS = {
    'opus' : ['av01','vp9'],
    'mp4a' : ['vp9','avc1'],
}

VIDEO_CODECS = {
    'av01' : ['opus'],
    'vp9': ['opus','mp4a'],
    'avc1': ['mp4a'],
}