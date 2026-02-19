import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AttendanceService } from '../../services/attendance.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, Chart, registerables } from 'chart.js';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';
import { NotificationService } from '../../services/notification.service';
import { LeaveService } from '../../services/leave.service';
import { StatsGridComponent } from './stats-grid.component';
import { CommunicationService, Announcement } from '../../services/communication.service';

import { AdminService } from '../../services/admin.service';

Chart.register(...registerables);

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule, BaseChartDirective, StatsGridComponent],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit, OnDestroy {
    loading = false;
    hasData = false;
    isAdmin = false;
    canViewAll = false;
    showStatsCards = false;

    // Announcements
    announcements: Announcement[] = [];
    showNoticeModal = false;
    newNotice = { title: '', content: '' };
    isPosting = false;

    // Drill Down State
    showDrillDown = false;
    drillDownTitle = '';
    drillDownList: any[] = [];
    hideTimings = false;

    // Raw Data Storage
    private rawData: any[] = [];
    private filteredData: any[] = [];

    availableDates: string[] = [];
    availableEmps: string[] = [];

    // Selected Filters
    fromDate: string = '';
    toDate: string = '';
    selectedEmp: string = '';
    searchTerm: string = '';

    // UI Metadata
    activeEmployee: any = null;
    allEmployees: any[] = [];

    // Chart Configuration
    public pieChartOptions: ChartOptions<'pie'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
    };

    public barChartOptions: ChartOptions<'bar'> = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { min: 0, stacked: true },
            x: { stacked: true }
        },
        plugins: {
            legend: { display: true },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const index = context.dataIndex;
                        const label = context.dataset.label || '';
                        const val = (context.parsed && typeof context.parsed.y === 'number') ? context.parsed.y : 0;
                        const stats = this.dailyChartStats[index];
                        if (stats) {
                            if (this.activeEmployee) {
                                return `Hours: ${val.toFixed(1)}h`;
                            }
                            const currentSum = stats.present + stats.absent + stats.onLeave;
                            const headCount = this.allEmployees && this.allEmployees.length > 0 ? this.allEmployees.length : currentSum;
                            const lines = [
                                `Status: ${label}`,
                                `---`,
                                `Present: ${stats.present}`,
                                `Absent: ${stats.absent}`
                            ];
                            if (stats.onLeave > 0) lines.push(`On Leave: ${stats.onLeave}`);
                            lines.push(`Total Workforce: ${headCount}`);
                            lines.push(`Avg Hours: ${stats.avgH.toFixed(1)}h`);
                            return lines;
                        }
                        return `${label}: ${val}`;
                    }
                }
            }
        }
    };

    public lineChartOptions: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { min: 0 } },
        plugins: {
            legend: { display: true },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const val = (context.parsed && typeof context.parsed.y === 'number') ? context.parsed.y : 0;
                        return `Avg Hours: ${val.toFixed(1)}h`;
                    }
                }
            }
        }
    };

    public barData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };
    public lineData: ChartConfiguration<'line'>['data'] = { labels: [], datasets: [] };
    public pieData: ChartConfiguration<'pie'>['data'] = { labels: [], datasets: [] };
    showTrendChart = false;

    private subs = new Subscription();

    public stats = {
        present: 0,

        absent: 0,
        onLeave: 0,
        avgHours: 0,
        label: 'Latest'
    };

    private dailyChartStats: any[] = [];
    allHolidays: any[] = [];
    upcomingHolidays: any[] = [];


    constructor(
        private attendanceService: AttendanceService,
        public authService: AuthService,
        private notificationService: NotificationService,
        private leaveService: LeaveService,
        private commService: CommunicationService,
        private adminService: AdminService
    ) { }

    ngOnInit() {
        const user = this.authService.currentUser;
        this.isAdmin = ['SUPER_ADMIN', 'CEO'].includes(this.authService.getUserRole() || '');
        const role = this.authService.getUserRole();
        this.canViewAll = this.isAdmin || role === 'HR' || role === 'CEO';

        this.loadAnnouncements();

        if (!this.canViewAll && user) {
            this.selectedEmp = user.emp_id;
        }

        // Fetch Holidays
        const todayStr = new Date().toISOString().split('T')[0];
        this.leaveService.getHolidays().subscribe(data => {
            this.allHolidays = data;
            this.upcomingHolidays = data.filter((h: any) => String(h.date).split('T')[0] >= todayStr);
            if (this.attendanceService.typeAData.length > 0) this.syncData();
        });



        this.loading = true;

        // Fetch All Employees first to know who is absent
        this.adminService.getEmployees().subscribe(emps => {
            this.allEmployees = emps;
            // If data is already available in service, sync it now
            if (this.attendanceService.typeAData.length > 0 || this.attendanceService.typeBData.length > 0) {
                this.syncData();
                this.loading = false;
            }
        });

        // Listen for data updates
        this.subs.add(this.attendanceService.typeAData$.subscribe(data => {
            if (data && data.length > 0) {
                this.syncData();
                this.loading = false;
            }
        }));

        this.subs.add(this.attendanceService.hasData$.subscribe(has => {
            this.hasData = has;
            if (has) this.loading = false;
        }));

        this.subs.add(this.authService.currentUser$.subscribe(u => {
            if (u) {
                const r = u.role;
                this.isAdmin = r === 'SUPER_ADMIN' || r === 'CEO';
                this.canViewAll = this.isAdmin || r === 'HR' || r === 'CEO';

                if (!this.canViewAll) {
                    this.selectedEmp = u.emp_id;
                    this.applyFilters();
                }
            }
        }));
    }

    private syncTimeout: any;
    syncData() {
        // Debounce sync to avoid double-firing from multiple data subjects
        if (this.syncTimeout) clearTimeout(this.syncTimeout);
        this.syncTimeout = setTimeout(() => this._performSync(), 50);
    }

    private _performSync() {
        const dataA = this.attendanceService.typeAData;
        const dataB = this.attendanceService.typeBData;

        // Unified merge map for high-speed deduplication
        const mergeMap = new Map<string, any>();
        const allRecs = [...dataA, ...dataB];

        for (const rec of allRecs) {
            const dateStr = String(rec.Date).split('T')[0];
            const key = `${rec.EmpID}_${dateStr}`;
            const existing = mergeMap.get(key);

            if (!existing) {
                mergeMap.set(key, { ...rec, Date: dateStr });
            } else {
                // Priority: Merge missing details
                existing.In_Duration = existing.In_Duration || rec.In_Duration;
                existing.Out_Duration = existing.Out_Duration || rec.Out_Duration;
                existing.Total_Duration = existing.Total_Duration || rec.Total_Duration;

                // Priority: Present > On Leave > Absent
                const priority: Record<string, number> = { 'Present': 2, 'On Leave': 1, 'Absent': 0 };
                const currentStatus = rec.Attendance || 'Absent';
                const existingStatus = existing.Attendance || 'Absent';

                if ((priority[currentStatus] || 0) > (priority[existingStatus] || 0)) {
                    existing.Attendance = currentStatus;
                }
            }
        }

        // Optimized Gap Filling: Only process unique dates found in records
        if (this.allEmployees.length > 0) {
            const datesInRecords = new Set<string>();
            mergeMap.forEach(v => datesInRecords.add(v.Date));

            for (const dateStr of datesInRecords) {
                for (const emp of this.allEmployees) {
                    const key = `${emp.EmpID}_${dateStr}`;
                    if (!mergeMap.has(key)) {
                        mergeMap.set(key, {
                            Date: dateStr,
                            EmpID: emp.EmpID,
                            Employee_Name: emp.Name,
                            Attendance: 'Absent',
                            First_In: '--:--',
                            Last_Out: '--:--',
                            In_Duration: '00:00',
                            Total_Duration: '00:00'
                        });
                    } else {
                        const rec = mergeMap.get(key);
                        if (!rec.Employee_Name || rec.Employee_Name === 'Unknown' || rec.Employee_Name === '--') {
                            rec.Employee_Name = emp.Name;
                        }
                    }
                }
            }
        }

        // Final Filter: Efficiency filter for weekends/holidays
        const finalData: any[] = [];
        const holidayMap = new Set(this.allHolidays.map(h => String(h.date).split('T')[0]));

        mergeMap.forEach(rec => {
            const date = new Date(rec.Date);
            const isSunday = date.getDay() === 0;
            const isHoliday = holidayMap.has(rec.Date);

            if (!((isSunday || isHoliday) && rec.Attendance !== 'Present')) {
                finalData.push(rec);
            }
        });

        this.rawData = finalData;
        this.updateFilterOptions();
        this.applyFilters();
    }

    ngOnDestroy() {
        this.subs.unsubscribe();
    }

    updateFilterOptions() {
        const now = new Date();
        const y = now.getFullYear();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        const d = String(now.getDate()).padStart(2, '0');
        const todayStr = `${y}-${m}-${d}`;

        this.availableDates = [...new Set(this.rawData.map(d => String(d.Date).split('T')[0]))]
            .filter(d => d && d !== "null" && d <= todayStr)
            .sort();

        this.availableEmps = [...new Set(this.rawData.map(d => String(d['EmpID'])))]
            .filter(id => id && id !== "null" && id !== "undefined")
            .sort();
    }

    resetFilters() {
        this.fromDate = '';
        this.toDate = '';
        this.searchTerm = '';

        if (this.canViewAll) {
            this.selectedEmp = '';
        } else {
            const user = this.authService.currentUser;
            this.selectedEmp = user?.emp_id || '';
        }
        this.activeEmployee = null;
        this.showStatsCards = false;
        this.applyFilters();
    }

    applyFilters() {
        // Validation: If no filters, show organization-wide for latest date (handled in calculateStats)
        let filtered = [...this.rawData];

        // 1. Date Range Filtering
        if (this.fromDate) {
            const start = this.fromDate;
            const end = this.toDate || this.fromDate; // If "To" is blank, use "From" for single day
            filtered = filtered.filter(d => {
                const dateStr = String(d.Date).split('T')[0];
                return dateStr >= start && dateStr <= end;
            });
        } else {
            // Default: Only past/present dates
            const todayStr = new Date().toISOString().split('T')[0];
            filtered = filtered.filter(d => String(d.Date).split('T')[0] <= todayStr);
        }

        // 2. Employee Filtering
        if (this.selectedEmp) {
            filtered = filtered.filter(d => String(d['EmpID']) === this.selectedEmp);
        } else if (this.searchTerm.trim()) {
            const term = this.searchTerm.trim().toLowerCase();
            filtered = filtered.filter(r => {
                const empIdMatch = (r.EmpID && r.EmpID.toLowerCase() === term);
                const nameMatch = r.Employee_Name && r.Employee_Name.toLowerCase().includes(term);
                return empIdMatch || nameMatch;
            });
        }

        this.filteredData = filtered;

        // 3. Visibility and Metadata
        const isIndividualSearch = this.selectedEmp || (this.searchTerm.trim() && filtered.length > 0 && this.isExactMatch(filtered));
        this.showStatsCards = !!(this.fromDate && !this.toDate) || !!isIndividualSearch;

        if (isIndividualSearch) {
            const firstWithInfo = filtered.find(r => r.Employee_Name);
            if (firstWithInfo) {
                this.activeEmployee = {
                    EmpID: firstWithInfo.EmpID,
                    Name: firstWithInfo.Employee_Name
                };
            } else if (filtered.length > 0) {
                this.activeEmployee = { EmpID: filtered[0].EmpID, Name: 'Unknown Employee' };
            }
        } else {
            this.activeEmployee = null;
        }

        this.calculateStats(filtered);
        this.processChartData(filtered);
    }

    private calculateStats(data: any[]) {
        if (!data || data.length === 0) {
            this.stats = { present: 0, absent: 0, onLeave: 0, avgHours: 0, label: 'No Data' };
            return;
        }

        const dates = [...new Set(data.map(d => String(d.Date).split('T')[0]))].sort();

        if (this.fromDate || this.selectedEmp || this.searchTerm) {
            // Filtered view
            const present = data.filter(d => d.Attendance === 'Present').length;
            const absent = data.filter(d => d.Attendance === 'Absent').length;
            const onLeave = data.filter(d => d.Attendance === 'On Leave').length;

            const hours = data.filter(d => d.Attendance === 'Present')
                .map(r => this.parseDuration(r.Total_Duration || r.In_Duration));
            let avgH = hours.length > 0 ? hours.reduce((a, b) => a + b, 0) / hours.length : 0;
            if (avgH === 0 && present > 0) avgH = 8.0;

            this.stats = {
                present,
                absent,
                onLeave,
                avgHours: avgH,
                label: this.fromDate && !this.toDate ? this.fromDate : 'Filtered'
            };
        } else {
            // Default: Show latest date summary
            const latestDate = dates[dates.length - 1];
            const latestRecords = data.filter(d => String(d.Date).split('T')[0] === latestDate);

            const present = latestRecords.filter(d => d.Attendance === 'Present').length;
            const absent = latestRecords.filter(d => d.Attendance === 'Absent').length;
            const onLeave = latestRecords.filter(d => d.Attendance === 'On Leave').length;

            const hours = latestRecords.filter(d => d.Attendance === 'Present')
                .map(r => this.parseDuration(r.Total_Duration || r.In_Duration));
            let avgH = hours.length > 0 ? hours.reduce((a, b) => a + b, 0) / hours.length : 0;
            if (avgH === 0 && present > 0) avgH = 8.0;

            this.stats = {
                present,
                absent,
                onLeave,
                avgHours: avgH,
                label: 'Latest'
            };
        }
    }

    private processChartData(data: any[]) {
        if (!data || data.length === 0) {
            this.barData = { labels: [], datasets: [] };
            this.lineData = { labels: [], datasets: [] };
            this.pieData = { labels: [], datasets: [] };
            return;
        }

        const labels = [...new Set(data.map(d => String(d.Date).split('T')[0]))].sort();
        this.showTrendChart = labels.length > 1;

        const dailyStats = labels.map(date => {
            const dayRecords = data.filter(d => String(d.Date).split('T')[0] === date);
            const present = dayRecords.filter(d => d.Attendance === 'Present').length;
            const absent = dayRecords.filter(d => d.Attendance === 'Absent').length;
            const onLeave = dayRecords.filter(d => d.Attendance === 'On Leave').length;

            const activeRecords = dayRecords.filter(d => d.Attendance === 'Present');
            const hours = activeRecords.map(r => this.parseDuration(r.Total_Duration || r.In_Duration));
            let avgH = hours.length > 0 ? hours.reduce((a, b) => a + b, 0) / hours.length : 0;
            if (avgH === 0 && present > 0) avgH = 8.0;

            return { date, present, absent, onLeave, avgH };
        });

        this.dailyChartStats = dailyStats;

        // For single employee (ID or specific search match)
        const isSingleEmp = this.selectedEmp || (this.activeEmployee && labels.length > 1);

        this.barData = {
            labels: labels,
            datasets: [
                {
                    data: dailyStats.map(s => isSingleEmp ? (s.present > 0 ? (s.avgH || 8) : 0) : s.present),
                    label: isSingleEmp ? 'Office Hours' : 'Present',
                    backgroundColor: '#1e3a5f',
                    borderRadius: 6,
                    stack: 'attendance'
                },
                {
                    data: dailyStats.map(s => isSingleEmp ? (s.absent > 0 ? 1 : 0) : s.absent),
                    label: 'Absent',
                    backgroundColor: '#9e9e9e',
                    borderRadius: 6,
                    stack: 'attendance'
                },
                {
                    data: dailyStats.map(s => isSingleEmp ? (s.onLeave > 0 ? 1 : 0) : s.onLeave),
                    label: 'On Leave',
                    backgroundColor: '#ffa500',
                    borderRadius: 6,
                    stack: 'attendance'
                }
            ]
        };

        this.lineData = {
            labels: labels,
            datasets: [{
                data: dailyStats.map(s => s.avgH),
                label: 'Avg Hours',
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }]
        };

        // Aggregate Pie Data over ALL filtered results
        const totalPresent = dailyStats.reduce((sum, s) => sum + s.present, 0);
        const totalAbsent = dailyStats.reduce((sum, s) => sum + s.absent, 0);
        const totalLeave = dailyStats.reduce((sum, s) => sum + s.onLeave, 0);

        this.pieData = {
            labels: ['Present', 'Absent', 'On Leave'],
            datasets: [{
                data: [totalPresent, totalAbsent, totalLeave],
                backgroundColor: ['#1e3a5f', '#9e9e9e', '#ffa500'],
                borderWidth: 0
            }]
        };
    }

    private isExactMatch(data: any[]): boolean {
        if (data.length === 0) return false;
        const firstId = data[0].EmpID;
        return data.every((r: any) => r.EmpID === firstId);
    }

    viewStatusDetails(status: string) {
        // Allowed for everyone (individual or admin)

        let targetData = this.filteredData;
        if (!this.fromDate && !this.activeEmployee && !this.selectedEmp) {
            const dates = [...new Set(this.filteredData.map(d => String(d.Date).split('T')[0]))].sort();
            const latestDate = dates[dates.length - 1];
            targetData = this.filteredData.filter(d => String(d.Date).split('T')[0] === latestDate);
        }

        this.drillDownTitle = `${status} List`;
        this.hideTimings = status === 'Absent' || status === 'On Leave';
        this.drillDownList = targetData
            .filter((d: any) => d.Attendance === status)
            .map((d: any) => ({
                Date: String(d.Date).split('T')[0],
                EmpID: d.EmpID,
                Name: d.Employee_Name || '--',
                status: d.Attendance,
                in: d.First_In,
                out: d.Last_Out,
                duration: d.Total_Duration
            }));
        this.showDrillDown = true;
    }

    closeDrillDown() {
        this.showDrillDown = false;
        this.drillDownList = [];
    }

    private parseDuration(d: any): number {
        if (!d) return 0;
        const s = String(d).trim();
        if (s === '' || s === '0' || s.toLowerCase() === 'nan' || s === '00:00') return 0;
        try {
            if (s.includes(':')) {
                const parts = s.split(':').map(Number);
                if (parts.length >= 2) return parts[0] + (parts[1] / 60);
            }
            return isNaN(Number(s)) ? 0 : Number(s);
        } catch { return 0; }
    }

    // Announcement Logic
    loadAnnouncements() {
        this.commService.getAnnouncements().subscribe(data => this.announcements = data);
    }

    toggleNoticeModal() {
        this.showNoticeModal = !this.showNoticeModal;
        if (!this.showNoticeModal) {
            this.newNotice = { title: '', content: '' };
        }
    }

    postAnnouncement() {
        if (!this.newNotice.title || !this.newNotice.content) {
            this.notificationService.showAlert('Please fill all fields', 'error');
            return;
        }
        this.isPosting = true;
        this.commService.postAnnouncement(this.newNotice).subscribe({
            next: () => {
                this.notificationService.showAlert('Announcement posted!', 'success');
                this.loadAnnouncements();
                this.toggleNoticeModal();
                this.isPosting = false;
            },
            error: () => {
                this.notificationService.showAlert('Failed to post announcement', 'error');
                this.isPosting = false;
            }
        });
    }

    deleteAnnouncement(id: number) {
        if (confirm('Are you sure you want to delete this announcement?')) {
            this.commService.deleteAnnouncement(id).subscribe(() => {
                this.notificationService.showAlert('Announcement deleted', 'info');
                this.loadAnnouncements();
            });
        }
    }


}
