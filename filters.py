import arrow
import os
import mimetypes

def datetimeformat(date_str):
    dt = arrow.get(date_str)
    return dt.humanize()

def file_type(key):
    file_info = os.path.splitext(key)
    file_extension = file_info[1].lower()
    try:
        return mimetypes.types_map[file_extension]
    except:
        return 'Unknown'

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)