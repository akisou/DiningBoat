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
        mode = request.POST.get("mode") #��ȡģʽ
        user = request.POST.get("logname") #��ȡ�û���
        pwd = request.POST.get("logpass") #��ȡ����

        content = {}
        content['Name'] = user
        #�û�ģʽ
        if mode=='user_mode':
            user_ifright = user_authenticate(request, username=user, password=pwd)  # ��֤�û����������Ƿ�һ��
            if user_ifright:
                return render(request, 'userMode.html', content)
            else:
                return render(request, 'login.html', {'msg': '��¼ʧ��!'})
        #�̼�ģʽ
        elif mode=='store_mode':
            store_id = store_authenticate(request, username=user, password=pwd)  # ��֤�û����������Ƿ�һ��
            if store_id > 0:
                return render(request, 'storeMode.html', content)
            else:
                return render(request, 'login.html', {'msg': '��¼ʧ��!'})


#�û��˺���֤
def user_authenticate(request, username, password):
    #�˴�Ӧ�����˺�������֤���ݿ���֤���Ƿ����
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

#�̼��˺�
def store_authenticate(request,username, password):
    # �˴�Ӧ�����˺�������֤���ݿ���֤���Ƿ����
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


#�û����̼Ҳ���
def user_stores(request):
    #�˴�sql����ʾ�����̵꣬ע������sql����Ӧ������Ӧ��ʵ���ID���磬��sql�������SID��һ�����к���Ҳ�����
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
        #�˴�Ϊ�����û��������Ʒ����ģ���������ܵĵ��̣�sql����ʾ
        if 'search_stores' in request.GET:
            print('search_stores')
            #ע�⣬�˴�SnameΪ�û������룬����ȷ����Sname����Ҫ����ģʽƥ��ģ������
            Sname = request.GET['Sname']
            stores = query(
                'select Sname, Saddress, Spopularity, SID from store where Sname like \'%s\' order by Spopularity desc'
                % ('%' + '%'.join(list(Sname)) + '%'))
            #�˴�sql�����п��ܵĵ��
            content['stores'] = stores

        elif 'Rank_order' in request.GET:
            # �˴�Ϊѡ����������������
            print("Rank_operation")
            Rank_order = request.GET['Rank_order']
            print(Rank_order)
            conn = connect()
            # �˴����յõ���������������sql�����̼�
            # Rank_orderֵ��ΪSpopularity_down��Saddress_up
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
            # ��ʼ�Ƽ�
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

                for store in stores_list1: # ϲ�����ֵ굫�ǲ�һ��ϲ����ҵ�
                        kind_score[store['Skind']] += store['num']
                        store['score'] += float((store['evasum'] - 3))


                for store in stores_list1:
                    if store['score'] < 0:
                        stores_list1.remove(store)

                for kind, score in kind_score.items():
                    # Ѱ������Ϊkind��score���̵�
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
                response.write("<script language='javascript'>alert('��ȡ�̻��Ƽ�ʧ�ܣ�');"
                               "this.location='/Diningboat/login';</script>")
                return response

    return render(request, "user_stores.html", content)


