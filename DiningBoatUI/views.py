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
        mode = request.POST.get("mode") #��ȡģʽ
        user = request.POST.get("logname") #��ȡ�û���
        pwd = request.POST.get("logpass") #��ȡ����

        print(user, pwd)
        #�û�ģʽ
        if mode=='user_mode':
            user_ifright = user_authenticate(username=user, password=pwd)  # ��֤�û����������Ƿ�һ��
            if user_ifright:
                return render(request, 'userMode.html', {'msg': '��¼�ɹ�!'})
            else:
                return render(request, 'login.html', {'msg': '��¼ʧ��!'})
        #�̼�ģʽ
        elif mode=='store_mode':
            user_ifright = store_authenticate(username=user, password=pwd)  # ��֤�û����������Ƿ�һ��
            if user_ifright:
                return render(request, 'storeMode.html', {'msg': '��¼�ɹ�!'})
            else:
                return render(request, 'login.html', {'msg': '��¼ʧ��!'})
    return render(request, "login.html")


#�û��˺���֤
def user_authenticate(username, password):
    #�˴�Ӧ�����˺�������֤���ݿ���֤���Ƿ����
    if username=='1234' and password== '1234':
        return True

#�̼��˺�
def store_authenticate(username, password):
    # �˴�Ӧ�����˺�������֤���ݿ���֤���Ƿ����
    if username=='1235' and password== '1235':
        return True

def user_mode(request):
    return render(request, "userMode.html")



#�û����̼Ҳ���
def user_stores(request):
    #�˴�sql����ʾ�����̵꣬ע������sql����Ӧ������Ӧ��ʵ���ID���磬��sql�������SID��һ�����к���Ҳ�����
    content = {}
    stores = [{
        'Sname': '����ʳ��',
        'Saddress': '����',
        'Spopularity': 14
    },
        {
            'Sname': '����ʳ��',
            'Saddress': '����',
            'Spopularity': 14
         }
    ]

    content['stores'] = stores


    if request.method=='GET':
        #�˴�Ϊ�����û��������Ʒ����ģ���������ܵĵ��̣�sql����ʾ
        if 'search_stores' in request.GET:
            print('search_stores')
            #ע�⣬�˴�SnameΪ�û������룬����ȷ����Sname����Ҫ����ģʽƥ��ģ������
            Sname = request.GET['Sname']
            print(Sname)

            #�˴�sql�����п��ܵĵ��

            stores=[]
            content['stores'] = stores
            return render(request, "user_stores.html", content)
        elif 'Rank_order' in request.GET:
            #�˴�Ϊѡ����������������
            print("Rank_operation")
            Rank_order = request.GET['Rank_order']
            print(Rank_order)

            #�˴����յõ���������������sql�����̼�
            #Rank_orderֵ��ΪSpopularity_down��Saddress_up

            stores = []
            content['stores'] = stores
            return render(request, "user_stores.html", content)
        elif 'Stores_recommendation' in request.GET:
            print('Stores_recommendation')
            #��ʼ�Ƽ�

            stores = [{
        'Sname': '����ʳ��',
        'Saddress': '����',
        'Spopularity': 14
    },
        {
            'Sname': '����ʳ��',
            'Saddress': '����',
            'Spopularity': 14
         }
    ]
            content['stores'] = stores
            return render(request, "user_stores.html", content)


    return render(request, "user_stores.html", content)

