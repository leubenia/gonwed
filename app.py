from os import name
from flask_admin import model
from pymongo import MongoClient
from bson.objectid import ObjectId
import flask_admin as admin
from pymongo.common import partition_node
from wtforms import form, fields
from flask_admin.form import Select2Widget
from flask_admin.contrib.pymongo import ModelView, filters, view
from bson.json_util import dumps
import json
from bson import json_util
import html
from flask import Flask, render_template, jsonify, request, session, url_for, redirect, flash
# from flask_pymongo import PyMongo
from wtforms.fields.simple import FileField
from werkzeug.security import generate_password_hash, check_password_hash


#회원가입 비밀번호 암호화를 위해 werkzeug import

# Create application
app = Flask(__name__)

conn = MongoClient('localhost',27017)


db = conn.bdd
app.config['SECRET_KEY'] = '123456790'

# Create models






# User admin
# author 배성현
class menu_form(form.Form):
    img = fields.StringField('사진')
    menu = fields.StringField('메뉴')
    price = fields.StringField('가격')
    category = fields.SelectField('카테고리', choices= [('김치', '김치'),
                ('기본반찬/나물', '기본반찬/나물'), ('국/탕/찌개', '국/탕/찌개'), ('조림/구이', '조림/구이'), ('튀김/전', '튀김/전'), ('도시락', '도시락'), ('제사/명절','제사/명절')])
    hide = fields.SelectField('숨김/보임 (1/0)', choices= [('0','보임'), ('1','숨김')] )

    # DB에 저장할때 사용하는 key = fields.StringField('name') < value 값이 저장되는 inputbox


# User admin
# author 배성현
class order_form(form.Form):
    state = fields.SelectField ('주문 상태', choices= [('입금확인중','입금확인중'),('결제완료', '결제완료'),('상품준비중','상품준비중'),('배송중','배송중'),('배송완료','배송완료')])
    deliverynum = fields.StringField('송장번호')
    deliverycompany = fields.SelectField ('택배 회사', choices= [('kr.chunilps','천일택배'),('kr.cjlogistics', 'CJ대한통운'),('kr.cupost','CU 편의점택배'),('kr.cvsnet','GS Postbox 택배'),('kr.cway','CWAY (Woori Express)'),('kr.daesin','대신택배'),('kr.epost','우체국 택배'),('kr.hanips','한의사랑택배'),('kr.hanjin','한진택배'),('kr.hdexp','합동택배'),('kr.homepick','홈픽'),('kr.honamlogis','한서호남택배'),('kr.ilyanglogis','일양로지스'),('kr.kdexp','경동택배'),('kr.kunyoung','건영택배'),('kr.logen','로젠택배'),('kr.lotte','롯데택배')])
    

class origin_form(form.Form):
    name = fields.StringField ('재료명')
    origin = fields.StringField ('원산지')

class user_form(form.Form):
    pw = fields.StringField ('비밀번호 변경')
    # 구현해야할지 말아야할지?



class menu_view(ModelView):

    column_list = ('img', 'menu', 'price','category','hide') #db에서 불러올때 사용하는 key값
    

    form = menu_form

class order_view(ModelView):
    column_list = ('name', 'menu', 'phone', 'address','postcode', 'price', 'state' , 'date','postmsg' , 'today', 'deliverycompany', 'deliverynum')
    column_sortable_list = ('name', 'menu', 'phone', 'address','postcode', 'price', 'state' , 'date','postmsg' , 'today' ,'deliverycompany', 'deliverynum')
    can_edit = True

    form = order_form


class origin_view(ModelView):

    column_list = ('name', 'origin')

    form = origin_form

class user_view(ModelView):

    column_list = ('userid', 'pw', 'phone', 'postcode', 'address', 'extraAddress')

    form = user_form
# User admin

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)




# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/footer')
def footer():
    return render_template('footer.html')

@app.route('/change')
def change():
    return render_template('change.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/join')
def join():
    return render_template('join.html')

# API 역할을 하는 부분
@app.route('/api/list', methods=['GET'])
def show_stars():
    sample_receive = request.args.get('sample_give')
    print(sample_receive)
    return jsonify({'msg': 'list 연결되었습니다!'})

