from uliweb import expose

@expose('/ui')
def ui():
    response.template = 'ui/ui_demo_layout.html'
    return {}

@expose('/ui/<path:name>')
def ui_example(name):
    response.template = 'ui/{}.html'.format(name)
    return {}