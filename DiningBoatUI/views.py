#-*-coding:GBK-*-
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connections
import json

def dictfetchall(cursor):
    desc=cursor.description
    return[
        dict(zip([col[0] for col in desc],row))
        for row in cursor.fetchall()
    ]

def login(request):
    if request.method == "POST":
        print("the POST method")
        mode = request.POST.get("mode") #获取模式
        user = request.POST.get("logname") #获取用户名
        pwd = request.POST.get("logpass") #获取密码

        print(user, pwd)
        #用户模式
        if mode=='user_mode':
            user_ifright = user_authenticate(username=user, password=pwd)  # 验证用户名和密码是否一样
            if user_ifright:
                return render(request, 'userMode.html', {'msg': '登录成功!'})
            else:
                return render(request, 'login.html', {'msg': '登录失败!'})
        #商家模式
        elif mode=='store_mode':
            user_ifright = store_authenticate(username=user, password=pwd)  # 验证用户名和密码是否一样
            if user_ifright:
                return render(request, 'storeMode.html', {'msg': '登录成功!'})
            else:
                return render(request, 'login.html', {'msg': '登录失败!'})
    return render(request, "login.html")


#用户账号验证
def user_authenticate(username, password):
    #此处应该用账号密码验证数据库验证中是否存在
    if username=='1234' and password== '1234':
        return True

#商家账号
def store_authenticate(username, password):
    # 此处应该用账号密码验证数据库验证中是否存在
    if username=='1235' and password== '1235':
        return True

def user_mode(request):
    return render(request, "userMode.html")



#用户看商家部分
def user_stores(request):
    #此处sql并显示所有商店，注意所有sql都理应包含对应的实体的ID，如，此sql必须包含SID，一下所有函数也是如此
    content = {}
    stores = [{
        'Sname': '东区食堂',
        'Saddress': '东区',
        'Spopularity': 14
    },
        {
            'Sname': '东区食堂',
            'Saddress': '东区',
            'Spopularity': 14
         }
    ]

    content['stores'] = stores


    if request.method=='GET':
        #此处为按照用户输入的商品名来模糊搜索可能的店铺，sql并显示
        if 'search_stores' in request.GET:
            print('search_stores')
            #注意，此处Sname为用户的输入，不是确定的Sname，需要进行模式匹配模糊搜索
            Sname = request.GET['Sname']
            print(Sname)

            #此处sql出所有可能的店家

            stores=[]
            content['stores'] = stores
            return render(request, "user_stores.html", content)
        elif 'Rank_order' in request.GET:
            #此处为选择排序依据排序店家
            print("Rank_operation")
            Rank_order = request.GET['Rank_order']
            print(Rank_order)

            #此处按照得到的排序依据重新sql所有商家
            #Rank_order值域为Spopularity_down和Saddress_up

            stores = []
            content['stores'] = stores
            return render(request, "user_stores.html", content)
        elif 'Stores_recommendation' in request.GET:
            print('Stores_recommendation')
            #开始推荐

            stores = [{
        'Sname': '东区食堂',
        'Saddress': '东区',
        'Spopularity': 14
    },
        {
            'Sname': '东区食堂',
            'Saddress': '东区',
            'Spopularity': 14
         }
    ]
            content['stores'] = stores
            return render(request, "user_stores.html", content)


    return render(request, "user_stores.html", content)

def user_store_goods(request):
    #主要是对用户购买该商店商品的处理和对进入商家的响应处理
    content={}
    goods = []

    if request.method=='GET':
        print("GET")
        # 从user_stores界面进入到某一个store
        if 'enter_store' in request.GET:
            print('enter_store')
            SID = request.GET['SID']
            print(SID)

            # 此处sql出该店铺所有商品
            # 且显示的商品必须显示是否有富余Gifrest，不能给用户看一个商家有多少剩余量
            # Gifrest为是否富余，值域为['是'.'否’},此外对应的剩余量aount也得包含，详情在对应的html中查看

            goods = [
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '是',
                    'Amount': 4,
                    'GID': 1
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '否',
                    'Amount': 0,
                    'GID': 2
                },
            ]

            content['goods'] = goods

            content['SID'] = SID

            return render(request, "user_store_goods.html", content)
        elif 'choose_goods' in request.GET:
            #格式为request.GET["Buy_amount_" + str(GID)] = 对应的购买量
            #需要遍历该商店所有的商品
            print('choose_goods')
            SID = request.GET['SID']

            #此处使用各商品的购买量对DB进行修改

            #此处重新sql出该商店所有商品，同样显示富余情况if和对应的剩余量

            goods=[
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '是',
                    'Amount': 4,
                    'GID': '1'
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '否',
                    'Amount': 0,
                    'GID': '2'
                },
            ]
            print(request.GET['Buy_amount_1'])
            print(SID)
            content['goods'] = goods
            content['SID']=SID
            return render(request, "user_store_goods.html", content)
    return render(request, "user_store_goods.html", content)

