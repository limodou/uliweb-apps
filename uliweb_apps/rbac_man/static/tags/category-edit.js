/* 用来实现分类的展示 */
riot.tag2('category', '<div class="search" if="{!editing}"> <div class="form-group has-feedback"> <input type="text" name="search" class="form-control" placeholder="分类搜索" onkeyup="{searching}"> <span class="fa fa-search form-control-feedback" aria-hidden="true"></span> </div> </div> <div class="{all:true, selected:!selected}" onclick="{select_all}">全部</div> <ol class="{sortable:true, editable:editing}"> <virtual each="{item in data}"> <li data-is="treeitem" data="{item}"></li> </virtual> </ol> <div class="new_item" show="{editing}"> <input type="text" name="new_item" onkeyup="{edit}"> </div> <div class="tools"> <a href="#" onclick="{toggle}" class="tool-btn btn btn-xs" style="color:#9dabc1">{edit_text}</a> <a href="#" onclick="{save}" if="{editing}" class="tool-btn btn btn-xs" style="color:#9dabc1">保存退出</a> </div>', 'category .placeholder,[riot-tag="category"] .placeholder,[data-is="category"] .placeholder{ outline: 1px dashed #4183C4; } category .mjs-nestedSortable-error,[riot-tag="category"] .mjs-nestedSortable-error,[data-is="category"] .mjs-nestedSortable-error{ background: #fbe3e4; border-color: transparent; } category ol.sortable,[riot-tag="category"] ol.sortable,[data-is="category"] ol.sortable{ max-width: 300px; padding-left: 15px; padding-right: 15px; } category ol,[riot-tag="category"] ol,[data-is="category"] ol{ padding-right:0px; padding-left:25px; } category ol.sortable,[riot-tag="category"] ol.sortable,[data-is="category"] ol.sortable,category ol.sortable ol,[riot-tag="category"] ol.sortable ol,[data-is="category"] ol.sortable ol{ list-style-type: none; } category .sortable li div,[riot-tag="category"] .sortable li div,[data-is="category"] .sortable li div{ border: 1px solid transparent; cursor: default; margin: 0; padding: 5px; } category .all,[riot-tag="category"] .all,[data-is="category"] .all{ border: 1px solid transparent; cursor: default; max-width: 300px; margin: 0; padding: 0 20px; } category .sortable.editable li div,[riot-tag="category"] .sortable.editable li div,[data-is="category"] .sortable.editable li div{ cursor: move; } category .sortable li div:hover,[riot-tag="category"] .sortable li div:hover,[data-is="category"] .sortable li div:hover{ background-color: bisque; border-radius: 3px; } category li.mjs-nestedSortable-collapsed.mjs-nestedSortable-hovering div,[riot-tag="category"] li.mjs-nestedSortable-collapsed.mjs-nestedSortable-hovering div,[data-is="category"] li.mjs-nestedSortable-collapsed.mjs-nestedSortable-hovering div{ border-color: #999; } category .disclose,[riot-tag="category"] .disclose,[data-is="category"] .disclose{ width: 10px; display: none; font: normal normal normal 14px/1 FontAwesome; margin-right:4px; } category .editable .disclose,[riot-tag="category"] .editable .disclose,[data-is="category"] .editable .disclose{ cursor: pointer; } category .sortable li.mjs-nestedSortable-collapsed > ol,[riot-tag="category"] .sortable li.mjs-nestedSortable-collapsed > ol,[data-is="category"] .sortable li.mjs-nestedSortable-collapsed > ol{ display: none; } category .sortable li.mjs-nestedSortable-branch > div > .disclose,[riot-tag="category"] .sortable li.mjs-nestedSortable-branch > div > .disclose,[data-is="category"] .sortable li.mjs-nestedSortable-branch > div > .disclose{ display: inline-block; } category .sortable li.mjs-nestedSortable-collapsed > div > .disclose > span:before,[riot-tag="category"] .sortable li.mjs-nestedSortable-collapsed > div > .disclose > span:before,[data-is="category"] .sortable li.mjs-nestedSortable-collapsed > div > .disclose > span:before{ content: "\\f196"; } category .sortable li.mjs-nestedSortable-expanded > div > .disclose > span:before,[riot-tag="category"] .sortable li.mjs-nestedSortable-expanded > div > .disclose > span:before,[data-is="category"] .sortable li.mjs-nestedSortable-expanded > div > .disclose > span:before{ content: "\\f147"; } category .sortable li.mjs-nestedSortable-branch > div > .disclose,[riot-tag="category"] .sortable li.mjs-nestedSortable-branch > div > .disclose,[data-is="category"] .sortable li.mjs-nestedSortable-branch > div > .disclose{ display: inline-block; } category .sortable span.ui-icon,[riot-tag="category"] .sortable span.ui-icon,[data-is="category"] .sortable span.ui-icon{ display: inline-block; margin: 0; padding: 0; } category li.listitem,[riot-tag="category"] li.listitem,[data-is="category"] li.listitem{ position: relative; } category .treeitem.selected,[riot-tag="category"] .treeitem.selected,[data-is="category"] .treeitem.selected{ background-color: #b2c5ec; } category .treeitem,[riot-tag="category"] .treeitem,[data-is="category"] .treeitem{ position: relative; } category .treeitem .delete,[riot-tag="category"] .treeitem .delete,[data-is="category"] .treeitem .delete{ display:none; cursor: pointer; } category .editable .treeitem.show .delete,[riot-tag="category"] .editable .treeitem.show .delete,[data-is="category"] .editable .treeitem.show .delete{ position: absolute; right:5px; top:5px; display:inline-block; } category .inline-editor,[riot-tag="category"] .inline-editor,[data-is="category"] .inline-editor{ position:absolute; top:2px; left:2px; } category .tools,[riot-tag="category"] .tools,[data-is="category"] .tools{ position: absolute; left: 0px; bottom: 0px; width: 100%; background-color: #3c5681; padding:0; } category .tools a.tool-btn,[riot-tag="category"] .tools a.tool-btn,[data-is="category"] .tools a.tool-btn{ color: #9dabc1; } category .tools a.tool-btn:hover,[riot-tag="category"] .tools a.tool-btn:hover,[data-is="category"] .tools a.tool-btn:hover{ background-color: #2e415c; } category .new_item,[riot-tag="category"] .new_item,[data-is="category"] .new_item,category .search,[riot-tag="category"] .search,[data-is="category"] .search{ padding-left:20px; padding-right:20px; width:100%; } category .new_item input,[riot-tag="category"] .new_item input,[data-is="category"] .new_item input,category .search input,[riot-tag="category"] .search input,[data-is="category"] .search input{ width:100%; } category .search,[riot-tag="category"] .search,[data-is="category"] .search{margin-top:10px;}', '', function(opts) {
    var self = this
    this._data = new DataSet(opts.data || [], {parentFieldId:'parent'})
    this._old_data = opts.data
    this.data = this._data.tree()
    this.editing = false
    this.edit_text = '编辑'
    this.adding = false
    this.max_id = 10
    this.selected = null

    this.on('mount', function(){
      $('.disclose', self.root).on('click', function() {
  			$(this).closest('li').toggleClass('mjs-nestedSortable-collapsed').toggleClass('mjs-nestedSortable-expanded');
  		})
    })

    this.toggle = function(){
      self.editing = !self.editing
      if (self.editing) {
        $('.sortable', self.root).nestedSortable({
          forcePlaceholderSize: true,
          handle: 'div',
          helper:	'clone',
          items: 'li',
          opacity: .6,
          placeholder: 'placeholder',
          revert: 250,
          tabSize: 25,
          tolerance: 'pointer',
          toleranceElement: '> div',
          maxLevels: 4,
          isTree: true,
          expandOnHover: 700,
          startCollapsed: false
        });
        self.edit_text = '取消退出'
      } else {
        $('.sortable', self.root).nestedSortable('destroy')
        self.edit_text = '编辑'
        self._data.clear()
        self._data.add(self._old_data)
        self.data = self._data.tree()
      }
    }

    this.save = function() {
      var result = self.serialize()
      self._data.update(result)
      self._old_data = self._data.get()
      self.edit_text = '编辑'
      self.editing = false
      self.data = self._data.tree()
      if (opts.onSave){
        opts.onSave(self._data.get({order:['parent', 'order']}))
      }
    }

    this.edit = function(e) {
      if (e.keyCode == 13){
        self._data.add({name:self.new_item.value, parent:0})
        self.data = self._data.tree()
        self.new_item.value = ''
      } else if (e.keyCode == 27) {
        self.new_item.value = ''
      }
    }

    this.searching = function(e) {
      function s(v) {
        function f(item) {
          return item['name'].indexOf(v) != -1
        }
        return f
      }
      if ( self.search.value )
        self.data = self._data.get({filter:s(self.search.value)})
      else
        self.data = self._data.tree()
    }

    this.select = function(e) {
      if (!self.editing){
        var id = e.item.item.id;
        self.selected = id;
        if (opts.onSelect) {
          opts.onSelect(self._data.get(id)).bind(self)
        }
      }
    }

    this.select_all = function(e){
      if (!self.editing){
        self.selected = null;
      }
    }

    this.serialize = function () {
      return $('.sortable', self.root).nestedSortable('serialize', {parentField:'parent'});
    }

    this.remove = function(e){
      var delete_children = function(p) {
        var item
        if (p.nodes && p.nodes.length > 0) {
          for(var i=0, len=p.nodes.length; i<len; i++) {
            item = p.nodes[i]
            delete_children(item)
            self._data.remove(item.id)
          }
        }
      }
      var id = e.item.item.id
      var flag = false
      var find = function (d, id) {
        d.forEach(function(v, i){
          if (v.id == id) {
            delete_children(v)
            self._data.remove(id)
            return true
          }
          if (v.nodes && v.nodes.length > 0) {
            flag = find (v.nodes, id)
            if (flag)
              return true
          }

        })
      }
      find(self.data, id)
      self.data = self._data.tree()
      self.update()
    }
});

