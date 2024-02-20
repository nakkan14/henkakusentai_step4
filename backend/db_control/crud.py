# uname() error回避
import platform
print("platform", platform.uname())
 
 
from sqlalchemy import create_engine, insert, delete, update, select
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
import pandas as pd
import datetime
 
from db_control.connect import engine
from db_control import create_tables # 初回だけコメントアウトを消す
from .mymodels import Tax

 

def datetime_handler(x):

    if isinstance(x, datetime.datetime):

        return x.isoformat()
    raise TypeError("Unknown type")
 
def myinsertOne(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
 
    query = insert(mymodel).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
            session.flush()  # Ensure all data is flushed before commit
            inserted_primary_key = result.inserted_primary_key[0]  # 取引一意キーのidを取得
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
        return None  # Insertion failed due to IntegrityError
 
    # セッションを閉じる
    session.close()
    return inserted_primary_key  # 取引一意キーのidをreturn

def myinsertMultiple(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
 
    query = insert(mymodel).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
 
    # セッションを閉じる
    session.close()
    return "multiple inserted"

def myselect(mymodel, key_value, key_name):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
   
    if key_value == "last": #key_valueにlastが入ってくると最新で登録された情報を返す
        query = session.query(mymodel).order_by(getattr(mymodel, key_name).desc()).limit(1)
    else:
        query = session.query(mymodel).filter(getattr(mymodel, key_name) == key_value)
    try:
        # トランザクションを開始
        with session.begin():
            result = query.all()
        # 結果をオブジェクトから辞書に変換し、リストに追加
        result_dict_list = []
        for row in result:
            row_dict = {column.key: getattr(row, column.key) for column in mymodel.__table__.columns}
            result_dict_list.append(row_dict)
        # リストをJSONに変換
        # result_json = json.dumps(result_dict_list, ensure_ascii=False)
        result_json = json.dumps(result_dict_list, ensure_ascii=True, default=datetime_handler)
 
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
 
    # セッションを閉じる
    session.close()
    return result_json
 
def myselectAll(mymodel):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = select(mymodel)
    try:
        # トランザクションを開始
        with session.begin():
            df = pd.read_sql_query(query, con=engine)
            # 日付が存在する場合、指定された形式に変換
            for column in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column] = pd.to_datetime(df[column], unit='ms').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
            result_json = df.to_json(orient='records', force_ascii=False)
 
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        result_json = None
 
    # セッションを閉じる
    session.close()
    return result_json
 
def myupdate(mymodel, values, key_value, key_name):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
 
    print(values)
 
    query = update(mymodel).where(getattr(mymodel, key_name)==key_value).values(**values)
    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError as e:
        print("更新中にエラーが発生しました:", e)
        session.rollback()
        return None  # エラーが発生した場合はNoneを返す
    finally:
        # セッションを閉じる
        session.close()
    return str(key_value) + " is updated"
 
def mydelete(mymodel, key_value, key_name):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = delete(mymodel).where(getattr(mymodel, key_name)==key_value)
    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
 
    # セッションを閉じる
    session.close()
    return str(key_value) + " is deleted"

def get_tax_rate(tax_code):
    with engine.begin() as connection:
        result = connection.execute(
            select(Tax.percent).where(Tax.code == tax_code)
        ).scalar()
    if result:
        return float(result) / 100  # パーセントを小数点表記に変換
    else:
        return None  # 税率が見つからない場合はNoneを返す