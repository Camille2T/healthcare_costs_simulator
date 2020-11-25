from flask import Flask, render_template, request, redirect, flash, jsonify, Markup
import pandas as pd
import requests
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
import dill
from math import sin, cos, sqrt, atan2, radians

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

#define a dictionnary
app.vars={}
CMS_dic = dill.load(open('CMS_dic.pkd', 'rb'))#app.vars['zipcode'] = request.form['zipcode_val']
inv_CMS_dic= {v: k for k, v in CMS_dic.items()}
app.vars['dicdic']=dill.load(open('CMS2DRG_dic.pkd', 'rb'))

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html',CMS=inv_CMS_dic)
    else:

        app.vars['choice_cms'] = int(request.form.get('select1'))
        #app.vars['age'] = request.form['age_lulu'
        #return render_template('index_2.html', DRG=app.vars['dicdic'][app.vars['choice_cms']])
        return  redirect('/index_2')


@app.route('/index_2',methods=['GET','POST'])
def index_2():
  if request.method == 'GET':
      return render_template('index_2.html',DRG=app.vars['dicdic'][app.vars['choice_cms']])
  else:

      app.vars['choice_drg'] = request.form.get('select2')
      return redirect('/index_3')

@app.route('/index_3',methods=['GET','POST'])
def index_3():
  if request.method == 'GET':
      return render_template('/index_3.html')
  else:

      app.vars['choice_zipcode'] = str(request.form['select3'])
      return redirect('/results')

