from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import json
from db_control import crud, mymodels
from datetime import datetime

# Pydantic models for request body
class Item(BaseModel):
    id: Optional[int] = None
    code: str
    name: str
    price: float

class TransactionInfo(BaseModel):
    cashier_code: str = Field(default='9999999999')
    store_code: str
    pos_id: str

class PurchaseRequest(BaseModel):
    transactionInfo: TransactionInfo
    items: List[Item]


app = FastAPI()
# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

@app.get("/")
def index():
    return {"message": "FastAPI top page!"}
 

@app.get("/product")
def read_product(code: str):
    result = crud.myselect(mymodels.Product, code, "code")
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content=json.loads(result))

@app.post("/purchase")
def purchase(purchase_data: PurchaseRequest):
    # transactionData = request.get_json()  # 不要なので削除
    total_amount = 0
    total_amount_ex_tax = 0  # 税抜き合計金額

    # transactionDataに直接purchase_dataを使用
    transaction_id = crud.myinsertOne(mymodels.Trade, {
        "datetime": datetime.now(),
        "emp_cd": purchase_data.transactionInfo.cashier_code,
        "store_cd": purchase_data.transactionInfo.store_code,
        "pos_cd": purchase_data.transactionInfo.pos_id,
        "total_amt": 0
    })

    # 1-2,3 Register transaction details and calculate total amount
    for item in purchase_data.items:
        crud.myinsertMultiple(mymodels.Trade_detail, {
            "trd_id": transaction_id,
            "prd_id": item.id,
            "prd_code": item.code,
            "prd_name": item.name,
            "prd_price": item.price
        })
        total_amount_ex_tax += item.price
        
    tax_rate = crud.get_tax_rate("10")  # 仮に消費税区分が"10"で固定
    total_amount = total_amount_ex_tax * (1 + tax_rate)

    # 1-4 取引テーブルを更新する
    crud.myupdate(mymodels.Trade, {
        "total_amt": total_amount,  # 合計金額（税込）
        "ttl_amt_ex_tax": total_amount_ex_tax  # 合計金額（税抜）
    }, transaction_id, "id")
    
    # 1-5 Return total amount to the front end
    return JSONResponse(content={"success": True, "total_amount": total_amount, "total_amount_ex_tax": total_amount_ex_tax})
