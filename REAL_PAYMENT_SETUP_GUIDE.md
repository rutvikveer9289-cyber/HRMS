# Real Payment Integration - Complete Setup Guide

## 🎉 Congratulations!

Your HRMS now has **REAL PAYMENT** capability! You can transfer actual money from your bank account to employees.

---

## 📋 Quick Setup Checklist

### Phase 1: Razorpay Account (Do This First)
- [ ] Create Razorpay account at https://razorpay.com/
- [ ] Complete KYC verification (takes 24-48 hours)
- [ ] Add your bank account to Razorpay
- [ ] Get API keys (test mode available immediately)

### Phase 2: Backend Setup
- [ ] Install Razorpay Python library
- [ ] Configure environment variables
- [ ] Run database migration
- [ ] Register API routes
- [ ] Test connection

### Phase 3: Testing
- [ ] Test with Razorpay test mode
- [ ] Verify single payment
- [ ] Verify bulk payment
- [ ] Check transaction tracking

### Phase 4: Go Live
- [ ] Switch to live API keys
- [ ] Process first real payment
- [ ] Monitor transactions

---

## 🚀 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd backend
pip install razorpay==1.3.0
```

### Step 2: Configure Environment Variables

Create or update `backend/.env`:

```env
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
RAZORPAY_ACCOUNT_NUMBER=your_razorpay_account_number
RAZORPAY_MODE=test

# Get these from: https://dashboard.razorpay.com/app/keys
```

**Important:** 
- Start with `test` mode
- Never commit `.env` to Git
- Keep API keys secure

### Step 3: Run Database Migration

```bash
cd backend
python migrations/add_razorpay_fields.py
```

This adds:
- `transaction_id` - Stores Razorpay payout ID
- `utr_number` - Stores bank UTR reference

### Step 4: Register API Routes

Update `backend/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import razorpay

# Add this line with other route includes
api_router.include_router(razorpay.router)
```

### Step 5: Restart Backend

```bash
# Stop current backend (Ctrl+C)
# Start again
python -m uvicorn app.main:app --reload
```

---

## 🧪 Testing Guide

### Test 1: Connection Test

```bash
# Using curl or Postman
GET http://localhost:8000/api/v1/razorpay/test-connection
Authorization: Bearer <your_token>
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Razorpay connection successful",
  "mode": "test",
  "balance": 1000000.00,
  "currency": "INR"
}
```

### Test 2: Check Balance

```bash
GET http://localhost:8000/api/v1/razorpay/balance
Authorization: Bearer <your_token>
```

### Test 3: Single Payment (Test Mode)

```bash
POST http://localhost:8000/api/v1/razorpay/payout/single
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payroll_id": 1,
  "mode": "IMPS"
}
```

**Test Bank Account (Use in Employee Profile):**
```
Account Number: 1234567890
IFSC Code: SBIN0007105
Account Holder Name: Test Employee
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment of ₹45000 processed successfully",
  "transaction_id": "pout_xxxxxxxxxxxxx",
  "utr": "123456789012",
  "status": "processing",
  "emp_id": "RBIS0001"
}
```

### Test 4: Bulk Payment

```bash
POST http://localhost:8000/api/v1/razorpay/payout/bulk
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payroll_ids": [1, 2, 3],
  "mode": "IMPS"
}
```

### Test 5: Check Payment Status

```bash
POST http://localhost:8000/api/v1/razorpay/payout/status
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payout_id": "pout_xxxxxxxxxxxxx"
}
```

---

## 💡 How to Use in Frontend

### Option 1: Update Existing Pay Button

The current "Pay" button can be modified to use Razorpay:

In `payroll-management.component.ts`, update `markAsPaid`:

```typescript
markAsPaid(payrollId: number, paymentMethod: string = 'Bank Transfer'): void {
  // Ask user: Manual or Razorpay?
  const useRazorpay = confirm('Use Razorpay for real payment? (Click OK for Yes, Cancel for manual tracking)');
  
  if (useRazorpay) {
    // Call Razorpay API
    this.processRazorpayPayment(payrollId, paymentMethod);
  } else {
    // Existing manual tracking
    const paymentDate = new Date().toISOString().split('T')[0];
    this.payrollService.updatePaymentStatus(payrollId, 'PAID', paymentDate, paymentMethod).subscribe({
      next: () => {
        alert('Payment status updated (manual tracking)');
        this.loadPayrollRecords();
      },
      error: (err) => {
        console.error('Error updating status:', err);
        alert('Error updating payment status');
      }
    });
  }
}

processRazorpayPayment(payrollId: number, mode: string): void {
  this.http.post('/api/v1/razorpay/payout/single', {
    payroll_id: payrollId,
    mode: mode === 'Bank Transfer' ? 'IMPS' : 'NEFT'
  }).subscribe({
    next: (result: any) => {
      alert(`Real payment successful! Transaction ID: ${result.transaction_id}`);
      this.loadPayrollRecords();
    },
    error: (err) => {
      alert(`Payment failed: ${err.error.detail}`);
    }
  });
}
```

### Option 2: Add Separate Razorpay Button

Add a new button specifically for Razorpay payments:

```html
<button class="btn-razorpay" (click)="payViaRazorpay(record.id)">
  💳 Pay via Razorpay
