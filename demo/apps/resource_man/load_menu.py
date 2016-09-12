def call(args, options, global_options):
    from uliweb import functions
    from sqlalchemy import and_

    if len(args) < 2:
        print "Please use 'uliweb call {} <menuname> [menu_filename]".format(args[0])
        return

    name = args[1]
    if len(args) == 3:
        filename = args[2]
    else:
        filename = name + '.txt'

    text = ''
    with open(filename) as f:
        text = f.read()

    menus = eval(text)
    R = functions.get_model('resource')

    def _f(m, parent=0):
        for item in m:
            item['parent'] = parent
            item['type'] = 'M0000'
            obj = R.get(and_(R.c.name==item['name'], R.c.parent==parent, R.c.type=='M0000'))
            if not obj:
                obj = R(**item)
            else:
                obj.update(**item)
            if item.get('children'):
                obj.has_children = True
            obj.save()
            if item.get('children'):
                _f(item['children'], obj.id)

    _f(menus)
