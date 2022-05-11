#-*-coding:GBK-*-
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connections
import pymysql
import time
import json
from decimal import *
from datetime import datetime

def connect():
    try:
        conn = pymysql.connect(host='127.0.0.1',
                               user='boat',
                               database='DiningBoat',
                               password='dining')
        return conn
    except:
        return None

def dictfetchall(cursor):
    desc=cursor.description
    return[
        dict(zip([col[0] for col in desc],row))
        for row in cursor.fetchall()
    ]

def conn_query(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return dictfetchall(cursor)
    except:
        return []

def query(sql):
    # print(sql)
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        raw = dictfetchall(cursor)
        return raw
    except:
        return []

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        print("the POST method")
        mode = request.POST.get("mode") #获取模式
        user = request.POST.get("logname") #获取用户名
        pwd = request.POST.get("logpass") #获取密码

        content = {}
        content['Name'] = user
        #用户模式
        if mode=='user_mode':
            user_ifright = user_authenticate(request, username=user, password=pwd)  # 验证用户名和密码是否一样
            if user_ifright:
                return render(request, 'userMode.html', content)
            else:
                return render(request, 'login.html', {'msg': '登录失败!'})
        #商家模式
        elif mode=='store_mode':
            store_id = store_authenticate(request, username=user, password=pwd)  # 验证用户名和密码是否一样
            if store_id > 0:
                return render(request, 'storeMode.html', content)
            else:
                return render(request, 'login.html', {'msg': '登录失败!'})


#用户账号验证
def user_authenticate(request, username, password):
    #此处应该用账号密码验证数据库验证中是否存在
    conn = connect()
    user_pass = conn_query(
        conn,
        'select Cpassword, CID from customer where Caccount=\'%s\'' % username)
    print(user_pass)
    if user_pass == [] or user_pass[0]['Cpassword'] != password:
        # conn.close()
        return False
    else:
        request.session['CID'] = user_pass[0]['CID']
        request.session['pwd'] = password
        request.session['name'] = username
        conn.close()
        return True

#商家账号
def store_authenticate(request,username, password):
    # 此处应该用账号密码验证数据库验证中是否存在
    if username == '1235' and password == '1235':
        return True
    conn = connect()
    user_pass = conn_query(
        conn,
        'select Spassword, SID from store where Sname=\'%s\'' % username)
    print(user_pass)
    if user_pass == [] or user_pass[0]['Spassword'] != password:
        # conn.close()
        return False
    else:
        request.session['id'] = user_pass[0]['SID']
        request.session['pwd'] = password
        request.session['name'] = username
        conn.close()
        return True

def user_mode(request):
    return render(request, "userMode.html")


#用户看商家部分
def user_stores(request):
    #此处sql并显示所有商店，注意所有sql都理应包含对应的实体的ID，如，此sql必须包含SID，一下所有函数也是如此
    pwd = request.session['pwd']
    user = request.session['name']
    cid = request.session['CID']

    conn = connect()
    stores = conn_query(
        conn,
        'select Sname, Saddress, Spopularity, SID from store order by Spopularity desc'
    )
    content = {}
    content['Name'] = user
    content['stores'] = stores
    conn.close()
    if request.method == 'GET':
        #此处为按照用户输入的商品名来模糊搜索可能的店铺，sql并显示
        if 'search_stores' in request.GET:
            print('search_stores')
            #注意，此处Sname为用户的输入，不是确定的Sname，需要进行模式匹配模糊搜索
            Sname = request.GET['Sname']
            stores = query(
                'select Sname, Saddress, Spopularity, SID from store where Sname like \'%s\' order by Spopularity desc'
                % ('%' + '%'.join(list(Sname)) + '%'))
            #此处sql出所有可能的店家
            content['stores'] = stores

        elif 'Rank_order' in request.GET:
            # 此处为选择排序依据排序店家
            print("Rank_operation")
            Rank_order = request.GET['Rank_order']
            print(Rank_order)
            conn = connect()
            # 此处按照得到的排序依据重新sql所有商家
            # Rank_order值域为Spopularity_down和Saddress_up
            if Rank_order == "Spopularity_down":
                print("OK")
                stores = conn_query(
                    conn,
                    'select Sname, Saddress, Spopularity, SID from store order by Spopularity desc'
                )
            elif Rank_order == "Saddress_up":
                raw = conn_query(conn, "select Caddr_longitude, Caddr_latitude from customer where cid = '%d'" %(cid))
                Clongitude = float(raw[0]['Caddr_longitude'])
                Clatitude = float(raw[0]['Caddr_latitude'])

                stores = conn_query(conn, "select Sname, Saddress, Spopularity, SID,(POWER(Saddr_latitude-'%f',2) + POWER(Saddr_longitude-'%f',2)) as distance "
                                          "from store "
                                          "order by distance "%(Clatitude,Clongitude))

            content['stores'] = stores
        elif 'Stores_recommendation' in request.GET:
            print('Stores_recommendation')
            # 开始推荐
            conn = connect()
            cursor = conn.cursor()
            try:
                cursor.execute("select store.Sname,store.Saddress,store.SID,store.Spopularity,Skind,ifnull((sum(Oevaluation)/count(*)),3) as evasum,count(*) as num "
                               "from own,store,diningorder "
                               "where cid = '%d' and store.sid = own.sid and own.oid = diningorder.oid "
                               "GROUP BY store.sid "
                               "order by evasum desc limit 5" % (cid))
                stores_list1 = dictfetchall(cursor)

                if len(stores_list1) == 0:
                    cursor.execute("select Sname, Saddress, Spopularity, SID from store order by Spopularity desc")
                    content['store'] = dictfetchall(cursor)
                    return render(request, "user_stores.html", content)

                kind_score = {}
                for store in stores_list1:
                        kind_score[store['Skind']] = 0
                        store['score'] = 0

                for store in stores_list1: # 喜欢这种店但是不一定喜欢这家店
                        kind_score[store['Skind']] += store['num']
                        store['score'] += float((store['evasum'] - 3))


                for store in stores_list1:
                    if store['score'] < 0:
                        stores_list1.remove(store)

                for kind, score in kind_score.items():
                    # 寻找种类为kind的score个商店
                    cursor.execute("select Sname, Saddress, Spopularity, SID,Skind from store where skind = '%s' order by Spopularity desc limit 3" %(str(kind)))
                    stores_list2 = dictfetchall(cursor)
                    # print(stores_list2)
                    for store in stores_list2:
                        store['score'] = score * (store['Spopularity'] / 100)

                    for store in stores_list2:
                        for previous_store in stores_list1:
                            if store['SID'] == previous_store['SID']:
                                previous_store['score'] += store['score']
                                stores_list2.remove(store)

                    stores_list1.extend(stores_list2)

                sorted_stores_list = sorted(stores_list1, key=lambda x: (x['score'], x['Spopularity']), reverse=True)
                print(sorted_stores_list)
                content['stores'] = sorted_stores_list
            except:
                response = HttpResponse()
                response.write("<script language='javascript'>alert('获取商户推荐失败！');"
                               "this.location='/Diningboat/login';</script>")
                return response

    return render(request, "user_stores.html", content)


def user_store_goods(request):
    #主要是对用户购买该商店商品的处理和对进入商家的响应处理
    pwd = request.session['pwd']
    user = request.session['name']

    content = {}
    content['Name'] = user
    CID = request.session['CID']
    print('cid: %s' % CID)

    if request.method == 'GET':
        print("GET")
        # 从user_stores界面进入到某一个store
        if 'enter_store' in request.GET:
            print('enter_store')
            SID = request.GET['SID']
            print('sid: %s' % SID)

            # 此处sql出该店铺所有商品
            # 且显示的商品必须显示是否有富余Gifrest，不能给用户看一个商家有多少剩余量
            # Gifrest为是否富余，值域为['是'.'否’},此外对应的剩余量aount也得包含，详情在对应的html中查看
            goods = query(
                'select Gname, Gprice, Gpopularity, if (Amount > 0, \'是\', \'否\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                % SID)

            content['goods'] = goods

            content['SID'] = SID

            return render(request, "user_store_goods.html", content)
        elif 'choose_goods' in request.GET:
            # 格式为request.GET["Buy_amount_" + str(GID)] = 对应的购买量
            # 需要遍历该商店所有的商品
            print('choose_goods')
            SID = request.GET['SID']

            conn = connect()

            try:
                goods = conn_query(
                    conn,
                    'select Gname, Gprice, Gpopularity, if (Amount > 0, \'是\', \'否\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                    % SID)

                user = conn_query(
                    conn,
                    'select Caddress, Caddr_longitude, Caddr_latitude from customer where CID=%s'
                    % CID)[0]
                # 创建订单
                conn_query(
                    conn,
                    'insert into diningorder(Oprice, Ostatus, Odestination, Otime, Odestin_longitude, Odestin_latitude) values (%s, \'%s\', \'%s\', \'%s\', %s, %s)'
                    % ('0', 'P', user['Caddress'], str(datetime.now()),
                       user['Caddr_longitude'], user['Caddr_latitude']))

                oid = conn_query(conn,
                                 'select LAST_INSERT_ID() AS OID')[0]['OID']
                # 关联用户、商家、订单
                conn_query(
                    conn,
                    'insert into own values(%s, %s, %s)' % (SID, oid, CID))

                Oprice = Decimal(0)

                for item in goods:
                    Amount = request.GET['Buy_amount_' + str(item['GID'])]
                    if Amount != '0':
                        #此处使用各商品的购买量对DB进行修改
                        Oprice += (item['Gprice'] * Decimal(Amount))
                        # update include
                        conn_query(
                            conn, 'insert into include values(%s, %s, %s)' %
                            (item['GID'], oid, Amount))
                        # update provide
                        conn_query(
                            conn,
                            'update provide set Amount=Amount-%s where provide.GID=%s and provide.SID=%s'
                            % (Amount, item['GID'], SID))
                # 修改价格
                conn_query(
                    conn, 'update diningorder set Oprice=%s where OID=%s' %
                    (str(Oprice), oid))

                conn.commit()
            except:
                conn.rollback()

            conn.close()

            #此处重新sql出该商店所有商品，同样显示富余情况if和对应的剩余量
            goods = query(
                'select Gname, Gprice, Gpopularity, if (Amount > 0, \'是\', \'否\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                % SID)

            content['goods'] = goods
            content['SID'] = SID
            return render(request, "user_store_goods.html", content)
    return render(request, "user_store_goods.html", content)


def user_orders(request):
    #此处为sql并显示该用户所有订单
    pwd = request.session['pwd']
    user = request.session['name']

    content = {}
    content['Name'] = user
    CID = request.session['CID']
    print('cid: %s' % CID)
    orders = query(
        'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID'
        % CID)
    content['orders'] = orders

    if request.method == 'GET':
        #取消某一订单，并重新sql出该用户所有订单，显示出来
        if 'cancel_order' in request.GET:
            print('cancel_order')
            OID = request.GET['OID']
            print('oid: %s' % OID)
            #此处sql取消该订单，注意并非在数据库删除这一订单，而是修改其状态为‘已取消’
            query('update diningorder set Ostatus=\'C\' where OID=%s' % OID)
            #此处重新sql该用户所有订单
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID'
                % CID)
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
            print(
                'update diningorder set Oevaluation=\'%s\', Ocomment=\'%s\' where OID=%s'
                % (Oevaluation, Ocomment, OID))
            query(
                'update diningorder set Oevaluation=\'%s\', Ocomment=\'%s\' where OID=%s'
                % (Oevaluation, Ocomment, OID))
            #此处重新sql出该用户全部订单
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID'
                % CID)
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #根据输入的日期sql输出那一天的订单
        elif 'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #此date为日而非数据库中的datetime
            date = request.GET['order_date']
            print(date)
            #此处用date查找对应订单并输出显示
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID and date(Otime)=\'%s\''
                % (CID, date))
            content['orders'] = orders
            return render(request, "user_order.html", content)
    return render(request, "user_order.html", content)


def user_order_goods(request):
    #sql并显示对应订单的全部商品,此处应该用不到，写下面if
    pwd = request.session['pwd']
    user = request.session['name']
    content = {}
    content['Name'] = user
    if request.method == 'GET':
        # 从"我的订单"转到某一订单的详情，OID为目标订单OID,并sql出该订单中所有商品的对应字段
        if 'order_details' in request.GET:
            print('order_details')
            OID = request.GET['OID']
            print(OID)

            content = {}
            order_goods = query(
                'select Gname, Gprice, Gpopularity, Amount, goods.GID from goods, include where include.GID=goods.GID and include.OID=%s'
                % OID)
            content['order_goods'] = order_goods
            content['OID'] = OID
            return render(request, "user_order_goods.html", content)

    return render(request, "user_order_goods.html", content)


def user_myInfo(request):
    #sql并显示该用户所有信息
    pwd = request.session['pwd']
    user = request.session['name']
    content = {}
    content['Name'] = user
    # content['Info'] = {}
    CID = request.session['CID']
    print('cid: %s' % CID)
    #此为输入的格式示例
    content['Info'] = query(
        'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
        % CID)[0]
    print(content['Info'])

    if request.method == 'GET':
        if 'change_Cname' in request.GET:
            print('change_Cname')
            Cname = request.GET['Cname']
            print(Cname)

            #此处用该用户的Cname更新数据库
            query('update customer set Cname=\'%s\' where CID=%s' %
                  (Cname, CID))

            #此处重新sql该用户所有个人信息
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)
        elif 'change_Cpassword' in request.GET:
            print('change_Cpassword')
            Cpassword = request.GET['Cpassword']
            print(Cpassword)
            #此处用该用户的Cpassword更新数据库
            query('update customer set Cpassword=\'%s\' where CID=%s' %
                  (Cpassword, CID))

            #此处重新sql该用户所有个人信息
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)
        elif 'change_Caddress' in request.GET:
            print('change_Caddress')
            Caddress = request.GET['Caddress']
            print(Caddress)

            #此处用该用户的Cpassword更新数据库
            query('update customer set Caddress=\'%s\' where CID=%s' %
                  (Caddress, CID))

            #此处重新sql该用户所有个人信息
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)

    return render(request, "userInfo.html", content)

