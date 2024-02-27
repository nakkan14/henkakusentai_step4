"use client"

import React, { useState } from 'react';

const TestPage = () => {
  const [input, setInput] = useState('');
  const [display, setDisplay] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault(); // フォームのデフォルト送信を防ぐ
    setDisplay(input); // 入力されたテキストを表示用の状態にセット
  };

  return (
    <div className="container">
      <h1>XSS Test Page</h1>
      <form onSubmit={handleSubmit} className="input-form">
        <textarea
          className="input-textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter some text here..."
        />
        <button type="submit" className="submit-button">Submit</button>
      </form>
      <div className="display-area">
        <h2>Input Display:</h2>
        {/* ユーザー入力を直接表示 */}
        {/* <div className="user-input">{display}</div>*/}
        {/* `dangerouslySetInnerHTML`を使用してユーザー入力をHTMLとして表示 */}
        <div dangerouslySetInnerHTML={{ __html: display }}></div>
      </div>

      <style jsx>{`
        .container {
          max-width: 600px;
          margin: auto;
          padding: 20px;
        }s
        .input-form {
          margin-bottom: 20px;
        }
        .input-textarea {
          width: 100%;
          height: 100px;
          margin-bottom: 10px;
          padding: 10px;
          font-size: 16px;
          border: 1px solid #ccc;
          border-radius: 5px;
        }
        .submit-button {
          width: 100%;
          padding: 10px;
          border: none;
          background-color: #007bff;
          color: white;
          font-size: 16px;
          cursor: pointer;
          border-radius: 5px;
        }
        .submit-button:hover {
          background-color: #0056b3;
        }
        .display-area {
          border: 1px solid #ccc;
          padding: 10px;
          border-radius: 5px;
        }
        .user-input {
          white-space: pre-wrap; /* 保持换行 */
        }
      `}</style>
    </div>
  );
};

export default TestPage;
