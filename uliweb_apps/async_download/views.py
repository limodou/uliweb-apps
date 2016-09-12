#coding=utf-8
import os
from uliweb import expose, functions

@expose('/download')
def download():
    try:
        action = {'command':'download', 
            'parameters':{
                'user_id':request.user.id, 
                'token':request.POST.get('token'), 
                'filename':request.POST.get('filename'),
                'alt':request.POST.get('alt'),
                'url':request.POST.get('url')
            }
        }
        functions.async_push(action, channel='manual')
        result = {'success':True, 'message':'正在处理请稍候...'}
    except:
        result = {'success':False, 'message':'后台处理失败'}
        raise
    return json(result)

@expose('/sep_download')
def sep_download():
    try:
        action = {'command':'sep_download',
            'parameters':{
                'user_id':request.user.id,
                'token':request.POST.get('token'),
                'filename':request.POST.get('filename'),
                'alt':request.POST.get('alt'),
                'url':request.POST.get('url')
            }
        }
        functions.async_push(action, channel='manual')
        result = {'success':True, 'message':'正在处理请稍候...'}
    except:
        result = {'success':False, 'message':'后台处理失败'}
        raise
    return json(result)

@expose('/check_download')
def check_download():
    cache = functions.get_cache()
    token = request.GET.get('token')
    url = cache.get(token, None)
    if url:
        cache.delete(token)
        return json({'success':True, 'url':url})
    return json({})

@expose('/check_sep_download')
def check_sep_download():
    import json as json_lib

    cache = functions.get_cache()
    token = request.GET.get('token')
    m = cache.get(token, None)
    if m:
        cache.delete(token)
        return json({'success':True, 'message':'请到ITDM中查看并下载'})
    return json({})


@expose('/downloads/<path:filename>')
def filedown(filename):
    from uliweb import request
    import urllib2
    from uliweb.utils.common import application_path
    from uliweb.contrib.upload import FileServing

    backend = FileServing()
    backend.x_sendfile = False
    alt_filename = request.GET.get('alt')
    if not alt_filename:
        alt_filename = filename
    else:
        alt_filename = urllib2.unquote(alt_filename)
    x_filename = filename
    return backend.download(alt_filename, real_filename=os.path.join(settings.get_var('GENERIC/DOWNLOAD_DIR'), filename))