def user_store_goods(request):
    #��Ҫ�Ƕ��û�������̵���Ʒ�Ĵ���ͶԽ����̼ҵ���Ӧ����
    pwd = request.session['pwd']
    user = request.session['name']

    content = {}
    content['Name'] = user
    CID = request.session['CID']
    print('cid: %s' % CID)

    if request.method == 'GET':
        print("GET")
        # ��user_stores������뵽ĳһ��store
        if 'enter_store' in request.GET:
            print('enter_store')
            SID = request.GET['SID']
            print('sid: %s' % SID)

            # �˴�sql���õ���������Ʒ
            # ����ʾ����Ʒ������ʾ�Ƿ��и���Gifrest�����ܸ��û���һ���̼��ж���ʣ����
            # GifrestΪ�Ƿ��ֵ࣬��Ϊ['��'.'��},�����Ӧ��ʣ����aountҲ�ð����������ڶ�Ӧ��html�в鿴
            goods = query(
                'select Gname, Gprice, Gpopularity, if (Amount > 0, \'��\', \'��\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                % SID)

            content['goods'] = goods

            content['SID'] = SID

            return render(request, "user_store_goods.html", content)
        elif 'choose_goods' in request.GET:
            # ��ʽΪrequest.GET["Buy_amount_" + str(GID)] = ��Ӧ�Ĺ�����
            # ��Ҫ�������̵����е���Ʒ
            print('choose_goods')
            SID = request.GET['SID']

            conn = connect()

            try:
                goods = conn_query(
                    conn,
                    'select Gname, Gprice, Gpopularity, if (Amount > 0, \'��\', \'��\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                    % SID)

                user = conn_query(
                    conn,
                    'select Caddress, Caddr_longitude, Caddr_latitude from customer where CID=%s'
                    % CID)[0]
                # ��������
                conn_query(
                    conn,
                    'insert into diningorder(Oprice, Ostatus, Odestination, Otime, Odestin_longitude, Odestin_latitude) values (%s, \'%s\', \'%s\', \'%s\', %s, %s)'
                    % ('0', 'P', user['Caddress'], str(datetime.now()),
                       user['Caddr_longitude'], user['Caddr_latitude']))

                oid = conn_query(conn,
                                 'select LAST_INSERT_ID() AS OID')[0]['OID']
                # �����û����̼ҡ�����
                conn_query(
                    conn,
                    'insert into own values(%s, %s, %s)' % (SID, oid, CID))

                Oprice = Decimal(0)

                for item in goods:
                    Amount = request.GET['Buy_amount_' + str(item['GID'])]
                    if Amount != '0':
                        #�˴�ʹ�ø���Ʒ�Ĺ�������DB�����޸�
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
                # �޸ļ۸�
                conn_query(
                    conn, 'update diningorder set Oprice=%s where OID=%s' %
                    (str(Oprice), oid))

                conn.commit()
            except:
                conn.rollback()

            conn.close()

            #�˴�����sql�����̵�������Ʒ��ͬ����ʾ�������if�Ͷ�Ӧ��ʣ����
            goods = query(
                'select Gname, Gprice, Gpopularity, if (Amount > 0, \'��\', \'��\') as Gifrest, Amount, goods.GID from goods, provide where provide.SID=%s and goods.GID=provide.GID order by Gpopularity desc'
                % SID)

            content['goods'] = goods
            content['SID'] = SID
            return render(request, "user_store_goods.html", content)
    return render(request, "user_store_goods.html", content)


def user_orders(request):
    #�˴�Ϊsql����ʾ���û����ж���
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
        #ȡ��ĳһ������������sql�����û����ж�������ʾ����
        if 'cancel_order' in request.GET:
            print('cancel_order')
            OID = request.GET['OID']
            print('oid: %s' % OID)
            #�˴�sqlȡ���ö�����ע�Ⲣ�������ݿ�ɾ����һ�����������޸���״̬Ϊ����ȡ����
            query('update diningorder set Ostatus=\'C\' where OID=%s' % OID)
            #�˴�����sql���û����ж���
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID'
                % CID)
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #�޸�ĳһ������Oevaluation��Ocomment��������sql���û����ж�������ʾ����
        elif 'change_orderInfo' in request.GET:
            print('change_orderInfo')
            OID = request.GET['OID']
            print(OID)
            Oevaluation = request.GET['Oevaluation']
            Ocomment = request.GET['Ocomment']
            print(Oevaluation, Ocomment)
            #�˴�sql�޸���������
            print(
                'update diningorder set Oevaluation=\'%s\', Ocomment=\'%s\' where OID=%s'
                % (Oevaluation, Ocomment, OID))
            query(
                'update diningorder set Oevaluation=\'%s\', Ocomment=\'%s\' where OID=%s'
                % (Oevaluation, Ocomment, OID))
            #�˴�����sql�����û�ȫ������
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID'
                % CID)
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #�������������sql�����һ��Ķ���
        elif 'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #��dateΪ�ն������ݿ��е�datetime
            date = request.GET['order_date']
            print(date)
            #�˴���date���Ҷ�Ӧ�����������ʾ
            orders = query(
                'select own.OID, Sname as OSname, Oprice, Otime, OfinishedTime, Ostatus, Oevaluation, Ocomment from diningorder, own, store where own.CID=%s and own.OID = diningorder.OID and store.SID=own.SID and date(Otime)=\'%s\''
                % (CID, date))
            content['orders'] = orders
            return render(request, "user_order.html", content)
    return render(request, "user_order.html", content)


