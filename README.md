# RBIS HRMS - Human Resource Management System

A comprehensive, clean, and professional HRMS application for managing employees, attendance, leaves, payroll, and more.

## ✨ Features

### 👥 Employee Management
- Complete employee master data management
- Role-based access control (Super Admin, CEO, HR, Employee)
- Employee profiles with bank details and documents
- Department and designation management

### 📊 Attendance Management
- Biometric attendance file upload support
- Real-time attendance tracking and analytics
- Daily, weekly, and monthly reports
- Visual dashboards with charts and graphs


### 🏖️ Leave Management
- Multiple leave types (Casual, Sick, Earned, etc.)
- Leave request and approval workflow (HR → CEO)
- Leave balance tracking
- Holiday calendar management
- Leave history and reports

### 💰 Payroll Management
- Automated salary calculations
- Deduction management (PF, ESI, TDS, etc.)

- Payslip generation and download (PDF)
- Salary structure templates

### 📢 Communication
- Company-wide announcements
- Real-time notifications
- Email integration for important updates
- In-app notification center

### 📈 Analytics & Reports
- Interactive dashboards
- Attendance trends and patterns
- Leave utilization reports
- Payroll summaries
- Export capabilities (Excel, PDF)

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+** and **npm** (Frontend)
- **SQL Server LocalDB** or **SQL Server Express**
- **Angular CLI** (`npm install -g @angular/cli`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rbis-hrms-main
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # From project root
   python backend/reset_system.py
   ```
   This will:
   - Create all database tables
   - Seed admin users (Super Admin, CEO, HR)
   - Import employees from Excel
   - Add 2026 holidays

5. **Verify Installation**
   ```bash
   python verify.py
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```
Backend will run on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
ng serve
```
Frontend will run on: `http://localhost:4200`

### Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | superadmin@rbistech.com | Rbis@123 |
| CEO | ceo@rbistech.com | Rbis@123 |
| HR | hr@rbistech.com | Rbis@123 |

## 📁 Project Structure

```
rbis-hrms-main/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access layer
│   │   ├── schemas/        # Pydantic schemas
│   │   └── core/           # Core configurations
│   ├── main.py             # Application entry point
│   └── reset_system.py     # Database reset script
├── frontend/               # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # UI components
│   │   │   └── services/   # API services
│   │   └── assets/         # Static assets
│   └── package.json
├── files/                  # Data files
│   ├── Employee_Details.xlsx
│   └── Attendance files
├── cleanup.py              # Project cleanup script
├── verify.py               # Installation verification
└── README.md
```

## 🎨 UI/UX Highlights

- **Modern Design**: Clean, professional interface with smooth animations
- **Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Dark Mode Support**: Eye-friendly color schemes
- **Interactive Charts**: Real-time data visualization using Chart.js
- **Intuitive Navigation**: Easy-to-use menu system
- **Professional Color Scheme**:
  - Present: Dark Blue (#1e3a5f)
  - Absent: Gray (#9e9e9e)
  - Leave: Orange (#ffa500)

## 🔧 Configuration

### Backend (.env)
```env
DATABASE_URL=mssql+pyodbc://...
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=480
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Frontend (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

## 📝 Common Tasks

### Reset Database
```bash
python backend/reset_system.py
```

### Clean Project
```bash
python cleanup.py
```
Removes:
- Python cache files (__pycache__)
- Test files (*.spec.ts)
- Temporary files

### Verify Installation
```bash
python verify.py
```

### Add New Employee
1. Login as HR or Super Admin
2. Navigate to "Employee Master Management"
3. Click "Add New Employee"
4. Fill in details and save

### Upload Attendance
1. Login as HR or Super Admin
2. Navigate to "Attendance Operations"
3. Click "Upload Attendance File"
4. Select Excel file and upload

### Process Payroll
1. Navigate to "Payroll Management"
2. Select month and year
3. Click "Generate Payroll"
4. Review and approve

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Passlib** - Password hashing
- **Python-Jose** - JWT token handling
- **Pandas** - Excel file processing

### Frontend
- **Angular 18** - Frontend framework
- **TypeScript** - Type-safe JavaScript
- **Chart.js** - Data visualization
- **Lucide Icons** - Modern icon library
- **RxJS** - Reactive programming

### Database
- **SQL Server LocalDB** - Development database
- **SQL Server** - Production database

## 📊 Key Metrics

- **30+ Employees** managed
- **11 Holidays** configured for 2026
- **Multiple Leave Types** supported
- **Automated Payroll** processing
- **Real-time Analytics** and reporting

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- CORS protection
- Rate limiting
- OTP verification for password reset

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1920x1080 and above)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667 and above)

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if SQL Server is running
# Verify .env configuration
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database connection issues
```bash
# Verify SQL Server LocalDB is installed
sqllocaldb info
# Recreate database
python backend/reset_system.py
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run `python verify.py` to diagnose issues
3. Review application logs in `backend/logs/`

## 📄 License

Proprietary - RBIS Tech Pvt Ltd

## 🎯 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] Biometric device integration
- [ ] Advanced analytics with AI/ML
- [ ] Multi-language support
- [ ] Cloud deployment (Azure/AWS)
- [ ] Performance appraisal module
- [ ] Recruitment management

---

**Made with ❤️ by RBIS Tech Pvt Ltd**
