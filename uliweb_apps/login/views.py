#coding=utf8

from uliweb.core.SimpleFrame import functions, expose, redirect
from uliweb.i18n import ugettext_lazy as _
from uliweb.utils._compat import import_

unquote = import_('urllib.parse', 'unquote')


def add_prefix(url):
    from uliweb import settings
    return settings.DOMAINS.static.get('url_prefix', '') + url or '/'


def login():
    from uliweb.contrib.auth import login

    form = functions.get_form('auth.LoginForm')()

    if request.user:
        next = request.values.get('next')
        if next:
            return redirect(next)

    next = request.values.get('next')
    if not next:
        next = add_prefix('/')
    if request.method == 'GET':
        form.next.data = next
        return {'next': next}
    if request.method == 'POST':
        flag = form.validate(request.values)
        if flag:
            f, d = functions.authenticate(username=form.username.data, password=form.password.data)
            if f:
                request.session.remember = form.rememberme.data
                login(form.username.data)
                next = unquote(next)
                return redirect(next)
            else:
                form.errors.update(d)
        if request.is_xhr:
            return json({'success': False, '_': 'Login Failed', 'errors': form.errors})
        else:
            msg = form.errors.get('_', '') or _('Login failed!')
            return {'form': form, 'msg': str(msg)}


def register():
    from uliweb import settings
    from uliweb.contrib.auth import create_user, login

    if not settings.LOGIN.register:
        error('不允许用户自行注册')

    next = request.values.get('next')
    if not next:
        next = request.referrer
        if not next or (next and next.endswith('/register')):
            next = add_prefix('/')

    form = functions.get_form('auth.RegisterForm')()

    if request.method == 'GET':
        form.next.data = next
        return {'form': form, 'msg': ''}
    if request.method == 'POST':
        flag = form.validate(request.values)
        if flag:
            from uliweb import settings
            f, d = create_user(username=form.username.data,
                               password=form.password.data,
                               auth_type=settings.AUTH.AUTH_TYPE_DEFAULT)
            if f:
                # add auto login support 2012/03/23
                login(d)
                next = unquote(next)
                return redirect(next)
            else:
                form.errors.update(d)

        if request.is_xhr:
            return json({'success': False, '_': 'Register Failed', 'errors': form.errors})
        else:
            msg = form.errors.get('_', '') or _('Register failed!')
            return {'form': form, 'msg': str(msg)}

def logout():
    from uliweb.contrib.auth import logout as out
    from uliweb import settings
    out()
    next = unquote(request.POST.get('next', add_prefix('/')))
    return redirect(next)
