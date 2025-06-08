// requestCreateOrderService.js

const applyFabricToken = require("./applyFabricTokenService");
const tools = require("../utils/tools");
const config = require("../config/config");
const axios = require("axios");

exports.createOrder = async (req, res) => {
  try {
    const { title, amount } = req.body;

    // Step 1: Get Fabric Token
    const { token: fabricToken } = await applyFabricToken();

    // Step 2: Send Create Order Request
    const createOrderResult = await exports.requestCreateOrder(fabricToken, title, amount);
    console.log("🧾 createOrderResult:", createOrderResult);

    // Step 3: Prepare Prepay Payload
    const prepayId = createOrderResult.biz_content?.prepay_id;
    const rawRequest = createRawRequest(prepayId);

    res.send(rawRequest);
  } catch (err) {
    console.error("❌ Failed to create order:", err.message || err);
    res.status(500).json({ error: "Order creation failed" });
  }
};

exports.requestCreateOrder = async (fabricToken, title, amount) => {
  const reqObject = createRequestObject(title, amount);

  try {
    const response = await axios.post(
      `${config.baseUrl}/payment/v1/merchant/preOrder`,
      reqObject,
      {
        headers: {
          "Content-Type": "application/json",
          "X-APP-Key": config.fabricAppId,
          Authorization: fabricToken,
        },
        httpsAgent: new (require("https").Agent)({ rejectUnauthorized: false }), // Optional: skip self-signed certs
      }
    );

    return response.data;
  } catch (error) {
    console.error("❌ Error from SuperApp API:", error.response?.data || error.message);
    throw error;
  }
};

function createRequestObject(title, amount) {
  const req = {
    timestamp: tools.createTimeStamp(),
    nonce_str: tools.createNonceStr(),
    method: "payment.preorder",
    version: "1.0",
  };

  const biz = {
    notify_url: "https://your-publicly-accessible-notify-url.com/notify", // Must match whitelisted
    trade_type: "InApp",
    appid: config.merchantAppId,
    merch_code: config.merchantCode,
    merch_order_id: createMerchantOrderId(),
    title: title,
    total_amount: amount,
    trans_currency: "ETB",
    timeout_express: "120m",
    payee_identifier: config.merchantCode,
    payee_identifier_type: "04",
    payee_type: "3000",
    redirect_url: "https://your-redirect-url.com",
  };

  req.biz_content = biz;

  // Sign the request
  req.sign = tools.signRequestObject(req);
  req.sign_type = "SHA256WithRSA";

  return req;
}

function createMerchantOrderId() {
  return `${Date.now()}`;
}

function createRawRequest(prepayId) {
  const map = {
    appid: config.merchantAppId,
    merch_code: config.merchantCode,
    nonce_str: tools.createNonceStr(),
    prepay_id: prepayId,
    timestamp: tools.createTimeStamp(),
  };

  const sign = tools.signRequestObject(map);

  return [
    `appid=${map.appid}`,
    `merch_code=${map.merch_code}`,
    `nonce_str=${map.nonce_str}`,
    `prepay_id=${map.prepay_id}`,
    `timestamp=${map.timestamp}`,
    `sign=${sign}`,
    `sign_type=SHA256WithRSA`,
  ].join("&");
}

module.exports = exports;
