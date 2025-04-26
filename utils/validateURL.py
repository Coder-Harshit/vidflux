def validate(url:str) -> bool :
    if url.startswith('https://') or url.startswith('http://'):
        return True
    return False