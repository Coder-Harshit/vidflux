def validate(url:str) -> bool :
    if url.startswith('https://') or url.startswith('http://'):
        return True
    else: return False