from flask import Blueprint, render_template, request, redirect
import flask_app.views.my_module as my_module



do_si = []
features = []



hungry_bp = Blueprint('hungry', __name__)



@hungry_bp.route('/hungry/', methods=['GET', 'POST'])
def where():

    if request.method == 'GET':

        import datetime
        now = datetime.datetime.now()

        if now.hour > 12:
            h = now.hour-12
            a = "오후"
        else:
            h = now.hour
            a = "오전"

        return render_template('2_where.html', a=a, h=h, m=now.minute)
    
    elif request.method == 'POST':

        global do_si
        do_si = []
        do = request.form['do']
        si = request.form['si']
        do_si.append(do)
        do_si.append(si)

        location = my_module.get_location()
        worked = len(location[(location['광역시도명'] == do) & (location['시군구명'] == si)])

        if worked == 0:
            return redirect('error')
        else:
            return redirect('weather')



@hungry_bp.route('/hungry/error/')
def error():
    do, si = do_si
    return render_template('error.html', do=do, si=si)    



@hungry_bp.route('/hungry/weather/')
def weather():
    do, si = do_si

    global features
    text, features = my_module.explain(do, si)

    return render_template('3_weather.html', text=text)



@hungry_bp.route('/hungry/result/', methods=['GET'])
def result():
    result = my_module.to_model(features)
    return render_template('4_result.html', result=result)
