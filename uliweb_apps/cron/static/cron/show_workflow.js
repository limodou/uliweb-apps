/*
  如果 data 是 plain object, 则直接处理为数据
  否则为URL

  options = {
    'data':data,
    'url':url,
    'callback': function(){},
    'onNode':function(node){},
  }
  */
function show_workflow(element_id, options)
{

    var nodes_data = null;
    var workflow = null;
    var _nodes = null;
    var _edges = null;
    var _default_opts = {data:{}, callback:function(){}};
    var opts = $.extend(true, {}, _default_opts, options);


    function get_node(from){
        var item;
        for(var i=0, _len=nodes_data.length; i<_len; i++){
            item = nodes_data[i];
            if (item.id == from){
                return item;
            }
        }
    }


    function load(){
        if (opts.url){
            $.get(opts.url).success(function(r){
                nodes_data = r.tasks;
                draw();
            });
        }else{
            nodes_data = opts.data;
            draw();
        }
    }


    function draw(){
        var v=[], x, y, i, j, node, index,
        _len_i, _len_j, item_x, item_y, e=[],
        //保存结点
        nodes={},
        //结点ID
        ids=[],
        //保存结点关系
        rel={},
        has_edges={};

        //生成node和edge数据
        for(i=0, _len_i=nodes_data.length; i<_len_i; i++){
            item_x = nodes_data[i];
            x = {id:item_x.id,
                label:item_x.label,
                title:item_x.title,
                shape:'box',
                size:50};
            if (item_x.children_count>0){
                x.shape = 'box';
                x.shapeProperties = {borderDashes:[5,5]};
            }
            if (opts.onNode)
                opts.onNode(item_x, x);
            v.push(x);
            nodes[x.id] = x;
            ids.push(x.id)

            //处理依赖结点
            for(j=0, _len_j=item_x.depend_tasks.length; j<_len_j; j++){
                _id = item_x.depend_tasks[j];
                y = {from:item_x.id, to:_id, arrows:'to', label:'依赖'};
                e.push(y);
                has_edges[item_x.id] = true;
            }

            //处理父结点
            if (item_x.parent_task && !has_edges[item_x.id]){
                y = {from:item_x.id, to:item_x.parent_task, arrows:'to',
                    label:'属于'};
                e.push(y);
            }
        }

        //计算结点level值
        for(i=0, _len_i=e.length; i<_len_i; i++){
            var x = e[i];
            if (!nodes[x.to] || !nodes[x.from])
                continue;
            if (rel[x.to]) rel[x.to].push(x.from);
            else rel[x.to] = [x.from];
            index = ids.indexOf(x.from);
            if (index > -1) ids.splice(index, 1);
        }

        function cal_level(s, level){
            var next;
            for(var i=0, _len_i=s.length; i<_len_i; i++){
                nodes[s[i]].level = level;
                next = rel[s[i]];
                if (next)
                    cal_level(next, level+1);
            }
        }

        cal_level(ids, 1);

        _nodes = new vis.DataSet(v);
        _edges = new vis.DataSet(e);

        // create a network
        var container = document.getElementById(element_id);
        var data = {
            nodes: _nodes,
            edges: _edges
        };
        var options = {
            layout: {
                hierarchical: {
                    direction: 'UD'
                }
            }
        }
        workflow = new vis.Network(container, data, options);

        if (opts.callback) opts.callback(workflow);
    };

    load();
}
