
riot.tag2('query-condition', '<div class="query-condition"> <form method="get" action="{opts.action}"> <div each="{row, i in layout}" show="{i==0 || show}" class="{condition-row:true, condition-row-more:i>0}"> <div each="{field in row}" class="condition-cell"> <span class="condition-label">{fields[this.field].label || field}</span> <input-field field="{fields[field]}" data="{data}" type="{fields[this.field].type || \'str\'}"></input-field> </div> <div show="{i==0 && !show}" class="condition-cell"> <button class="btn btn-primary btn-flat" type="submit">查询</button> <button class="btn btn-default btn-flat" type="button" onclick="{parent.reset}">清除条件</button> </div> </div> <div class="condition-row condition-row-more" show="{show}"> <button class="btn btn-primary btn-flat" type="submit">查询</button> <button class="btn btn-default btn-flat" type="button" onclick="{reset}">清除条件</button> </div> <div class="{condition-more:true, visible:layout.length>1}"> <span if="{layout.length > 1}" href="#" onclick="{click}"> {show? \'收起\' : \'更多条件\'} <i class="{fa:true, fa-angle-up:show, fa-angle-down:!show}"></i> </span> </div> </form> </div>', 'query-condition .query-condition,[riot-tag="query-condition"] .query-condition,[data-is="query-condition"] .query-condition{ margin-bottom:5px; background-color: white; padding: 5px; } query-condition .condition-row,[riot-tag="query-condition"] .condition-row,[data-is="query-condition"] .condition-row{ margin-top: 5px; margin-bottom: 5px; padding-top: 5px; } query-condition .condition-row-more,[riot-tag="query-condition"] .condition-row-more,[data-is="query-condition"] .condition-row-more{ border-top: 1px solid #ddd; } query-condition .condition-row:last-child,[riot-tag="query-condition"] .condition-row:last-child,[data-is="query-condition"] .condition-row:last-child{ border-bottom: none; } query-condition .condition-label,[riot-tag="query-condition"] .condition-label,[data-is="query-condition"] .condition-label{ min-width: 80px; margin-left:8px; margin-right:8px; display: inline-block; text-align: right; } query-condition .condition-cell,[riot-tag="query-condition"] .condition-cell,[data-is="query-condition"] .condition-cell{ display: inline-block; } query-condition .condition-more,[riot-tag="query-condition"] .condition-more,[data-is="query-condition"] .condition-more{ text-align: center; margin-top: 5px; margin-bottom: 10px; } query-condition .condition-more.visible,[riot-tag="query-condition"] .condition-more.visible,[data-is="query-condition"] .condition-more.visible{ border-top:1px solid #ddd; } query-condition .condition-more span,[riot-tag="query-condition"] .condition-more span,[data-is="query-condition"] .condition-more span{ border: 1px solid #ddd; border-top: 1px solid white;; margin: 0 auto; padding: 4px 16px; cursor: pointer; font-size: 8px; } query-condition .form-control,[riot-tag="query-condition"] .form-control,[data-is="query-condition"] .form-control{ display:inline-block; width: 200px; min-width: 200px; vertical-align: middle; } query-condition .select2-container--bootstrap,[riot-tag="query-condition"] .select2-container--bootstrap,[data-is="query-condition"] .select2-container--bootstrap{ display: inline-block; } query-condition .select2-container--bootstrap .select2-selection--single .select2-selection__rendered,[riot-tag="query-condition"] .select2-container--bootstrap .select2-selection--single .select2-selection__rendered,[data-is="query-condition"] .select2-container--bootstrap .select2-selection--single .select2-selection__rendered{ padding: 0; } query-condition .select2-container--bootstrap .select2-selection--single,[riot-tag="query-condition"] .select2-container--bootstrap .select2-selection--single,[data-is="query-condition"] .select2-container--bootstrap .select2-selection--single{ line-height: 30px; } query-condition .multiselect-container li input[type="radio"],[riot-tag="query-condition"] .multiselect-container li input[type="radio"],[data-is="query-condition"] .multiselect-container li input[type="radio"]{margin-left:-200px;}', '', function(opts) {
      var self = this
      this.layout = opts.layout
      this.fields = {}

      opts.fields.forEach(function(v){
        self.fields[v['name']] = v
      })
      this.show = false
      this.data = opts.data || {}

      if (!this.layout) {
          this.layout = []
          var s = []
          this.layout.push(s)
          for (k in this.fields) {
              s.push(k);
          }
      }

      this.click = function(e){
        self.show = !self.show
      }

      this.reset = function(e){
        for (k in self.fields) {
          var field = self.fields[k]
          if (field.type == 'select') {

            $('[name='+k+']', self.root)
              .multiselect('deselectAll', false)
              .multiselect('updateButtonText')
          } else
            $('[name='+k+']', self.root).val(null)
        }
      }

});

riot.tag2('input-field', '<input type="text" name="{opts.field.name}" class="form-control" field-type="str" if="{opts.type==\'str\'}" placeholder="{opts.field.placeholder}"> <input type="password" name="{opts.field.name}" class="form-control" field-type="password" if="{opts.type==\'password\'}" placeholder="{opts.field.placeholder}"> <select __multiple="{opts.field.multiple}" if="{opts.type==\'select\'}" field-type="select" style="width:200px" name="{opts.field.name}"> <option if="{opts.field.placeholder && !opts.field.multiple}">{opts.field.placeholder}</option> <option each="{value in opts.field.choices}" value="{value[0]}"> {value[1]} </option> </select> <input type="text" name="{opts.field.name}" class="form-control" field-type="date" if="{opts.type==\'date\'}" placeholder="{opts.field.placeholder}"> <input type="text" name="{opts.field.name}" class="form-control" field-type="datetime" if="{opts.type==\'datetime\'}" placeholder="{opts.field.placeholder}">', '', '', function(opts) {
    var self = this

    this.on('mount', function(){

      if (opts.type == 'select') {
        var _opts = $.extend({}, {
            includeSelectAllOption: true,
            selectAllText: '全部选中',

            buttonClass: 'btn btn-default btn-flat',
            numberDisplayed: 2,
            selectedClass: '',
            nonSelectedText: opts.field.placeholder,
            maxHeight: 200
            }, opts.field.opts || {})
        load('ui.bootstrap.multiselect', function(){
          var el = $('[name='+opts.field.name+']', self.root).multiselect(_opts);
          if (opts.data[opts.field.name])
            el.multiselect('select', opts.data[opts.field.name])
          return
        })
      } else if (opts.type == 'date') {
        var _opts = {format: 'YYYY-MM-DD', showTime:false};
        load('ui.pikaday', function(){
          $('[name='+opts.field.name+']').pikaday(_opts);
        })
      } else if (opts.type == 'datetime') {
        var _opts = {format: 'YYYY-MM-DD hh:mm:ss', showTime:true, use24hour:true}
        load('ui.pikaday', function(){
          $('[name='+opts.field.name+']').pikaday(_opts);
        })
      } else {
      }
      if (opts.data[opts.field.name])
        $('[name='+opts.field.name+']').val(opts.data[opts.field.name])

    })
});
