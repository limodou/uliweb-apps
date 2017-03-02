riot.tag2('card', '<div class="card col-sm-3 col-xs-12"> <div class="row"> <div class="col-xs-4 col-sm-12"> <span class="card-icon"><i class="fa fa-{opts.card.icon}"></i></span> </div> <div class="col-xs-8 col-sm-12"> <h4 class="card-title">{opts.card.title}</h4> <p>{opts.card.desc}</p> </div> </div> </div>', '', '', function(opts) {
});

riot.tag2('cards', '<div class="row"> <card each="{opts.cards}" card="{this}"></card> </div>', 'cards .card,[data-is="cards"] .card{text-align:center;} cards .card .card-icon,[data-is="cards"] .card .card-icon{font-size:400%;}', '', function(opts) {
});

riot.tag2('footer-cards', '<footer-card each="{opts.cards}" items="{this}" size="{12/parent.opts.cards.length}"></footer-card>', '', '', function(opts) {
});

riot.tag2('footer-card', '<div class="col-sm-{opts.size}"> <ul> <li each="{item, i in opts.items}" class="{heading: i == 0}"> <a href="{item[0]}" if="{i>0}">{item[1]}</a> <span if="{i == 0}">{item[1]}</span> </li> </ul> </div>', '', '', function(opts) {

  this.on('mount', function(){
    console.log('aaaaa', opts)
  });
});

riot.tag2('custom-menu', '<ul class="nav navbar-nav" if="{opts.messages}"> <li class="{m.class}" each="{m in opts.messages}"> <a href="{m.url}"> <i class="fa fa-{m.icon}"></i> <span class="label label-{m.type}" if="{m.count}">{m.count}</span> </a> </li> <li class="dropdown user user-menu" if="{opts.user}" data-is="user-info" user="{opts.user}"></li> </ul> <ul class="nav navbar-nav" if="{!opts.user}"> <li> <a href="/login" class="btn-menubar">登录</a> </li> <li if="{opts.enable_register}"> <a href="/register" class="btn btn-default btn-ghost-light btn-menubar">注册</a> </li> </ul>', 'custom-menu .user-menu .dropdown-menu,[data-is="custom-menu"] .user-menu .dropdown-menu{ position: absolute; right: 0; left: auto; }', '', function(opts) {
});

riot.tag2('user-info', '<a href="#" class="dropdown-toggle" data-toggle="dropdown"> <img riot-src="{opts.user.image_url}" class="user-image" alt="User Image"> <span class="hidden-xs">{opts.user.name}</span> </a> <ul class="dropdown-menu"> <li class="user-header bg-light-blue"> <img riot-src="{opts.user.image_url}" class="img-circle" alt="avatar"> <p> <span>{opts.user.name}</span> <small if="{opts.user.email}">{opts.user.email}</small> </p> </li> <li class="user-footer"> <div class="pull-left"> <a href="{opts.user.url}" class="btn btn-default btn-flat">访问</a> </div> <div class="pull-right"> <a href="/logout" class="btn btn-default btn-flat">注销</a> </div> </li> </ul>', '', '', function(opts) {
});