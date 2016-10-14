from uliweb.form import *

class ChooserForm(Form):
    name = StringField('Name')
    type = SelectField('Type', choices=[('1', 'Choice A'), ('2', 'Choice B')])