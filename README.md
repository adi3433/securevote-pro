# Secure Voting System - B.Tech Final Year Project

A comprehensive voting system demonstration that showcases advanced data structures and algorithms in a practical application. This project implements a secure, auditable voting system with tamper-evident logging and efficient duplicate detection.

## 🎯 Project Overview

This voting system demonstrates the practical application of key data structures taught in computer science courses:

- **Hash Tables**: O(1) voter eligibility and duplicate checking
- **Merkle Trees**: Tamper-evident ballot logging with O(log n) inclusion proofs
- **Bloom Filters**: Fast duplicate pre-checking to reduce database load
- **Stacks**: LIFO audit trail for demo undo operations
- **Lab Algorithms**: Manhattan distance, collinearity checks, triangular numbers

## 🏗️ Architecture

```
Frontend (HTML/JS/Tailwind) ↔ Backend (FastAPI/Python) ↔ Database (PostgreSQL) + Cache (Redis)
                                        ↓
                            Data Structures Layer
                    ┌─────────────────────────────────┐
                    │ Hash Tables │ Merkle Tree │ Stack │
                    │ Bloom Filter│ Lab Utils   │ Crypto│
                    └─────────────────────────────────┘
```

## 🚀 Features

### Core Voting Features
- **Voter Registration**: Secure salted hash storage of voter IDs
- **OTAC System**: One-time access codes for anonymous voting
- **Ballot Casting**: Cryptographically secure vote recording
- **Real-time Results**: Live tally with tamper-evident Merkle root
- **Audit Trail**: Complete system event logging

### Security Features
- **Salted Hashing**: Voter privacy protection
- **Merkle Proofs**: Ballot inclusion verification
- **Bloom Filter**: Fast duplicate detection
- **Demo Undo**: Stack-based operation reversal (demo mode only)

### Data Structure Demonstrations
- **O(1) Operations**: Hash table voter lookups
- **O(log n) Proofs**: Merkle tree inclusion proofs
- **Constant Space**: Bloom filter with configurable error rates
- **LIFO Operations**: Stack-based audit system

## 📁 Project Structure

```
voting_system/
├── config.py                 # Configuration settings
├── database.py               # SQLAlchemy models and setup
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── data_structures/          # Core data structure implementations
│   ├── bloom_filter.py       # Bloom filter with MMH3 hashing
│   ├── merkle_tree.py        # Binary Merkle tree with proofs
│   └── audit_stack.py        # Stack-based audit system
├── services/                 # Business logic layer
│   └── voting_service.py     # Main voting operations
├── utils/                    # Utility functions
│   ├── crypto_utils.py       # Cryptographic operations
│   └── lab_utils.py          # Course lab algorithm implementations
├── static/                   # Frontend assets
│   └── app.js               # JavaScript frontend
├── tests/                    # Test suite
│   └── test_voting_system.py # Comprehensive tests
└── evaluation/               # Performance analysis
    └── performance_tests.py  # Benchmarking and complexity analysis
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd voting_system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost/voting_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
VOTER_SALT=voting-system-salt-2024
DEMO_MODE=true
```

4. **Initialize database**
```bash
# Create PostgreSQL database
createdb voting_db

# Tables will be created automatically on first run
```

5. **Start the application**
```bash
python main.py
```

6. **Access the system**
- Open browser to `http://localhost:8000`
- Use the web interface for all operations

## 📊 Usage Guide

### Admin Operations

1. **Register Voters**
   - Upload CSV file with voter IDs
   - System creates salted hashes for privacy
   - Bloom filter updated for fast lookups

2. **Issue OTACs**
   - Generate one-time access codes
   - Secure mapping to voter hashes
   - Distribute codes to eligible voters

3. **Monitor System**
   - View real-time statistics
   - Check Merkle tree status
   - Review audit trail

### Voter Operations

1. **Cast Vote**
   - Enter OTAC and select candidate
   - System validates eligibility
   - Ballot recorded with Merkle proof

2. **Verify Vote**
   - Use ballot hash to get inclusion proof
   - Client-side verification available
   - Tamper detection through root comparison

### Audit Operations

1. **View Audit Trail**
   - Complete system event log
   - PII-redacted for privacy
   - Chronological event ordering