@app.route('/results',methods=['GET'])
def results():
    df_local=dill.load(open('df_local.pkd', 'rb'))
    if app.vars['choice_zipcode'] in df_local['Zip'].values:
            city_home= df_local[df_local['Zip']==app.vars['choice_zipcode']].City.values[0]

            X_full=dill.load(open('X_full.pkd', 'rb'))

            dic_num_to_DRG=dill.load(open('dic_num_to_DRG.pkd', 'rb'))
                #for each hospital calculate the distance
                #calculate distance, point 1 is home
                # approximate radius of earth in miles

            coor=df_local[df_local['Zip']==app.vars['choice_zipcode']]

            R = 3963.0

            lat1 = radians(coor['Latitude'].values[0])
            lon1 = radians(coor['Longitude'].values[0])
            X_full['lat2']=X_full['Latitude'].apply(lambda x: radians(x))
            X_full['lon2']=X_full['Longitude'].apply(lambda x: radians(x))
            X_full['dlon'] = X_full['lon2'] - lon1
            X_full['dlat'] = X_full['lat2'] - lat1
            X_full['a'] =X_full['dlat'].apply(lambda x: sin(x/2)**2) + cos(lat1) *X_full['lat2'].apply(lambda x : cos(x)) * X_full['dlon'].apply(lambda x : sin(x / 2)**2)
            X_full['c'] = 2 * X_full['a'].apply(lambda x : atan2(sqrt(x), sqrt(1 - x)))
            X_full['distance'] = R * X_full['c']


                #Project the price


                #add a column with the DRG
            X_full['DRG']=dic_num_to_DRG[int(app.vars['choice_drg'])]
            est_1=dill.load(open('est_1.pkd', 'rb'))
            est_2=dill.load(open('est_2.pkd', 'rb'))
            est_comb_1_2=dill.load(open('est_comb_1_2.pkd', 'rb'))
            categorical_columns,numeric_columns, categorical_columns_1,numeric_columns_1, categorical_columns_2,numeric_columns_2=dill.load(open('cat_num_col.pkd', 'rb'))

            X_full['price_1']=est_1.predict(X_full.loc[:,categorical_columns_1+ numeric_columns_1])

            X_full['price_2']=est_2.predict(X_full.loc[:,categorical_columns_2+ numeric_columns_2])
            X_full['price']=est_comb_1_2.predict(X_full.loc[:,['price_2','price_1']])

            X_full['rank']=''

                # dans un rayon de 50 miles
            first_pred=X_full[X_full['distance']<50]
            first_pred_f=pd.DataFrame(first_pred.sort_values(by=['price']).head(1))
            first_pred_4=first_pred[first_pred['hosp_rating'].isin(['4','5'])].sort_values(by=['price']).head(1)
            first_pred_5=first_pred[first_pred['hosp_rating']=='5'].sort_values(by=['price']).head(1)
            result_1=pd.concat([first_pred_f,first_pred_4,first_pred_5])

            result_1['rank']='within 50 miles'

                # in your state
            second_pred=pd.DataFrame(X_full[X_full['state']==coor['State'].values[0]])
            second_pred_f=pd.DataFrame(second_pred.sort_values(by=['price']).head(1))
            second_pred_4=second_pred[second_pred['hosp_rating'].isin(['4','5'])].sort_values(by=['price']).head(1)
            second_pred_5=second_pred[second_pred['hosp_rating']=='5'].sort_values(by=['price']).head(1)
            result_2=pd.concat([second_pred_f,second_pred_4,second_pred_5])
                #result_2.drop_duplicates(inplace=True, keep='first')
                #result_2.reset_index(drop=True, inplace=True)
            result_2['rank']='in your state'

                #aux US parmi les hopitaux notés 5

            #third_pred_f=pd.DataFrame(X_full.sort_values(by=['price']).head(1))
            third_pred_4=X_full[X_full['hosp_rating'].isin(['4','5'])].sort_values(by=['price']).head(1)
            third_pred_5=X_full[X_full['hosp_rating']=='5'].sort_values(by=['price']).head(1)
            result_3=pd.concat([third_pred_4,third_pred_5])
                #result_3.drop_duplicates(inplace=True, keep='first')
                #result_3.reset_index(drop=True, inplace=True)
            result_3['rank']='in the US'

            result=pd.concat([result_1,result_2,result_3])[['hosp_name', 'zipcode', 'state',
                   'countyname', 'hosp_rating', 'distance', 'price', 'rank']]
            result.drop_duplicates(inplace=True, keep='first',subset=['hosp_name', 'zipcode', 'state',
                   'countyname', 'hosp_rating', 'distance', 'price'])
            result.reset_index(drop=True, inplace=True)

            result.hosp_name=result.hosp_name.apply(lambda x : ' '.join(map(lambda y : y.capitalize(), x.split()) ))
            result.countyname=result.countyname.apply(lambda x : ' '.join(map(lambda y : y.capitalize(), x.split()) ))
            result.distance=result.distance.apply(lambda x :  str(round(x))+' mi')
            result.price=result.price.apply(lambda x :  '$ '+str(round(x/1000))+',000')
            result.hosp_rating=result.hosp_rating.apply(lambda x :  str(x) + '/5' if x in ('1','2','3','4','5') else x )

            result_1=result[result['rank']=='within 50 miles']
            result_2=result[result['rank']=='in your state']
            result_3=result[result['rank']=='in the US']

            empty_list=['','','','','','','','']
            new_row=dict(zip(result.columns, empty_list))

            while result_1.shape[0]<4:
                result_1=result_1.append(new_row, ignore_index=True)

            while result_2.shape[0]<4:
                result_2=result_2.append(new_row, ignore_index=True)
            while result_3.shape[0]<4:
                result_3=result_3.append(new_row, ignore_index=True)

            hosp_select_1=result_1.to_dict('index')
            hosp_select_2=result_2.to_dict('index')
            hosp_select_3=result_3.to_dict('index')

            name_of_DRG=dic_num_to_DRG[int(app.vars['choice_drg'])][6:]


            return render_template('results.html',drg=app.vars['choice_drg'],
                                   zipcode=app.vars['choice_zipcode'], city=city_home,
                                    hospitals_select_1=hosp_select_1,
                                    hospitals_select_2=hosp_select_2,
                                    hospitals_select_3=hosp_select_3,
                                    name_of_DRG= name_of_DRG)
    else:
        return 'zipcode not found'

      #app.vars['age'] = request.form['age_lulu'
      #return render_template('info.html', zip=CMS_dic)#@app.route('/background_process', methods=['POST', 'GET'])
#def background_process():#
#    CMS = request.args.get('CMS')


	# values stored in the list later to be passed as df while prediction


#    return CMS



@app.route('/about')
def about():
  return render_template('about2.html')

@app.route('/Model')
def Model():
  return render_template('Model.html')

if __name__ == '__main__':
  app.run(port=33507, debug=True)

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