def user_order_goods(request):
    #sql����ʾ��Ӧ������ȫ����Ʒ,�˴�Ӧ���ò�����д����if
    pwd = request.session['pwd']
    user = request.session['name']
    content = {}
    content['Name'] = user
    if request.method == 'GET':
        # ��"�ҵĶ���"ת��ĳһ���������飬OIDΪĿ�궩��OID,��sql���ö�����������Ʒ�Ķ�Ӧ�ֶ�
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
    #sql����ʾ���û�������Ϣ
    pwd = request.session['pwd']
    user = request.session['name']
    content = {}
    content['Name'] = user
    # content['Info'] = {}
    CID = request.session['CID']
    print('cid: %s' % CID)
    #��Ϊ����ĸ�ʽʾ��
    content['Info'] = query(
        'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
        % CID)[0]
    print(content['Info'])

    if request.method == 'GET':
        if 'change_Cname' in request.GET:
            print('change_Cname')
            Cname = request.GET['Cname']
            print(Cname)

            #�˴��ø��û���Cname�������ݿ�
            query('update customer set Cname=\'%s\' where CID=%s' %
                  (Cname, CID))

            #�˴�����sql���û����и�����Ϣ
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)
        elif 'change_Cpassword' in request.GET:
            print('change_Cpassword')
            Cpassword = request.GET['Cpassword']
            print(Cpassword)
            #�˴��ø��û���Cpassword�������ݿ�
            query('update customer set Cpassword=\'%s\' where CID=%s' %
                  (Cpassword, CID))

            #�˴�����sql���û����и�����Ϣ
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)
        elif 'change_Caddress' in request.GET:
            print('change_Caddress')
            Caddress = request.GET['Caddress']
            print(Caddress)

            #�˴��ø��û���Cpassword�������ݿ�
            query('update customer set Caddress=\'%s\' where CID=%s' %
                  (Caddress, CID))

            #�˴�����sql���û����и�����Ϣ
            content['Info'] = query(
                'select CID, Cname, Caccount, Cpassword, Caddress from customer where CID=%s'
                % CID)[0]

            return render(request, "userInfo.html", content)

    return render(request, "userInfo.html", content)

