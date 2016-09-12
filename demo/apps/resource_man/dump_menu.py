def call(args, options, global_options):
    from uliweb.utils.common import dumps
    from uliweb import functions
    from uliweb.utils.sorteddict import SortedDict

    if len(args) < 2:
        print "Please use 'uliweb call {} <menuname> [filename]".format(args[0])
        return

    name = args[1]
    R = functions.get_model('resource')
    query = R.filter(R.c.type == 'M0000', R.c.status == '00001', R.c.name==name)
    text = dumps(query.tree(parent_field='parent',
                fields=['name', 'title', 'description', 'value', 'target',
                        'icon', 'deploy_type', 'order', 'status']),
                beautiful=True)
    filename = name + '.txt'
    if len(args) > 2:
        filename = args[2]
    with open(filename, 'wb') as f:
        f.write(text)

    print 'Menu {} is outputed to {}'.format(name, filename)