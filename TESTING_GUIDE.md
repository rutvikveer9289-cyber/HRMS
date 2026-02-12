# RBIS HRMS - Comprehensive Testing Guide

## 🎯 Overview
This guide provides step-by-step instructions to test all major features of the RBIS HRMS application.

**Last Updated:** 2026-02-12  
**Application Version:** 2.0.0

---

## 🚀 Pre-Testing Setup

### 1. Backend Server
```powershell
cd d:\HRMS\rbis-hrms-main\backend
.\venv\Scripts\activate
python main.py
```
**Expected:** Server running on `http://localhost:8000`  
**Verify:** Visit `http://localhost:8000` - should show `{"message":"Welcome to RBIS HRMS API","status":"Online"}`

### 2. Frontend Server
```powershell
cd d:\HRMS\rbis-hrms-main\frontend
npm start
```
**Expected:** Angular dev server on `http://localhost:4200`

### 3. Default Admin Credentials
- **Email:** `admin@rbis.com`
- **Password:** `Admin@123`
- **Role:** SUPER_ADMIN

---

## 📋 Module Testing Checklist

### ✅ 1. Authentication & Authorization

#### Test 1.1: Login Flow
1. Navigate to `http://localhost:4200`
2. Enter admin credentials
3. Click "Login"
4. **Expected:** Redirected to dashboard, user menu shows "Super Admin"

#### Test 1.2: Role-Based Access
1. Login as SUPER_ADMIN
2. Verify access to all modules: Dashboard, Attendance, Leave, Payroll, Onboarding
3. **Expected:** All navigation items visible

#### Test 1.3: Profile Management
1. Click user menu → "Profile"
2. Click "Edit Profile"
3. Update bank details (Bank Name, Account No, IFSC)
4. Click "Save Changes"
5. **Expected:** Success notification, changes persisted

---

### ✅ 2. Employee Onboarding

#### Test 2.1: Single Employee Onboarding
1. Navigate to "Onboarding" module
2. System suggests next Employee ID (e.g., RBIS0002)
3. Fill in:
   - First Name: "John"
   - Last Name: "Doe"
   - Phone: "9876543210"
   - Designation: "Software Engineer"
   - Email: Auto-generated (e.g., `johnd@rbistech.com`)
4. Click "Onboard Employee"
5. **Expected:** Success message, form resets, next ID incremented

#### Test 2.2: Bulk Upload (Optional)
1. Click "Download Template"
2. Fill Excel with multiple employees
3. Upload via "Upload Employee Master"
4. **Expected:** Batch processing success message

---

### ✅ 3. Attendance Management

#### Test 3.1: File Upload
1. Navigate to "Attendance" module
2. Click "Upload Files"
3. Select attendance report file (In/Out Duration Report format)
4. **Expected:** 
   - File processed successfully
   - Records appear in attendance table
   - Status badges show: Present (Green), Half Day (Orange), Absent (Red), On Leave (Blue)

#### Test 3.2: Attendance Record Validation
1. Check uploaded records
2. Verify:
   - Employee IDs match format `RBISxxxx`
   - Dates are correct
   - Duration calculations are accurate
   - Attendance status logic:
     - **Present:** ≥7 hours AND ≥4 punches
     - **Half Day:** ≥3.5 hours but <7 hours
     - **Absent:** <3.5 hours

#### Test 3.3: Manual Edit
1. Click edit icon on any record
2. Change attendance status
3. Save changes
4. **Expected:** Record updated, changes reflected immediately

---

### ✅ 4. Leave Management

#### Test 4.1: Leave Application
1. Navigate to "Leave Management"
2. Go to "Apply Leave" tab
3. Select:
   - Leave Type: "Sick Leave"
   - Start Date: Tomorrow
   - End Date: Tomorrow
   - Reason: "Medical appointment"
4. Click "Apply"
5. **Expected:** 
   - Success message
   - Request appears in "My Requests" with status "PENDING"
   - Balance deducted from available quota

#### Test 4.2: Holiday Exclusion
1. Add a holiday (HR/Admin only):
   - Navigate to Leave → Click "Manage Holidays"
   - Add holiday for next week