riot.tag2('treeitem', '<div class="{treeitem:true, selected:is_selected(id)}" onmouseenter="{enter}" onclick="{parents(\'category\').select}" onmouseleave="{leave}" ondblclick="{edit}"> <span class="disclose"><span></span></span>{name} <span class="delete" onclick="{parents(\'category\').remove}">&times;</span> </div> <ol if="{isFolder()}"> <virtual each="{item in nodes}"> <li data-is="treeitem" data="{item}"></li> </virtual> </ol>', '', 'id="{id}" class="{listitem:true, mjs-nestedSortable-expanded: isFolder(),     mjs-nestedSortable-branch: isFolder()}"', function(opts) {

  var self = this
  self.id = opts.data.id
  self.name = opts.data.name
  self.nodes = opts.data.nodes
  var parent = this.parents('category')
  self._data = parent._data
  self.data = parent.data

  this.isFolder = function() {
    return self.nodes && self.nodes.length
  }

  this.is_selected = function(id) {
    return id && (id == parent.selected)
  }

  this.enter = function(e){
    $(e.target).addClass('show')
  }

  this.leave = function(e){
    $(e.target).removeClass('show')
  }

  this.edit = function(e){
    if (self.parents('category').editing) {
      var el = $(e.target)
      var pos = el.position()
      var w = el.width(), h = el.height
      var p = $(el.parents('li')[0])
      var input = $('<input type="text" class="inline-editor"></input>')
      var value;
      var id = e.item.item.id
      input.css({width:w, height:h})
      p.append(input)
      el.css('visibility', 'hidden')
      input.focus()
      input.keyup(function(e){
        if (e.keyCode == 13){
          value = input.val()
          self._data.update({id:id, name:value})
          parent.data = self._data.tree()
          input.remove()
          el.css('visibility', 'visible')
          parent.update()
        } else if (e.keyCode == 27) {
          input.remove()
          el.css('visibility', 'visible')
        }
      })
      input.blur(function(e){
        input.remove()
        el.css('visibility', 'visible')
      })
    }
  }

});
