"use client"
import React, { useRef, useState } from 'react';

const POSPage = () => {
    // 商品コード入力用のrefを作成
    const productCodeRef = useRef(null);
    const [productData, setProductData] = useState(null);
    const [purchaseList, setPurchaseList] = useState([]);

    // for popup
    const [showPopup, setShowPopup] = useState(false);
    const [totalAmountWithTax, setTotalAmountWithTax] = useState(0);

    // 商品コード読み込みボタンのイベントハンドラー
    const handleLoadProduct = async () => {
        const productCode = productCodeRef.current.value;
        if (productCode) {
            try {
                const response = await fetch(`http://localhost:8000/product?code=${productCode}`, { cache: "no-cache" });
                if (!response.ok) throw new Error('Response not ok');
                const data = await response.json();
                if (data.length === 0) { // データが空の場合
                    setProductData({ id: '', code: '', name: '商品マスタが未登録です', price: 0 });
                } else {
                    console.log(data["0"])
                    setProductData(data["0"]); // Set the state with the fetched data
                }
            } catch (error) {
                console.error('商品情報の読み込みに失敗しました', error);
                setProductData({ id: '', code: '', name: '商品マスタが未登録です', price: 0 }); // エラー時の処理を追加
            }
        }
    };

    // 追加ボタンのイベントハンドラー
    const handleAddProduct = () => {
        if (productData) {
            // 新しい商品を追加、quantityは常に1
            setPurchaseList([...purchaseList, { ...productData, quantity: 1 }]);

            setProductData(null); // 商品データをクリア
            if (productCodeRef.current) {
                productCodeRef.current.value = ''; // 商品コード入力欄をクリア
            }
        }
    };

    const handlePurchase = async () => {
        const transactionData = {
            items: purchaseList,
            transactionInfo: {
                cashier_code: '', // 実際のデータまたは状態変数に置き換えてください
                store_code: '30', // 例の店舗コード
                pos_id: '90' // 例のPOS ID
            }
        };

        try {
            const response = await fetch(`http://localhost:8000/purchase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(transactionData),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // // 標準ポップアップを使用↓
            // // 税率10%を加算
            // const totalWithTax = data.total_amount * 1.1;
            // // ポップアップで表示
            // window.alert(`合計金額（税込）: ${totalWithTax.toFixed(2)}円`);

            // カスタムポップアップを使用↓
            // 成功した場合、以下を実行:
            setTotalAmountWithTax(data.total_amount);
            setShowPopup(true);

        } catch (error) {
            console.error('Error during the purchase:', error);
        }
    };

    return (
        <>
            <div className="border-2 border-gray-300 p-4 rounded-lg shadow-md m-4">
                <div className="flex">
                    <div className="flex-1 bg-blue-100 m-2 p-2">
                        {/* コード入力エリア */}
                        <div className="flex flex-col items-center w-full mb-4">
                            <div className="w-full m-2">
                                <input
                                    ref={productCodeRef} // refをinputに紐付ける
                                    type="text"
                                    placeholder="コードを入力"
                                    name="productCode"
                                    className="input input-bordered w-full"
                                />
                            </div>
                            <button
                                onClick={handleLoadProduct} // イベントハンドラーをボタンに紐付ける
                                className="btn btn-primary m-2 w-full">
                                商品コード読み込み
                            </button>
                        </div>
                        <div className="flex flex-col items-center w-full mb-4">
                            <div className="w-full m-2">
                                <div className="label">
                                    <span className="label-text">商品名</span>
                                </div>
                                <div className="input input-bordered w-full bg-gray-100 text-gray-600 flex items-center justify-center">
                                    {productData ? productData.name : '商品名'}
                                </div>
                            </div>
                            <div className="w-full m-2">
                                <div className="label">
                                    商品単価
                                </div>
                                <div className="input input-bordered w-full bg-gray-100 text-gray-600 flex items-center justify-center">
                                    {productData ? `${productData.price}円` : '単価'}
                                </div>
                            </div>
                            <button
                                onClick={handleAddProduct} // イベントハンドラーを追加ボタンに紐付ける
                                className="btn btn-primary m-2 w-full"
                                disabled={!productData || productData.code === ''} // productDataがnullまたはcodeが空の場合はボタンを無効化
                            >
                                追加
                            </button>
                        </div>
                    </div>
                    <div className="flex-1 bg-green-100 m-2 p-2">
                        {/* 購入リストエリア */}
                        <h2 className="text-center text-lg font-bold mb-4">購入リスト</h2>
                        <div className="border-2 border-gray-300 p-4 rounded-lg">
                            <div className="overflow-x-auto">
                                <table className="table w-full">
                                    {/* ...テーブルヘッダー... */}
                                    <thead>
                                        <tr>
                                            <th>商品名</th>
                                            <th>単価</th>
                                            <th>数量</th>
                                            <th>小計</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {purchaseList.map((product, index) => (
                                            <tr key={index}>
                                                <td>{product.name}</td>
                                                <td>{product.price}円</td>
                                                <td>{product.quantity}</td> {/* 数量は仮に1としています */}
                                                <td>{product.price * product.quantity}円</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* 購入ボタン */}
                        <div className="flex gap-4 mt-4">
                            <button
                                onClick={handlePurchase} // イベントハンドラーを追加ボタンに紐付ける
                                className="btn btn-success w-full"
                                disabled={purchaseList.length === 0} // purchaseListに追加していない状態では、購入をdisabledにする
                            >
                                購入
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* ポップアップ */}
            {showPopup && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
                    <div className="bg-white p-4 rounded-lg shadow-lg text-center">
                        <h2 className="text-lg font-bold">購入完了</h2>
                        <p>合計金額（10%税込）: {totalAmountWithTax.toFixed(0)}円</p>
                        <button
                            className="btn btn-primary mt-4 mx-auto"
                            onClick={() => {
                                setShowPopup(false); // ポップアップを閉じる
                                setPurchaseList([]); // 購入リストをリセット
                            }}
                        >
                            OK
                        </button>
                    </div>
                </div>
            )}
        </>
    );
};

export default POSPage;