2. Apply leave spanning the holiday
3. **Expected:** Holiday automatically excluded from total days requested

#### Test 4.3: HR Approval Flow
1. Login as HR role
2. Navigate to "Leave Management" → "Approvals" tab
3. View pending requests
4. Click "Approve" or "Reject"
5. Add remarks
6. **Expected:** Status changes to "APPROVED_BY_HR" or "REJECTED"

#### Test 4.4: CEO Final Approval
1. Login as CEO role
2. Navigate to "Leave Management" → "Approvals" tab
3. View HR-approved requests
4. Click "Approve" or "Reject"
5. **Expected:** 
   - Status changes to "APPROVED" or "REJECTED"
   - If approved: Attendance records auto-marked as "On Leave"
   - Balance updated

---

### ✅ 5. Payroll Processing

#### Test 5.1: Setup Salary Structure
1. Navigate to "Payroll" → "Salary Management"
2. Select employee
3. Define salary components:
   - Basic Salary
   - HRA
   - Transport Allowance
   - Dearness Allowance
   - Medical Allowance
   - Special Allowance
4. Save structure
5. **Expected:** Gross salary auto-calculated

#### Test 5.2: Setup Deductions
1. Navigate to "Deductions" tab
2. Add deduction type (e.g., "PF - 12%")
3. Assign to employee
4. **Expected:** Deduction appears in employee's deduction list

#### Test 5.3: Process Monthly Payroll
1. Navigate to "Payroll Management"
2. Select month and year
3. Click "Run Payroll for All"
4. **Expected:**
   - Processing starts
   - Payroll records created for all employees
   - Status: "PROCESSED"
   - Attendance summary visible:
     - Present days (including 0.5 for half-days)
     - On Leave days
     - Half days count
     - Absent days

#### Test 5.4: Verify Payroll Calculations
1. Open any payroll record
2. Verify:
   - **Gross Salary** = Basic + All Allowances + Overtime
   - **Net Salary** = Gross - Total Deductions
   - **Attendance Tags:** Shows `20P 2L 1H 2A` format
   - Working days calculation excludes Sundays

#### Test 5.5: Edit Payroll Record
1. Click edit icon on PROCESSED record
2. Modify any allowance or deduction
3. Save changes
4. **Expected:** 
   - Gross and Net recalculated automatically
   - Cannot edit PAID records

#### Test 5.6: Download Payslip
1. Click download icon on any record
2. **Expected:** PDF payslip generated with:
   - Company header
   - Employee details
   - Earnings breakdown
   - Deductions breakdown
   - Net salary
   - Attendance summary

---

### ✅ 6. Payment Processing

#### Test 6.1: Manual Payment Marking
1. Select payroll record with status "PROCESSED"
2. Click "Disburse" button
3. Select payment method (e.g., "Bank Transfer")
4. Enter transaction details
5. Confirm
6. **Expected:** 
   - Status changes to "PAID"
   - Payment date recorded
   - Green checkmark appears

#### Test 6.2: Bulk Payment
1. Select multiple PROCESSED records (checkboxes)
2. Footer shows "X Members Selected"
3. Select payment method from dropdown
4. Click "Disburse Total"
5. **Expected:** 
   - Confirmation dialog
   - All selected records marked as PAID
   - Selection cleared

#### Test 6.3: Razorpay Integration (If Configured)
**Prerequisites:** Valid Razorpay credentials in `.env`

1. Select record with bank details
2. Click "Disburse"
3. Choose "Real Payment via Razorpay"
4. Confirm
5. **Expected:**
   - Real money transfer initiated
   - Transaction ID and UTR recorded
   - Status updated to PAID

---

### ✅ 7. Reporting & History

#### Test 7.1: Master Ledger View
1. Navigate to Payroll Management
2. Click "Master Ledger" button
3. **Expected:**
   - View changes to historical archive
   - Shows all payroll records across all months
   - Columns: Personnel, Disbursed Amount, Payment Session

#### Test 7.2: Employee Leave History
1. Navigate to Leave Management → "Explorer" tab
2. Enter employee ID
3. Click "Search"
4. **Expected:**
   - Shows all leave requests for that employee
   - Displays balances for current year
   - Shows approval history

