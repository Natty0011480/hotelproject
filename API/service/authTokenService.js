const applyFabricToken = require("./applyFabricTokenService");
const tools = require("../utils/tools");
const config = require("../config/config");
const https = require("http");

exports.authToken = async (req, res) => {
  let appToken = req.body.authToken;
  console.log("token = ", appToken);
  let applyFabricTokenResult = await applyFabricToken();
  console.log("applyFabricTokenResult", applyFabricTokenResult);
  let fabricToken = applyFabricTokenResult.token;
  let result = await exports.requestAuthToken(fabricToken, appToken);
  res.send(result);
};

exports.requestAuthToken = async (fabricToken, appToken) => {
  return new Promise((resolve) => {
    let reqObject = createRequestObject(appToken);
    var options = {
      method: "POST",
      url: config.baseUrl + "/payment/v1/auth/authToken",
      headers: {
        "Content-Type": "application/json",
        "X-APP-Key": config.fabricAppId,
        Authorization: fabricToken,
      },
      rejectUnauthorized: false, //add when working with https sites
      requestCert: false, //add when working with https sites
      agent: false, //add when working with https sites
      body: JSON.stringify(reqObject),
    };
    request(options, function (error, response) {
      if (error) throw new Error(error);
      console.log(response.body);
      let result = JSON.parse(response.body);
      console.log(result);
      resolve(result);
    });
  });
};

function createRequestObject(appToken) {
  let req = {
    timestamp: tools.createTimeStamp(),
    nonce_str: tools.createNonceStr(),
    method: "payment.authtoken",
    version: "1.0",
  };
  let biz = {
    access_token: appToken,
    trade_type: "InApp",
    appid: config.merchantAppId,
    resource_type: "OpenId",
  };
  req.biz_content = biz;
  req.sign = tools.signRequestObject(req);
  req.sign_type = "SHA256WithRSA";
  console.log(req);
  return req;
}

// module.exports = authToken;
