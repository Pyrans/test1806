from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.cache import caches
from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import View

from .tasts import send_verify_mail
from .models import *
from .my_utils import *

cache = caches['confirm']


def home(req):
    wheels = Wheel.objects.all()
    menus = Nav.objects.all()
    mustbuys = MustBuy.objects.all()
    shops = Shop.objects.all()
    mainshows = MainShow.objects.all()
    result = {
        'title': '首页',
        'wheels': wheels,
        'menus': menus,
        'mustbuys': mustbuys,
        'shop0': shops[0],
        'shop1_3': shops[1: 3],
        'shop3_7': shops[3: 7],
        'shop_last': shops[7:],
        'mainshows': mainshows,
    }
    return render(req, 'home/home.html', result)


def market(req):
    return redirect(reverse('axf:market_params', args=('104749', '0', 0)))


def market_with_params(req, type_id, sub_type_id, order_type):
    # 获取所有的一级分类
    types = FootTypes.objects.all()

    # 获取二级分类数据
    current_cate = types.filter(typeid=type_id)[0]
    childtypenames = current_cate.childtypenames.split('#')
    # sub_types = []
    # for i in childtypenames:
    #     temp = i.split(':')
    #     sub_types.append(i)
    sub_types = [i.split(':') for i in childtypenames]

    # 根据typeid获取商品列表
    goods = Goods.objects.filter(
        categoryid=type_id
    )
    # 根据二级分类的数据查询商品的id
    if sub_type_id == '0':
        pass
    else:
        goods = goods.filter(childcid=int(sub_type_id))

    '''
    0:综合排序
    1:价格排序
    2:销量排序
    '''
    NO_SORT = 0
    PRICE_SORT = 1
    SALES_SORT = 2

    if int(order_type) == 0:
        pass
    elif int(order_type) == 1:
        goods = goods.order_by('price')
    else:
        goods = goods.order_by('productnum')

    # 添加num属性
    # 知道用户的购物车商品对应的数量
    user = req.user
    if isinstance(user, MyUser):
        tmp_dict = {}
        #     去购物车查询该用户的商品数据
        cart_nums = Cart.objects.filter(user=user)
        for i in cart_nums:
            tmp_dict[i.goods.id] = i.num
        for i in goods:
            i.num = tmp_dict.get(i.id) if tmp_dict.get(i.id) else 0

    result = {
        'title': '闪购',
        'types': types,
        'goods': goods,
        'current_type_id': type_id,
        'sub_types': sub_types,
        'current_sub_type_id': sub_type_id,
        'order_type': int(order_type),
    }
    return render(req, 'market/market.html', result)

@login_required(login_url='/axf/login')
def cart(req):
    # 确定用户
    user = req.user
    # 根据用户 去购物车表搜索该用户的数据
    data = Cart.objects.filter(user_id=user.id)

    # 算钱
    sum_money = get_cart_money(data)
    # 判断全选按钮的状态(有购物车商品 并且所有商品全被选中)
    if data.exists() and not data.filter(is_selected=False).exists():
        is_all_select = True
    else:
        is_all_select = False

    result = {
        'title': '购物车',
        'uname': user.username,
        'phone': user.phone if user.phone else '暂无',
        'address': user.address if user.address else '暂无',
        'cart_items': data,
        'sum_money': sum_money,
        'is_all_select': is_all_select
    }
    return render(req, 'cart/cart.html', result)


# @login_required(login_url='/axf/login')
def mine(req):
    btns = MineBtns.objects.filter(is_used=True)
    user = req.user
    is_login = True
    if isinstance(user, AnonymousUser):
        is_login = False

    u_name = user.username if is_login else ''
    icon = 'http://' + req.get_host() + '/static/uploads/' + user.icon.url if is_login else ''
    result = {
        'title': '我的',
        'btns': btns,
        'is_login': is_login,
        'u_name': u_name,
        'icon': icon
    }
    return render(req, 'mine/mine.html', result)


