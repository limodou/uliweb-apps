<card>
  <div class="card col-sm-3 col-xs-12">
    <div class="row">
      <div class="col-xs-4 col-sm-12">
        <span class="card-icon"><i class="fa fa-{ opts.card.icon }"></i></span>
      </div>
      <div class="col-xs-8 col-sm-12">
        <h4 class="card-title">{ opts.card.title }</h4>
        <p>{ opts.card.desc }</p>
      </div>
    </div>
  </div>
</card>

<cards>
  <style>
    .card {text-align:center;}
    .card .card-icon {font-size:400%;}
  </style>

  <div class="row">
    <card each={ opts.cards } card={ this }></card>
  </div>
</cards>

<footer-cards>
    <footer-card each={ opts.cards } items={ this } size={ 12/parent.opts.cards.length }></footer-card>
</footer-cards>

<footer-card>
  <div class="col-sm-{ opts.size }">
      <ul>
        <li each={ i, item in opts.items } class="{ heading: i == 0 }">
            <a href="{ item[0] }" if={ i>0 }>{ item[1] }</a>
            <span if={ i == 0 }>{ item[1] }</span>
        </li>
      </ul>
  </div>
</footer-card>

<custom-menu>
<ul class="nav navbar-nav">
  <li class="{ m.class }" each="m in messages">
    <a href="{ m.url }">
        <i class="fa fa-{ m.icon }"></i>
        <span class="label label-{ m.type }" if={ m.count }>{ m.count }</span>
    </a>
  </li>

<!-- User Account: style can be found in dropdown.less -->
<li class="user user-menu">
  <a href="{ opts.user_url }">
    <img src="{ opts.user_image_url }" class="user-image" alt="User Image">
    <span class="hidden-xs">{ opts.user_name }</span>
  </a>
</li>
</ul>
</custom-menu>