# 🚀 QUICK REFERENCE - Real Payment Integration

## ⚡ 30-Second Overview

**What:** Real money transfer from your bank to employees
**How:** Razorpay Payouts API integration
**Cost:** ₹3-5 per payment
**Time:** 15 minutes vs 2 hours (manual)

---

## 📋 Setup in 5 Steps

```bash
# 1. Install
pip install razorpay==1.3.0

# 2. Configure (.env file)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
RAZORPAY_MODE=test

# 3. Migrate
python backend/migrations/add_razorpay_fields.py

# 4. Register routes (in api.py)
from app.api.v1.endpoints import razorpay
api_router.include_router(razorpay.router)

# 5. Restart
python -m uvicorn app.main:app --reload
```

---

## 🎯 API Endpoints

```
POST /api/v1/razorpay/payout/single
POST /api/v1/razorpay/payout/bulk
POST /api/v1/razorpay/payout/status
GET  /api/v1/razorpay/balance
GET  /api/v1/razorpay/test-connection
```

---

## 💡 Usage

### Single Payment
```json
POST /api/v1/razorpay/payout/single
{
  "payroll_id": 1,
  "mode": "IMPS"
}
```

### Bulk Payment
```json
POST /api/v1/razorpay/payout/bulk
{
  "payroll_ids": [1, 2, 3, 4, 5],
  "mode": "IMPS"
}
```

---

## 🔑 Test Credentials

**Test Bank Account:**
- Account: 1234567890
- IFSC: SBIN0007105
- Name: Test Employee

**Get Test API Keys:**
https://dashboard.razorpay.com/app/keys

---

## ✅ Verification

```bash
# Test connection
curl -X GET http://localhost:8000/api/v1/razorpay/test-connection \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return:
{
  "success": true,
  "mode": "test",
  "balance": 1000000.00
}
```

---

## 📊 Payment Modes

- **IMPS** - Instant (24/7) - ₹5
- **NEFT** - 2-4 hours - ₹4
- **RTGS** - 30 mins (₹2L+) - ₹3

---

## 🔐 Security

```env
# .gitignore
.env
*.env

# Never commit API keys!
# Use environment variables only
```

---

## 📞 Support

**Razorpay:** 1800-102-0555
**Docs:** https://razorpay.com/docs/payouts/

---

## 🎓 Training (2 Minutes)

```
1. Process payroll → Click "Process All"
2. Select employees → Check boxes
3. Pay → Click "Pay Selected"
4. Choose → "Razorpay IMPS"
5. Confirm → Click OK
6. Done! ✅
```

---

## 🐛 Quick Troubleshooting

| Error | Solution |
|-------|----------|
| Credentials not configured | Add to .env file |
| Bank details missing | Update employee profile |
| Insufficient balance | Add funds in Razorpay |
| Invalid IFSC | Verify at ifsc.razorpay.com |

---

## 📁 Files Created

```
backend/
├── app/
│   ├── services/razorpay_service.py ✨
│   ├── api/v1/endpoints/razorpay.py ✨
│   └── models/payroll.py (updated)
├── migrations/add_razorpay_fields.py ✨
└── .env (create this)

docs/
├── RAZORPAY_INTEGRATION_GUIDE.md
├── REAL_PAYMENT_SETUP_GUIDE.md
├── REAL_PAYMENT_COMPLETE.md
└── QUICK_REFERENCE.md (this file)
```

---

## ⚡ Quick Commands

```bash
# Check balance
curl -X GET http://localhost:8000/api/v1/razorpay/balance

# Test connection
curl -X GET http://localhost:8000/api/v1/razorpay/test-connection

# Single payment
curl -X POST http://localhost:8000/api/v1/razorpay/payout/single \
  -H "Content-Type: application/json" \
  -d '{"payroll_id": 1, "mode": "IMPS"}'
```

---

## 🎯 Go-Live Checklist

- [ ] KYC approved
- [ ] Live keys configured
- [ ] Test mode verified
- [ ] Team trained
- [ ] Limits set
- [ ] First small payment tested

---

## 💰 Cost Example

```
50 employees × ₹5 = ₹250/month
vs
Manual: 2 hours × ₹500 = ₹1,000/month

Savings: ₹750 + time!
```

---

## 🚀 Status Flow

```
DRAFT → PROCESSED → PAID
         ↓           ↓
    (Calculate)  (Razorpay)
                    ↓
              Transaction ID
              UTR Number
              Payment Date
```

---

## 📖 Full Documentation

1. **Setup:** REAL_PAYMENT_SETUP_GUIDE.md
2. **Razorpay:** RAZORPAY_INTEGRATION_GUIDE.md
3. **User Guide:** QUICK_START_PAYMENT_GUIDE.md
4. **Summary:** REAL_PAYMENT_COMPLETE.md

---

## ✨ You're Ready!

**Test Mode:** Available now
**Live Mode:** After KYC (24-48 hrs)

**Start testing immediately!** 🎉