class RegisterAPI(View):

    def get(self, req):
        return render(req, 'user/register.html')

    def post(self, req):
        # 解析参数
        params = req.POST
        icon = req.FILES.get('u_icon')
        name = params.get('u_name')
        pwd = params.get('u_pwd')
        confirm_pwd = params.get('u_confirm_pwd')
        email = params.get('u_email')
        # 校验密码
        if pwd and confirm_pwd and pwd == confirm_pwd and len(pwd) >= 6:
            # 判断用户名是否可用
            if MyUser.objects.filter(username=name).exists():
                return render(req, 'user/register.html', {'help_msg': '该用户已存在'})
            else:
                user = MyUser.objects.create_user(
                    username=name,
                    password=pwd,
                    email=email,
                    icon=icon,
                    is_active=False
                )
                # 生成验证连接
                unique_str = get_unique_str()
                url = 'http://' + req.get_host() + '/axf/confirm/' + unique_str
                # 发送邮件
                send_verify_mail.delay(url, user.id, email, unique_str)
                # 设置缓存， 返回登录页面
                return render(req, 'user/login.html')


class LoginAPI(View):
    def get(self, req):
        return render(req, 'user/login.html')

    def post(self, req):
        # 1 解析参数
        params = req.POST
        name = params.get('name')
        pwd = params.get('pwd')
        print(pwd)
        # 2 校验数据
        if not name or not pwd:
            data = {
                'code': 2,
                'msg': '账号或密码不能为空',
                'data': ''
            }
            return JsonResponse(data)
        # 3 使用用户名 密码校验用户
        user = authenticate(username=name, password=pwd)
        # 4 如果校验成功 登录
        if user:
            login(req, user)
            data = {
                'code': 1,
                'msg': 'ok',
                'data': '/axf/mine'
            }
            return JsonResponse(data)
        # 5 失败则返回错误提示
        else:
            data = {
                'code': 3,
                'msg': '账号或密码错误',
                'data': ''
            }
            return JsonResponse(data)


class LogoutAPI(View):

    def get(self, req):
        logout(req)
        return redirect(reverse('axf:mine'))


def confirm(req, uuid_str):
    # 1 去缓存拿数据
    user_id = cache.get(uuid_str)
    # 找到用户对象，修改is_active对象
    if user_id:
        user = MyUser.objects.get(pk=int(user_id))
        user.is_active = True
        user.save()
        return redirect(reverse('axf:login'))
    # 没拿到则返回操作失败
    else:
        return HttpResponse('<h2>链接已失效</h2>')


def check_uname(req):
    # 解析参数
    u_name = req.GET.get('u_name')
    # 判断数据不能为空白, 然后去搜索用户
    data = {
        'code': 1,
        'data': ''
    }
    if u_name and len(u_name) >= 3:
        if MyUser.objects.filter(username=u_name).exists():
            data['msg'] = '账号已存在'
        else:
            data['msg'] = '√'
    else:
        data['msg'] = '×'

    return JsonResponse(data)


class CartAPI(View):

    def post(self, req):

        # 先看用户是否登录
        user = req.user
        if not isinstance(user, MyUser):
            data = {
                'code': 2,
                'msg': 'not login',
                'data': '/axf/login'
            }
            return JsonResponse(data)

        # 拿参数
        op_type = req.POST.get('type')
        g_id = int(req.POST.get('g_id'))
        # 先获取商品数据
        goods = Goods.objects.get(pk=g_id)
        if op_type == 'add':
            # 添加购物车的操作
            goods_num = 1
            if goods.storenums > 1:
                cart_goods = Cart.objects.filter(
                    user=user,
                    goods=goods
                )
                if cart_goods.exists():
                    #         不是第一次添加
                    cart_item = cart_goods.first()
                    cart_item.num += 1
                    cart_item.save()
                    # 修改返回数量
                    goods_num = cart_item.num
                else:
                    #         是第一次添加
                    Cart.objects.create(
                        user=user,
                        goods=goods
                    )
                data = {
                    'code': 1,
                    'msg': 'ok',
                    'data': goods_num
                }
                return JsonResponse(data)
            else:
                data = {
                    'code': 3,
                    'msg': '库存不足',
                    'data': ''
                }
                return JsonResponse(data)


        elif op_type == 'sub':
            #     先去查询购物车的数据
            cart_item = Cart.objects.get(
                user=user,
                goods=goods
            )
            cart_item.num -= 1
            cart_item.save()
            if cart_item.num == 0:
                #         如果为0，删除商品
                cart_item.delete()
                goods_num = 0
            else:
                goods_num = cart_item.num

            data = {
                'code': 1,
                'msg': 'ok',
                'data': goods_num
            }
            return JsonResponse(data)