def user_orders(request):

    #此处为sql并显示该用户所有订单
    content = {}
    orders = [
        {
            "OID":2,
            "OSname":"akisou",
            "Oprice":"akisou" ,
            "Otime":"akisou" ,
            "OfinishedTime":"akisou" ,
            "Ostatus":"akisou" ,
            "Oevaluation":3,
            "Ocomment":"akisou"
        },
        {
            "OID":3,
            "OSname": "akisou",
            "Oprice": "akisou",
            "Otime": "akisou",
            "OfinishedTime": "akisou",
            "Ostatus": "akisou",
            "Oevaluation": 3,
            "Ocomment": "akisou"
        }
    ]
    content['orders'] = orders


    if request.method=='GET':
        #取消某一订单，并重新sql出该用户所有订单，显示出来
        if 'cancel_order' in request.GET:
            print('cancel_order')
            OID = request.GET['OID']
            print(OID)
            #此处sql取消该订单，注意并非在数据库删除这一订单，而是修改其状态为‘已取消’

            #此处重新sql该用户所有订单

            orders = []
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #修改某一订单的Oevaluation和Ocomment，并重新sql该用户所有订单，显示出来
        elif 'change_orderInfo' in request.GET:
            print('change_orderInfo')
            OID = request.GET['OID']
            print(OID)
            Oevaluation = request.GET['Oevaluation']
            Ocomment = request.GET['Ocomment']
            print(Oevaluation, Ocomment)
            #此处sql修改两个属性

            #此处重新sql出该用户全部订单
            orders = []
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #根据输入的日期sql输出那一天的订单
        elif 'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #此date为日而非数据库中的datetime
            date = request.GET['order_date']
            print(date)
            #此处用date查找对应订单并输出显示

            orders=[]
            content['orders']=orders
            return render(request, "user_order.html", content)
    return render(request, "user_order.html", content)

def user_order_goods(request):
    #sql并显示对应订单的全部商品,此处应该用不到，写下面if
    content = {}

    goods = [
        '东区食堂', '中区食堂'
    ]
    content['goods'] = goods
    if request.method=='GET':
        # 从"我的订单"转到某一订单的详情，OID为目标订单OID,并sql出该订单中所有商品的对应字段
        if 'order_details' in request.GET:
            print('order_details')
            OID = request.GET['OID']
            print(OID)

            content = {}
            order_goods = [
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Amount': 4,
                    'GID': 1
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Amount': 0,
                    'GID': 2
                },
            ]
            content['order_goods'] = order_goods
            content['OID'] = OID
            return render(request, "user_order_goods.html", content)

    return render(request, "user_order_goods.html", content)

def user_goodsRecommendation(request):
    #此处sql显示用户推荐,包括原来的从商家进去购买商品的商品属性，还有对应的商品的商家名
    content={}
    content['goods'] = [
        {
            'Gname': 'rice',
            'Sname': 'east',
            'Gprice': 2,
            'Gpopularity': 15,
            'Gifrest': '是',
            'Amount': 4,
            'GID': '1'
        },
        {
            'Gname': 'noodles',
            'Sname': 'east',
            'Gprice': 5,
            'Gpopularity': 20,
            'Gifrest': '是',
            'Amount': 3,
            'GID': '2'
        },
    ]

    #此处为用户推荐界面的下单识别和处理，和商户入口的商品下单一样
    if request.method == 'GET':
        if 'choose_goods' in request.GET:
            # 格式为request.GET["Buy_amount_" + str(GID)] = 对应的购买量
            # 需要遍历该商店所有的商品
            print('choose_goods')
            SID = request.GET['SID']

            # 此处使用各商品的购买量对DB进行修改

            # 此处重新sql出所有推荐商品，同样显示富余情况if和对应的剩余量
            goods = [
                {
                    'Gname': 'rice',
                    'Sname': 'east',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '是',
                    'Amount': 4,
                    'GID': '1'
                },
                {
                    'Gname': 'noodles',
                    'Sname': 'east',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '是',
                    'Amount': 3,
                    'GID': '2'
                },
            ]
            print(request.GET['Buy_amount_1'])
            print(SID)
            content['goods'] = goods
            content['SID'] = SID
            return render(request, 'user_goodsRecommendation.html', content)

    return render(request, 'user_goodsRecommendation.html', content)