#아이디중복체크
@app.route('/api/idcheck', methods=['GET'])
def idcheck():
    userid = request.args.get('userid_give')
    id_check= list(db.users.find({'userid': userid}, {'_id': False}))
    print(id_check)
    if id_check==[]:
        return jsonify({'result':'success','msg': '아이디 가능합니다.'})
    else:
        return jsonify({'msg': '기존에 동일한 아이디가 존재합니다.'})

# 회원가입
@app.route('/join', methods=['POST'])
def join_page():
    # title_receive로 클라이언트가 준 title 가져오기
    userid = request.form['userid_give']
    pw = request.form['pw_give']
    name = request.form['name_give']
    mail = request.form['mail_give']
    address = request.form['address_give']
    phone = request.form['phone_give']

    # DB에 삽입할 review 만들기
    doc = {
        'userid': userid,
        'pw': generate_password_hash(pw),
        'name': name,
        'mail': mail,
        'address': address,
        'phone': phone,

    }
    # member에 review 저장하기
    db.users.insert_one(doc)
    # 성공 여부 & 성공 메시지 반환
    
    return jsonify({'msg': '회원가입 완료'})


@app.route('/api/like', methods=['POST'])
def like_star():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': 'like 연결되었습니다!'})


@app.route('/api/delete', methods=['POST'])
def delete_star():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': 'delete 연결되었습니다!'})

@app.route('/login_main', methods=['GET', 'POST'])
def login_main():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        userid = request.form.get("userid", type=str)
        pw = request.form.get("userPW", type=str)

        if userid == "":
            flash("아이디를 입력하세요")
            return render_template('login.html')
        elif pw == "":
            flash("비밀번호를 입력하세요")
            return render_template('login.html')
        else:
            users = db.users
            id_check = users.find_one({"userid": userid})
            if id_check is None:
                flash("아이디가 존재하지 않습니다.")
                return render_template('login.html')
            elif check_password_hash(id_check["pw"],pw):
                session["logged_in"] = userid
                return render_template('index.html', userid = userid)
            else:
                flash("비밀번호가 틀렸습니다.")
                return render_template('login.html')




# 회원정보 가져오기 (id가 idid 인 사람)
@app.route('/user', methods=['GET'])
def read_membership():
    membership = db.users.find_one({'userid': 'idid'},{'_id':False})
    return jsonify({'user_membership': membership})



#아이디중복체크
@app.route('/api/idcheck', methods=['GET'])
def idcheck():
    userid = request.args.get('userid_give')
    id_check= list(db.member.find({'userid': userid}, {'_id': False}))
    # print(id_check)
    if id_check==[]:
        return jsonify({'result':'success','msg': '아이디 가능합니다.'})
    else:
        return jsonify({'msg': '기존에 동일한 아이디가 존재합니다.'})


# 회원정보 수정 (id가 idid 인 사람)
@app.route('/api/change', methods=['POST'])
def change_membership():
    userid = request.form['userid_give']
    pw = request.form['pw_give']
    name = request.form['name_give']
    mail = request.form['mail_give']
    address = request.form['address_give']
    phone = request.form['phone_give']

    title_receive = db.users.update_one({'userid':'idid'},{'$set':{'userid':userid, 'pw':pw, 'name':name, 'mail':mail, 'address':address, 'phone':phone}})
    print(title_receive)
    return jsonify({'result':'success', 'msg': '회원정보가 수정되었습니다.'})



if __name__ == '__main__':
    admin = admin.Admin(app, name='맘스키친', url='/dodo')
    
    # Add views
    admin.add_view(menu_view(db.menu, '매뉴', url='/Product_management'))
    admin.add_view(order_view(db.order, '일단 테스트', url='/Order_details'))
    admin.add_view(origin_view(db.origin, '원산지표기', url='/Country_of_origin'))
    admin.add_view(user_view(db.users, '회원 정보', url='/moms_users'))
    
    # Start app
    app.run('0.0.0.0', port=5000, debug=True)