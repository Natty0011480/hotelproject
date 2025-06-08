// utils/sign.js
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Load your private key
const privateKey = fs.readFileSync(path.join(__dirname, '../keys/your_private_key.pem'), 'utf8');

function generateSignature(params) {
    const filtered = { ...params };
    delete filtered.sign;
    delete filtered.sign_type;

    const sortedKeys = Object.keys(filtered).sort();
    const signingString = sortedKeys.map(key => `${key}=${filtered[key]}`).join('&');

    const signer = crypto.createSign('RSA-SHA256');
    signer.update(signingString, 'utf8');
    const signature = signer.sign(privateKey, 'base64');

    return {
        ...params,
        sign_type: 'SHA256WithRSA',
        sign: signature,
    };
}

module.exports = { generateSignature };