def user_myInfo(request):
    #sql并显示该用户所有信息
    content={}
    content['Info']={}

    #此为输入的格式示例
    content['Info']={
        'CID':1,
        'Cname':'akisou',
        'Caccount':1234,
        'Cpassword':1234,
        'Caddress':'东七'
    }

    if request.method=='GET':
        if 'change_Cname' in request.GET:
            print('change_Cname')
            Cname = request.GET['Cname']
            print(Cname)
            #此处用该用户的Cname更新数据库

            #此处重新sql该用户所有个人信息

            content['Info']={
                'CID': 1,
                'Cname': Cname,
                'Caccount': 1234,
                'Cpassword': 1234,
                'Caddress': '东七'

            }
            return render(request, "userInfo.html", content)
        elif 'change_Cpassword' in request.GET:
            print('change_Cpassword')
            Cpassword = request.GET['Cpassword']
            print(Cpassword)
            #此处用该用户的Cpassword更新数据库

            #此处重新sql该用户所有个人信息

            content['Info']={
                'CID': 1,
                'Cname': 'akisou',
                'Caccount': 1234,
                'Cpassword': Cpassword,
                'Caddress': '东七'

            }
            return render(request, "userInfo.html", content)
        elif 'change_Caddress' in request.GET:
            print('change_Caddress')
            Caddress = request.GET['Caddress']
            print(Caddress)
            #此处用该用户的Cpassword更新数据库

            #此处重新sql该用户所有个人信息

            content['Info']={
                'CID': 1,
                'Cname': 'akisou',
                'Caccount': 1234,
                'Cpassword': 1234,
                'Caddress': Caddress

            }
            return render(request, "userInfo.html", content)

    return render(request, "userInfo.html", content)







##商家模式



def store_mode(request):
    return render(request, "storeMode.html")


def store_goods(request):
    # uid = request.COOKIES['id']
    # pwd = request.COOKIES['password']
    #
    # try:
    #     conn = pymysql.connect(host='127.0.0.1', user=uid, database='qa', password=pwd)
    # except:
    #     response = HttpResponse()
    #     response.write("<script language='javascript'>alert('无权限访问系统！');this.location='/login';</script>")
    #     return response
    # cursor = conn.cursor()

    # name_search = request.GET['name_search']
    content = {}

    '''
    try:
        uid = 1
        cursor = connections['default'].cursor()
        cursor.execute(
            "select goods.GID, goods.Gname,goods.Gprice,goods.Gpopularity,provide.Amount from goods,provide where goods.GID = provide.GID and provide.SID ="
            + str(uid)
        )
        raw = dictfetchall(cursor)
        #print(raw)

        content['goods'] = raw
        return render(request, 'store_goods.html', content)
    except:
        print("Error:unable to fetch data")
        return
    '''
    uid = 1
    cursor = connections['default'].cursor()
    cursor.execute(
        "select goods.GID, goods.Gname,goods.Gprice,goods.Gpopularity,provide.Amount from goods,provide where goods.GID = provide.GID and provide.SID ="
        + str(uid)
    )
    raw = dictfetchall(cursor)
    # print(raw)

    content['goods'] = raw


    if request.method=='GET':
        #此处为修改该商家商品数据，商品数据是一个商品一个商品修改的
        if 'store_goods_change' in request.GET:
            print('store_goods_change')

            GID = request.GET['GID']
            Gname = request.GET['Gname']
            Gprice = request.GET['Gprice']
            Amount = request.GET['Amount']

            print(GID, Gname, Gprice, Amount)

            #此处为sql更新该商家商品数据

            #重新sql出该商家所有商品，并显示

            goods=[]
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

        #删除商品
        elif 'store_goods_cancel' in request.GET:

            print('store_goods_cancel')

            GID = request.GET['GID']
            print(GID)

            #删除该商品，再sql出商品
            goods = []
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

        #增添商品
        elif 'store_goods_add' in request.GET:
            print('store_goods_add')
            #生成GID，人气默认为0
            Gname = request.GET['Gname']
            Gprice = request.GET['Gprice']
            Amount = request.GET['Amount']

            print(Gname, Gprice, Amount)

            #sql该用户所有商品
            goods = []
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

            #sql添加新商品



    return render(request, 'store_goods.html', content)



