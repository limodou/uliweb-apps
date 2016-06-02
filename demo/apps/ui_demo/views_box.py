from uliweb import expose

@expose('/ui/<path:name>')
def ui_example(name):
    response.template = 'ui/{}.html'.format(name)
    return {}