</button>
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# NEVER commit these to Git
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 2. API Key Protection
- Store in environment variables only
- Never log API keys
- Rotate keys periodically
- Use different keys for test/live

### 3. Transaction Limits
Set limits in Razorpay dashboard:
- Per transaction limit: ₹50,000
- Daily limit: ₹5,00,000
- Monthly limit: ₹50,00,000

### 4. Approval Workflow
For production, add approval:
```python
# Require CEO approval for payments > ₹1,00,000
if amount > 100000:
    # Send approval request
    # Wait for approval
    # Then process payment
```

---

## 💰 Cost Calculator

### Example Monthly Costs

**Scenario 1: 50 Employees**
```
50 employees × ₹5 per payout = ₹250/month
Time saved: 2 hours
Value: Priceless!
```

**Scenario 2: 200 Employees**
```
200 employees × ₹4 per payout = ₹800/month
(Volume discount applies)
```

**Scenario 3: 500 Employees**
```
500 employees × ₹3 per payout = ₹1,500/month
(Higher volume discount)
```

---

## 🐛 Troubleshooting

### Error: "Razorpay credentials not configured"

**Solution:**
```bash
# Check .env file exists
ls backend/.env

# Verify variables are set
cat backend/.env | grep RAZORPAY

# Restart backend after adding variables
```

### Error: "Bank details not available"

**Solution:**
1. Go to Employee Management
2. Edit employee
3. Add bank account number and IFSC code
4. Save and retry payment

### Error: "Insufficient balance"

**Solution:**
1. Login to Razorpay dashboard
2. Go to Payouts → Balance
3. Add funds from your bank account
4. Wait for confirmation
5. Retry payment

### Error: "Invalid IFSC code"

**Solution:**
- Verify IFSC code is correct
- Format: XXXX0NNNNNN (11 characters)
- Example: SBIN0001234
- Check at: https://ifsc.razorpay.com/

### Payment Status: "Queued"

**Meaning:** Insufficient balance, payment queued
**Solution:** Add funds to Razorpay account

### Payment Status: "Processing"

**Meaning:** Payment in progress
**Action:** Wait 5-10 minutes, check status again

### Payment Status: "Reversed"

**Meaning:** Payment failed and reversed
**Action:** Check failure reason, fix issue, retry

---

## 📊 Monitoring & Reports

### View Transactions in Razorpay

1. Login to https://dashboard.razorpay.com/
2. Go to Payouts → Transactions
3. Filter by date, status, amount
4. Download reports

### In HRMS

Check transaction details in payroll table:
- `transaction_id` - Razorpay payout ID
- `utr_number` - Bank reference number
- `payment_date` - When paid
- `payment_method` - How paid

---

## 🎓 Training for HR Team

### Quick Training Script

```
1. Process Payroll (as usual)
   - Select month/year
   - Click "Process All Payroll"

2. Verify Bank Details
   - Check all employees have bank info
   - Fix any missing details

3. Make Payment
   - Select employees to pay
   - Click "Pay Selected"
   - Choose "Razorpay IMPS"
   - Confirm payment

4. Verify Success
   - Check status changes to "PAID"
   - Note transaction ID
   - Download payslips

5. Monitor in Razorpay
   - Login to Razorpay dashboard
   - Verify all payments successful
   - Download transaction report
```

---

## 🚀 Going Live Checklist

Before processing real payments:

- [ ] KYC approved by Razorpay
- [ ] Live API keys configured
- [ ] Bank account verified
- [ ] Test mode thoroughly tested
- [ ] All employees have valid bank details
- [ ] Transaction limits configured
- [ ] Backup plan ready
- [ ] HR team trained
- [ ] CEO approval obtained
- [ ] First payment amount < ₹1,000 (test)

---

## 📞 Support Contacts

### Razorpay Support
- **Email:** support@razorpay.com
- **Phone:** 1800-102-0555
- **Dashboard:** Live chat available
- **Docs:** https://razorpay.com/docs/payouts/

### HRMS Technical Support
- Check documentation in `/docs` folder
- Review error logs in backend
- Contact your development team

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Test connection returns success
2. ✅ Balance shows in dashboard
3. ✅ Test payment completes
4. ✅ Transaction ID saved in database
5. ✅ Status updates to PAID
6. ✅ UTR number received
7. ✅ Money appears in test account

---

## 🎉 You're Ready!

Your HRMS can now:
- ✅ Transfer real money to employees
- ✅ Process bulk payments
- ✅ Track all transactions
- ✅ Automatic reconciliation
- ✅ Generate audit reports

**Start with test mode, verify everything works, then go live!**

---

## 📝 Next Steps

1. **Now:** Set up Razorpay account
2. **Today:** Configure and test
3. **This Week:** Train HR team
4. **Next Month:** Go live with real payments

**Welcome to automated payroll! 🚀**