def store_orders(request):
    #sql出该商家所有订单
    content = {}
    orders = [
        {
            "Caccount":2,
            "OSname":"akisou",
            "Oprice":"akisou" ,
            "Otime":"akisou" ,
            "OfinishedTime":"已完成" ,
            "Ostatus":"akisou" ,
            'Odestination': 'akisou',
            "Oevaluation":3,
            "Ocomment":"akisou"
        },
        {
            "Caccount":3,
            "OSname": "akisou",
            "Oprice": "akisou",
            "Otime": "akisou",
            "OfinishedTime": "已完成",
            'Odestination': 'akisou',
            "Ostatus": "akisou",
            "Oevaluation": 3,
            "Ocomment": "akisou"
        }
    ]
    content['orders'] = orders
    content['SID'] = 1

    if request.method=='GET':
        #修改状态
        if 'change_order_status' in request.GET:
            print('change_order_status')
            OID = request.GET['OID']
            Ostatus = request.GET['Ostatus']#注意Ostatus为字符串，需要转换为字母

            print(OID, Ostatus)

            #此处sql更新数据库

            #此处再此sql出全部订单
            orders=[]
            content['orders'] = orders
            return render(request, "store_orders.html", content)

        #按照date查询对应的orders
        elif  'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #此date为日而非数据库中的datetime
            date = request.GET['order_date']
            print(date)
            #此处用date查找对应订单并输出显示

            orders=[
                {
                    "Caccount": 2,
                    "OSname": "akisou",
                    "Oprice": "akisou",
                    "Otime": "akisou",
                    "OfinishedTime": "已完成",
                    "Ostatus": "akisou",
                    'Odestination': 'akisou',
                    "Oevaluation": 3,
                    "Ocomment": "akisou"
                },
                {
                    "Caccount": 3,
                    "OSname": "akisou",
                    "Oprice": "akisou",
                    "Otime": "akisou",
                    "OfinishedTime": "已完成",
                    'Odestination': 'akisou',
                    "Ostatus": "akisou",
                    "Oevaluation": 3,
                    "Ocomment": "akisou"
                }
            ]
            content['orders']=orders
            return render(request, "store_orders.html", content)

    return render(request, "store_orders.html", content)


def store_order_goods(request):
    # sql并显示对应订单的全部商品,此处应该用不到，写下面if
    content = {}

    goods = [
        '东区食堂', '中区食堂'
    ]
    content['goods'] = goods
    print('ashi')
    if request.method == 'GET':
        # 从"我的订单"转到某一订单的详情，OID为目标订单OID,并sql出该订单中所有商品的对应字段
        if 'order_details' in request.GET:
            print('order_details')
            OID = request.GET['OID']
            print(OID)

            content = {}
            order_goods = [
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '是',
                    'Amount': 4,
                    'GID': 1
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '否',
                    'Amount': 0,
                    'GID': 2
                },
            ]
            content['order_goods'] = order_goods
            content['OID'] = OID
            return render(request, "store_order_goods.html", content)

    return render(request, "store_order_goods.html", content)




def store_myInfo(request):
    # sql并显示该用户所有信息
    content = {}
    content['Info'] = {}

    # 此为输入的格式示例
    content['Info'] = {
        'SID': 1,
        'Sname': 'akisou',
        'Spassword': 1234,
        'Saddress': '东七',
        'Spopularity': 12
    }

    if request.method == 'GET':
        if 'change_Sname' in request.GET:
            print('change_Sname')
            Sname = request.GET['Sname']
            print(Sname)
            # 此处用该用户的Cname更新数据库

            # 此处重新sql该用户所有个人信息

            content['Info'] = {
                'SID': 1,
                'Sname': Sname,
                'Spassword': 1234,
                'Saddress': '东七',
                'Spopularity': 12

            }
            return render(request, "storeInfo.html", content)
        elif 'change_Spassword' in request.GET:
            print('change_Spassword')
            Spassword = request.GET['Spassword']
            print(Spassword)
            # 此处用该用户的Cpassword更新数据库

            # 此处重新sql该用户所有个人信息

            content['Info'] = {
                'SID': 1,
                'Sname': 'akisou',
                'Spassword': Spassword,
                'Saddress': '东七',
                'Spopularity': 12

            }
            return render(request, "storeInfo.html", content)
        elif 'change_Saddress' in request.GET:
            print('change_Saddress')
            Saddress = request.GET['Saddress']
            print(Saddress)
            # 此处用该用户的Cpassword更新数据库

            # 此处重新sql该用户所有个人信息

            content['Info'] = {
                'SID': 1,
                'Sname': 'akisou',
                'Spassword': 1234,
                'Saddress': Saddress,
                'Spopularity': 12
            }
            return render(request, "storeInfo.html", content)

    return render(request, "storeInfo.html", content)