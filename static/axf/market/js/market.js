var cate_tag = true;
var sort_tag = true;
$(function () {
//    给全部类型加点击事件
    $('#all_cate').click(cate_toggle);
    $('#cates').click(cate_toggle);

//    排序
    $('#all_sort').click(sort_toggle);
    $('#sorts').click(sort_toggle);

//    加操作
    $('.addShopping').click(function () {
        $current_bt = $(this);
        //    获取点击的商品的id
        var g_id = $current_bt.attr('g_id');
        // console.log(g_id);

        $.ajax({
            url: '/axf/cart_api',
            data: {
                g_id: g_id,
                type: 'add'
            },
            method: 'post',
            success: function (res) {
                // console.log(res);
                if (res.code == 1) {
                    $current_bt.prev().html(res.data);
                }
                if (res.code == 2) {
                    //    跳转到登录
                    window.open(res.data, target = '_self')
                }
            }
        })
    });

    //    减操作
    $('.subShopping').click(function () {
        $current_bt = $(this);
        //    获取点击的商品的id
        var g_id = $current_bt.attr('g_id');
        // console.log(g_id);

        if ($current_bt.next().html() == '0') {
            return;
        }

        $.ajax({
            url: '/axf/cart_api',
            data: {
                g_id: g_id,
                type: 'sub'
            },
            method: 'post',
            success: function (res) {
                // console.log(res);
                if (res.code == 1) {
                    $current_bt.next().html(res.data);
                }
                if (res.code == 2) {
                    //    跳转到登录
                    window.open(res.data, target = '_self')
                }
            }
        })
    })
});

function cate_toggle() {
    $('#cates').toggle();
    if (cate_tag) {
        $('#all_cate').find('span').removeClass().addClass('glyphicon glyphicon-chevron-up');
        cate_tag = false;
    } else {
        $('#all_cate').find('span').removeClass().addClass('glyphicon glyphicon-chevron-down');
        cate_tag = true;
    }
}

function sort_toggle() {
    $('#sorts').toggle();
    if (sort_tag) {
        $('#all_sort').find('span').removeClass().addClass('glyphicon glyphicon-chevron-up');
        sort_tag = false;
    } else {
        $('#all_sort').find('span').removeClass().addClass('glyphicon glyphicon-chevron-down');
        sort_tag = true;
    }
}