##商家模式
def store_mode(request):
    return render(request, "storeMode.html")

def store_goods(request):
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('无权限访问系统！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    cursor = conn.cursor()

    try:
        cursor.execute(
            "select goods.GID,goods.Gname,goods.Gprice,goods.Gpopularity,provide.Amount "
            "from goods,provide "
            "where goods.GID = provide.GID and provide.SID = '%d' "% (sid))
    except:
        conn.rollback()
        response = HttpResponse()
        response.write("<script language='javascript'>alert('查询商户商品失败！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    raw = dictfetchall(cursor)

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
            try:
                cursor.execute("update goods "
                               "set Gname = '%s',Gprice = '%s'"
                               "where GID = '%s' " % (Gname, Gprice, GID))

                cursor.execute("update provide "
                               "set Amount = '%s' "
                               "where GID = '%s'" %(Amount,GID))

                #重新sql出该商家所有商品，并显示
                cursor.execute(
                    "select goods.GID,goods.Gname,goods.Gprice,goods.Gpopularity,provide.Amount "
                    "from goods,provide "
                    "where goods.GID = provide.GID and provide.SID = '%d' " % (sid))
                goods = dictfetchall(cursor)
                content['goods'] = goods
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('修改商品信息失败，请重试！');"
                               "this.location='/DiningBoat/store_mode/goods/';</script>")
                return response

    return render(request, 'store_goods.html', content)

def Merge(dict1, dict2):
    return(dict1.update(dict2))

def store_orders(request):
    #sql出该商家所有订单
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name
    content['SID'] = sid

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('无权限访问系统！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    cursor = conn.cursor()

    try:
        # start = time.time()
        cursor.execute(
            "select `Caccount`,own.OID,Sname,Oprice,Otime,OfinishedTime,Ostatus,Odestination,Oevaluation,Ocomment "
            "from `diningorder`,own,`store`,`customer`"
            "where `diningorder`.OID = own.OID and store.SID = own.SID and customer.CID = own.CID and own.SID = '%d'" % (sid))
        # end = time.time()
        # print("Running time: %s seconds" % (end - start))
        raw = dictfetchall(cursor)
        content['orders'] = raw

        # start = time.time()
        # cursor.execute("select own.OID,Oprice,Otime,OfinishedTime,Ostatus,Odestination,Oevaluation,Ocomment "
        #                "from `diningorder`,own "
        #                "where `diningorder`.OID = own.OID and own.SID = 1")
        # raw1 = dictfetchall(cursor)
        #
        # cursor.execute("select Caccount "
        #                "from `customer`,own "
        #                "where customer.CID = own.CID and own.SID = 1")
        # raw2 = dictfetchall(cursor)
        # end =  time.time()
        # print("Running time: %s seconds" % (end - start))

        # for i in range(0,len(raw1)):
        #     raw1[i].update(raw2[i])
        #     raw1[i]['Sname'] = name
        #
        # raw = dictfetchall(cursor)
        # content['orders'] = raw1
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('查询商户订单失败！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    if request.method=='GET':
        #修改状态
        if 'change_order_status' in request.GET:
            OID = request.GET['OID']
            Ostatus = request.GET['Ostatus']#注意Ostatus为字符串，需要转换为字母

            print(OID, Ostatus)

            #此处sql更新数据库
            try:
                cursor.execute("update diningorder set Ostatus = '%s'"
                               "where OID = '%s' " % (Ostatus, OID))

                #此处再此sql出全部订单
                cursor.execute(
                    "select `Caccount`,Sname,own.OID,Oprice,Otime,OfinishedTime,Ostatus,Odestination,Oevaluation,`Ocomment` "
                    "from `diningorder`,own,`store`,`customer`"
                    "where `diningorder`.OID = own.OID and store.SID = own.SID and customer.CID = own.CID and own.SID = '%d'" % (
                        sid))
                orders = dictfetchall(cursor)
                content['orders'] = orders
                print(orders[0])
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('修改订单信息失败，请重试！');"
                               "this.location='/DiningBoat/store_mode/orders';</script>")
                return response

        #按照date查询对应的orders
        elif  'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #此date为日而非数据库中的datetime
            date = request.GET['order_date']
            print(date)
            #此处用date查找对应订单并输出显示

            if len(date) > 0:
                try:
                    cursor.execute(
                        "select `Caccount`,Sname,own.OID,Oprice,Otime,OfinishedTime,Ostatus,Odestination,Oevaluation,`Ocomment` "
                        "from `diningorder`,own,`store`,`customer`"
                        "where `diningorder`.OID = own.OID and store.SID = own.SID and customer.CID = own.CID "
                        "and own.SID = '%d' and date(diningorder.Otime) = '%s' " % (sid,date) )
                    orders = dictfetchall(cursor)
                    content['orders'] = orders
                except:
                    response = HttpResponse()
                    response.write("<script language='javascript'>alert('查询某日订单信息失败！');"
                                   "this.location='/Diningboat/store_mode/orders';</script>")
                    return response

            else:
                try:
                    cursor.execute(
                        "select `Caccount`,Sname,own.OID,Oprice,Otime,OfinishedTime,Ostatus,Odestination,Oevaluation,`Ocomment` "
                        "from `diningorder`,own,`store`,`customer`"
                        "where `diningorder`.OID = own.OID and store.SID = own.SID and customer.CID = own.CID and own.SID = '%d'" % (
                            sid))
                    orders = dictfetchall(cursor)
                    content['orders'] = orders
                except:
                    response = HttpResponse()
                    response.write("<script language='javascript'>alert('查询商户订单失败！');"
                                   "this.location='/Diningboat/store_mode/orders';</script>")
                    return response

    return render(request, "store_orders.html", content)


def store_order_goods(request):
    # sql并显示对应订单的全部商品,此处应该用不到，写下面if
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name

    goods = [
        '东区食堂', '中区食堂'
    ]
    content['goods'] = goods

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('无权限访问系统！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    cursor = conn.cursor()

    if request.method == 'GET':
        # 从"我的订单"转到某一订单的详情，OID为目标订单OID,并sql出该订单中所有商品的对应字段
        if 'order_details' in request.GET:
            print('order_details11')
            OID = request.GET['OID']
            print(OID)

            try:
                cursor.execute("select Gname,Gprice,Gpopularity,goods.GID,Amount "
                               "from goods,include "
                               "where goods.GID = include.GID and include.OID = '%s'" % (OID))
                order_goods = dictfetchall(cursor)
                content['order_goods'] = order_goods
                content['OID'] = OID
            except:
                response = HttpResponse()
                response.write("<script language='javascript'>alert('查询订单详情失败！');"
                               "this.location='/Diningboat/store_mode/orders';</script>")
                return response

    return render(request, "store_order_goods.html", content)



def store_myInfo(request):
    # sql并显示该用户所有信息
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('无权限访问系统！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    cursor = conn.cursor()

    try:
        cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                       "from store "
                       "where SID = '%d'" %(sid))
        info = dictfetchall(cursor)
        content['Info'] = info[0]
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('查询用户信息失败！');"
                       "this.location='/Diningboat/login';</script>")
        return response

    if request.method == 'GET':
        if 'change_Sname' in request.GET:
            print('change_Sname')
            Sname = request.GET['Sname']
            print(Sname)

            try:
                # 此处用该用户的Cname更新数据库
                cursor.execute("update store "
                               "set Sname = '%s' "
                               "where SID = '%d'" % (Sname, sid))
                # 此处重新sql该用户所有个人信息
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('更改用户信息失败！');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

        elif 'change_Spassword' in request.GET:
            print('change_Spassword')
            Spassword = request.GET['Spassword']
            print(Spassword)
            try:
                # 此处用该用户的Cpassword更新数据库
                cursor.execute("update store "
                               "set Spassword = '%s' "
                               "where SID = '%d'" % (Spassword, sid))
                # 此处重新sql该用户所有个人信息
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('更改用户信息失败！');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

        elif 'change_Saddress' in request.GET:
            print('change_Saddress')
            Saddress = request.GET['Saddress']
            print(Saddress)
            try:
                # 此处用该用户的Cpassword更新数据库
                cursor.execute("update store "
                               "set Saddress = '%s' "
                               "where SID = '%d'" % (Saddress, sid))
                # 此处重新sql该用户所有个人信息
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('更改用户信息失败！');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

    return render(request, "storeInfo.html", content)