---

## 🧪 Integration Tests (Backend)

### Run Automated Tests
```powershell
cd d:\HRMS\rbis-hrms-main\backend
.\venv\Scripts\python.exe -m pytest test_leave_system.py
.\venv\Scripts\python.exe test_integration.py
```

### Expected Results
- ✅ Leave system workflow (Apply → HR Approve → CEO Approve)
- ✅ Holiday exclusion in leave calculations
- ✅ Payroll attendance summary (Present, Half, Leave, Absent)
- ✅ Employee onboarding flow

---

## 🔍 Data Validation Checklist

### Attendance Data Quality
- [ ] All Employee IDs follow `RBISxxxx` format
- [ ] No duplicate records for same employee + date
- [ ] Duration calculations are accurate
- [ ] Status logic correctly applied

### Leave Data Integrity
- [ ] No overlapping leave requests
- [ ] Balance never goes negative
- [ ] Approved leaves reflect in attendance
- [ ] Holidays excluded from work days

### Payroll Accuracy
- [ ] Gross = Sum of all earnings
- [ ] Net = Gross - Deductions
- [ ] Attendance days match uploaded records
- [ ] Half-days counted as 0.5
- [ ] On Leave days not counted as Absent

---

## 🐛 Common Issues & Solutions

### Issue 1: Frontend Not Loading
**Solution:** 
```powershell
cd frontend
npm install
npm start
```

### Issue 2: Backend Database Locked
**Solution:** 
```powershell
# Stop backend
# Delete hrms.db.lock if exists
# Restart backend
```

### Issue 3: Attendance File Rejected
**Cause:** Invalid format or missing columns  
**Solution:** Ensure file is "In/Out Duration Report" with required columns:
- S.No, Employee Code, Employee Name, In Duration, Out Duration, Punch Records

### Issue 4: Payroll Not Processing
**Cause:** Missing salary structure  
**Solution:** Define salary structure for all employees before running payroll

### Issue 5: Leave Balance Not Updating
**Cause:** Leave type not initialized  
**Solution:** Run `seed_leave_types.py` to create default leave types

---

## 📊 Performance Benchmarks

### Expected Response Times
- Login: <500ms
- Attendance Upload (100 records): <2s
- Payroll Processing (50 employees): <5s
- Leave Application: <300ms
- PDF Generation: <1s

### Database Size Estimates
- 100 employees, 1 year data: ~50MB
- 500 employees, 1 year data: ~250MB

---

## ✨ New Features Tested (v2.0.0)

### Enhanced Attendance
- ✅ Half-Day detection and tracking
- ✅ On Leave status protection
- ✅ Color-coded status badges

### Smart Leave Management
- ✅ Automatic holiday exclusion
- ✅ Weekend-aware calculations
- ✅ Multi-level approval workflow

### Advanced Payroll
- ✅ Detailed attendance breakdown in records
- ✅ Half-day fractional counting (0.5)
- ✅ Compact attendance tags in UI
- ✅ Razorpay payment integration
- ✅ Professional PDF payslips

---

## 📝 Test Completion Sign-off

| Module | Tested By | Date | Status | Notes |
|--------|-----------|------|--------|-------|
| Authentication | | | ⬜ | |
| Onboarding | | | ⬜ | |
| Attendance | | | ⬜ | |
| Leave Management | | | ⬜ | |
| Payroll Processing | | | ⬜ | |
| Payment Processing | | | ⬜ | |
| Reporting | | | ⬜ | |

---

## 🎓 Training Resources

### For HR Personnel
1. Employee onboarding workflow
2. Attendance file upload and validation
3. Leave approval process
4. Payroll review and correction

### For Finance Team
1. Salary structure management
2. Deduction configuration
3. Payroll processing
4. Payment disbursement
5. Razorpay integration

### For Employees
1. Profile management
2. Leave application
3. Attendance viewing
4. Payslip download

---

## 📞 Support

For technical issues or questions:
- Check backend logs: `d:\HRMS\rbis-hrms-main\backend\logs\`
- Review frontend console (F12 in browser)
- Verify `.env` configuration
- Run integration tests to isolate issues

---

**End of Testing Guide**
