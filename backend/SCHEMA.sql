-- RBIS HRMS Database Schema (MS SQL Server)
-- Database Name: HRMS

USE [master];
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'HRMS')
BEGIN
    CREATE DATABASE [HRMS];
END
GO

USE [HRMS];
GO

-- 1. Employees Table
CREATE TABLE employees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) UNIQUE,
    full_name VARCHAR(200),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(150) UNIQUE,
    designation VARCHAR(100),
    password_hash VARCHAR(255),
    is_verified BIT DEFAULT 0,
    verification_code VARCHAR(10),
    otp_code VARCHAR(10),
    otp_created_at DATETIME,
    otp_purpose VARCHAR(20),
    role VARCHAR(50) DEFAULT 'EMPLOYEE',
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT GETDATE()
);
CREATE INDEX ix_employees_emp_id ON employees (emp_id);
CREATE INDEX ix_employees_email ON employees (email);
GO

-- 2. Attendance Table
CREATE TABLE attendance (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    first_in VARCHAR(50),
    last_out VARCHAR(50),
    in_duration VARCHAR(100),
    out_duration VARCHAR(100),
    total_duration VARCHAR(100),
    punch_records VARCHAR(2000),
    attendance_status VARCHAR(50),
    employee_name VARCHAR(200),
    source_file VARCHAR(255),
    is_manually_corrected BIT DEFAULT 0,
    corrected_by VARCHAR(100),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);
CREATE INDEX ix_attendance_emp_id ON attendance (emp_id);
CREATE INDEX ix_attendance_date ON attendance (date);
GO

-- 3. File Uploads Table
CREATE TABLE file_uploads (
    id INT IDENTITY(1,1) PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_at DATETIME DEFAULT GETDATE(),
    uploaded_by VARCHAR(50),
    report_type VARCHAR(100),
    file_hash VARCHAR(64) UNIQUE,
    file_path VARCHAR(500)
);
GO

-- 4. Leave Types Table
CREATE TABLE leave_types (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    annual_quota INT DEFAULT 12,
    is_paid BIT DEFAULT 1,
    allow_carry_forward BIT DEFAULT 0,
    is_active BIT DEFAULT 1
);
GO

-- 5. Leave Balances Table
CREATE TABLE leave_balances (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50),
    leave_type_id INT,
    year INT,
    allocated INT,
    used INT DEFAULT 0,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(id) ON DELETE CASCADE
);
CREATE INDEX ix_leave_balances_emp_id ON leave_balances (emp_id);
GO

-- 6. Leave Requests Table
CREATE TABLE leave_requests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50),
    leave_type_id INT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INT,
    reason VARCHAR(500),
    status VARCHAR(20) DEFAULT 'PENDING',
    hr_remarks VARCHAR(500),
    ceo_remarks VARCHAR(500),
    attachment_path VARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(id) ON DELETE CASCADE
);
CREATE INDEX ix_leave_requests_emp_id ON leave_requests (emp_id);
GO

-- 7. Leave Approval Logs Table
CREATE TABLE leave_approval_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT,
    approver_id VARCHAR(50),
    action VARCHAR(20),
    remarks VARCHAR(500),
    action_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (request_id) REFERENCES leave_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
GO

-- 8. Holidays Table
CREATE TABLE holidays (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    day VARCHAR(20)
);
GO

-- 9. Salary Structures Table
CREATE TABLE salary_structures (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    basic_salary DECIMAL(10,2) NOT NULL,
    hra DECIMAL(10,2) DEFAULT 0,
    transport_allowance DECIMAL(10,2) DEFAULT 0,
    special_allowance DECIMAL(10,2) DEFAULT 0,
    other_allowances DECIMAL(10,2) DEFAULT 0,
    gross_salary DECIMAL(10,2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    created_by VARCHAR(50),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
CREATE INDEX ix_salary_structures_emp_id ON salary_structures (emp_id);
GO

-- 10. Deduction Types Table
CREATE TABLE deduction_types (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    calculation_type VARCHAR(20) NOT NULL,
    default_value DECIMAL(10,2),
    is_mandatory BIT DEFAULT 0,
    is_active BIT DEFAULT 1
);
GO

-- 11. Employee Deductions Table
CREATE TABLE employee_deductions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    deduction_type_id INT NOT NULL,
    calculation_type VARCHAR(20) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    is_active BIT DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE NULL,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (deduction_type_id) REFERENCES deduction_types(id)
);
CREATE INDEX ix_employee_deductions_emp_id ON employee_deductions (emp_id);
GO

-- 12. Payroll Records Table
CREATE TABLE payroll_records (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    basic_salary DECIMAL(10,2) NOT NULL,
    hra DECIMAL(10,2) DEFAULT 0,
    transport_allowance DECIMAL(10,2) DEFAULT 0,
    special_allowance DECIMAL(10,2) DEFAULT 0,
    other_allowances DECIMAL(10,2) DEFAULT 0,
    overtime_amount DECIMAL(10,2) DEFAULT 0,
    gross_salary DECIMAL(10,2) NOT NULL,
    total_deductions DECIMAL(10,2) DEFAULT 0,
    net_salary DECIMAL(10,2) NOT NULL,
    deduction_details VARCHAR(MAX),
    working_days INT,
    present_days INT,
    absent_days INT,
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'DRAFT',
    processed_at DATETIME,
    processed_by VARCHAR(50),
    payment_date DATE,
    remarks VARCHAR(500),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
    UNIQUE(emp_id, month, year)
);
CREATE INDEX ix_payroll_records_emp_id ON payroll_records (emp_id);
CREATE INDEX ix_payroll_records_month_year ON payroll_records (month, year);
GO

-- 13. Overtime Records Table
CREATE TABLE overtime_records (
    id INT IDENTITY(1,1) PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    regular_hours DECIMAL(5,2) DEFAULT 8.0,
    actual_hours DECIMAL(5,2) NOT NULL,
    overtime_hours DECIMAL(5,2) NOT NULL,
    overtime_rate DECIMAL(5,2) DEFAULT 1.5,
    overtime_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'PENDING',
    approved_by VARCHAR(50),
    approved_at DATETIME,
    remarks VARCHAR(500),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
CREATE INDEX ix_overtime_records_emp_id ON overtime_records (emp_id);
CREATE INDEX ix_overtime_records_date ON overtime_records (date);
GO
