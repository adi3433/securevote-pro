# SecureVote Pro 🗳️

**Advanced Electronic Voting System with JWT Authentication & 2FA**

A production-ready voting system demonstrating practical application of data structures, cryptographic security, and modern web development. Built for B.Tech final year project showcasing real-world software engineering practices.

---

## ✨ Key Features

### 🔐 **Security First**
- **JWT Authentication** with role-based access control
- **Two-Factor Authentication** via email OTP
- **Cryptographic Ballot Hashing** for tamper evidence
- **Salted Password Storage** and secure session management

### 🏗️ **Advanced Data Structures**
- **Hash Tables**: O(1) voter registry and eligibility checking
- **Merkle Trees**: Tamper-evident ballot logging with O(log n) proofs  
- **Bloom Filters**: Fast duplicate detection with configurable error rates
- **Audit Stack**: LIFO operations for demo undo functionality

### 🎯 **Core Functionality**
- **Dual Interface**: Separate admin dashboard and voter portal
- **OTAC System**: One-Time Access Codes for secure voting
- **Real-time Results** with comprehensive audit trails
- **Email Integration** for 2FA OTP delivery

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Gmail account (for 2FA emails)

### Installation
```bash
# Clone repository
git clone https://github.com/adi3433/securevote-pro.git
cd securevote-pro

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Gmail SMTP credentials

# Run application
python main.py
```

### Access Points
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎭 User Roles

### 👨‍💼 **Admin Dashboard**
- Register voters via CSV upload
- Issue OTACs to eligible voters
- Monitor real-time voting statistics
- Generate audit reports and Merkle proofs
- **Login**: `admin` / `admin123`

### 🗳️ **Voter Portal**  
- Secure 2FA login with email OTP
- Cast votes using OTAC tokens
- Receive cryptographic vote receipts
- **Login**: `voter` / `voter123` + email

---

## ⚙️ Configuration

### Environment Setup
```env
# Production Settings
DEVELOPMENT_MODE=false
DEMO_MODE=false

# Security
SECRET_KEY=your-secure-jwt-secret

# Gmail SMTP (for 2FA)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Database
DATABASE_URL=sqlite:///./voting_system.db
```

### Gmail App Password Setup
1. Enable 2-Step Verification in Google Account
2. Generate App Password: Account → Security → App passwords
3. Use the 16-character password in `SMTP_PASSWORD`

---

## 🏛️ Architecture

### Backend Stack
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Database ORM with SQLite
- **JWT**: Secure token-based authentication
- **SMTP**: Email integration for 2FA

### Frontend
- **Responsive Design**: Modern CSS with mobile support
- **Real-time Updates**: Dynamic voting interface
- **Security UX**: Clear 2FA flow and vote confirmation

### Data Structures Implementation
```python
# Hash Tables for O(1) voter lookup
voter_registry = HashTable()

# Merkle Trees for ballot integrity
ballot_tree = MerkleTree()

# Bloom Filters for duplicate detection  
duplicate_filter = BloomFilter(size=100000, hash_count=7)

# Audit Stack for demo operations
audit_stack = AuditStack()
```

---

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User authentication with 2FA
- `POST /auth/verify-otp` - Complete 2FA verification

### Admin Operations
- `POST /admin/register-voters` - Bulk voter registration
- `POST /admin/issue-otacs` - Generate access codes
- `GET /admin/results` - Voting results
- `GET /admin/audit-trail` - System audit logs

### Voter Operations
- `POST /voter/cast-vote` - Submit ballot with OTAC
- `GET /generate-proof/{ballot_hash}` - Merkle proof verification

---

## 🧪 Testing & Demo

### Demo Mode Features
- **Undo Operations**: Demonstrate audit stack functionality
- **Sample Data**: Pre-loaded voters and candidates
- **Educational Logging**: Detailed operation tracking

### Performance Metrics
- **Voter Lookup**: O(1) average case
- **Ballot Verification**: O(log n) Merkle proofs
- **Concurrent Users**: Multi-user support
- **Security**: Cryptographic integrity

---

## 🔒 Security Model

### Authentication Flow
1. **User Login** → JWT token issued
2. **Voter 2FA** → Email OTP verification  
3. **Role Validation** → Admin/Voter access control
4. **Session Management** → Secure token handling

### Cryptographic Security
- **SHA-256 Hashing** for ballot integrity
- **Salted Storage** for voter credentials
- **Merkle Proofs** for tamper evidence
- **JWT Signing** for session security

---

## 🎓 Academic Value

### Data Structures Demonstrated
- **Hash Tables**: Efficient voter registry
- **Merkle Trees**: Blockchain-inspired integrity
- **Bloom Filters**: Probabilistic duplicate detection
- **Stacks**: Audit trail management

### Software Engineering Practices
- **Clean Architecture**: Modular, maintainable code
- **Security by Design**: Authentication, authorization, encryption
- **API Design**: RESTful endpoints with documentation
- **Configuration Management**: Environment-based settings

---

## 📝 License & Disclaimer

**MIT License** - Open source for educational use

**⚠️ Educational Purpose**: This system demonstrates voting concepts for academic projects. Production elections require additional security audits, legal compliance, and professional deployment practices.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open Pull Request

---

**Built with ❤️ for B.Tech Computer Science | Showcasing Data Structures in Real-World Applications**
