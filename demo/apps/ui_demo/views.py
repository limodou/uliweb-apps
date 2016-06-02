from uliweb import expose

@expose('/ui')
def ui():
    response.template = 'ui_demo_layout.html'
    return {}