class CartStatusAPI(View):

    def patch(self, req):
        params = QueryDict(req.body)
        c_id = int(params.get('c_id'))
        user = req.user
        # 先拿到跟这个人有关系的购物车数据
        cart_items = Cart.objects.filter(user_id=user.id)

        # 拿到用户c_id对应的数据
        cart_data = cart_items.get(id=c_id)

        # 修改状态  取反
        cart_data.is_selected = not cart_data.is_selected
        cart_data.save()

        # 算钱
        sum_money = get_cart_money(cart_items)

        # 判断是否全选
        if cart_items.filter(is_selected=False).exists():
            is_all_select = False
        else:
            is_all_select = True

        # 返回数据
        result = {
            'code': 1,
            'msg': 'ok',
            'data': {
                'is_all_select': is_all_select,
                'sum_money': sum_money,
                'status': cart_data.is_selected
            }
        }
        return JsonResponse(result)


class CartAllStatusAPI(View):

    def put(self, req):
        user = req.user

        # 判断操作
        cart_items = Cart.objects.filter(user_id=user.id)
        is_all_select = True
        if cart_items.exists() and cart_items.filter(is_selected=False):
            # 由于当前属于未全选的状态，将所有未选中的商品状态置反
            # for i in cart_items.filter(is_selected=False):
            #     i.is_selected = True
            #     i.save()
            cart_items.update(is_selected = True)
            # 算钱
            sum_money = get_cart_money(cart_items)
        else:
            cart_items.update(is_selected=False)
            is_all_select = False
            sum_money = 0

        # 返回数据
        result = {
            'code': 1,
            'msg': 'ok',
            'data':{
                'sum_money': sum_money,
                'all_select': is_all_select
            }
        }
        return JsonResponse(result)


class CartItemAPI(View):

    def post(self, req):
        # 用户
        user = req.user
        c_id = int(req.POST.get('c_id'))

        # 确定购物车数据
        cart_item = Cart.objects.get(id=int(c_id))
        # 检查库存
        if cart_item.goods.storenums < 1:
            data = {
                'code': 2,
                'msg': '库存不足',
                'data': ''
            }
            return JsonResponse(data)

        cart_item.num += 1
        cart_item.save()

        cart_items = Cart.objects.filter(
            user_id=user.id, is_selected=True
        )

        sum_money = get_cart_money(cart_items)

        # 返回数据
        data = {
            'code': 1,
            'msg': 'ok',
            'data': {
                'num': cart_item.num,
                'sum_money': sum_money
            }
        }
        return JsonResponse(data)

    def delete(self, req):
        # 用户
        user = req.user

        # 购物车商品
        c_id = QueryDict(req.body).get('c_id')
        cart_item = Cart.objects.get(pk=int(c_id))

        # 减数量
        cart_item.num -= 1
        cart_item.save()

        # 判断是否为0
        if cart_item.num == 0:
            goods_num = 0
            cart_item.delete()
        else:
            goods_num = cart_item.num
        # 算钱
        cart_items = Cart.objects.filter(
            user_id=user.id,
            is_selected=True
        )
        sum_money = get_cart_money(cart_items)
        result = {
            'code': 1,
            'msg': 'ok',
            'data': {
                'num': goods_num,
                'sum_money': sum_money
            }
        }
        return JsonResponse(result)


class OrderAPI(View):
    def get(self, req):
        user = req.user
        # 先获取购物车里的数据
        cart_items = Cart.objects.filter(
            user_id=user.id,
            is_selected=True
        )

        if not cart_items.exists():
            return redirect(reverse('axf:cart'))
        # 创建order
        order = Order.objects.create(
            user=user
        )
        # 循环创建我们的订单数据
        for i in cart_items:
            OrderItem.objects.create(
                order=order,
                goods = i.goods,
                num=i.num,
                buy_money=i.goods.price
            )
        # 算钱
        sum_money = get_cart_money(cart_items)

        # 清空购物车的商品
        cart_items.delete()
        data = {
            'sum_money': sum_money,
            'order': order
        }
        return render(req, 'order/order_detail.html', data)