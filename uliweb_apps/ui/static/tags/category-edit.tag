/* 用来实现分类的展示 */
<category>
  <style scoped>
    .placeholder {
      outline: 1px dashed #4183C4;
    }

    .mjs-nestedSortable-error {
      background: #fbe3e4;
      border-color: transparent;
    }

    ol.sortable {
      max-width: 300px;
      padding-left: 15px;
      padding-right: 15px;
    }
    ol {
      padding-right:0px;
      padding-left:25px;
    }

    ol.sortable,ol.sortable ol {
      list-style-type: none;
    }

    .sortable li div {
      border: 1px solid transparent;
      cursor: default;
      margin: 0;
      padding: 5px;
    }
    .all {
      position: relative;
      border: 1px solid transparent;
      cursor: default;
      max-width: 300px;
      margin: 0 15px;
      padding: 5px;
    }
    .sortable.editable li div {
      cursor: move;
    }
    .sortable li div:hover, .all:hover {
      background-color: bisque;
      border-radius: 3px;
    }

    li.mjs-nestedSortable-collapsed.mjs-nestedSortable-hovering div {
      border-color: #999;
    }

    .disclose {
			width: 10px;
			display: none;
      font: normal normal normal 14px/1 FontAwesome;
      margin-right:4px;
		}

    .editable .disclose {
      cursor: pointer;
    }

    .sortable li.mjs-nestedSortable-collapsed > ol {
      display: none;
    }

    .sortable li.mjs-nestedSortable-branch > div > .disclose {
			display: inline-block;
		}

		.sortable li.mjs-nestedSortable-collapsed > div > .disclose > span:before {
			content: "\f196";
		}

		.sortable li.mjs-nestedSortable-expanded > div > .disclose > span:before {
			content: "\f147";
		}

    .sortable li.mjs-nestedSortable-branch > div > .disclose {
      display: inline-block;
    }

    .sortable span.ui-icon {
      display: inline-block;
      margin: 0;
      padding: 0;
    }

    li.listitem {
      position: relative;
    }
    .treeitem.selected, .all.selected {
      background-color: #b2c5ec;
    }
    .treeitem {
      position: relative;
    }
    .treeitem .delete {
      display:none;
      cursor: pointer;
    }
    .editable .treeitem.show .delete{
      position: absolute;
      right:5px;
      top:3px;
      font-size: 16px;
      font-weight: bold;
      display:inline-block;
    }
    .category-number {
        position: absolute;
        right:5px;
        top:7px;
        display:inline-block;
    }
    .inline-editor {
      position:absolute;
      top:2px;
      left:2px;
    }
    .tools {
      width: 100%;
      background-color: #3c5681;
      padding:0;
    }
    .tools a.tool-btn {
      color: #9dabc1;
    }
    .tools a.tool-btn:hover {
      background-color: #2e415c;
    }
    .new_item, .search {
      padding-left:15px;
      padding-right:15px;
      width:100%;
    }
    .new_item input, .search input {
      width:100%;
    }
    .search {margin-top:10px;}
  </style>

  <div class="tools" if={enableChange}>
    <a href="#" onclick={toggle} class="tool-btn btn btn-xs" style="color:#9dabc1">{edit_text}</a>
    <a href="#" onclick={save} if={editing} class="tool-btn btn btn-xs" style="color:#9dabc1">保存退出</a>
  </div>

  <div class="search" if={!editing}>
    <div class="form-group has-feedback">
      <input type="text" name="search" class="form-control" placeholder="分类搜索" onkeyup={searching}>
        <span class="fa fa-search form-control-feedback" aria-hidden="true"></span>
      </div>
  </div>
  <div class={all:true, selected:!selected} onclick={select_all}>全部
      <!-- <span if={_data.length && !editing} class="label label-info category-number">{_data.length}</span> -->
  </div>
  <ol class={sortable:true, editable:editing}>
    <virtual each={item in data}>
      <li data-is="treeitem" data={item}></li>
    </virtual>
  </ol>
  <div class="new_item" show={editing}>
    <input type="text" name=new_item onkeyup={edit}>
  </div>

  <script>
    var self = this
    this._data = new DataSet(opts.data || [], {parentField:'parent'})
    this._old_data = opts.data
    this.data = this._data.tree()
    this.enableChange = opts.enableChange //是否允许编辑
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

    /*
     * 处理切换
     */
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

    /*
     * 处理返回
     */
    this.save = function() {
      var result = self.serialize()
      self._data.update(result)
      if (opts.onSave){
        opts.onSave(self._data.get({order:['parent', 'order']})).then(function(r){
            self._data.load(r.data)
            self._old_data = self._data.get()
            self.edit_text = '编辑'
            self.editing = false
            self.data = self._data.tree()
            self.update()
        });
      }
      else {
          self._old_data = self._data.get()
          self.edit_text = '编辑'
          self.editing = false
          self.data = self._data.tree()
          self.update()
      }
    }

    this.edit = function(e) {
      if (e.keyCode == 13){ //enter
        self._data.add({name:self.new_item.value, parent:0})
        self.data = self._data.tree()
        self.new_item.value = ''
      } else if (e.keyCode == 27) { //esc
        self.new_item.value = ''
      }
    }

    //处理搜索
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

    //选中处理
    this.select = function(e) {
      if (!self.editing){
        var id = e.item.item.id;
        self.selected = id;
        if (opts.onSelect) {
          opts.onSelect.call(self, self._data.get(id))
        }
      }
    }

    this.select_all = function(e){
      if (!self.editing){
        self.selected = null;
        if (opts.onSelect) {
          opts.onSelect.call(self)
        }
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
          if (v.id == id) { //找到后删除子结点
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
  </script>
</category>

<treeitem id="{id}" class={listitem:true, mjs-nestedSortable-expanded: isFolder(),
    mjs-nestedSortable-branch: isFolder()}>

  <div class={treeitem:true, selected:is_selected(id)} onmouseenter={enter}
    onclick={parents('category').select}
    onmouseleave={leave} ondblclick={edit}>
    <span class="disclose"><span></span></span>{name}
    <span class="delete" onclick={parents('category').remove}>&times;</span>
    <span if={opts.data.number && !parents('category').editing} class="label label-info category-number">{opts.data.number}</span>
  </div>

  <ol if={ isFolder() }>
    <virtual each={ item in nodes }>
      <li data-is="treeitem" data={item}></li>
    </virtual>
  </ol>

  var self = this
  self.id = opts.data.id
  self.name = opts.data.name
  self.nodes = opts.data.nodes
  var parent = this.parents('category')
  self._data = parent._data
  self.data = parent.data
  //this.remove = this.parent.remove

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
        if (e.keyCode == 13){ //enter
          value = input.val()
          self._data.update({id:id, name:value})
          parent.data = self._data.tree()
          input.remove()
          el.css('visibility', 'visible')
          parent.update()
        } else if (e.keyCode == 27) { //esc
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


</treeitem>
