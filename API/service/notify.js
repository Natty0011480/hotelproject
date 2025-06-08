const express = require('express');
const router = express.Router();
const crypto = require('crypto');
const fs = require('fs');
const axios = require('axios');

// Load SuperApp public key
const superAppPublicKey = fs.readFileSync('./keys/superapp_public.pem', 'utf8');

router.post('/payment/notify', express.json(), async (req, res) => {
    const { sign, sign_type, ...payload } = req.body;

    // 1. Sort payload alphabetically by keys
    const sortedKeys = Object.keys(payload).sort();
    const signingString = sortedKeys.map(key => `${key}=${payload[key]}`).join('&');

    // 2. Verify signature
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(signingString, 'utf8');
    const isVerified = verifier.verify(superAppPublicKey, sign, 'base64');

    if (!isVerified) {
        console.warn("❌ Invalid signature in payment notification");
        return res.sendStatus(400);
    }

    // ✅ Signature valid
    console.log("🔔 Payment Notification Received and Verified:", payload);

    // 3. Forward to Django backend
    try {
        const response = await axios.post('http://localhost:8000/payment/webhook/', {
            transaction_id: payload.transaction_id,
            status: payload.status  // must be 'success' or 'failed'
        });

        console.log("✅ Forwarded to Django:", response.data);
        return res.sendStatus(200); // Acknowledge SuperApp
    } catch (error) {
        console.error("🚫 Failed to forward to Django:", error.message);
        return res.sendStatus(500); // SuperApp will retry
    }
});

module.exports = router;