2. **Verify Integrity**
   - Generate Merkle inclusion proofs
   - Verify ballot authenticity
   - Detect any tampering attempts

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/test_voting_system.py -v
```

### Run Performance Tests
```bash
python evaluation/performance_tests.py
```

This generates:
- `performance_analysis.png` - Performance charts
- `performance_report.txt` - Detailed analysis

### Test Coverage
- Data structure implementations
- Cryptographic functions
- API endpoints
- Integration workflows
- Performance benchmarks

## 📈 Performance Analysis

### Complexity Analysis
- **Merkle Tree Build**: O(n)
- **Merkle Proof Generation**: O(log n)
- **Bloom Filter Operations**: O(1)
- **Hash Table Lookups**: O(1)
- **Stack Operations**: O(1)

### Benchmarking Results
| Operation | 1K Items | 5K Items | 10K Items |
|-----------|----------|----------|-----------|
| Merkle Build | 0.05s | 0.25s | 0.52s |
| Proof Generation | 0.001s | 0.002s | 0.003s |
| Bloom Insert | 0.01s | 0.05s | 0.10s |
| Hash Lookup | 0.001s | 0.001s | 0.001s |

## 🔒 Security Considerations

### Implemented Security
- **Salted Hashing**: Voter ID protection
- **Cryptographic Randomness**: Secure OTAC generation
- **Tamper Evidence**: Merkle tree integrity
- **Input Validation**: All API endpoints protected
- **Rate Limiting**: Configurable request limits

### Security Disclaimers
⚠️ **NOT FOR REAL ELECTIONS** - This is a demonstration system only
- Demo undo functionality compromises immutability
- No advanced cryptographic voting protocols
- Simplified threat model for educational purposes

## 🎓 Educational Value

### Data Structures Demonstrated
1. **Hash Tables**: Voter registry with O(1) operations
2. **Merkle Trees**: Tamper-evident logging with logarithmic proofs
3. **Bloom Filters**: Probabilistic duplicate detection
4. **Stacks**: LIFO audit operations
5. **Lab Algorithms**: Manhattan distance, collinearity, triangular numbers

### Course Integration
This project reuses algorithms from typical CS curriculum:
- **Manhattan Distance**: Polling station assignment
- **Collinearity Checks**: Route visualization
- **Triangular Numbers**: Compact pair indexing
- **Brute Force Algorithms**: Performance comparison baselines

## 📋 API Documentation

### Voter Management
- `POST /api/registerVoters` - Upload voter CSV
- `POST /api/issueOtacs` - Generate access codes

### Voting Operations
- `POST /api/castVote` - Submit ballot
- `GET /api/results` - Current tally
- `GET /api/merkleRoot` - Current root hash

### Audit & Verification
- `POST /api/proof` - Generate inclusion proof
- `POST /api/verifyProof` - Verify proof validity
- `GET /api/auditTrail` - System event log

### System Management
- `GET /api/stats` - System statistics
- `POST /api/undoLast` - Undo operation (demo mode)

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
VOTER_SALT=unique-salt-string
DEMO_MODE=true
BLOOM_FILTER_SIZE=100000
BLOOM_FILTER_HASH_COUNT=7
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Database Schema
- **voters**: Salted voter hashes and voting status
- **ballots**: Ballot records with sequence numbers
- **tally**: Candidate vote counts
- **audit**: System event log
- **leaves**: Merkle tree leaf storage
- **otac_mappings**: OTAC to voter mappings

## 🚀 Deployment

### Local Development
```bash
python main.py
# Access at http://localhost:8000
```

### Production Considerations
- Use proper PostgreSQL instance
- Configure Redis for session management
- Set secure environment variables
- Enable HTTPS in production
- Configure proper logging

## 📊 Evaluation Metrics

### Performance Metrics
- Vote casting latency
- Proof generation time
- Memory usage patterns
- Database query efficiency

### Security Metrics
- Hash collision resistance
- Merkle proof verification
- Bloom filter false positive rates
- Audit trail completeness

## 🤝 Contributing

This is an educational project. Contributions welcome for:
- Additional data structure demonstrations
- Performance optimizations
- Security enhancements
- Documentation improvements

## 📄 License

Educational use only. Not licensed for production voting systems.

## 🙏 Acknowledgments

- Course instructors for data structures curriculum
- FastAPI and SQLAlchemy communities
- Cryptographic libraries used
- Educational resources referenced

---

**Project Status**: ✅ Complete - Ready for demonstration and evaluation

**Demo Script**: 8-minute presentation covering all major features and data structures

**Report Ready**: Performance analysis, complexity evaluation, and security discussion included

---

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
