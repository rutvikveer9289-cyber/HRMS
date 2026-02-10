"""
Database Migration: Add Razorpay Transaction Fields
Adds transaction_id and utr_number to payroll_records table
"""

# Run this SQL in your database to add the new fields

ALTER_TABLE_SQL = """
-- Add transaction tracking fields to payroll_records table
ALTER TABLE payroll_records 
ADD COLUMN transaction_id VARCHAR(100) NULL COMMENT 'Razorpay payout ID for tracking';

ALTER TABLE payroll_records 
ADD COLUMN utr_number VARCHAR(50) NULL COMMENT 'Unique Transaction Reference from bank';

-- Create index for faster lookups
CREATE INDEX idx_payroll_transaction_id ON payroll_records(transaction_id);
CREATE INDEX idx_payroll_utr_number ON payroll_records(utr_number);
"""

# For SQLite (if using SQLite)
SQLITE_SQL = """
-- SQLite doesn't support ADD COLUMN with COMMENT, so use this instead
ALTER TABLE payroll_records ADD COLUMN transaction_id VARCHAR(100);
ALTER TABLE payroll_records ADD COLUMN utr_number VARCHAR(50);

CREATE INDEX idx_payroll_transaction_id ON payroll_records(transaction_id);
CREATE INDEX idx_payroll_utr_number ON payroll_records(utr_number);
"""

if __name__ == "__main__":
    print("=" * 70)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 70)
    print("\nThis migration adds Razorpay transaction tracking fields")
    print("\nFor MySQL/PostgreSQL, run:")
    print("-" * 70)
    print(ALTER_TABLE_SQL)
    print("\nFor SQLite, run:")
    print("-" * 70)
    print(SQLITE_SQL)
    print("=" * 70)
