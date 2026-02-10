# Razorpay Payout Integration Guide

## Overview
This guide will help you integrate Razorpay Payouts to enable REAL money transfers from your bank account to employees.

## Prerequisites

### 1. Razorpay Account Setup
1. Go to https://razorpay.com/
2. Click "Sign Up" 
3. Choose "Payouts" product
4. Complete KYC verification
5. Add your bank account
6. Get API credentials

### 2. Required Information
- Razorpay Account ID
- Razorpay API Key
- Razorpay API Secret
- Your bank account linked to Razorpay

### 3. Costs
- Setup: FREE
- Per Payout: ₹3-5 (depending on volume)
- No monthly fees
- No hidden charges

## Step-by-Step Setup

### Step 1: Create Razorpay Account

```
1. Visit: https://dashboard.razorpay.com/signup
2. Enter business details
3. Verify email and phone
4. Complete KYC (takes 24-48 hours)
5. Add bank account for payouts
```

### Step 2: Get API Credentials

```
1. Login to Razorpay Dashboard
2. Go to Settings → API Keys
3. Generate Test Keys (for testing)
4. Generate Live Keys (for production)
5. Copy and save securely:
   - Key ID: rzp_test_xxxxxxxxxxxxx
   - Key Secret: xxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Configure in HRMS

Create a file: `backend/.env` and add:

```env
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
RAZORPAY_ACCOUNT_NUMBER=your_account_number
RAZORPAY_MODE=test  # Change to 'live' for production
```

### Step 4: Install Dependencies

Run these commands in your backend directory:

```bash
# For Python backend
pip install razorpay

# Update requirements.txt
echo "razorpay==1.3.0" >> requirements.txt
```

### Step 5: Test Mode First

**IMPORTANT:** Always test with test mode first!

```
Test Mode Features:
- No real money transferred
- Test with dummy bank accounts
- Verify integration works
- Check error handling

Once verified, switch to Live Mode
```

## How It Works

### Payment Flow

```
1. HR processes payroll in HRMS
   ↓
2. HR selects employees to pay
   ↓
3. HR clicks "Pay Selected"
   ↓
4. System sends request to Razorpay
   ↓
5. Razorpay debits your account
   ↓
6. Razorpay credits employee accounts
   ↓
7. System receives confirmation
   ↓
8. HRMS updates status to PAID
   ↓
9. Transaction ID saved for reference
```

### Security Features

1. **API Authentication**: Secure key-based auth
2. **HTTPS Only**: All requests encrypted
3. **Webhook Verification**: Confirms genuine responses
4. **Transaction Limits**: Set daily/per-transaction limits
5. **Approval Workflow**: Optional multi-level approval

## Testing

### Test Bank Accounts (Razorpay Provides)

```
For Testing Success:
Account Number: 1234567890
IFSC Code: SBIN0007105
Account Holder: Test Account

For Testing Failure:
Account Number: 0987654321
IFSC Code: HDFC0000001
Account Holder: Fail Test
```

### Test Scenarios

1. **Single Payout**
   - Select one employee
   - Click Pay
   - Verify success message
   - Check Razorpay dashboard

2. **Bulk Payout**
   - Select multiple employees
   - Click Pay Selected
   - Verify all processed
   - Check transaction IDs

3. **Failed Payout**
   - Use test failure account
   - Verify error handling
   - Check status remains PENDING

4. **Insufficient Balance**
   - Test with amount > balance
   - Verify proper error message

## Going Live

### Checklist Before Production

- [ ] KYC completed and approved
- [ ] Bank account verified
- [ ] Test mode thoroughly tested
- [ ] Live API keys generated
- [ ] Environment variables updated
- [ ] Transaction limits configured
- [ ] Webhook URL configured
- [ ] Error notifications setup
- [ ] Backup plan ready

### Switch to Live Mode

```env
# Update backend/.env
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
RAZORPAY_MODE=live
```

## Features Enabled

### 1. Real-Time Transfers
- Money transferred within minutes
- IMPS/NEFT/RTGS supported
- Works 24/7 including holidays

### 2. Bulk Payouts
- Process up to 100 employees at once
- Automatic retry on failure
- Detailed status for each transfer

### 3. Transaction History
- All transactions logged
- Download statements
- Reconciliation reports

### 4. Automatic Reconciliation
- Auto-update payment status
- Transaction ID tracking
- Failed payment alerts

## Pricing

### Razorpay Payout Charges

```
Volume per Month          Cost per Payout
0 - 100 payouts          ₹5
101 - 1,000 payouts      ₹4
1,001 - 10,000 payouts   ₹3
10,000+ payouts          Custom pricing
```

### Example Calculation

```
50 employees × ₹5 = ₹250 per month
vs
Manual process time: 2 hours × ₹500/hour = ₹1,000

Savings: ₹750 + time saved!
```

## Support

### Razorpay Support
- Email: support@razorpay.com
- Phone: 1800-102-0555
- Dashboard: Live chat available
- Docs: https://razorpay.com/docs/payouts/

### Common Issues

**Issue 1: Payout Failed**
- Check employee bank details
- Verify IFSC code
- Ensure sufficient balance
- Check Razorpay dashboard for details

**Issue 2: Webhook Not Received**
- Verify webhook URL is accessible
- Check firewall settings
- Verify webhook signature

**Issue 3: Insufficient Balance**
- Add funds to Razorpay account
- Link additional bank accounts
- Set up auto-reload

## Security Best Practices

1. **Never commit API keys to Git**
2. **Use environment variables**
3. **Enable IP whitelisting**
4. **Set transaction limits**
5. **Enable 2FA on Razorpay account**
6. **Regular security audits**
7. **Monitor unusual activity**

## Compliance

### Legal Requirements
- Maintain transaction records for 7 years
- TDS deduction before payout
- PF/ESI compliance
- Professional tax handling

### Razorpay Handles
- Payment gateway compliance
- Banking regulations
- Security standards
- Data protection

## Next Steps

1. **Create Razorpay Account** (if not done)
2. **Complete KYC** (takes 24-48 hours)
3. **Get API Keys** (test mode first)
4. **I'll integrate the code** (next step)
5. **Test thoroughly** (use test mode)
6. **Go live** (when ready)

## Ready to Proceed?

Once you have:
✅ Razorpay account created
✅ KYC completed (or in progress)
✅ API keys ready

I'll integrate the payment functionality into your HRMS!

**Note:** You can start with test mode immediately while KYC is being processed.
