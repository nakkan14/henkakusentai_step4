from flask import Flask, request
from flask import jsonify
import json
from flask_cors import CORS

from db_control import crud, mymodels

import requests

from datetime import datetime

# Azure Database for MySQL
# REST APIでありCRUDを持っている
app = Flask(__name__)
CORS(app)
 

@app.route("/")
def index():
    return "<p>Flask top page!</p>"
 

@app.route("/product", methods=['GET'])
def read_product():
    model = mymodels.Product
    target_code = request.args.get('code') #クエリパラメータ
    result = crud.myselect(mymodels.Product, target_code, "code")
    return result, 200

@app.route("/purchase", methods=['POST'])
def purchase():
    transactionData = request.get_json()
    total_amount = 0
    total_amount_ex_tax = 0  # 税抜き合計金額

    # 1-1 Register transaction
    cashier_code = transactionData["transactionInfo"]["cashier_code"] if transactionData["transactionInfo"]["cashier_code"] != '' else '9999999999'
    transaction_id = crud.myinsertOne(mymodels.Trade, {
        "datetime": datetime.now(),
        "emp_cd": cashier_code,
        "store_cd": transactionData["transactionInfo"]["store_code"],
        "pos_cd": transactionData["transactionInfo"]["pos_id"],
        "total_amt": 0
    })


    # 1-2,3 Register transaction details and calculate total amount
    for item in transactionData.get('items', []):
        crud.myinsertMultiple(mymodels.Trade_detail, {
            "trd_id": transaction_id,
            "prd_id": item.get('id'),
            "prd_code": item.get('code'),
            "prd_name": item.get('name'),
            "prd_price": item.get('price')
        })
        total_amount_ex_tax += item.get('price', 0)
        
    tax_rate = crud.get_tax_rate("10")  # 仮に消費税区分が"10"で固定
    total_amount = total_amount_ex_tax * (1 + tax_rate)

    # 1-4 取引テーブルを更新する
    crud.myupdate(mymodels.Trade, {
        "total_amt": total_amount,  # 合計金額（税込）
        "ttl_amt_ex_tax": total_amount_ex_tax  # 合計金額（税抜）
    }, transaction_id, "trd_id")
    
    # 1-5 Return total amount to the front end
    return jsonify({"success": True, "total_amount": total_amount, "total_amount_ex_tax": total_amount_ex_tax}), 200
