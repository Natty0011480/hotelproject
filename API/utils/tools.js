// utils/tools.js

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

exports.createNonceStr = () => {
  return Math.random().toString(36).substr(2, 15);
};

exports.createTimeStamp = () => {
  return Math.floor(Date.now() / 1000).toString();
};

exports.signRequestObject = (data) => {
  const privateKeyPath = path.resolve(__dirname, "../keys/your_private_key.pem");
  const privateKey = fs.readFileSync(privateKeyPath, "utf8");

  // Sort the keys alphabetically
  const sortedKeys = Object.keys(data).sort();
  const queryString = sortedKeys
    .map((key) => {
      const value = typeof data[key] === "object" ? JSON.stringify(data[key]) : data[key];
      return `${key}=${value}`;
    })
    .join("&");

  const signer = crypto.createSign("RSA-SHA256");
  signer.update(queryString);
  signer.end();

  const signature = signer.sign(privateKey, "base64");
  return signature;
};
