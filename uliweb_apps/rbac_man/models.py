# coding=utf8

from uliweb.orm import *
from uliweb.utils.common import get_var

class Perm_Category(Model):
    __verbose_name__ = u'权限分类'

    name = Field(str, max_length=255, verbose_name=u'名称', index=True, unique=True)
    parent = Reference(verbose_name=u'父分类')
    order = Field(int, verbose_name=u'序号', index=True)
    deleted = Field(bool, verbose_name=u'删除标志')
    modified_user = Reference('user', verbose_name=u'修改人')
    modified_time = Field(DATETIME, verbose_name=u'修改时间', auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name

class Permission(Model):
    name = Field(str, verbose_name=u'名称', max_length=80, required=True, index=True, unique=True)
    cn_name = Field(str, verbose_name=u'中文名称', max_length=80)
    order = Field(int, verbose_name=u'显示顺序')
    description = Field(str, verbose_name=u'描述', max_length=255)
    category = Reference('perm_category', verbose_name=u'分类')
    modified_user = Reference('user', verbose_name=u'修改人')
    modified_time = Field(DATETIME, verbose_name=u'修改时间', auto_now=True, auto_now_add=True)

    def get_users(self):
        for role in self.perm_roles.all():
            for u in role.users.all():
                yield u

    def get_users_ids(self):
        for role in self.perm_roles.all():
            for u in role.users.ids():
                yield u
                
    def get_url(self):
        return '<a href = "/config/permissions/view/%d">%s</a>' % (self.id, self.name)

    def __unicode__(self):
        return self.name

    class Table:
        fields = ['name', 'cn_name', 'order', 'description']

    class AddForm:
        fields = ['name', 'cn_name', 'order', 'description']

    class EditForm:
        fields = ['name', 'cn_name', 'order', 'description']

    class DetailView:
        fields = ['name', 'cn_name', 'order', 'description',
                  'modified_user', 'modified_time']


class Role_Category(Model):
    __verbose_name__ = u'角色分类'

    name = Field(str, max_length=255, verbose_name=u'名称')
    parent = Reference(verbose_name=u'父分类')
    order = Field(int, verbose_name=u'序号')

    def __unicode__(self):
        return self.name

class Role(Model):
    name = Field(str, max_length=80,
                 verbose_name='角色名', required=True)
    sub_name = Field(str, max_length=20, verbose_name='子名称')
    cn_name = Field(str, verbose_name='中文名称', max_length=80)
    order = Field(int, verbose_name='显示顺序')
    description = Field(str, max_length=255, verbose_name='描述')
    category = Reference('role_category', verbose_name='分类')
    reserve = Field(bool, verbose_name='是否保留')
    users = ManyToMany(
        'user', verbose_name='包含人员', through='role_user_rel',
        through_reference_fieldname='user',
        collection_name='user_roles')
    # 角色所属的机构
    belong_dept = Reference('usergroup', verbose_name='所属机构')
    # departments 机构下的人具有该角色
    departments = ManyToMany('usergroup', verbose_name='成员机构')
    # 角色所属用户，可以管理的机构
    manage_depts = ManyToMany('usergroup', verbose_name='管理机构')

    parent_role = SelfReference(verbose_name='父角色')
    child_count = Field(int, verbose_name='子角色数')
    permissions = ManyToMany(
        'permission', verbose_name='关联权限', through='role_perm_rel',

        collection_name='perm_roles')

    modified_user = Reference('user', verbose_name='修改人')
    modified_time = Field(DATETIME, verbose_name='修改时间', auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '<a href = "/config/roles/view/%d">%s</a>' % (self.id, self.name)

    class Table:
        fields = [
            {'name': 'name', 'width': 200},
            {'name': 'sub_name', 'width': 200},
            {'name': 'cn_name', 'width': 150},
            {'name': 'description', 'width': 200},
            {'name': 'order', 'width': 100},
            {'name': 'child_count', 'hidden': True}
        ]

    class AddForm:
        fields = [
                'parent_role', 'name', 'sub_name', 'cn_name', 'order', 'description',
                'reserve', 'belong_dept',
                'departments', 'manage_depts', 'permissions', ]

    class EditForm:
        fields = [
                'parent_role', 'name', 'sub_name', 'cn_name', 'order', 'description',
                'reserve', 'belong_dept',
                'departments', 'manage_depts', 'permissions']

    class DetailView:
        fields = ['parent_role', 'name', 'sub_name', 'cn_name', 'order', 'description',
                  'reserve', 'belong_dept',
                  'departments', 'manage_depts', 'permissions',
                  'modified_user', 'modified_time']
        layout = [('parent_role', 'cn_name'),
                  ('classify', 'description'),
                  ('reserve', 'belong_dept'),
                  ('departments', 'manage_depts'),
                  'permissions',
                  ('modified_user', 'modified_time')]

    @classmethod
    def OnInit(cls):
        Index('role_idx', cls.c.name, cls.c.sub_name, unique=True)


class Role_Perm_Rel(Model):
    role = Reference('role', index=True)
    permission = Reference('permission', index=True)
    modified_time = Field(DATETIME, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    modified_user = Reference('user', verbose_name='修改人')


class Role_User_Rel(Model):
    role = Reference('role', verbose_name='角色', required=True, index=True)
    user = Reference('user', verbose_name='用户', required=True, index=True)
    is_admin = Field(bool, verbose_name='是否为管理员')
    modified_time = Field(DATETIME, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    modified_user = Reference('user', verbose_name='修改人')
    order = Field(int, verbose_name='序号', server_default=99990000)

