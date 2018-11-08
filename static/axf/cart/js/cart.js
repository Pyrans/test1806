$(function () {
    $('.confirm').click(function () {
        $current_bt = $(this);
        // 知道点击的是那个数据
        var c_id = $(this).parents('li').attr('c_id');
        //    发送请求
        $.ajax({
            url: '/axf/cart_status',
            data: {
                c_id: c_id
            },
            method: 'patch',
            success: function (res) {
                // console.log(res);
                if (res.code == 1) {
                    //    修改当前按钮的对勾
                    if (res.data.status) {
                        $current_bt.find('span').find('span').html('√');
                    } else {
                        $current_bt.find('span').find('span').html('');
                    }
                    //    修改钱数
                    $('#money_id').html(res.data.sum_money);
                    //    修改我们全选按钮
                    if (res.data.is_all_select) {
                        $('.all_select').find('span').find('span').html('√');
                    } else {
                        $('.all_select').find('span').find('span').html('');
                    }

                }
            }
        })
    });

    $('.all_select').click(function () {
        $.ajax({
            url: '/axf/cart_all_status',
            data: {},
            method: 'put',
            success: function (res) {
                if (res.code == 1) {
                    // 修改总价
                    $('#money_id').html(res.data.sum_money);
                    if (res.data.all_select) {
                        $('.all_select>span>span').html('√');
                        // 循环修改商品状态
                        $('.confirm').each(function () {
                            $(this).find('span').find('span').html('√');
                        });
                    } else {
                        $('.all_select>span>span').html('');
                        $('.confirm').each(function () {
                            $(this).find('span').find('span').html('');
                        });
                    }
                }
            }
        })
    });

    $('.addBtn').click(function () {
        // 确定数据id
        var $current_btn = $(this);
        var c_id = $current_btn.parents('li').attr('c_id');
        // 发送请求
        $.ajax({
            url: '/axf/cart_item',
            data: {
                c_id: c_id
            },
            method: 'post',
            success: function (res) {
                if (res.code == 1) {
                    // console.log(res)
                    // 更新总价
                    $('#money_id').html(res.data.sum_money);

                    //    更新显示的数量
                    $current_btn.prev().html(res.data.num);
                } else {
                    alert(res.msg)
                }
            }
        })
    });

    $('.subBtn').click(function () {
        var $current_btn = $(this);
        //    获取购物车数据
        var c_id = $current_btn.parents('li').attr('c_id');

        $.ajax({
            url: '/axf/cart_item',
            data:{
                c_id: c_id
            },
            method: 'delete',
            success: function (res) {
                // console.log(res)
                if(res.code==1){
                    //更新商品数量
                    if(res.data.num==0){
                        $current_btn.parents('li').remove();
                    }else{
                        $current_btn.next().html(res.data.num);
                    }
                //    更新总价
                    $('#money_id').html(res.data.sum_money);
                }else{
                    alert(res.msg);
                }
            }
        })
    });

    $('#order').click(function () {
        var money = $('#money_id').html();
        if(money=='0'){
            alert('请选择商品');
        }else{
            window.open('/axf/order', target='_self');
        }
    });
})