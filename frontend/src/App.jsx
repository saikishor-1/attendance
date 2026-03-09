import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Users,
  CheckCircle,
  XCircle,
  Clock,
  LayoutDashboard,
  FileText,
  MessageSquare,
  Search,
  Filter,
  Save,
  Menu,
  ChevronRight,
  User,
  BookOpen
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

function App() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [activeTab, setActiveTab] = useState('mark'); // 'mark', 'summary', 'report'
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [attendanceData, setAttendanceData] = useState({}); // {student_id: {status, time_in, time_out}}
  const [searchTerm, setSearchTerm] = useState('');
  const [historyData, setHistoryData] = useState([]);
  const [offlineQueue, setOfflineQueue] = useState([]);

  useEffect(() => {
    fetchCourses();
    const queue = JSON.parse(localStorage.getItem('attendance_sync_queue') || '[]');
    setOfflineQueue(queue);
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      setStudents([]);
      setAttendanceData({});
      setHistoryData([]);
      fetchStudents(selectedCourse.id);
      fetchHistory(selectedCourse.id);
    }
  }, [selectedCourse]);

  const fetchCourses = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/courses/`);
      setCourses(resp.data);
      localStorage.setItem('offline_courses', JSON.stringify(resp.data));
      if (resp.data.length > 0) setSelectedCourse(resp.data[0]);
    } catch (err) {
      console.warn("Offline: Loading courses from cache", err);
      const cached = localStorage.getItem('offline_courses');
      if (cached) {
        const parsed = JSON.parse(cached);
        setCourses(parsed);
        if (parsed.length > 0) setSelectedCourse(parsed[0]);
      }
    }
  };

  const fetchStudents = async (courseId) => {
    setLoading(true);
    try {
      const resp = await axios.get(`${API_BASE}/courses/${courseId}/get_students/`);
      setStudents(resp.data);
      localStorage.setItem(`offline_students_${courseId}`, JSON.stringify(resp.data));

      const initData = {};
      resp.data.forEach(s => {
        initData[s.id] = s.attendance;
      });
      setAttendanceData(initData);
    } catch (err) {
      console.warn("Offline: Loading students from cache", err);
      const cached = localStorage.getItem(`offline_students_${courseId}`);
      if (cached) {
        const parsed = JSON.parse(cached);
        setStudents(parsed);
        const initData = {};
        parsed.forEach(s => {
          initData[s.id] = s.attendance;
        });
        setAttendanceData(initData);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (courseId) => {
    try {
      const resp = await axios.get(`${API_BASE}/courses/${courseId}/attendance_report/`);
      setHistoryData(resp.data);
      localStorage.setItem(`offline_history_${courseId}`, JSON.stringify(resp.data));
    } catch (err) {
      console.warn("Offline: Loading history from cache", err);
      const cached = localStorage.getItem(`offline_history_${courseId}`);
      if (cached) {
        setHistoryData(JSON.parse(cached));
      }
    }
  };

  const handleAttendanceChange = (studentId, field, value) => {
    setAttendanceData(prev => {
      const newState = { ...prev };

      if (field === 'time_in' || field === 'time_out') {
        // Update the time for ALL students
        students.forEach(s => {
          const sData = newState[s.id] || { status: 'Present', time_in: '09:00', time_out: '10:00' };
          newState[s.id] = { ...sData, [field]: value };
        });
      } else {
        // Normal update for a single student (e.g. status changes)
        const updatedRecord = { ...(newState[studentId] || { status: 'Present', time_in: '09:00', time_out: '10:00' }), [field]: value };
        if (field === 'status' && value !== 'Present') {
          updatedRecord.time_in = '';
          updatedRecord.time_out = '';
        } else if (field === 'status' && value === 'Present') {
          updatedRecord.time_in = '09:00';
          updatedRecord.time_out = '10:00';
        }
        newState[studentId] = updatedRecord;
      }

      return newState;
    });
  };

  const markAllPresent = () => {
    const newData = { ...attendanceData };
    students.forEach(s => {
      newData[s.id] = { ...newData[s.id], status: 'Present', time_in: '09:00', time_out: '10:00' };
    });
    setAttendanceData(newData);
  };

  const submitAttendance = async () => {
    if (!selectedCourse) return;

    const records = students.map(s => {
      const data = attendanceData[s.id] || {};
      return {
        student_id: s.id,
        status: data.status || 'Present',
        time_in: data.status === 'Present' ? (data.time_in || '09:00') : null,
        time_out: data.status === 'Present' ? (data.time_out || '10:00') : null
      };
    });

    const payload = {
      records: records,
      course_id: selectedCourse.id,
      recorded_by: selectedCourse.faculty_name,
      date: new Date().toISOString().split('T')[0]
    };

    try {
      await axios.post(`${API_BASE}/attendance/bulk_mark_attendance/`, payload);
      alert('Attendance Submitted Successfully!');
      fetchHistory(selectedCourse.id);
      setActiveTab('report');
    } catch (err) {
      console.warn("Offline: Queueing attendance for later", err);
      const queue = JSON.parse(localStorage.getItem('attendance_sync_queue') || '[]');
      queue.push(payload);
      localStorage.setItem('attendance_sync_queue', JSON.stringify(queue));
      setOfflineQueue(queue);
      alert('You are offline! Attendance saved locally and queued for sync.');
      setActiveTab('report');
    }
  };

  const popSyncQueue = async () => {
    const queue = JSON.parse(localStorage.getItem('attendance_sync_queue') || '[]');
    if (queue.length === 0) return;

    let successCount = 0;
    for (const payload of queue) {
      try {
        await axios.post(`${API_BASE}/attendance/bulk_mark_attendance/`, payload);
        successCount++;
      } catch (e) {
        console.error("Failed to sync a payload", e);
      }
    }

    const remaining = queue.slice(successCount);
    localStorage.setItem('attendance_sync_queue', JSON.stringify(remaining));
    setOfflineQueue(remaining);

    if (successCount > 0) {
      alert(`Synchronized ${successCount} offline attendance sessions!`);
      if (selectedCourse) fetchHistory(selectedCourse.id);
    } else {
      alert("Sync failed. Check your internet connection.");
    }
  };

  const generateWhatsApp = async () => {
    try {
      const resp = await axios.post(`${API_BASE}/attendance/generate_whatsapp_report/`, {
        course_id: selectedCourse.id
      });
      const encodedMsg = encodeURIComponent(resp.data.message);
      window.open(`https://web.whatsapp.com/send?text=${encodedMsg}`, '_blank');
    } catch (err) {
      console.error("Error generating WhatsApp report", err);
    }
  };

  const resetAttendance = async () => {
    if (!window.confirm("Are you sure you want to reset today's attendance for this course? This cannot be undone.")) return;
    try {
      await axios.post(`${API_BASE}/attendance/reset_attendance/`, {
        course_id: selectedCourse.id
      });
      fetchStudents(selectedCourse.id);
      fetchHistory(selectedCourse.id);
    } catch (err) {
      console.error("Error resetting attendance", err);
    }
  };

  const filteredStudents = students.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.register_number.includes(searchTerm)
  );

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <CheckCircle size={32} color="#22d3ee" />
          <span>ATTENDLY</span>
        </div>

        <div className="nav-links">
          <div
            className={`nav-item ${activeTab === 'mark' ? 'active' : ''}`}
            onClick={() => setActiveTab('mark')}
          >
            <Users size={20} />
            <span>Mark Attendance</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            <LayoutDashboard size={20} />
            <span>Summary</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            <FileText size={20} />
            <span>Detailed Report</span>
          </div>
        </div>

        <div style={{ marginTop: 'auto' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'block', marginBottom: '0.5rem' }}>
            Select Course
          </label>
          <select
            style={{ width: '100%' }}
            value={selectedCourse?.id || ''}
            onChange={(e) => setSelectedCourse(courses.find(c => c.id === parseInt(e.target.value)))}
          >
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.course_code} - {c.course_name}</option>
            ))}
          </select>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <div className="title">
            {activeTab === 'mark' ? 'Mark Attendance' : activeTab === 'summary' ? 'Attendance Summary' : 'Student Reports'}
          </div>
          <p className="subtitle">
            {selectedCourse?.course_name} | {selectedCourse?.faculty_name}
          </p>
        </header>

        {/* Dashboard Stats (Show on all tabs) */}
        {(() => {
          const total_students = students.length;
          const present_count = students.filter(s => attendanceData[s.id]?.status === 'Present').length;
          const absent_count = students.filter(s => attendanceData[s.id]?.status === 'Absent').length;
          const leave_count = students.filter(s => attendanceData[s.id]?.status === 'Leave').length;
          const attendance_percentage = total_students > 0 ? ((present_count / total_students) * 100) : 0;

          return (
            <section className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Total Students</span>
                <span className="stat-value">{total_students}</span>
              </div>
              <div className="stat-card" style={{ borderLeft: '4px solid var(--success)' }}>
                <span className="stat-label">Present</span>
                <span className="stat-value">{present_count}</span>
              </div>
              <div className="stat-card" style={{ borderLeft: '4px solid var(--danger)' }}>
                <span className="stat-label">Absent</span>
                <span className="stat-value">{absent_count}</span>
              </div>
              <div className="stat-card" style={{ background: 'var(--primary-gradient)' }}>
                <span className="stat-label" style={{ color: 'white' }}>Percentage</span>
                <span className="stat-value" style={{ color: 'white' }}>
                  {attendance_percentage.toFixed(1)}%
                </span>
              </div>
            </section>
          );
        })()}

        {/* Actions Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          {offlineQueue.length > 0 && (
            <div style={{ background: 'var(--danger)', color: 'white', padding: '0.5rem 1rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, marginRight: '1rem' }}>
              <span>You have {offlineQueue.length} pending offline sessions!</span>
              <button onClick={popSyncQueue} style={{ marginLeft: 'auto', background: 'white', color: 'var(--danger)', border: 'none', padding: '0.25rem 0.75rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Sync Now</button>
            </div>
          )}
        </div>

        {activeTab === 'mark' && (
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={18} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-secondary)' }} />
              <input
                placeholder="Search by name or register number..."
                style={{ width: '100%', paddingLeft: '40px' }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" onClick={submitAttendance}>
              <Save size={18} />
              Submit Attendance
            </button>
            <button className="btn btn-outline" onClick={markAllPresent}>Mark All Present</button>
            <button className="btn btn-outline" onClick={resetAttendance} style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}>Reset Today</button>
            <button className="btn btn-outline" onClick={generateWhatsApp}>
              <MessageSquare size={18} />
              WhatsApp
            </button>
          </div>
        )}

        {/* Attendance Table */}
        <div className="table-container animate-fade">
          <table>
            <thead>
              <tr>
                <th>S.No</th>
                <th>Register No</th>
                <th>Student Name</th>
                <th>Status</th>
                <th>Time In</th>
                <th>Time Out</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((s, idx) => {
                const data = attendanceData[s.id] || { status: '', time_in: '09:00', time_out: '10:00' };
                return (
                  <tr key={s.id}>
                    <td>{idx + 1}</td>
                    <td><span className="reg-no">{s.register_number.split('_')[0]}</span></td>
                    <td><div style={{ fontWeight: '600' }}>{s.name}</div><div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>24S08</div></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.25rem' }}>
                        <button
                          className={`badge ${data.status === 'Present' ? 'badge-present' : 'btn-outline'}`}
                          onClick={() => handleAttendanceChange(s.id, 'status', 'Present')}
                          style={{ padding: '0.2rem 0.5rem', cursor: 'pointer', border: 'none' }}
                        >
                          Present ✓
                        </button>
                        <button
                          className={`badge ${data.status === 'Absent' ? 'badge-absent' : 'btn-outline'}`}
                          onClick={() => handleAttendanceChange(s.id, 'status', 'Absent')}
                          style={{ padding: '0.2rem 0.5rem', cursor: 'pointer', border: 'none' }}
                        >
                          Absent ✗
                        </button>
                        <button
                          className={`badge ${data.status === 'Leave' ? 'badge-leave' : 'btn-outline'}`}
                          onClick={() => handleAttendanceChange(s.id, 'status', 'Leave')}
                          style={{ padding: '0.2rem 0.5rem', cursor: 'pointer', border: 'none' }}
                        >
                          Leave ⊙
                        </button>
                      </div>
                    </td>
                    <td>
                      <input
                        type="time"
                        value={data.time_in}
                        disabled={data.status !== 'Present'}
                        onChange={(e) => handleAttendanceChange(s.id, 'time_in', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="time"
                        value={data.time_out}
                        disabled={data.status !== 'Present'}
                        onChange={(e) => handleAttendanceChange(s.id, 'time_out', e.target.value)}
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Absentees Section */}
        {(() => {
          const absentees = students.filter(s => attendanceData[s.id]?.status === 'Absent');
          if (activeTab === 'mark' && absentees.length > 0) {
            return (
              <div className="table-container animate-fade" style={{ marginTop: '2rem', padding: '1.5rem' }}>
                <h3 style={{ marginBottom: '1rem', color: 'var(--danger)' }}><XCircle size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> Absentees List</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                  {absentees.map(s => (
                    <div key={`absent-${s.id}`} style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                      <div style={{ fontWeight: 'bold' }}>{s.name}</div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }} className="reg-no">{s.register_number.split('_')[0]}</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          }
          return null;
        })()}

        {/* Detailed Report / History Section */}
        {activeTab === 'report' && (
          <div className="table-container animate-fade">
            <h3 style={{ padding: '1.5rem', margin: 0, borderBottom: '1px solid var(--glass-border)' }}>Class History</h3>
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Student Name</th>
                  <th>Register No</th>
                  <th>Status</th>
                  <th>Time In</th>
                  <th>Time Out</th>
                </tr>
              </thead>
              <tbody>
                {historyData.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>No history found for this course.</td>
                  </tr>
                ) : (
                  historyData.slice().reverse().map(record => (
                    <tr key={record.id}>
                      <td>{record.date}</td>
                      <td><div style={{ fontWeight: '600' }}>{record.student_name}</div></td>
                      <td><span className="reg-no">{record.register_number.split('_')[0]}</span></td>
                      <td>
                        <span className={`badge badge-${record.status.toLowerCase()}`}>
                          {record.status}
                        </span>
                      </td>
                      <td>{record.time_in || '-'}</td>
                      <td>{record.time_out || '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