def user_store_goods(request):
    #��Ҫ�Ƕ��û�������̵���Ʒ�Ĵ���ͶԽ����̼ҵ���Ӧ����
    content={}
    goods = []

    if request.method=='GET':
        print("GET")
        # ��user_stores������뵽ĳһ��store
        if 'enter_store' in request.GET:
            print('enter_store')
            SID = request.GET['SID']
            print(SID)

            # �˴�sql���õ���������Ʒ
            # ����ʾ����Ʒ������ʾ�Ƿ��и���Gifrest�����ܸ��û���һ���̼��ж���ʣ����
            # GifrestΪ�Ƿ��ֵ࣬��Ϊ['��'.'��},�����Ӧ��ʣ����aountҲ�ð����������ڶ�Ӧ��html�в鿴

            goods = [
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '��',
                    'Amount': 4,
                    'GID': 1
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '��',
                    'Amount': 0,
                    'GID': 2
                },
            ]

            content['goods'] = goods

            content['SID'] = SID

            return render(request, "user_store_goods.html", content)
        elif 'choose_goods' in request.GET:
            #��ʽΪrequest.GET["Buy_amount_" + str(GID)] = ��Ӧ�Ĺ�����
            #��Ҫ�������̵����е���Ʒ
            print('choose_goods')
            SID = request.GET['SID']

            #�˴�ʹ�ø���Ʒ�Ĺ�������DB�����޸�

            #�˴�����sql�����̵�������Ʒ��ͬ����ʾ�������if�Ͷ�Ӧ��ʣ����

            goods=[
                {
                    'Gname': 'rice',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '��',
                    'Amount': 4,
                    'GID': '1'
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '��',
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

    #�˴�Ϊsql����ʾ���û����ж���
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
        #ȡ��ĳһ������������sql�����û����ж�������ʾ����
        if 'cancel_order' in request.GET:
            print('cancel_order')
            OID = request.GET['OID']
            print(OID)
            #�˴�sqlȡ���ö�����ע�Ⲣ�������ݿ�ɾ����һ�����������޸���״̬Ϊ����ȡ����

            #�˴�����sql���û����ж���

            orders = []
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

            #�˴�����sql�����û�ȫ������
            orders = []
            content['orders'] = orders
            return render(request, "user_order.html", content)

        #�������������sql�����һ��Ķ���
        elif 'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #��dateΪ�ն������ݿ��е�datetime
            date = request.GET['order_date']
            print(date)
            #�˴���date���Ҷ�Ӧ�����������ʾ

            orders=[]
            content['orders']=orders
            return render(request, "user_order.html", content)
    return render(request, "user_order.html", content)

def user_order_goods(request):
    #sql����ʾ��Ӧ������ȫ����Ʒ,�˴�Ӧ���ò�����д����if
    content = {}

    goods = [
        '����ʳ��', '����ʳ��'
    ]
    content['goods'] = goods
    if request.method=='GET':
        # ��"�ҵĶ���"ת��ĳһ���������飬OIDΪĿ�궩��OID,��sql���ö�����������Ʒ�Ķ�Ӧ�ֶ�
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
    #�˴�sql��ʾ�û��Ƽ�,����ԭ���Ĵ��̼ҽ�ȥ������Ʒ����Ʒ���ԣ����ж�Ӧ����Ʒ���̼���
    content={}
    content['goods'] = [
        {
            'Gname': 'rice',
            'Sname': 'east',
            'Gprice': 2,
            'Gpopularity': 15,
            'Gifrest': '��',
            'Amount': 4,
            'GID': '1'
        },
        {
            'Gname': 'noodles',
            'Sname': 'east',
            'Gprice': 5,
            'Gpopularity': 20,
            'Gifrest': '��',
            'Amount': 3,
            'GID': '2'
        },
    ]

    #�˴�Ϊ�û��Ƽ�������µ�ʶ��ʹ������̻���ڵ���Ʒ�µ�һ��
    if request.method == 'GET':
        if 'choose_goods' in request.GET:
            # ��ʽΪrequest.GET["Buy_amount_" + str(GID)] = ��Ӧ�Ĺ�����
            # ��Ҫ�������̵����е���Ʒ
            print('choose_goods')
            SID = request.GET['SID']

            # �˴�ʹ�ø���Ʒ�Ĺ�������DB�����޸�

            # �˴�����sql�������Ƽ���Ʒ��ͬ����ʾ�������if�Ͷ�Ӧ��ʣ����
            goods = [
                {
                    'Gname': 'rice',
                    'Sname': 'east',
                    'Gprice': 2,
                    'Gpopularity': 15,
                    'Gifrest': '��',
                    'Amount': 4,
                    'GID': '1'
                },
                {
                    'Gname': 'noodles',
                    'Sname': 'east',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '��',
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
    #sql����ʾ���û�������Ϣ
    content={}
    content['Info']={}

    #��Ϊ����ĸ�ʽʾ��
    content['Info']={
        'CID':1,
        'Cname':'akisou',
        'Caccount':1234,
        'Cpassword':1234,
        'Caddress':'����'
    }

    if request.method=='GET':
        if 'change_Cname' in request.GET:
            print('change_Cname')
            Cname = request.GET['Cname']
            print(Cname)
            #�˴��ø��û���Cname�������ݿ�

            #�˴�����sql���û����и�����Ϣ

            content['Info']={
                'CID': 1,
                'Cname': Cname,
                'Caccount': 1234,
                'Cpassword': 1234,
                'Caddress': '����'

            }
            return render(request, "userInfo.html", content)
        elif 'change_Cpassword' in request.GET:
            print('change_Cpassword')
            Cpassword = request.GET['Cpassword']
            print(Cpassword)
            #�˴��ø��û���Cpassword�������ݿ�

            #�˴�����sql���û����и�����Ϣ

            content['Info']={
                'CID': 1,
                'Cname': 'akisou',
                'Caccount': 1234,
                'Cpassword': Cpassword,
                'Caddress': '����'

            }
            return render(request, "userInfo.html", content)
        elif 'change_Caddress' in request.GET:
            print('change_Caddress')
            Caddress = request.GET['Caddress']
            print(Caddress)
            #�˴��ø��û���Cpassword�������ݿ�

            #�˴�����sql���û����и�����Ϣ

            content['Info']={
                'CID': 1,
                'Cname': 'akisou',
                'Caccount': 1234,
                'Cpassword': 1234,
                'Caddress': Caddress

            }
            return render(request, "userInfo.html", content)

    return render(request, "userInfo.html", content)







##�̼�ģʽ



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
    #     response.write("<script language='javascript'>alert('��Ȩ�޷���ϵͳ��');this.location='/login';</script>")
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
        #�˴�Ϊ�޸ĸ��̼���Ʒ���ݣ���Ʒ������һ����Ʒһ����Ʒ�޸ĵ�
        if 'store_goods_change' in request.GET:
            print('store_goods_change')

            GID = request.GET['GID']
            Gname = request.GET['Gname']
            Gprice = request.GET['Gprice']
            Amount = request.GET['Amount']

            print(GID, Gname, Gprice, Amount)

            #�˴�Ϊsql���¸��̼���Ʒ����

            #����sql�����̼�������Ʒ������ʾ

            goods=[]
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

        #ɾ����Ʒ
        elif 'store_goods_cancel' in request.GET:

            print('store_goods_cancel')

            GID = request.GET['GID']
            print(GID)

            #ɾ������Ʒ����sql����Ʒ
            goods = []
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

        #������Ʒ
        elif 'store_goods_add' in request.GET:
            print('store_goods_add')
            #����GID������Ĭ��Ϊ0
            Gname = request.GET['Gname']
            Gprice = request.GET['Gprice']
            Amount = request.GET['Amount']

            print(Gname, Gprice, Amount)

            #sql���û�������Ʒ
            goods = []
            content['goods'] = goods
            return render(request, 'store_goods.html', content)

            #sql�������Ʒ



    return render(request, 'store_goods.html', content)



def store_orders(request):
    #sql�����̼����ж���
    content = {}
    orders = [
        {
            "Caccount":2,
            "OSname":"akisou",
            "Oprice":"akisou" ,
            "Otime":"akisou" ,
            "OfinishedTime":"�����" ,
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
            "OfinishedTime": "�����",
            'Odestination': 'akisou',
            "Ostatus": "akisou",
            "Oevaluation": 3,
            "Ocomment": "akisou"
        }
    ]
    content['orders'] = orders
    content['SID'] = 1

    if request.method=='GET':
        #�޸�״̬
        if 'change_order_status' in request.GET:
            print('change_order_status')
            OID = request.GET['OID']
            Ostatus = request.GET['Ostatus']#ע��OstatusΪ�ַ�������Ҫת��Ϊ��ĸ

            print(OID, Ostatus)

            #�˴�sql�������ݿ�

            #�˴��ٴ�sql��ȫ������
            orders=[]
            content['orders'] = orders
            return render(request, "store_orders.html", content)

        #����date��ѯ��Ӧ��orders
        elif  'search_orders_by_date' in request.GET:
            print('search_orders_by_date')
            #��dateΪ�ն������ݿ��е�datetime
            date = request.GET['order_date']
            print(date)
            #�˴���date���Ҷ�Ӧ�����������ʾ

            orders=[
                {
                    "Caccount": 2,
                    "OSname": "akisou",
                    "Oprice": "akisou",
                    "Otime": "akisou",
                    "OfinishedTime": "�����",
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
                    "OfinishedTime": "�����",
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
    # sql����ʾ��Ӧ������ȫ����Ʒ,�˴�Ӧ���ò�����д����if
    content = {}

    goods = [
        '����ʳ��', '����ʳ��'
    ]
    content['goods'] = goods
    print('ashi')
    if request.method == 'GET':
        # ��"�ҵĶ���"ת��ĳһ���������飬OIDΪĿ�궩��OID,��sql���ö�����������Ʒ�Ķ�Ӧ�ֶ�
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
                    'Gifrest': '��',
                    'Amount': 4,
                    'GID': 1
                },
                {
                    'Gname': 'noodles',
                    'Gprice': 5,
                    'Gpopularity': 20,
                    'Gifrest': '��',
                    'Amount': 0,
                    'GID': 2
                },
            ]
            content['order_goods'] = order_goods
            content['OID'] = OID
            return render(request, "store_order_goods.html", content)

    return render(request, "store_order_goods.html", content)




def store_myInfo(request):
    # sql����ʾ���û�������Ϣ
    content = {}
    content['Info'] = {}

    # ��Ϊ����ĸ�ʽʾ��
    content['Info'] = {
        'SID': 1,
        'Sname': 'akisou',
        'Spassword': 1234,
        'Saddress': '����',
        'Spopularity': 12
    }

    if request.method == 'GET':
        if 'change_Sname' in request.GET:
            print('change_Sname')
            Sname = request.GET['Sname']
            print(Sname)
            # �˴��ø��û���Cname�������ݿ�

            # �˴�����sql���û����и�����Ϣ

            content['Info'] = {
                'SID': 1,
                'Sname': Sname,
                'Spassword': 1234,
                'Saddress': '����',
                'Spopularity': 12

            }
            return render(request, "storeInfo.html", content)
        elif 'change_Spassword' in request.GET:
            print('change_Spassword')
            Spassword = request.GET['Spassword']
            print(Spassword)
            # �˴��ø��û���Cpassword�������ݿ�

            # �˴�����sql���û����и�����Ϣ

            content['Info'] = {
                'SID': 1,
                'Sname': 'akisou',
                'Spassword': Spassword,
                'Saddress': '����',
                'Spopularity': 12

            }
            return render(request, "storeInfo.html", content)
        elif 'change_Saddress' in request.GET:
            print('change_Saddress')
            Saddress = request.GET['Saddress']
            print(Saddress)
            # �˴��ø��û���Cpassword�������ݿ�

            # �˴�����sql���û����и�����Ϣ

            content['Info'] = {
                'SID': 1,
                'Sname': 'akisou',
                'Spassword': 1234,
                'Saddress': Saddress,
                'Spopularity': 12
            }
            return render(request, "storeInfo.html", content)

    return render(request, "storeInfo.html", content)