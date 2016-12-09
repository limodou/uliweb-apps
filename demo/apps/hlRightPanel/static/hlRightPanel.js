/**
 * Created by HoseaLee on 16/12/6.
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['jquery'], factory);
    } else if (typeof exports === 'object') {
        // Node, CommonJS之类的
        module.exports = factory(require('jquery'));
    } else {
        // 浏览器全局变量(root 即 window)
        root.returnExports = factory(root.jQuery);
    }
}(this, function ($) {
    $.extend({
        hlRightPanel: function (_data) {
            //模版
            var uli_global_toolbar = $('' +
                '<div id="uli-global-toolbar">' +
                '   <div class="uli-toolbar-wrap">' +
                '       <div class="uli-toolbar">' +
                '           <div class="uli-toolbar-panels"> </div>' +
                '           <div class="uli-toolbar-tabs"> </div>' +
                '       </div>' +
                '   </div>' +
                '</div>');
            var uli_toolbar_panel = '<div data-name="" class="uli-toolbar-panel" style="visibility:hidden"></div>';
            var uli_toolbar_tab = '<div data-name="" class="uli-toolbar-tab"></div>';
            var uli_toolbar_panel_header = '<h3 class="uli-toolbar-panel-header"></h3>';
            var uli_toolbar_panel_main = '<div class="uli-toolbar-panel-main"></div>';
            var uli_toolbar_panel_footer = '<div class="uli-toolbar-panel-footer"></div>';

            //缓存, "bar_name":{"tab":jqObj, "panel":jqObj}
            var toolbar_cache = {};

            //遍历数据集合,生成tab和panel,放入缓存, 调用绑定事件
            $.each(_data, function (k, v) {
                add(v);
            });
            //遍历缓存, 添加到主模版
//                $.each(toolbar_cache, function (k, v) {
//                    $("div.uli-toolbar-panels", uli_global_toolbar).append(toolbar_cache[k]['panel']);
//                    $("div.uli-toolbar-tabs", uli_global_toolbar).append(toolbar_cache[k]['tab']);
//                });

            //主模版添加到视图中
            $("body").append(uli_global_toolbar);

            //添加一个toolbar
            function add(v){
                var tab = $(uli_toolbar_tab).attr("data-name", v.name).attr("data-type", v.type);
                var panel = null;
                if (v.type == "bar") {
                    $(tab).append('<i class="tab-icon"></i><em class="tab-text"></em>');
                    $("i.tab-icon", tab).addClass(v.labelIcon);
                    $("em.tab-text", tab).html(v.label);
                    panel = $(uli_toolbar_panel).attr("data-name", v.name).html(v.content);
                    panel.append(uli_toolbar_panel_main);
                    $(".uli-toolbar-panel-main", panel).css("height", "100%");
                    if (v.header) {
                        panel.append(uli_toolbar_panel_header);
                        $(".uli-toolbar-panel-header", panel).append(v.header);
                    }
                    if (v.footer) {
                        panel.append(uli_toolbar_panel_footer);
                        $(".uli-toolbar-panel-footer", panel).append(v.footer);
                        $(".uli-toolbar-panel-main", panel).css("margin-bottom", $(".uli-toolbar-panel-footer", panel).height());
                    }
                    if (v.content_type == "iframe") {
                        //第二次修改,使用下文的template作模版处理, iframe暂时不用,但是不删除该功能
                        tab.attr("data-content-type", v.content_type);
                        panel.attr("data-iframe", v.src)
                    }
                    if (v.template && /#((?:[\w\u00c0-\uFFFF-]|\\.)+)/.test(v.template)) {
                        //v.template是元素的ID选择器
                        var template = "";
                        if ($(v.template)[0].tagName == "SCRIPT") {
                            template = $($(v.template).html());
                        } else {
                            template = $(v.template);
                        }
                        $(".uli-toolbar-panel-main", panel).append(template);
                    } else if (v.template && (typeof v.template == 'function')) {
                        //v.template不是ID选择器,而是function
                        var returnValue = v.template();
                        $(".uli-toolbar-panel-main", panel).append($(returnValue));
                    } else if (v.template && (typeof v.template == 'string')) {
                        //v.template不是ID选择器, 不是function, 而是字符串
                        $(".uli-toolbar-panel-main", panel).append($(v.template));
                    }
                    if (typeof v.template == 'undefined') {
                        //未定义template, 这里开始检查ajax
                        if (v.ajax && typeof v.ajax == "string") {
                            $.get(v.ajax).success(function (_r) {
                                $(".uli-toolbar-panel-main", panel).append($(_r));
                            });
                        } else if (v.ajax && typeof v.ajax == "object") {
                            var opts = {
                                url: "",
                                method: "POST",
                                dataType: "json",
                                data: {}
                            };
                            opts = $.extend({}, opts, v.ajax);
                            $.ajax($.extend({}, opts, {
                                success: function (_r) {
                                    var _result = {data: _r, panel: panel, tab: tab};
                                    if (v.ajax.success) {
                                        v.ajax.success(_result);
                                    } else {
                                        $(".uli-toolbar-panel-main", panel).append($(_r.content));
                                    }
                                },
                                complete: function () {

                                }
                            }))
                        }
                    }
                } else if (v.type == "link") {
                    var el = $('<a><i class="tab-icon"></i><em class="tab-text"></em></a>');
                    tab.append(el);
                    if (v.target) {
                        $("a", tab).attr("target", v.target);
                    }
                    if (v.href) {
                        $("a", tab).attr("href", v.href);
                    } else {
                        $("a", tab).attr("href", "#")
                    }
                    $("i.tab-icon", tab).addClass(v.labelIcon);
                    $("em.tab-text", tab).html(v.label);
                }
                processTabPanel(tab, panel);
                toolbar_cache[v.name] = {
                    panel: panel,
                    tab: tab
                };
                $("div.uli-toolbar-panels", uli_global_toolbar).append(panel);
                $("div.uli-toolbar-tabs", uli_global_toolbar).append(tab);
            }

            //取得一个toolbar(tab,panel)
            function get(name){
                return toolbar_cache[name]
            }

            //删除一个toolbar(tab,panel)
            function del(name){
                var toolbar = get(name);
                var toolbar_copy = $.extend(true, {}, toolbar);
                $(toolbar.panel).remove();
                $(toolbar.tab).remove();
                delete toolbar_cache[name];
                return toolbar_copy;
            }

            //tab & panel的事件响应和对应关系的绑定
            function processTabPanel(_tab, _panel) {

                //鼠标悬停和移除事件
                _tab.hover(function () {
                    $(this).addClass("uli-toolbar-tab-hover");
                }, function () {
                    $(this).removeClass("uli-toolbar-tab-hover");
                });
                //tab点击
                _tab.on("click", function () {
                    if (_tab.attr("data-type") == "bar") {
                        if (!ifShowPanels()) {
                            //panels未打开
                            if (_tab.hasClass("uli-toolbar-tab-selected")) {
                                _tab.removeClass("uli-toolbar-tab-selected");
                                showPanel();
                                hidePanels();
                            } else {
                                showPanels();
                                showPanel(_tab.attr("data-name"));
                            }
                        } else {
                            //panels已打开
                            if (_tab.hasClass("uli-toolbar-tab-selected")) {
                                //当前点击的tab是selected(打开的tab)_tab.removeClass("uli-toolbar-tab-selected");
                                showPanel();
                                hidePanels();
                            } else {
                                //当前点击的tab不是selected(未打开的tab),切换panel
                                showPanel(_tab.attr("data-name"));
                            }
                        }

                        //panel内容加载

                    } else if (_tab.attr("data-type") == "link") {
                        return true;
                    }

                });
            }

            //检查panels是否显示
            function ifShowPanels() {
                return $("div.uli-toolbar-wrap", uli_global_toolbar).hasClass("uli-toolbar-open");
            }

            //显示panels
            function showPanels() {
                $("div.uli-toolbar-wrap", uli_global_toolbar).addClass("uli-toolbar-open");
            }

            //隐藏panels
            function hidePanels() {
                $("div.uli-toolbar-wrap", uli_global_toolbar).removeClass("uli-toolbar-open");
            }

            //显示panel
            function showPanel(name) {
                $.each(toolbar_cache, function (k, v) {
                    if ($(v.tab).hasClass("uli-toolbar-tab-selected")) {
                        v.tab.removeClass("uli-toolbar-tab-selected");
                        v.panel.removeClass("toolbar-animate-in").addClass("toolbar-animate-out").css("visibility", "hidden");
                        return false;
                    }
                });
                if (name != '' && name != undefined) {
                    toolbar_cache[name].tab.addClass("uli-toolbar-tab-selected");
                    toolbar_cache[name].panel.removeClass("toolbar-animate-out").addClass("toolbar-animate-in").css("visibility", "visible");
                    panelLoaded(name);
                }
            }

            //组装加载panel内容
            function panelLoaded(name) {
                var toolbar_dom = toolbar_cache[name];
                if (!toolbar_dom['panel'].data("iframeLoaded") && toolbar_dom['tab'].data("contentType") == "iframe") {
                    $(".uli-toolbar-panel-main", toolbar_dom['panel']).append('<iframe class="uli-toolbar-panel-iframe" src="' + toolbar_dom['panel'].data("iframe") + '"></iframe>');
                    toolbar_dom['panel'].data('iframeLoaded', true)
                }
            }

            return {
                add:add,
                get:get,
                del:del
            }
        }
    });
}));