##�̼�ģʽ
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
        response.write("<script language='javascript'>alert('��Ȩ�޷���ϵͳ��');"
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
        response.write("<script language='javascript'>alert('��ѯ�̻���Ʒʧ�ܣ�');"
                       "this.location='/Diningboat/login';</script>")
        return response

    raw = dictfetchall(cursor)

    content['goods'] = raw

    if request.method=='GET':
        #�˴�Ϊ�޸ĸ��̼���Ʒ���ݣ���Ʒ������һ����Ʒһ����Ʒ�޸ĵ�
        if 'store_goods_change' in request.GET:
            print('store_goods_change')

            GID = request.GET['GID']
            Gname = request.GET['Gname']
            Gprice = request.GET['Gprice']
            Amount = request.GET['Amount']

            print(GID, Gname, Gprice, Amount)

            #�˴�Ϊsql���¸��̼���Ʒ����
            try:
                cursor.execute("update goods "
                               "set Gname = '%s',Gprice = '%s'"
                               "where GID = '%s' " % (Gname, Gprice, GID))

                cursor.execute("update provide "
                               "set Amount = '%s' "
                               "where GID = '%s'" %(Amount,GID))

                #����sql�����̼�������Ʒ������ʾ
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
                response.write("<script language='javascript'>alert('�޸���Ʒ��Ϣʧ�ܣ������ԣ�');"
                               "this.location='/DiningBoat/store_mode/goods/';</script>")
                return response

    return render(request, 'store_goods.html', content)

def Merge(dict1, dict2):
    return(dict1.update(dict2))

def store_orders(request):
    #sql�����̼����ж���
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
        response.write("<script language='javascript'>alert('��Ȩ�޷���ϵͳ��');"
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
        response.write("<script language='javascript'>alert('��ѯ�̻�����ʧ�ܣ�');"
                       "this.location='/Diningboat/login';</script>")
        return response

    if request.method=='GET':
        #�޸�״̬
        if 'change_order_status' in request.GET:
            OID = request.GET['OID']
            Ostatus = request.GET['Ostatus']#ע��OstatusΪ�ַ�������Ҫת��Ϊ��ĸ

            print(OID, Ostatus)

            #�˴�sql�������ݿ�
            try:
                cursor.execute("update diningorder set Ostatus = '%s'"
                               "where OID = '%s' " % (Ostatus, OID))

                #�˴��ٴ�sql��ȫ������
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
                response.write("<script language='javascript'>alert('�޸Ķ�����Ϣʧ�ܣ������ԣ�');"
                               "this.location='/DiningBoat/store_mode/orders';</script>")
                return response

        #����date��ѯ��Ӧ��orders
        elif  'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #��dateΪ�ն������ݿ��е�datetime
            date = request.GET['order_date']
            print(date)
            #�˴���date���Ҷ�Ӧ�����������ʾ

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
                    response.write("<script language='javascript'>alert('��ѯĳ�ն�����Ϣʧ�ܣ�');"
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
                    response.write("<script language='javascript'>alert('��ѯ�̻�����ʧ�ܣ�');"
                                   "this.location='/Diningboat/store_mode/orders';</script>")
                    return response

    return render(request, "store_orders.html", content)


def store_order_goods(request):
    # sql����ʾ��Ӧ������ȫ����Ʒ,�˴�Ӧ���ò�����д����if
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name

    goods = [
        '����ʳ��', '����ʳ��'
    ]
    content['goods'] = goods

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('��Ȩ�޷���ϵͳ��');"
                       "this.location='/Diningboat/login';</script>")
        return response

    cursor = conn.cursor()

    if request.method == 'GET':
        # ��"�ҵĶ���"ת��ĳһ���������飬OIDΪĿ�궩��OID,��sql���ö�����������Ʒ�Ķ�Ӧ�ֶ�
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
                response.write("<script language='javascript'>alert('��ѯ��������ʧ�ܣ�');"
                               "this.location='/Diningboat/store_mode/orders';</script>")
                return response

    return render(request, "store_order_goods.html", content)



def store_myInfo(request):
    # sql����ʾ���û�������Ϣ
    content = {}
    sid = request.session['id']
    pwd = request.session['pwd']
    name = request.session['name']
    content['Name'] = name

    try:
        conn = connect()
    except:
        response = HttpResponse()
        response.write("<script language='javascript'>alert('��Ȩ�޷���ϵͳ��');"
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
        response.write("<script language='javascript'>alert('��ѯ�û���Ϣʧ�ܣ�');"
                       "this.location='/Diningboat/login';</script>")
        return response

    if request.method == 'GET':
        if 'change_Sname' in request.GET:
            print('change_Sname')
            Sname = request.GET['Sname']
            print(Sname)

            try:
                # �˴��ø��û���Cname�������ݿ�
                cursor.execute("update store "
                               "set Sname = '%s' "
                               "where SID = '%d'" % (Sname, sid))
                # �˴�����sql���û����и�����Ϣ
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('�����û���Ϣʧ�ܣ�');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

        elif 'change_Spassword' in request.GET:
            print('change_Spassword')
            Spassword = request.GET['Spassword']
            print(Spassword)
            try:
                # �˴��ø��û���Cpassword�������ݿ�
                cursor.execute("update store "
                               "set Spassword = '%s' "
                               "where SID = '%d'" % (Spassword, sid))
                # �˴�����sql���û����и�����Ϣ
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('�����û���Ϣʧ�ܣ�');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

        elif 'change_Saddress' in request.GET:
            print('change_Saddress')
            Saddress = request.GET['Saddress']
            print(Saddress)
            try:
                # �˴��ø��û���Cpassword�������ݿ�
                cursor.execute("update store "
                               "set Saddress = '%s' "
                               "where SID = '%d'" % (Saddress, sid))
                # �˴�����sql���û����и�����Ϣ
                cursor.execute("select `SID`,Sname,Spassword,Saddress,Spopularity "
                               "from store "
                               "where SID = '%d'" % (sid))
                info = dictfetchall(cursor)
                content['Info'] = info[0]
                conn.commit()
            except:
                conn.rollback()
                response = HttpResponse()
                response.write("<script language='javascript'>alert('�����û���Ϣʧ�ܣ�');"
                               "this.location='/Diningboat/store_mode/myInfo';</script>")
                return response

    return render(request, "storeInfo.html", content)